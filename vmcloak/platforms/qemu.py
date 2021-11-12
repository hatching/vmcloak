# Copyright (C) 2018 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import logging
import os.path
import subprocess
import time
import shutil
from re import search
from pkg_resources import parse_version

from vmcloak.platforms import Machinery
from vmcloak.repository import vms_path, IPNet
from vmcloak.rand import random_vendor_mac
from vmcloak.machineconf import MachineConfDump
from vmcloak.ostype import get_os

log = logging.getLogger(__name__)
name = "QEMU"
disk_format = "qcow2"

machines = {}
confdumps = {}

default_net = IPNet("192.168.30.0/24")

QEMU_AMD64 = ["qemu-system-x86_64", "-monitor", "stdio"]

def _create_image_disk(path, size):
    log.info("Creating disk %s with size %s", path, size)
    subprocess.check_call(
        ["qemu-img", "create", "-f", "qcow2",
         "-o", "lazy_refcounts=on,cluster_size=2M", path, size]
    )

def _create_snapshot_disk(image_path, path):
    log.info("Creating snapshot %s with master %s", path, image_path)
    subprocess.check_call(["qemu-img", "create", "-f", "qcow2", "-o",
                           "lazy_refcounts=on,cluster_size=2M", "-b",
                           image_path, path])


def _make_pre_v41_args(attr):
    return [
        "-M", "q35",
        "-nodefaults",
        "-vga", "std",
        "-rtc", "base=localtime,driftfix=slew",
        "-realtime", "mlock=off",
        "-m", f"{attr['ramsize']}",
        "-smp", f"{attr['cpus']}",
        "-netdev", f"type=bridge,br={attr['adapter']},id=net0",
        "-device", f"rtl8139,netdev=net0,mac={attr['mac']},bus=pcie.0,addr=3",

        "-device", "ich9-ahci,id=ahci",
        "-device", "ide-drive,bus=ahci.0,unit=0,drive=disk,bootindex=2",
        "-device", "ide-cd,bus=ahci.1,unit=0,drive=cdrom,bootindex=1",
        "-device", "usb-ehci,id=ehci",
        "-device", "usb-tablet,bus=ehci.0",
        "-soundhw", "hda",
        "--enable-kvm"
    ]

# From 4.1 the -realtime mlock=off and -device ide-drive
# are deprecated and those are removed in higher versions.
def _make_post_v41_args(attr):
    return [
        "-nodefaults",
        "-M", "q35",
        "-vga", "std",
        "-smp", f"{attr['cpus']}",
        "-overcommit", "mem-lock=off",
        "-rtc", "base=localtime,driftfix=slew",
        "-m", f"{attr['ramsize']}",
        "-netdev", f"type=bridge,br={attr['adapter']},id=net0",
        "-device", f"rtl8139,netdev=net0,mac={attr['mac']},bus=pcie.0,addr=3",

        "-device", "ich9-ahci,id=ahci",
        "-device", "ide-hd,bus=ahci.0,unit=0,drive=disk,bootindex=2",

        "-device", "ide-cd,bus=ahci.1,unit=0,drive=cdrom,bootindex=1",
        "-device", "usb-ehci,id=ehci",
        "-device", "usb-tablet,bus=ehci.0",
        "-soundhw", "hda",
        "-enable-kvm"
    ]

def _make_args(attr, disk_placeholder=False, iso=None, display=None):

    if version() < parse_version("4.1"):
        args = _make_pre_v41_args(attr)
    else:
        args = _make_post_v41_args(attr)

    if iso:
        args.extend(["-drive", f"{iso}if=none,id=cdrom,readonly=on"])
    else:
        args.extend(["-drive", "if=none,id=cdrom,readonly=on"])

    if disk_placeholder:
        args.extend(
            ["-drive",
             "file=%DISPOSABLE_DISK_PATH%,format=qcow2,if=none,id=disk"]
        )
    else:
        args.extend(
            ["-drive",
             f"file={attr['path']},format=qcow2,if=none,id=disk"]
        )

    if display:
        args.extend(["-display", "gtk"])
    else:
        args.extend(["-display", "none"])

    return args


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
    attr["adapter"] = net
    if iso_path:
        iso = "file=%s,format=raw," % iso_path
    else:
        iso = ""

    if not attr.get("mac") or is_snapshot:
        attr["mac"] = random_vendor_mac()

    if is_snapshot:
        os_helper = get_os(attr["osversion"])
        confdumps[name] = MachineConfDump(
            name=name, ip=attr["ip"], agent_port=attr["port"],
            os_name=os_helper.os_name, os_version=os_helper.os_version,
            architecture=os_helper.arch, bridge=net, mac=attr["mac"],
            gateway=attr["gateway"], netmask=attr["netmask"],
            disk=os.path.basename(attr["path"]),
            start_args=_make_args(attr, disk_placeholder=True)
        )
        confdumps[name].machinery_version = str(version())
        confdumps[name].machinery = "qemu"

    args = QEMU_AMD64 + _make_args(
        attr, disk_placeholder=False, iso=iso, display=attr.get("vm_visible")
    )
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

def _get_vm_dir(vm_name):
    dirpath = os.path.join(vms_path, "qemu", vm_name)
    os.makedirs(dirpath, exist_ok=True, mode=0o775)
    return dirpath

def prepare_snapshot(name, attr):
    # Snapshots are stored in-line
    vm_dir = _get_vm_dir(name)
    path = os.path.join(vm_dir, f"disk.{disk_format}")
    attr["path"] = path
    if os.path.exists(path):
        return False

    return vm_dir

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

_DECOMPRESS_BINARIES = {
    "lz4": shutil.which("lz4"),
    "gzip": shutil.which("gzip")
}

_DECOMPRESS_COMMANDS = {
    "lz4": "-z > %SNAPSHOT_PATH%",
    "gzip": "-c -3 > %SNAPSHOT_PATH%"
}

def _get_exec_args(memsnapshot_path):
    for tool in ("lz4", "gzip"):
        binary = _DECOMPRESS_BINARIES.get(tool)
        if binary:
            args = _DECOMPRESS_COMMANDS[tool].replace(
                "%SNAPSHOT_PATH%", memsnapshot_path
            )
            return f"{binary} {args}"

    return f"/bin/cat > {memsnapshot_path}"


MEMORY_SNAPSHOT_NAME = "memory.snapshot"
def create_snapshot(name):
    m = machines[name]
    snapshot_path = os.path.join(_get_vm_dir(name), MEMORY_SNAPSHOT_NAME)
    confdumps[name].add_machine_field("memory_snapshot", MEMORY_SNAPSHOT_NAME)
    # Stop the machine so the memory does not change while making the
    # memory snapshot.
    m.stdin.write(b"stop\n")
    m.stdin.write(b"migrate_set_speed 1G\n")
    # Send the actual memory snapshot command. The args helper tries to find
    # lz4 of gzip binaries so we can compress the dump.
    m.stdin.write(
        f"migrate \"exec:{_get_exec_args(snapshot_path)}\"\n".encode()
    )
    m.stdin.write(b"quit\n")
    log.debug("Flushing snapshot commands to qemu.")
    m.stdin.flush()
    m.wait()

def create_machineinfo_dump(name, image):
    confdump = confdumps[name]
    confdump.tags_from_image(image)
    dump_path = os.path.join(_get_vm_dir(name), confdump.DEFAULT_NAME)
    confdump.write_dump(dump_path)

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
    m = machines.get(name)
    end = None
    if timeout:
        end = time.time() + timeout
    while True:
        m.poll()
        if m.returncode is not None:
            if m.returncode == 0:
                return True
            raise ValueError(f"Non-zero exit code: {m.returncode}")
        if end and time.time() > end:
            raise ValueError("Timeout")
        time.sleep(1)

def clone_disk(image, target):
    log.info("Cloning disk %s to %s", image.path, target)
    shutil.copy(image.path, target)

def export_vm(image, target):
    raise NotImplementedError

def restore_snapshot(name, snap_name):
    path = os.path.join(_get_vm_dir(name), f"disk.{disk_format}")
    subprocess.check_call(["qemu-img", "snapshot", "-a", snap_name, path])

def remove_hd(path):
    os.remove(path)


def version():
    """Get the QEMU version qemu in PATH. Returns a
    version object from pkg_resources.parse_version if a version is found.
    passes empty string to parse_version if no version could be determined and
    returns result"""
    vdata = subprocess.check_output(["qemu-system-x86_64", "--version"])
    # Read QEMU version as if it were semver. It is not, but looks similar.
    version_r = (
        br"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*"
        br"[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-]"
        br"[0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?"
    )

    match = search(version_r, vdata)
    if not match:
        return parse_version("")

    return parse_version(match.group().strip().decode())

#
# Helper class for dependencies
#

class VM(Machinery):
    def attach_iso(self, iso_path):
        m = machines.get(self.name)
        if not m:
            raise KeyError(
                "Cannot attach ISO to machine. Process handle not available."
            )

        m.stdin.write(f"change cdrom {iso_path}\n".encode())
        m.stdin.flush()

    def detach_iso(self):
        m = machines.get(self.name)
        if not m:
            raise KeyError(
                "Cannot attach ISO to machine. Process handle not available."
            )
        m.stdin.write(b"eject cdrom\n")
        m.stdin.flush()
