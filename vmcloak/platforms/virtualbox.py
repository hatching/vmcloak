# Copyright (C) 2014-2016,2018 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import logging
import os
import subprocess
import time
from os.path import exists, join

from vmcloak.abstract import Machinery
from vmcloak.exceptions import CommandError
from vmcloak.paths import get_path
from vmcloak.rand import random_mac
from vmcloak.repository import vms_path
from vmcloak.data.config import VBOX_CONFIG
from vmcloak.ostype import network_interface

log = logging.getLogger(__name__)
name = "VirtualBox"
vboxmanage = get_path("vboxmanage")


def _call(*args, **kwargs):
    cmd = [vboxmanage] + list(args)

    for k, v in kwargs.items():
        if v is None or v is True:
            cmd += ["--" + k]
        else:
            cmd += ["--" + k.rstrip("_"), str(v)]

    try:
        log.debug("Running command: %s", cmd)
        ret = subprocess.check_output(cmd)
    except Exception as e:
        # CalledProcessError
        log.error("[-] Error running command: %s", e)
        raise CommandError

    return ret.strip()

def create_vm(name, attr, is_snapshot=True):
    nictype = network_interface(attr["osversion"])
    vm = VM(name)
    vm.create_vm()
    vm.os_type(attr["osversion"])
    vm.cpus(attr["cpus"])
    vm.mouse("usbtablet")
    vm.ramsize(attr["ramsize"])
    vm.vramsize(attr["vramsize"])
    vm.attach_hd(attr["path"], multi=is_snapshot)
    # Ensure the slot is at least allocated for by an empty drive.
    vm.detach_iso()
    vm.hostonly(nictype=nictype, adapter=attr["adapter"])
    if attr.get("serial"):
        vm.uart(1, attr["serial"])
    return vm

def create_vm_for_image(name, image, is_snapshot=False):
    """Create a VM instance for an image
    Changes will be written to disk"""
    if vm_exists(name):
        # We should really check if it has the same properties
        return VM(name)
    return create_vm(name, image, None, False)

def vm_exists(name):
    return exists(join(vms_path, name))

def remove_vm(name, preserve_hd=False):
    vm = VM(name)
    if preserve_hd:
        vm.remove_hd()
    vm.delete_vm()

def remove_hd(path):
    _call("closemedium", "disk", path, delete=True)

class VM(Machinery):
    """Helper class to deal with VirtualBox VMs"""
    FIELDS = VBOX_CONFIG

    def vminfo(self, element=None):
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
        _call("createvm", name=self.name, basefolder=vms_path, register=True)

    def delete_vm(self):
        _call("unregistervm", self.name, delete=True)

    def ramsize(self, ramsize):
        return _call("modifyvm", self.name, memory=ramsize)

    def vramsize(self, vramsize):
        return _call("modifyvm", self.name, vram=vramsize)

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
        return _call("modifyvm", self.name,
                          ostype=operating_systems[osversion])

    def create_hd(self, hdd_path, fsize=256*1024):
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
        _call("clonehd", hdd_inpath, hdd_outpath)

    def remove_hd(self):
        time.sleep(1) # ...
        _call("storagectl", self.name, portcount=0,
                   name="IDE", remove=True)

    def cpus(self, count):
        _call("modifyvm", self.name, cpus=count, ioapic="on")

    def attach_iso(self, iso_path):
        """Mount an ISO to the Virtual Machine."""
        _call("storageattach", self.name, storagectl="IDE",
                   type_="dvddrive", port=1, device=0, medium=iso_path)

    def detach_iso(self):
        time.sleep(1)
        _call("storageattach", self.name, storagectl="IDE",
                   type_="dvddrive", port=1, device=0, medium="emptydrive")

    def set_field(self, key, value):
        return _call("setextradata", self.name, key, value)

    def modify_mac(self, macaddr=None, index=1):
        if macaddr is None:
            macaddr = random_mac()

        # VBoxManage prefers MAC addresses without colons.
        vbox_mac = macaddr.replace(":", "")

        mac = {"macaddress%d" % index: vbox_mac}
        _call("modifyvm", self.name, **mac)
        return macaddr

    def hostonly(self, nictype, macaddr=None, adapter=None):
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
        return _call("startvm", self.name,
                          type_="gui" if visible else "headless")

    def snapshot(self, label, description=""):
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
        return _call("controlvm", self.name, "poweroff")

    def list_settings(self):
        return _call("getextradata", self.name, "enumerate")

    def mouse(self, type):
        return _call("modifyvm", self.name, mouse=type)

    def vrde(self, port=3389, password=""):
        return _call("modifyvm", self.name, vrde="on", vrdeport=port,
                          vrdeproperty="VNCPassword=%s" % password)

    def export(self, filepath):
        return _call(
            "export", self.name, "--output", filepath, "--vsys", "0",
            product="VMCloak",
            producturl="http://vmcloak.org/",
            vendor="Cuckoo Sandbox",
            vendorurl="http://cuckoosandbox.org/",
            description="Cuckoo Sandbox Virtual Machine created by VMCloak",
        )
