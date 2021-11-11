# Copyright (C) 2018 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import logging
import os.path
import subprocess
import time

from vmcloak.platforms import Machinery
from vmcloak.repository import vms_path, IPNet

log = logging.getLogger(__name__)
name = "LibVirt"
disk_format = "qcow2"

VIRSH = ["virsh", "-c", "qemu:///system"]
VIRT_INSTALL = ["virt-install", "--connect", "qemu:///system"]

default_net = IPNet("192.168.122.0/24")

# virt-install doesn't seem to have anything newer than win7
libvirt_os_variants = {
    "winxp": "winxp",
    "win7x86": "win7",
    "win7x64": "win7",
    "win81x86": "win7",
    "win81x64": "win7",
    "win10x86": "win7",
    "win10x64": "win7",
}

def virsh(*args, **kwargs):
    log.info("virsh %s", " ".join(args))
    if kwargs.get("check", False):
        subprocess.check_call(VIRSH + list(args))
    else:
        subprocess.call(VIRSH + list(args))

def _create_image_disk(path, size):
    log.info("Creating disk %s with size %s", path, size)
    subprocess.check_call(["qemu-img", "create", "-f", "qcow2", path, size])

def _create_snapshot_disk(image_path, path):
    log.info("Creating snapshot %s with master %s", path, image_path)
    subprocess.check_call(["qemu-img", "create", "-f", "qcow2", "-b",
                           image_path, path])

def _create_vm(name, attr, iso_path=None, is_snapshot=False):
    log.info("Create VM instance for %s", name)
    if not os.path.exists(attr["path"]):
        # We assume the caller has already checked if existing files are a
        # problem
        if is_snapshot:
            _create_snapshot_disk(attr["imgpath"], attr["path"])
        else:
            _create_image_disk(attr["path"], "%sG" % attr["hddsize"])

    net = attr["adapter"] or "default"
    args = VIRT_INSTALL + ["--name", name,
                           "--vcpus", "%s" % attr["cpus"],
                           "--memory", "%s" % attr["ramsize"],
                           "--disk", attr["path"],
                           "--noautoconsole",
                           "--os-variant", libvirt_os_variants[attr["osversion"]],
                           "--network", "network=%s" % net]
    if not iso_path:
        # Even if we don't have an ISO, we do want a CD-ROM drive
        args.extend(["--disk", "device=cdrom"])
    if attr.get("vm_visible"):
        # Doesn't really work?
        args.extend(["--graphics", "sdl"])
    elif attr.get("vrde"):
        port = attr["vrde"]
        args.extend(["--graphics", "vnc,port=%s" % port])
    if iso_path:
        # Install a new image
        # TODO: cannot use --transient here because virt-install will fail
        args.extend(["--livecd", "--cdrom", iso_path,
                     "--wait", "-1"])
    else:
        # Create a new (snapshot) VM
        args.append("--import")
    log.debug("Execute: %s", " ".join(args))
    subprocess.check_call(args)

def _vm_state(name):
    try:
        state = subprocess.check_output(VIRSH + ["domstate", name])
    except subprocess.CalledProcessError:
        log.warning("Failed to get state of %s", name)
        return ""
    return state.rstrip().replace(" ", "")

#
# Platform API
#

def prepare_snapshot(name, attr):
    # Keep it in the root dir so libvirt doesn't create a storage
    # pool per VM
    path = os.path.join(vms_path, "%s.%s" % (name, disk_format))
    attr["path"] = path
    if os.path.exists(path):
        return False
    return vms_path

def create_new_image(name, _, iso_path, attr):
    if os.path.exists(attr["path"]):
        raise ValueError("Image %s already exists" % attr["path"])

    _create_vm(name, attr, iso_path=iso_path)

def create_snapshot_vm(image, name, attr):
    if os.path.exists(attr["path"]):
        raise ValueError("Snapshot %s already exists" % attr["path"])

    _create_vm(name, attr, is_snapshot=True)

def create_snapshot(name):
    virsh("snapshot-create-as",
          name,
          "--name", "vmcloak",
          "--description", "Snapshot created by VMCloak",
          "--diskspec", "hda,snapshot=internal",
          "--memspec", "file=,snapshot=internal",
          "--halt")

def start_image_vm(image, user_attr=None):
    """Start transient VM"""
    attr = image.attr()
    if user_attr:
        attr.update(user_attr)
    _create_vm(image.name, attr)

def remove_vm_data(name):
    """Remove VM definitions and snapshots but keep disk image intact"""
    log.info("Cleanup VM %s", name)
    if _vm_state(name):
        virsh("destroy", "--graceful", name, check=False)
        # TODO: will fail if there are more snapshots
        virsh("snapshot-delete", name, "--metadata", "vmcloak", check=False)
        virsh("undefine", name, check=False)
    path = os.path.join(vms_path, "%s.%s" % (name, disk_format))
    if os.path.exists(path):
        os.remove(path)

def wait_for_shutdown(name, timeout=None):
    while True:
        state = _vm_state(name)
        if state == "running":
            time.sleep(1)
        elif state == "shutoff":
            return True
        else:
            raise ValueError(state)

def clone_disk(image, target):
    log.info("Cloning disk %s to %s", image.path, target)
    subprocess.check_call(["qemu-img", "convert", "-f", "qcow2", image.path,
                           target])

def export_vm(image, target):
    raise NotImplementedError

def restore_snapshot(name, snap_name):
    virsh("restore", name, snap_name)

def remove_hd(path):
    os.remove(path)

def create_machineinfo_dump(name, image):
    pass

#
# Helper class for dependencies
#

class VM(Machinery):
    def attach_iso(self, iso_path):
        virsh("attach-disk", self.name, iso_path, "hdb",
              "--type", "cdrom",
              "--mode", "readonly")

    def detach_iso(self):
        virsh("attach-disk", self.name, "", "hdb",
              "--type", "cdrom",
              "--mode", "readonly")
