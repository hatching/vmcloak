# Copyright (C) 2018 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import logging
import os.path
import subprocess
import time

from vmcloak.platforms import Machinery
from vmcloak.repository import vms_path

log = logging.getLogger(__name__)
name = "QEMU"
disk_format = "qcow2"

machines = {}

QEMU_AMD64 = ["qemu-system-x86_64", "-enable-kvm",
              "-display", "none",
              "-monitor", "stdio"]

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

    net = attr["adapter"] or "br0"
    if iso_path:
        iso = "file=%s,format=raw," % iso_path
    else:
        iso = ""

    args = QEMU_AMD64 + [
        "-smp", "1,sockets=1,cores=%s,threads=1" % attr["cpus"],
        "-m", "%s" % attr["ramsize"],
        "-netdev", "type=bridge,br=%s,id=net0" % net,
        "-device", "rtl8139,netdev=net0",
        "-drive", "file=%s,format=qcow2,if=none,id=drive-ide0-0-0" % attr["path"],
        "-device", "ide-hd,bus=ide.0,unit=0,drive=drive-ide0-0-0,id=ide0-0-0,bootindex=2",
        "-drive", "%sif=none,id=drive-ide0-0-1,readonly=on" % iso,
        "-device", "ide-cd,bus=ide.0,unit=1,drive=drive-ide0-0-1,id=ide0-0-1,bootindex=1"
    ]

    if attr.get("vrde"):
        # Note that qemu will add 5900 to the port number
        port = attr["vrde"]
        args.extend(["-vnc", "0.0.0.0:%s" % port])

    log.debug("Execute: %s", " ".join(args))
    m = subprocess.Popen(args, stdin=subprocess.PIPE)
    machines[name] = m
    return m

#
# Platform API
#

def prepare_snapshot(name, attr):
    # Snapshots are stored in-line
    path = os.path.join(vms_path, "%s.%s" % (name, disk_format))
    attr["path"] = path
    if os.path.exists(path):
        return False
    return vms_path

def create_new_image(name, _, iso_path, attr):
    if os.path.exists(attr["path"]):
        raise ValueError("Image %s already exists" % attr["path"])

    m = _create_vm(name, attr, iso_path=iso_path)
    m.wait()
    if m.returncode != 0:
        raise ValueError(m.returncode)

def create_snapshot_vm(image, name, attr):
    if os.path.exists(attr["path"]):
        raise ValueError("Snapshot %s already exists" % attr["path"])

    _create_vm(name, attr, is_snapshot=True)

def create_snapshot(name):
    m = machines[name]
    m.stdin.write("savevm vmcloak\n")
    m.stdin.write("quit\n")
    m.wait()

def start_image_vm(image, user_attr=None):
    """Start transient VM"""
    attr = image.attr()
    if user_attr:
        attr.update(user_attr)
    _create_vm(image.name, attr)

def remove_vm_data(name):
    """Remove VM definitions and snapshots but keep disk image intact"""
    m = machines.get(name)
    if m:
        log.info("Cleanup VM %s", name)
        try:
            if m.returncode is None:
                m.kill()
        except OSError:
            pass
    else:
        log.info("Not running: %s", name)
    path = os.path.join(vms_path, "%s.%s" % (name, disk_format))
    if os.path.exists(path):
        os.remove(path)

def wait_for_shutdown(name, timeout=None):
    # TODO: timeout
    end = None
    if timeout:
        end = time.time() + timeout
    while True:
        m.poll()
        if m.returncode is not None:
            if m.returncode == 0:
                return True
            raise ValueError(m.returncode)
        if end and time.time() > end:
            raise ValueError("Timeout")
        time.sleep(1)

def clone_disk(image, target):
    log.info("Cloning disk %s to %s", image.path, target)
    subprocess.check_call(["qemu-img", "convert", "-f", "qcow2", image.path,
                           target])

def export_vm(image, target):
    raise NotImplementedError

def restore_snapshot(name, snap_name):
    path = os.path.join(vms_path, "%s.%s" % (name, disk_format))
    subprocess.check_call(["qemu-img", "snapshot", "-a", snap_name, path])

def remove_hd(path):
    os.remove(path)

#
# Helper class for dependencies
#

class VM(Machinery):
    def attach_iso(self, iso_path):
        m = machines[self.name]
        m.stdin.write("change ide1-cd0 %s\n" % iso_path)

    def detach_iso(self):
        m = machines[self.name]
        m.stdin.write("eject ide1-cd0\n")
