# Copyright (C) 2014-2017 Jurriaan Bremer.
# Copyright (C) 2018 Hatching B.V.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import logging
import os
import subprocess
import time
import libvirt
import xml.etree.ElementTree as ET

from string import ascii_letters

from vmcloak.abstract import Machinery
from vmcloak.data.config import VBOX_CONFIG
from vmcloak.exceptions import CommandError
from vmcloak.paths import get_path
from vmcloak.rand import random_mac
from vmcloak.repository import vms_path
from vmcloak.vmxml import Element
from vmcloak.constants import SNAPSHOT_XML_TEMPLATE

log = logging.getLogger(__name__)
logging.getLogger('libvirt').setLevel(logging.WARNING)

class VirtualBox(Machinery):
    FIELDS = VBOX_CONFIG

    def __init__(self, *args, **kwargs):
        Machinery.__init__(self, *args, **kwargs)
        self.vboxmanage = get_path("vboxmanage")

    def _call(self, *args, **kwargs):
        cmd = [self.vboxmanage] + list(args)

        for k, v in kwargs.items():
            if v is None or v is True:
                cmd += ["--" + k]
            else:
                cmd += ["--" + k.rstrip("_"), str(v)]

        try:
            log.debug("Running command: %s", cmd)
            ret = subprocess.check_output(cmd)
        except Exception as e:
            log.error("[-] Error running command: %s", e)
            raise CommandError

        return ret.strip()

    def vminfo(self, element=None):
        ret = {}
        lines = self._call("showvminfo", self.name, machinereadable=True)
        for line in lines.split("\n"):
            key, value = line.split("=", 1)

            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            elif value.isdigit():
                value = int(value)

            if key.startswith('"') and key.endswith('"'):
                key = key[1:-1]

            ret[key] = value
        return ret if element is None else ret.get(element)

    def wait_for_state(self, shutdown=False):
        while True:
            try:
                status = self.vminfo("VMState")
                if shutdown and status == "poweroff":
                    break
            except CommandError:
                pass

            time.sleep(1)

    def create_vm(self):
        return self._call("createvm", name=self.name,
                          basefolder=vms_path, register=True)

    def delete_vm(self):
        self._call("unregistervm", self.name, delete=True)

    def ramsize(self, ramsize):
        return self._call("modifyvm", self.name, memory=ramsize)

    def vramsize(self, vramsize):
        return self._call("modifyvm", self.name, vram=vramsize)

    def os_type(self, osversion):
        operating_systems = {
            "winxp": "WindowsXP",
            "win7x86": "Windows7",
            "win7x64": "Windows7_64",
            "win81x86": "Windows81",
            "win81x64": "Windows81_64",
            "win10x86": "Windows10",
            "win10x64": "Windows10_64",
        }
        return self._call("modifyvm", self.name,
                          ostype=operating_systems[osversion])

    def create_hd(self, hdd_path, fsize=256*1024):
        self._call("createhd", filename=hdd_path, size=fsize)
        self._call("storagectl", self.name, name="IDE", add="ide")
        self._call("storageattach", self.name, storagectl="IDE",
                   type_="hdd", device=0, port=0, medium=hdd_path)

    def attach_hd(self, hdd_path, multi=False):
        # When a harddisk is not attached to a Virtual Machine it will quickly
        # be forgotten. This seems to be within a couple of seconds. When this
        # happens, its "type" (multiattach in our case) is also forgotten,
        # resulting in issues when cloning. Therefore we quickly set its state
        # before attaching it to a Virtual Machine, hoping this approach
        # is "good enough".
        self._call("storagectl", self.name, name="IDE", add="ide")
        if multi:
            self._call("modifyhd", hdd_path, type_="multiattach")
        else:
            self._call("modifyhd", hdd_path, type_="normal")
        self._call("storageattach", self.name, storagectl="IDE",
                   type_="hdd", device=0, port=0, medium=hdd_path)

    def compact_hd(self, hdd_path):
        # We first make the HDD "more" compact - this should be basically
        # defragmenting it.
        self._call("modifyhd", hdd_path, compact=True)

    def clone_hd(self, hdd_inpath, hdd_outpath):
        self._call("clonehd", hdd_inpath, hdd_outpath)

    def remove_hd(self):
        time.sleep(1)
        self._call("storagectl", self.name, portcount=0,
                   name="IDE", remove=True)

    def cpus(self, count):
        self._call("modifyvm", self.name, cpus=count, ioapic="on")

    def attach_iso(self, iso_path):
        """Mount an ISO to the Virtual Machine."""
        self._call("storageattach", self.name, storagectl="IDE",
                   type_="dvddrive", port=1, device=0, medium=iso_path)

    def detach_iso(self):
        time.sleep(1)
        self._call("storageattach", self.name, storagectl="IDE",
                   type_="dvddrive", port=1, device=0, medium="emptydrive")

    def set_field(self, key, value):
        return self._call("setextradata", self.name, key, value)

    def modify_mac(self, macaddr=None, index=1):
        if macaddr is None:
            macaddr = random_mac()

        # VBoxManage prefers MAC addresses without colons.
        vbox_mac = macaddr.replace(":", "")

        mac = {"macaddress%d" % index: vbox_mac}
        self._call("modifyvm", self.name, **mac)
        return macaddr

    def hostonly(self, nictype, macaddr=None, adapter=None):
        index = self.network_index() + 1
        if not adapter:
            if os.name == "posix":
                adapter = "vboxnet0"
            else:
                adapter = "VirtualBox Host-Only Ethernet Adapter"

        # Ensure our hostonly interface is actually up and running.
        if adapter not in self._call("list", "hostonlyifs"):
            log.error("Have you configured %s?", adapter)
            log.info("Please refer to the documentation to configure it.")
            return False

        nic = {
            "nic%d" % index: "hostonly",
            "nictype%d" % index: nictype,
            "nicpromisc%d" % index: "allow-all",
            "hostonlyadapter%d" % index: adapter,
            "cableconnected%d" % index: "on",
        }
        self._call("modifyvm", self.name, **nic)
        return self.modify_mac(macaddr, index)

    def nat(self, nictype, macaddr=None):
        index = self.network_index() + 1

        nic = {
            "nic%d" % index: "nat",
            "nictype%d" % index: nictype,
            "nicpromisc%d" % index: "allow-all",
        }
        self._call("modifyvm", self.name, **nic)
        return self.modify_mac(macaddr, index)

    def hwvirt(self, enable=True):
        """Enable or disable the usage of Hardware Virtualization."""
        self._call("modifyvm", self.name, hwvirtex="on" if enable else "off")

    def start_vm(self, visible=False):
        return self._call("startvm", self.name,
                          type_="gui" if visible else "headless")

    def snapshot(self, label, description=""):
        return self._call("snapshot", self.name, "take", label,
                          description=description, live=True)

    def restore_snapshot(self, label=None):
        if label:
            return self._call("snapshot", self.name, "restore", label)
        else:
            return self._call("snapshot", self.name, "restorecurrent")

    def delete_snapshot(self, label):
        return self._call("snapshot", self.name, "delete", label)

    def stopvm(self):
        return self._call("controlvm", self.name, "poweroff")

    def list_settings(self):
        return self._call("getextradata", self.name, "enumerate")

    def mouse(self, type):
        return self._call("modifyvm", self.name, mouse=type)

    def vrde(self, port=3389, password=""):
        return self._call("modifyvm", self.name, vrde="on", vrdeport=port,
                          vrdeproperty="VNCPassword=%s" % password)

    def paravirtprovider(self, provider):
        return self._call("modifyvm", self.name, paravirtprovider=provider)

    def export(self, filepath):
        return self._call(
            "export", self.name, "--output", filepath, "--vsys", "0",
            product="VMCloak",
            producturl="http://vmcloak.org/",
            vendor="Cuckoo Sandbox",
            vendorurl="http://cuckoosandbox.org/",
            description="Cuckoo Sandbox Virtual Machine created by VMCloak",
        )


class KVM(Machinery):
    """Virtualization layer for KVM using libvirt utility."""
    FIELDS = {}

    def __init__(self, domain_path, *args, **kwargs):
        Machinery.__init__(self, *args, **kwargs)
        self.virsh = get_path("virsh")
        self.qemu_img = get_path("qemu-img")
        self.virt_install = get_path("virt-install")
        self.domain_path = domain_path

        if os.getenv("LIBVIRT_DEFAULT_URI"):
            self.QEMU_URI = os.getenv("LIBVIRT_DEFAULT_URI")
        else:
            self.QEMU_URI = "qemu:///system"

        self.virt_conn = libvirt.open(self.QEMU_URI)

        if self.virt_conn == None:
            log.error('Failed to open connection to qemu:///system')
            exit(1)

    def _call(self, *args, **kwargs):
        cmd = list(args)

        for k, v in kwargs.items():
            if v is None or v is True:
                cmd += ["--" + k]
            else:
                cmd += ["--" + k.rstrip("_"), str(v)]

        try:
            log.debug("Running command: %s", cmd)
            ret = subprocess.check_output(cmd)
        except Exception as e:
            log.error("[-] Error running command ({0}): {1}".format(" ".join(e.cmd), e.output.strip()))
            raise CommandError

        return ret.strip()


    def vminfo(self, element=None):
        """Returns a dictionary with all available information for the
        Virtual Machine."""
        raise

    def create_vm(self):
        """Create a new Virtual Machine."""
        if os.path.exists(self.domain_path):
            xml = open(self.domain_path).read()
        else:
            xml = self._call(self.virt_install, '--virt-type', self.virt_type,
                    '--name', self.name, '--os-type', self.os_type,
                    '--os-variant', self.os_variant, '--disk', self.disk_path,
                        '--print-xml', '--memory', '1024')
        self.domain = ET.fromstring(xml)

    def delete_vm(self):
        """Delete an existing Virtual Machine and its associated files."""
        return self._call(self.virsh, 'destroy', self.name)

    def ramsize(self, ramsize, unit='MiB'):
        """Modify the amount of RAM available for this Virtual Machine."""
        ram = self.domain.find('.//memory')
        if ram is not None:
            ram.text = str(ramsize)
            ram.attrib['unit'] = unit

    def vramsize(self, vramsize, vtype='qxl'):
        """Modify the amount of Video memory available for this Virtual
        Machine.
        <devices>
        <video>
            <model type='qxl' vram='16384' heads='1' primary='yes'>
                <acceleration accel3d='yes' accel2d='yes'/>
            </model>
        </video>
        </devices>
        """
        devices = self.domain.find('.//devices')
        video = self.domain.find('.//devices/video')
        if video is None:
            video = Element('video')
            modelAttrs = {
                'type': vtype,
                'vram': str(vramsize),
                'heads': '1',
                'primary': 'yes'
            }
            model = Element('model', **modelAttrs)
            video.appendChild(model)
            acceleration = Element('acceleration', accel2d="yes", accel3d="yes")
            model.appendChild(acceleration)
            devices.insert(0, video)
        else:
            try:
                model = video.iter('model').next()
                model.attrib['vram'] = str(vramsize)
            except StopIteration:
                log.debug('corrupted video element found!')
                exit(1)

    def wait_for_state(self, shutdown=False):
        while True:
            try:
                dom = self.virt_conn.lookupByName(self.name)
                state, reason = dom.state()
                if shutdown and state == libvirt.VIR_DOMAIN_SHUTOFF or \
                                    state == libvirt.VIR_DOMAIN_SHUTDOWN:
                    break
                if state == libvirt.VIR_DOMAIN_REBOOT_DEFAULT:
                    self.detach_iso()
            except CommandError:
                pass

            time.sleep(1)

    def os_type(self, osversion, ostype='windows', virttype='kvm'):
        """Set the OS type."""
        operating_systems = {
            "winxpx86": "winxp",
            "winxpx64": "winxp64",
            "win7x86": "win7",
            "win7x64": "win7",
            "win81x86": "win8.1",
            "win81x64": "win8.1",
            "win10x86": "win10",
            "win10x64": "win10",
        }
        self.os_type = ostype
        self.os_variant = operating_systems[osversion]
        self.virt_type = virttype


    def create_hd(self, disk_path, fmt='qcow2', size='20G'):
        """Create a harddisk."""
        self.disk_path = disk_path
        self._call(self.qemu_img, 'create', '-f', fmt, disk_path, size)

    def compact_hd(self, hdd_path, dtype='qcow2'):
        # We first make the HDD "more" compact - this should be basically
        # defragmenting it.
        disk_name = os.path.basename(hdd_path).split('.')[0]
        out_path = os.path.join(os.path.dirname(hdd_path),
                                disk_name+"_compact.qcow2")
        self._call(self.qemu_img, 'convert', '-O', dtype, '-c', hdd_path, out_path)

    def attach_hd(self, path, disk_format='qcow2', bus='virtio'):
        if os.path.exists(os.path.abspath(path)):
            self.disk_opt = "%s,format=%s,bus=%s"%(path, disk_format, bus)


    def immutable_hd(self, adapter_type, mode="persistent"):
        """Make a harddisk immutable or normal."""
        raise

    def remove_hd(self, hdd_path):
        """Remove a harddisk."""
        raise

    def clone_hd(self, hdd_outpath):
        """Clone a harddisk."""
        raise

    def cpus(self, count):
        """Set the number of CPUs to assign to this Virtual Machine."""
        vcpu = self.domain.find('.//vcpu')
        if vcpu is not None:
            vcpu.text = str(count)

    def attach_iso(self, iso, override=False):
        """Attach a ISO file as DVDRom drive."""
        cdrom = self.domain.findall(".//devices/disk[@device='cdrom']")
        boot_order = self.domain.findall(".//os/boot")
        if len(boot_order) > 1:
            if boot_order[0].attrib['dev'] == 'cdrom':
                log.info("load from CDROM.")
        else:
            cdrom = Element('boot', dev='cdrom')
            self.domain.find('.//os').insert(1, cdrom)
        dev_name = 'hdb'
        if cdrom is not None:
            idx = len(cdrom)
            dev_name = 'hd'+ascii_letters[idx+1]
        devices = self.domain.find('.//devices')
        if cdrom is None or not override:
            cdrom = Element('disk', type='file', device='cdrom')
            cdrom.appendChildWithArgs('driver', name='qemu', type='raw')
            cdrom.appendChildWithArgs('source', file=iso)
            cdrom.appendChildWithArgs('target', dev=dev_name, bus='ide')
            devices.insert(0, cdrom)
        else:
            try:
                source = cdrom.iter('source').next()
                source.attrib['file'] = iso
            except StopIteration:
                source = Element('source', file=iso)
                cdrom.insert(0, source)

    def detach_iso(self):
        """Detach the ISO file in the DVDRom drive."""
        boot_cdrom = self.domain.find(".//os/boot[@dev='cdrom']")
        if boot_cdrom is not None:
            self.domain.find(".//os").remove(boot_cdrom)
        cdrom = self.domain.find(".//devices/disk[@device='cdrom']")
        source = cdrom.iter('source').next()
        source.attrib['file'] = ""

    def set_field(self, key, value):
        """Set a specific field of a Virtual Machine."""
        raise

    def modify_mac(self, interface, macaddr=None):
        """Modify the MAC address of a Virtual Machine."""
        if macaddr is None:
            macaddr = random_mac()
        if isinstance(interface, Element):
            return interface.appendChildWithArgs('mac', address=macaddr)
        else:
            mac = interface.iter('mac').next()
            mac.attrib['address'] = macaddr
            return

    def network_index(self):
        """Get the index for the next network interface."""
        ret = self.network_idx
        self.network_idx += 1
        return ret

    def dumpXML(self):
        return ET.dump(self.domain)

    def hostonly(self, nictype="rtl8139", macaddr=None, adapter='virbr'):
        """Configure hostonly for the Virtual Machine.
        <interface type="bridge">
            <source bridge="virbr0"/>
            <mac address="52:54:00:fe:b3:c0"/>
        </interface>
        """
        devices = self.domain.find('.//devices')
        interface = self.domain.find('.//devices/interface')
        index = self.network_index()
        if interface is None:
            interface = Element('interface', type='network')
            interface.appendChildWithArgs('model', type=nictype)
            interface.appendChildWithArgs('source', bridge=adapter+str(index))
            interface = self.modify_mac(interface, macaddr)
            devices.insert(0, interface)
        else:
            interface.attrib['type'] = 'bridge'
            self.modify_mac(interface, macaddr)
            try:
                model = interface.iter('model').next()
                model.attrib['type'] = nictype
            except StopIteration:
                model = Element('model', type=nictype)
                interface.insert(0, model)
            try:
                source = interface.iter('source').next()
                source.attrib['bridge'] = adapter+str(index)
                #source.attrib['network'] = 'default'
            except StopIteration:
                source = Element('source', bridge=adapter+str(index))
                #source = Element('source', network='default')
                interface.insert(0, source)


    def nat(self, nictype="e1000", macaddr=None, adapter=None):
        """Configure NAT for the Virtual Machine."""
        raise

    def hwvirt(self, enable=True):
        """Enable or disable the usage of Hardware Virtualization."""
        raise

    def start_vm(self, visible=False):
        """Start the associated Virtual Machine."""
        # save finalized domain before start
        try:
            self.dom = self.virt_conn.lookupByName(self.name)
            state, reason = self.dom.state()
            if state == libvirt.VIR_DOMAIN_RUNNING:
                log.error('VM %s is already running!'%self.name)
            else:
                self.dom.create()
        except libvirt.libvirtError:
            self.dom = self.virt_conn.defineXML(ET.tostring(self.domain))
            self.dom.create()

    def sysinfo(self, element_dict):
        if isinstance(element_dict, dict):
            sysinfo = Element('sysinfo', type='smbios')
            for k, v in element_dict.items():
                elements = k.split('.')
                child = sysinfo.find('.//%s'%elements[0])
                if child is None:
                    child = Element(elements[0])
                # maximum recursion depth exceeded while calling a Python
                # object!!
                #if not isinstance(child, Element):
                #    child.__class__ = Element
                if not isinstance(child, Element):
                    e = Element('entry', name=elements[1], text=v)
                    child.append(e)
                else:
                    if isinstance(v, list):
                        for value in v:
                            child.appendChildWithArgs('entry', text=value)
                    else:
                        child.appendChildWithArgs('entry', name=elements[1] , text=v)
                sysinfo.append(child)
            self.domain.append(sysinfo)
        else:
            log.error("Wrong format for sysinfo element!")

    def save_domain(self):
        open(self.domain_path, 'w').write(ET.tostring(self.domain))

    def list_snapshots(self):
        """ Returns a list of snapshots for the specific VMX file """
        return self.dom.snapshotListNames()

    def snapshot(self, label):
        """Take a snapshot of the associated Virtual Machine."""
        snap_xml = SNAPSHOT_XML_TEMPLATE.format(**{'snapshot_name': label})
        self.dom.snapshotCreateXML(snap_xml, libvirt.VIR_DOMAIN_SNAPSHOT_CREATE_ATOMIC)

    def restore_snapshot(self, label=None):
        """ Revert to the latest snapshot available """
        if label in self.list_snapshots():
            flag = libvirt.VIR_DOMAIN_SNAPSHOT_REVERT_RUNNING
            self.dom.revertToSnapshot(label, flag)
        else:
            log.error("Snapshot %s doesn't exist."%label)

    def delete_snapshot(self, label, recursive=False):
        raise

    def disk_stats(self):
        disk_stats = dict()
        disk_path = self.domain.find(".//devices/disk[@device='disk']/source").get('file')
        if disk_path is not None:
            rd_req, rd_bytes, wr_req, wr_bytes, err = self.dom.blockStats(disk_path)
            disk_stats['rd_req'] = rd_req
            disk_stats['rd_bytes'] = rd_bytes
            disk_stats['wr_req'] = wr_req
            disk_stats['wr_bytes'] = wr_bytes
            return disk_stats

    def stopvm(self, powertype="soft"):
        """Stop the associated Virtual Machine."""
        self.dom.shutdownFlags(0)

    def remotedisplay(self, port=5901, password=""):
        """ Provides a VNC/RDP interface for GUI communication over the network """
        devices = self.domain.find('.//devices')
        graphics = self.domain.find('.//devices/graphics')
        if graphics is None:
            graphics = Element('graphics', type='vnc', port=port,
                                passwd=password)
            devices.insert(0, graphics)
        else:
            graphics.attrib['port'] = port
            graphics.attrib['passwd'] = password

    def enableparavirt(self):
        raise

    def export(self, filepath):
        raise

