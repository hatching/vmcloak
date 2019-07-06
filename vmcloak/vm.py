# Copyright (C) 2014-2017 Jurriaan Bremer.
# Copyright (C) 2018 Hatching B.V.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import logging
import os
import subprocess
import time
import re

from vmcloak.abstract import Machinery
from vmcloak.data.config import VBOX_CONFIG
from vmcloak.constants import _VMX_SVGA_TEMPLATE, _VMX_vramsize_DEFAULT,\
    _VMX_HDD_TEMPLATE, _VMX_CDROM, _VMX_ETHERNET, _VMX_MAC, _VMX_VNC
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


class VMware(Machinery):
    """Virtualization layer for VMware Workstation using vmrun utility."""
    FIELDS = {}

    def __init__(self, vmx_path, *args, **kwargs):
        Machinery.__init__(self, *args, **kwargs)
        self.vmrun = get_path("vmrun")
        self.vdiskman = get_path("vmware-vdiskmanager")
        self.ovftool = get_path("ovftool")
        self.vmx_path = vmx_path

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
            log.error("[-] Error running command ({0}): {1}".format(e.errno, e.strerror))
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

    def modifyvm(self, keyword, value, remove=False):
        """On success returns True otherwise False"""
        if keyword and value:
            try:
                with open(self.vmx_path, 'w') as f:
                    content = f.readlines()
                    for i, line in enumerate(content):
                        keyword_ = re.findall(r'(.*)\s=', line.rstrip())[0]
                        if keyword in keyword_:
                            content[i] = re.sub(r'"(.*)"', '\"%s\"' % value, line)
                        else:
                            return False
                    f.write(content)
                    return True
            except IOError as e:
                log.error("I/O error ({0}): {1}".format(e.errno, e.strerror))
                self.writevar(keyword, value)
        else:
            return False

    def readvar(self, name, var_type="runtimeConfig"):
        """ Reads a variable from the virtual machine state or
        runtime configuration as stored in the .vmx file"""
        return self._call(self.vmrun, 'readVariable', self.vmx_path, var_type, name)

    def writevar(self, name, value, var_type="runtimeConfig"):
        """ Writes a variable to the virtual machine state or guest. """
        return self._call(self.vmrun, 'writeVariable', self.vmx_path, var_type, name, value)

    def vminfo(self, element=None):
        """Returns a dictionary with all available information for the
        Virtual Machine."""
        vminf = self.vmx_parse()
        if element is not None:
            try:
                return vminf[element]
            except KeyError as e:
                log.error("vminfo error ({0}): {1}".format(e.errno, e.strerror))
                return None
        else:
            return vminf

    def create_vm(self):
        """Create a new Virtual Machine."""
        # displayName = "angr-dev"
        # guestOS = "ubuntu-64"
        return self._call("createvm", name=self.name,
                          basefolder=vms_path, register=True)

    def delete_vm(self):
        """Delete an existing Virtual Machine and its associated files."""
        return self._call(self.vmrun, 'deleteVM', self.vmx_path)

    def ramsize(self, ramsize):
        """Modify the amount of RAM available for this Virtual Machine."""
        reminder = ramsize % 4 # RAM-size should be a multiple of 4
        if reminder != 0:
            ramsize -= reminder
        return self.modifyvm('memsize', ramsize)

    def vramsize(self, width, height):
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
                self.writevar(key, value)
        except VMWareVMXError as e:
            log.error("[-] Error running command ({0}): {1}".format(e.errno, e.strerror))
            return False

        return True

    def os_type(self, osversion):
        """Set the OS type."""
        # http://sanbarrow.com/vmx/vmx-guestos.html
        operating_systems = {
            "winxp": "winxppro",
            "win7x86": "windows7",
            "win7x64": "windows7-64",
            "win81x86": "windows81",
            "win81x64": "windows81-64",
            "win10x86": "windows10",
            "win10x64": "windows10-64",
        }
        return self.modifyvm('guestOS', operating_systems[osversion])

    # https://www.vmware.com/pdf/VirtualDiskManager.pdf
    def create_hd(self, hdd_path, fsize="1GB", adapter_type='ide', disk_type='0'):
        """Create a harddisk."""
        if not any(s in fsize for s in ('GB', 'MB', 'KB')):
            raise CommandError('hdd_size should contain size specifier: %s' % fsize)
        if not any(a in adapter_type for a in ('ide', 'buslogic', 'lsilogic')):
            raise CommandError('adapter type is not valid: %s' % adapter_type)
        # sparse = 0 / flat = 2 disk_type
        if not any(dt in disk_type for dt in ('0', '2')):
            raise CommandError('disk type is not valid: %s' % disk_type)
        ret = self._call(self.vdiskman, '-c', '-t', disk_type, '-s', fsize, '-a' , adapter_type, hdd_path)
        if ret:
            # attach created vmdk to vmx file
            data = {
                'adapter_type': adapter_type,
                'vmdk_path': hdd_path,
                'mode': 'independent-persistent' if adapter_type is 'ide' else 'persistent'
            }
            content = _VMX_HDD_TEMPLATE % data
            with open(self.vmx_path, 'w+') as f:
                f.write(content)
                return ret
        else:
            return ret

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
            log.error("[-] Error running command ({0}): {1}".format(e.errno, e.strerror))
            raise CommandError
        if ret == 0:
            return True


    def clone_hd(self, hdd_outpath):
        """Clone a harddisk."""
        self._call(self.ovftool, self.vmx_path, hdd_outpath)

    def cpus(self, count):
        """Set the number of CPUs to assign to this Virtual Machine."""
        self.writevar('numvcpus', count)

    # http://www.sanbarrow.com/vmx/vmx-cd-settings.html
    def attach_iso(self, iso):
        """Attach a ISO file as DVDRom drive."""
        data_entry = _VMX_CDROM.format(**{'dev_type': 'cdrom-image', 'filename':iso})
        item_dict = dict([item.split(" = ") for item in data_entry.strip().split("\n")])
        for key, value in item_dict.items():
            self.writevar(key, value)

    def detach_iso(self):
        """Detach the ISO file in the DVDRom drive."""
        time.sleep(1)
        data_entry = _VMX_CDROM.format(**{'dev_type': 'cdrom-raw', 'filename':'auto detect'})
        item_dict = dict([item.split(" = ") for item in data_entry.strip().split("\n")])
        for key, value in item_dict.items():
            self.writevar(key, value)

    def set_field(self, key, value):
        """Set a specific field of a Virtual Machine."""
        self.writevar(key, value)


    # http://sanbarrow.com/vmx/vmx-network-advanced.html
    def modify_mac(self, macaddr=None, index=0):
        """Modify the MAC address of a Virtual Machine."""
        if macaddr is None:
            macaddr = random_mac()

        # VMRun accepts MAC addressed to be out-of-range
        data_entry = _VMX_MAC.format(**{'index': index, 'addr_type': 'static', 'mac_addr':macaddr})
        item_dict = dict([item.split(" = ") for item in data_entry.strip().split("\n")])
        for key, value in item_dict.items():
            self.writevar(key, value)
        return macaddr


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
        config = dict([item.split(" = ") for item in hostonly_config.strip().split("\n")])
        for key, value in config.items():
            self.writevar(key, value)

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
        config = dict([item.split(" = ") for item in nat_config.strip().split("\n")])
        for key, value in config.items():
            self.writevar(key, value)

        return self.modify_mac(macaddr, index)


    def hwvirt(self, enable=True):
        """Enable or disable the usage of Hardware Virtualization."""
        if enable:
            self.writevar("vhv.enable", "TRUE")
        else:
            self.writevar("vhv.enable", "FALSE")

    def start_vm(self, visible=False):
        """Start the associated Virtual Machine."""
        self._call(self.vmrun, "start", self.vmx_path, "gui" if visible else "nogui")

    def list_snapshots(self):
        """ Returns a list of snapshots for the specific VMX file """
        return self._call(self.vmrun, "listSnapshots", self.vmx_path)[1:]

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

    def stopvm(self, powertype="soft"):
        """Stop the associated Virtual Machine."""
        self._call(self.vmrun, "stop", self.vmx_path, powertype)

    def remotedisplay(self, port=5901, password=""):
        if len(password) < 8:
            log.info("You should provide a password at least 8 characters long.")
        vnc_config = _VMX_VNC.format(**{'password': password, 'port': port})
        config = dict([item.split(" = ") for item in vnc_config.strip().split("\n")])
        for key, value in config.items():
            self.writevar(key, value)

    # http://wiki.osx86project.org/wiki/index.php/Virtualization
    def enableparavirt(self):
        self._writevar("vmi.present", "TRUE")

    # https://www.virtuallyghetto.com/2019/01/quick-tip-import-ovf-ova-as-vm-template-using-ovftool-4-3-update-1.html
    def export(self, filepath):
        if filepath.split('.')[-1] != "ovf":
            filepath += ".ovf"
        return self._call(self.ovftool, self.vmx_path, "--acceptAllEulas", "--allowAllExtraConfig", filepath)
