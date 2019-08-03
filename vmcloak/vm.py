# Copyright (C) 2014-2017 Jurriaan Bremer.
# Copyright (C) 2018 Hatching B.V.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import logging
import os
import subprocess
import time
import re
import codecs
import glob

from vmcloak.abstract import Machinery
from vmcloak.data.config import VBOX_CONFIG
from vmcloak.constants import _VMX_SVGA_TEMPLATE, _VMX_vramsize_DEFAULT,\
    _VMX_HDD_TEMPLATE, _VMX_CDROM, _VMX_ETHERNET, _VMX_MAC, _VMX_VNC, _VMX_FLOPPY
from vmcloak.exceptions import VMWareError, CommandError, VMWareVMXError
from vmcloak.paths import get_path
from vmcloak.rand import random_mac
from vmcloak.repository import vms_path

log = logging.getLogger(__name__)

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
            log.error("[-] Error running command ({0}): {1}".format(e.errno, e.strerror))
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


class VMWare(Machinery):
    """Virtualization layer for VMware Workstation using vmrun utility."""
    FIELDS = {}

    def __init__(self, vmx_path, *args, **kwargs):
        Machinery.__init__(self, *args, **kwargs)
        self.vmrun = get_path("vmrun")
        self.vdiskman = get_path("vmware-vdiskmanager")
        self.ovftool = get_path("ovftool")
        self.vmx_path = vmx_path
        self.vmx_template = os.path.join(os.getcwdu(),
                                "vmcloak/data/template/template.vmx")

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
            log.error("[-] Error running command: %s" % str(e))
            raise CommandError

        return ret.strip()

    def vmx_parse(self):
        vminfo = dict()
        if not self.vmx_path.endswith(".vmx"):
            raise VMWareError("Wrong configuration: vm path not "
                              "ending witht .vmx: %s" % self.vmx_path)

        if not os.path.exists(self.vmx_path):
            raise VMWareError("VMX file %s not found" % self.vmx_path)

        with open(self.vmx_path, 'r') as f:
            content = f.readlines()

        for line in content:
            match = re.search(r'(?P<key>.*)\s=\s(?P<value>.*)', line.rstrip())
            if match:
                key = match.group('key')
                value = match.group('value')
                vminfo[key] = value
        return vminfo

    def wait_for_state(self, shutdown=False):
        while True:
            try:
                status = self.isrunning()
                if shutdown and not status:
                    break
            except CommandError:
                pass

            time.sleep(1)

    def isrunning(self):
        """ Check to see if the VM is running or not """
        vm_list = self._call(self.vmrun, 'list')
        instances = re.findall(r'Total running VMs:\s(\d+)', vm_list)
        running = False
        #import ipdb; ipdb.set_trace()
        if len(instances):
            if int(instances[0]) > 0:
                vm_list = vm_list.splitlines()[1:]
                for vm in vm_list:
                    if os.path.basename(vm) == os.path.basename(self.vmx_path):
                        running = True
        return running

    def exists(self, keyword, value=None):
        """ check the existence of a keyword in VMX config file """
        found = False
        line_num = 0
        pattern = re.compile(r'(?P<keyword>.*)\s=\s"(?P<value>.*)"')
        if keyword:
            try:
                with open(self.vmx_path, 'r+') as f:
                    content = f.readlines()
                    for i, line in enumerate(content):
                        # pass shebang
                        if line.startswith('#!'):
                            continue
                        result = re.match(pattern, line.rstrip())
                        if result:
                            keyword_,value_ = result.group('keyword'), result.group('value')
                        if keyword == keyword_:
                            found = True
                            line_num = line
                            if value is None:
                                value = value_
                            break
            except IOError as e:
                log.error("I/O error: %s"%e)
        return found, line_num, value

    def modifyvm(self, keyword, value, remove=False):
        """On success returns True otherwise False"""
        try:
            with open(self.vmx_path, 'r+') as f:
                content = f.readlines()
                found, line, _ = self.exists(keyword, value)
                # just to get rid of quotes!
                value = re.sub(r'\"(.*)\"', r"\1", value)
                if found:
                    content[content.index(line)] = re.sub(r'"(.*)"', '\"%s\"' % value, line)
                if not found:
                    attribute = "{0} = \"{1}\"\n".format(keyword, value)
                    content.append(attribute)
                f.seek(0)
                f.truncate()
                f.write(''.join(content))
                return True
        except IOError as e:
            log.error("I/O error: %s"%str(e))
            return False

    def readvar(self, name, var_type="runtimeConfig"):
        """ Reads a variable from the virtual machine state or
        runtime configuration as stored in the .vmx file"""
        if self.isrunning():
            return self._call(self.vmrun, 'readVariable', self.vmx_path, var_type, name)
        else:
            found, _, value = self.exists(name)
            if found:
                return value
            else:
                log.error("value not found")
                return None

    # deprecated: not working while VM is not running!
    def writevar(self, name, value, var_type="runtimeConfig"):
        """ Writes a variable to the virtual machine state or guest. """
        return self._call(self.vmrun, 'writeVariable', self.vmx_path, var_type, name, value)

    def batchmodify(self, items):
        item_dict = dict([item.split(" = ") for item in items.strip().split("\n")])
        try:
            for key, value in item_dict.items():
                self.modifyvm(key, value)
        except VMWareVMXError as e:
            log.error("[-] Error running command: %s" % str(e))
            return False

    def vminfo(self, element=None):
        """Returns a dictionary with all available information for the
        Virtual Machine."""
        vminf = self.vmx_parse()
        if element is not None:
            try:
                value = vminf[element].replace("\"","")
                if value.isdigit():
                    return int(value)
                if value == "TRUE":
                    return True
                if value == "FALSE":
                    return False
                else:
                    return value
            except KeyError as e:
                log.error("[-] Error running command: %s" % str(e))
                return None
        else:
            return vminf

    def create_vm(self):
        """Create a new Virtual Machine."""
        with open(self.vmx_template, "r") as f:
            vmx_tmp = f.read()
            with codecs.open(self.vmx_path, "w", "utf-8") as fh:
                content = vmx_tmp.format(**{"displayName": self.name, "guestOS":
                                            "", "name": self.name, "vmdk_path":
                                            ""})
                fh.write(content)

    def delete_vm(self):
        """Delete an existing Virtual Machine and its associated files."""
        if self.isrunning():
            self.stop_vm()
        return self._call(self.vmrun, 'deleteVM', self.vmx_path)

    def ramsize(self, ramsize):
        """Modify the amount of RAM available for this Virtual Machine."""
        reminder = ramsize % 4 # RAM-size should be a multiple of 4
        if reminder != 0:
            ramsize -= reminder
        return self.modifyvm('memsize', str(ramsize))

    def vramsize(self, width=1920, height=1080):
        """Modify the amount of Video memory available for this Virtual
        Machine."""
        mem_req = width * height * 4
        if mem_req > _VMX_vramsize_DEFAULT:
            vram_size = mem_req
        else:
            vram_size = _VMX_vramsize_DEFAULT

        data = {
            'reso_height': height,
            'reso_width': width,
            'vram_size': vram_size
        }

        vram_items = _VMX_SVGA_TEMPLATE % data
        item_dict = dict([item.split(" = ") for item in vram_items.strip().split("\n")])

        try:
            for key, value in item_dict.items():
                self.modifyvm(key, value)
        except VMWareVMXError as e:
            log.error("[-] Error running command: %s" % str(e))
            return False

        return True

    def os_type(self, osversion):
        """Set the OS type."""
        # http://sanbarrow.com/vmx/vmx-guestos.html
        operating_systems = {
            "winxp": "winxphome",
            "win7x86": "windows7",
            "win7x64": "windows7-64",
            "win81x86": "windows8",
            "win81x64": "windows8-64",
            "win10x86": "windows9",
            "win10x64": "windows9-64",
        }
        return self.modifyvm('guestOS', operating_systems[osversion])

    # https://www.vmware.com/pdf/VirtualDiskManager.pdf
    def create_hd(self, hdd_path, virtual_dev="lsisas1068", fsize="10GB",
                  adapter_type='lsilogic', disk_type='1'):
        """Create a harddisk.
            0- create a growable virtual disk contained in a single file (monolithicsparse)
            1-create a growable virtual disk split in to 2GB files (splitsparse)
            2-create a preallocated virtual disk contained in a single file (monolithicflat)
            3-create a preallocated virtual disk split into 2GB files (splitflat)
            4-create a preallocated virtual disk compatible with ESXserver (VMFSflat)
            5-create a compressed disk optimized for streaming.
            -----------------------
            scsi0:0.deviceType = "plainDisk"
            scsi0:0.deviceType = "PhysicalDrive0"
            scsi0:0.deviceType = "rawDisk"
            scsi0:0.deviceType = "scsi-hardDisk"
            scsi0:0.deviceType = "scsi-passthru"
            scsi0:0.deviceType = "scsi-nonpassThru-rdm"
            scsi0:0.deviceType = "scsi-passthru"
            scsi0:0.deviceType = "scsi-passThru-rdm"
            ------------------------
            scsi0.virtualDev = "buslogic" -> BusLogic SCSI
            scsi0.virtualDev = "lsilogic" -> LSI Logic SCSI
            scsi0.virtualDev = "lsisas1068" -> LSI Logic SAS
            scsi0.virtualDev = "pvscsi" -> VMware Paravirtual SCSI
            ------------------------
        """
        #import ipdb; ipdb.set_trace()
        guestOS = self.vminfo("guestOS")
        if not any(s in fsize for s in ('GB', 'MB', 'KB')):
            raise CommandError('hdd_size should contain size specifier: %s' % fsize)
        if not any(a in adapter_type for a in ('ide', 'buslogic', 'lsilogic')):
            raise CommandError('adapter type is not valid: %s' % adapter_type)
        # sparse = 0 / flat = 2 disk_type
        if not any(str(dt) in disk_type for dt in range(6)):
            raise CommandError('disk type is not valid: %s' % disk_type)
        #if self.vminfo("guestOS") == "winxppro":
        #    # change default value function by messing with *func_defaults*
        #    defaults_lst = list(self.create_hd.__func__.func_defaults)
        #    defaults_lst[defaults_lst.index(adapter_type)] = "buslogic"
        #    self.create_hd.__func__.func_defaults = tuple(defaults_lst)
        if "64" in guestOS and adapter_type == "buslogic":
            log.error("BusLogic SCSI controllers are not supported on 64-bit\
                      virtual machines.")
            adapter_type = "lsislogic"
        disk_path = re.findall(r'(.*).vmdk', hdd_path)[0]+"*"
        files = glob.glob(disk_path)
        if files:
            log.debug("disk already exists.. removing")
            for f in files:
                os.remove(f)
        ret = self._call(self.vdiskman, '-c', '-t', disk_type, '-s', fsize, '-a'
                         , adapter_type, hdd_path)
        if ret:
            # attach created vmdk to vmx file
            data = {
                'adapter_type': "scsi" if guestOS != "winxphome" else "ide",
                'vmdk_path': hdd_path,
                'virtual_dev': virtual_dev,
                #'mode': 'independent-persistent' if adapter_type is 'ide' else 'persistent'
            }
            content = _VMX_HDD_TEMPLATE % data
            self.batchmodify(content)
        else:
            return ret

    def upgrade_vm(self):
        if self.isrunning():
            self.stop_vm()
        self._call(self.vmrun, "upgradevm", self.vmx_path)

    def mount_floppy(self, image, present=True):
        floppy_config = _VMX_FLOPPY.format(**{'file_type': 'file',
                                             'file_name':os.path.abspath(image), 'present':
                                             "TRUE" if present else "FALSE"})
        return self.batchmodify(floppy_config)

    # https://communities.vmware.com/thread/389673
    def immutable_hd(self, adapter_type, mode="persistent"):
        """Make a harddisk immutable or normal."""
        if not any(m in mode.lower() for m in ('persistent', 'nonpersistent', 'undoable')):
            raise CommandError('hdd disk mode is not valid: %s' % mode)
        keyword = "%s0:0.mode" % adapter_type
        return self.modifyvm(keyword, mode)

    def remove_hd(self, hdd_path):
        """Remove a harddisk."""
        if not os.path.exists(hdd_path):
            return False
        cmd = ['rm', '-rf', hdd_path]
        try:
            log.debug("Running command: %s", cmd)
            ret = subprocess.check_output(cmd)
        except Exception as e:
            log.error("[-] Error running command: %s" % str(e))
            raise CommandError
        if ret == 0:
            return True

    def clone_hd(self, hdd_outpath):
        """Clone a harddisk."""
        self._call(self.ovftool, self.vmx_path, hdd_outpath)

    def compact_hd(self, hdd_path):
        # We first make the HDD "more" compact - this should be basically
        # defragmenting it.
        self._call(self.vdiskman, "-d", hdd_path)

    def cpus(self, count):
        """Set the number of CPUs to assign to this Virtual Machine."""
        self.modifyvm('numvcpus', str(count))

    # http://www.sanbarrow.com/vmx/vmx-cd-settings.html
    def attach_iso(self, iso, adapter_type="sata"):
        """
        Attach a ISO file as DVDRom drive.
        ----------------------------------
        scsi0:0.deviceType = "cdrom-image"
        scsi0:0.deviceType = "atapi-cdrom"
        scsi0:0.deviceType = "cdrom-raw"
        """
        iso_config = _VMX_CDROM.format(**{'dev_type': 'cdrom-image',
                                          'filename':iso, 'adapter_type': adapter_type})
        #if adapter_type == "sata":
        #    iso_config + 'sata0.present = "TRUE"\n'
        return self.batchmodify(iso_config)

    def detach_iso(self, adapter_type="sata"):
        """Detach the ISO file in the DVDRom drive."""
        time.sleep(1)
        iso_config = _VMX_CDROM.format(**{'dev_type': 'cdrom-raw',
                                          'filename':'auto detect',
                                          'adapter_type': adapter_type})
        return self.batchmodify(iso_config)

    # http://sanbarrow.com/vmx/vmx-network-advanced.html
    def modify_mac(self, macaddr=None, index=0):
        """Modify the MAC address of a Virtual Machine."""
        if macaddr is None:
            macaddr = random_mac()
        # VMRun accepts MAC addressed to be out-of-range
        mac_config = _VMX_MAC.format(**{'index': index, 'addr_type': 'static', 'mac_addr':macaddr})
        return self.batchmodify(mac_config)

    def network_index(self):
        """Get the index for the next network interface."""
        ret = self.network_idx
        self.network_idx += 1
        return ret

    # TODO: check existence of vboxnet1 iface on windows OS
    # http://www.sanbarrow.com/vmx/vmx-network.html
    def hostonly(self, nictype="e1000", macaddr=None, adapter=None):
        index = self.network_index()
        if not adapter:
            if os.name == "posix":
                adapter = "vmnet1"
            else:
                adapter = "VMWare Host-Only Ethernet Adapter"

        # Ensure our hostonly interface is actually up and running.
        if subprocess.check_output(['cat', '/sys/class/net/vmnet1/operstate']).strip() != "unknown":
            log.error("Have you configured %s?", adapter)
            log.info("Please refer to the documentation to configure it.")
            log.info("Also, please take case of signing vmmon and vmnet drivers on secure boot OS.")
            return False

        hostonly_config = _VMX_ETHERNET.format(**{'index': index, 'vdev': nictype, 'conn_type': 'hostonly'})
        self.batchmodify(hostonly_config)
        return self.modify_mac(macaddr, index)

    # TODO: check existence of vboxnet1 iface on windows OS
    # http://www.sanbarrow.com/vmx/vmx-network.html
    def nat(self, nictype="e1000", macaddr=None, adapter=None):
        """Configure NAT for the Virtual Machine."""
        index = self.network_index()
        if not adapter:
            if os.name == "posix":
                adapter = "vmnet8"
            else:
                adapter = "VMWare NAT Ethernet Adapter"
        # Ensure our hostonly interface is actually up and running.
        if subprocess.check_output(['cat', '/sys/class/net/vmnet8/operstate']).strip() != "unknown":
            log.error("Have you configured %s?", adapter)
            log.info("Please refer to the documentation to configure it.")
            log.info("Also, please take case of signing vmmon and vmnet drivers on secure boot OS.")
            return False
        nat_config = _VMX_ETHERNET.format(**{'index': index, 'conn_type': 'nat', 'vdev': nictype})
        self.batchmodify(nat_config)
        return self.modify_mac(macaddr, index)

    def hwvirt(self, enable=True):
        """Enable or disable the usage of Hardware Virtualization."""
        if enable:
            self.modifyvm("vhv.enable", "TRUE")
        else:
            self.modifyvm("vhv.enable", "FALSE")

    def start_vm(self, visible=False):
        """Start the associated Virtual Machine."""
        self._call(self.vmrun, "start", self.vmx_path, "gui" if visible else "nogui")

    def list_snapshots(self):
        """ Returns a list of snapshots for the specific VMX file """
        return self._call(self.vmrun, "listSnapshots", self.vmx_path)

    def snapshot(self, label):
        """Take a snapshot of the associated Virtual Machine.
        IF the VM was ON then VMWare by default put it on a suspended state,
        that's why we turn it on again!"""
        self._call(self.vmrun, "snapshot", self.vmx_path, label)

    def restore_snapshot(self, label=None):
        """ Revert to the latest snapshot available """
        if label:
            self._call(self.vmrun, "revertToSnapshot", self.vmx_path, label)
        else:
            try:
                self._call(self.vmrun, "revertToSnapshot", self.vmx_path, self.list_snapshots()[-1])
            except IndexError:
                log.error("There's no snapshot exists for the VM at %s" % self.vmx_path)
        self.start_vm()

    def delete_snapshot(self, label, recursive=False):
        if recursive:
            self._call(self.vmrun, "deleteSnapshot", self.vmx_path, label, "andDeleteChildren")
        else:
            self._call(self.vmrun, "deleteSnapshot", self.vmx_path, label)

    def stop_vm(self, powertype="hard"):
        """Stop the associated Virtual Machine."""
        self._call(self.vmrun, "stop", self.vmx_path, powertype)

    def remotedisplay(self, port=5901, password=""):
        if len(password) < 8:
            log.info("You should provide a password at least 8 characters long.")
        vnc_config = _VMX_VNC.format(**{'password': password, 'port': port})
        self.batchmodify(vnc_config)

    # http://wiki.osx86project.org/wiki/index.php/Virtualization
    def enableparavirt(self):
        self.modifyvm("vmi.present", "TRUE")

    # https://www.virtuallyghetto.com/2019/01/quick-tip-import-ovf-ova-as-vm-template-using-ovftool-4-3-update-1.html
    def export(self, filepath):
        if self.isrunning():
            self.stop_vm()
        if filepath.split('.')[-1] != "ovf":
            filepath += ".ovf"
        return self._call(self.ovftool, "--acceptAllEulas",
                          "--allowAllExtraConfig", "--compress=9", self.vmx_path, filepath)
