# Copyright (C) 2014-2016,2018 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import logging
import os
import os.path
import random
import subprocess
import time
from os.path import basename

from vmcloak.conf import load_hwconf
from vmcloak.data.config import VBOX_CONFIG
from vmcloak.exceptions import CommandError
from vmcloak.ostype import network_interface
from vmcloak.platforms import Machinery
from vmcloak.rand import random_mac, random_serial, random_uuid
from vmcloak.repository import vms_path, IPNet

log = logging.getLogger(__name__)
name = "VirtualBox"
disk_format = "vdi"

vboxmanage = "vboxmanage"

default_net = IPNet("192.168.56.0/24")

def _call(*args, **kwargs):
    cmd = [vboxmanage] + list(args)

    for k, v in kwargs.items():
        if v is None or v is True:
            cmd += ["--" + k]
        else:
            cmd += ["--" + k.rstrip("_"), str(v)]

    friendly_cmd = " ".join(
        repr(c) if any(bad in c for bad in " \"'") else c for c in cmd
    )
    try:
        log.debug("Run: %s", friendly_cmd)
        ret = subprocess.check_output(cmd)
    except Exception as e:
        # CalledProcessError
        log.error("[-] Error running command: %s", e)
        raise CommandError(str(e))

    return ret.strip()

def _set_common_attr(vm, attr):
    nictype = network_interface(attr["osversion"])
    vm.os_type(attr["osversion"])
    vm.paravirtprovider(attr["paravirtprovider"])
    vm.cpus(attr["cpus"])
    vm.mouse("usbtablet")
    vm.ramsize(attr["ramsize"])
    vm.vramsize(attr["vramsize"])
    vm.hostonly(nictype=nictype, adapter=attr["adapter"], macaddr=attr["mac"])
    port = attr.get("vrde")
    if port:
        if port is True:
            port = 3389
        vm.vrde(port=port)

def _create_vm(name, attr, iso_path=None, is_snapshot=True):
    if not attr.get("mac"):
        attr["mac"] = random_mac()

    vm = VM(name)
    vm.create_vm()
    _set_common_attr(vm, attr)
    if is_snapshot:
        vm.attach_hd(attr["imgpath"], multi=True)
    elif os.path.exists(attr["path"]):
        # TODO: assume caller has checked this is OK
        vm.attach_hd(attr["path"])
    else:
        vm.create_hd(attr["path"], attr["hddsize"] * 1024)
    if iso_path:
        vm.attach_iso(iso_path)
    else:
        # Ensure the slot is at least allocated for by an empty drive.
        vm.detach_iso()
    if attr.get("share"):
        path = attr["share"]
        if "=" in path:
            name, path = path.split("=", 1)
        else:
            name = basename(path.rstrip("\\/"))
        vm.share(name, path)
    if attr.get("serial"):
        vm.uart(1, attr["serial"])
    return vm

def remove_vm(name, preserve_hd=False):
    vm = VM(name)
    if preserve_hd:
        vm.remove_hd()
    vm.delete_vm()

#
# Platform API
#

def prepare_snapshot(name, attr):
    """We don't need to snapshot the disk, test if the snapshot
    exists instead."""
    base = os.path.join(vms_path, name)
    path = os.path.join(base, "%s.vbox" % name)
    if os.path.exists(path):
        return False
    return base

def create_new_image(name, _, iso_path, attr):
    """Create a VM instance for an image
    Changes will be written to disk"""
    _create_vm(name, attr, iso_path=iso_path, is_snapshot=False)

    log.info("Starting the Virtual Machine %r to install Windows.", name)
    m = VM(name)
    m.start_vm(visible=attr.get("vm_visible", False))
    wait_for_shutdown(name)

def create_snapshot_vm(image, name, attr):
    _create_vm(name, attr, is_snapshot=True)
    m = VM(name)
    m.start_vm(visible=attr.get("vm_visible", False))

def create_snapshot(name):
    vm = VM(name)
    vm.snapshot("vmcloak", "Snapshot created by VMCloak.")
    vm.stop_vm()

def start_image_vm(image, user_attr=None):
    """Start transient VM"""
    attr = image.attr()
    if user_attr:
        attr.update(user_attr)
    _create_vm(image.name, attr, is_snapshot=False)

    m = VM(image.name)
    m.start_vm(visible=attr.get("vm_visible", False))

def remove_vm_data(name):
    vm = VM(name)
    path = os.path.join(vms_path, name)
    # Hopefully...
    vm_exists = True
    status = ""
    try:
        status = vm.vminfo("VMState")
    except CommandError:
        vm_exists = False
    if vm_exists:
        if status != "poweroff":
            # Force shutdown
            vm.stop_vm()
            wait_for_shutdown(name)
        # VBox should not accidentally delete the image
        try:
            vm.remove_hd()
        except CommandError:
            pass
        vm.delete_vm()

    if os.path.exists(path):
        log.error(
            "Path %s still exists, you may need to delete it manually",
            path
        )

def wait_for_shutdown(name, timeout=None):
    m = VM(name)
    return m.wait_for_state(shutdown=True, timeout=timeout)

def clone_disk(image, target):
    m = VM(image.name)
    m.clone_hd(image.path, target)

def export_vm(image, target):
    m = _create_vm(image.name, image.attr(), is_snapshot=False)
    m.export(target)
    m.remove_hd()
    m.compact_hd(image.path)
    m.delete_vm()

def restore_snapshot(name, snap_name):
    m = VM(name)
    m.restore_snapshot(snap_name)

def remove_hd(path):
    _call("closemedium", "disk", path, delete=True)

def create_machineinfo_dump(name, image):
    pass

# --

class VM(Machinery):
    """Helper class to deal with VirtualBox VMs"""
    FIELDS = VBOX_CONFIG

    def __init__(self, *args, **kwargs):
        Machinery.__init__(self, *args, **kwargs)
        self.network_idx = 0

    def network_index(self):
        """Get the index for the next network interface."""
        ret = self.network_idx
        self.network_idx += 1
        return ret

    def vminfo(self, element=None):
        """Returns a dictionary with all available information for the
        Virtual Machine."""
        ret = {}
        lines = _call("showvminfo", self.name, machinereadable=True)
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

    def wait_for_state(self, shutdown=False, timeout=30):
        now = time.time()
        while timeout is None or (time.time() - now) < timeout:
            try:
                status = self.vminfo("VMState")
                if shutdown and status == "poweroff":
                    return True
            except CommandError:
                pass

            time.sleep(1)
        return False

    def create_vm(self):
        """Create a new Virtual Machine."""
        _call("createvm", name=self.name, basefolder=vms_path, register=True)

    def unregister_vm(self):
        """Delete an existing Virtual Machine but not any associated files."""
        _call("unregistervm", self.name)

    def delete_vm(self):
        """Delete an existing Virtual Machine and its associated files."""
        _call("unregistervm", self.name, delete=True)

    def ramsize(self, ramsize):
        """Modify the amount of RAM available for this Virtual Machine."""
        return _call("modifyvm", self.name, memory=ramsize)

    def vramsize(self, vramsize):
        """Modify the amount of Video memory available for this Virtual
        Machine."""
        return _call("modifyvm", self.name, vram=vramsize)

    def os_type(self, osversion):
        """Set the OS type."""
        operating_systems = {
            "winxp": "WindowsXP",
            "win7x86": "Windows7",
            "win7x64": "Windows7_64",
            "win81x86": "Windows81",
            "win81x64": "Windows81_64",
            "win10x86": "Windows10",
            "win10x64": "Windows10_64",
        }
        return _call("modifyvm", self.name,
                     ostype=operating_systems[osversion])

    def create_hd(self, hdd_path, fsize=256*1024):
        """Create a harddisk."""
        _call("createhd", filename=hdd_path, size=fsize)
        _call("storagectl", self.name, name="IDE", add="ide")
        _call("storageattach", self.name, storagectl="IDE",
                   type_="hdd", device=0, port=0, medium=hdd_path)

    def attach_hd(self, hdd_path, multi=False):
        if multi:
            mode = "multiattach"
        else:
            mode = "normal"
        # When a harddisk is not attached to a Virtual Machine it will quickly
        # be forgotten. This seems to be within a couple of seconds. When this
        # happens, its "type" (multiattach in our case) is also forgotten,
        # resulting in issues when cloning. Therefore we quickly set its state
        # before attaching it to a Virtual Machine, hoping this approach
        # is "good enough".
        #if multi:
        #    _call("modifyhd", hdd_path, type_="multiattach")
        #else:
        #    _call("modifyhd", hdd_path, type_="normal")
        _call("storagectl", self.name, name="IDE", add="ide")
        _call("storageattach", self.name, storagectl="IDE",
              type_="hdd", device=0, port=0, mtype=mode, medium=hdd_path)

    def compact_hd(self, hdd_path):
        # We first make the HDD "more" compact - this should be basically
        # defragmenting it.
        _call("modifyhd", hdd_path, compact=True)

    def clone_hd(self, hdd_inpath, hdd_outpath):
        """Clone a harddisk."""
        _call("clonehd", hdd_inpath, hdd_outpath)

    def remove_hd(self):
        """Remove a harddisk."""
        time.sleep(1) # ...
        _call("storagectl", self.name, portcount=0,
                   name="IDE", remove=True)

    def cpus(self, count):
        """Set the number of CPUs to assign to this Virtual Machine."""
        _call("modifyvm", self.name, cpus=count, ioapic="on")

    def attach_iso(self, iso_path):
        """Mount an ISO to the Virtual Machine."""
        _call("storageattach", self.name, storagectl="IDE",
                   type_="dvddrive", port=1, device=0, medium=iso_path)

    def detach_iso(self):
        """Detach the ISO file in the DVDRom drive."""
        time.sleep(1)
        _call("storageattach", self.name, storagectl="IDE",
                   type_="dvddrive", port=1, device=0, medium="emptydrive")

    def set_field(self, key, value):
        """Set a specific field of a Virtual Machine."""
        return _call("setextradata", self.name, key, value)

    def share(self, name, path):
        return _call("sharedfolder", "add", self.name, "--name", name,
                     "--hostpath", path)

    def modify_mac(self, macaddr=None, index=1):
        """Modify the MAC address of a Virtual Machine."""
        if macaddr is None:
            macaddr = random_mac()

        # VBoxManage prefers MAC addresses without colons.
        vbox_mac = macaddr.replace(":", "")

        mac = {"macaddress%d" % index: vbox_mac}
        _call("modifyvm", self.name, **mac)
        return macaddr

    def hostonly(self, nictype, macaddr=None, adapter=None):
        """Configure a hostonly adapter for the Virtual Machine."""
        index = self.network_index() + 1
        if not adapter:
            if os.name == "posix":
                adapter = "vboxnet0"
            else:
                adapter = "VirtualBox Host-Only Ethernet Adapter"

        # Ensure our hostonly interface is actually up and running.
        if adapter not in _call("list", "hostonlyifs"):
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
        _call("modifyvm", self.name, **nic)
        return self.modify_mac(macaddr, index)

    def nat(self, nictype, macaddr=None):
        """Configure NAT for the Virtual Machine."""
        index = self.network_index() + 1

        nic = {
            "nic%d" % index: "nat",
            "nictype%d" % index: nictype,
            "nicpromisc%d" % index: "allow-all",
        }
        _call("modifyvm", self.name, **nic)
        return self.modify_mac(macaddr, index)

    def hwvirt(self, enable=True):
        """Enable or disable the usage of Hardware Virtualization."""
        _call("modifyvm", self.name, hwvirtex="on" if enable else "off")

    def uart(self, port, path):
        """Add UART/serial port on given Unix-socket path"""
        iobase, irq = {1: (0x3F8, 4),
                       2: (0x2F8, 3),
                       3: (0x3E8, 4),
                       4: (0x2E8, 3)}[port]
        # Enable
        _call("modifyvm", self.name, "--uart%s" % port, "0x%x" % iobase,
                   str(irq))
        # Set path
        _call("modifyvm", self.name, "--uartmode%s" % port, "server",
                   path)

    def start_vm(self, visible=False):
        """Start the associated Virtual Machine."""
        return _call("startvm", self.name,
                          type_="gui" if visible else "headless")

    def snapshot(self, label, description=""):
        """Take a snapshot of the associated Virtual Machine."""
        return _call("snapshot", self.name, "take", label,
                          description=description, live=True)

    def restore_snapshot(self, label=None):
        if label:
            return _call("snapshot", self.name, "restore", label)
        else:
            return _call("snapshot", self.name, "restorecurrent")

    def delete_snapshot(self, label):
        return _call("snapshot", self.name, "delete", label)

    def stop_vm(self):
        """Stop the associated Virtual Machine."""
        return _call("controlvm", self.name, "poweroff")

    def list_settings(self):
        """List all settings of a Virtual Machine."""
        return _call("getextradata", self.name, "enumerate")

    def mouse(self, type):
        return _call("modifyvm", self.name, mouse=type)

    def vrde(self, port=3389, password=""):
        return _call("modifyvm", self.name, vrde="on", vrdeport=port,
                          vrdeproperty="VNCPassword=%s" % password)

    def paravirtprovider(self, provider):
        return _call("modifyvm", self.name, paravirtprovider=provider)

    def export(self, filepath):
        return _call(
            "export", self.name, "--output", filepath, "--vsys", "0",
            product="VMCloak",
            producturl="http://vmcloak.org/",
            vendor="Cuckoo Sandbox",
            vendorurl="http://cuckoosandbox.org/",
            description="Cuckoo Sandbox Virtual Machine created by VMCloak",
        )

    def init_vm(self, profile):
        """Initialize fields as specified by `FIELDS`."""
        hwconf = load_hwconf(profile=profile)

        def _init_vm(path, fields):
            for key, value in fields.items():
                key = path + "/" + key
                if isinstance(value, dict):
                    _init_vm(key, value)
                else:
                    if isinstance(value, tuple):
                        k, v = value
                        if k not in hwconf or not hwconf[k]:
                            value = "To be filled by O.E.M."
                        else:
                            if k not in config:
                                config[k] = random.choice(hwconf[k])

                            value = config[k][v]

                            # Some values have to be generated randomly.
                            if value is not None:
                                if value.startswith("<SERIAL>"):
                                    length = int(value.split()[-1])
                                    value = random_serial(length)
                                elif value.startswith("<UUID>"):
                                    value = random_uuid()

                    if value is None:
                        value = "To be filled by O.E.M."

                    log.debug("Setting %r to %r.", key, value)
                    ret = self.set_field(key, value)
                    if ret:
                        log.debug(ret)

        config = {}
        _init_vm("", self.FIELDS)
