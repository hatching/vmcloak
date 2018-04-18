# Copyright (C) 2014-2018 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

from __future__ import print_function

import click
import logging
import os.path
import requests
import shutil
import tempfile
import time

from sqlalchemy.orm.session import make_transient

import vmcloak.dependencies

from vmcloak.agent import Agent
from vmcloak.dependencies import Python
from vmcloak.exceptions import DependencyError, CommandError
from vmcloak.misc import wait_for_host, register_cuckoo, drop_privileges
from vmcloak.misc import ipaddr_increase
from vmcloak.rand import random_string
from vmcloak.repository import (vms_path, image_path, Session, Image, Snapshot,
                                iso_dst_path)
from vmcloak.ostype import get_os
from vmcloak.constants import VMCLOAK_VM_MODES

from vmcloak import repository

logging.basicConfig()
log = logging.getLogger("vmcloak")
log.setLevel(logging.WARNING)

def init_image_vm(name, vm_visible, user_attr):
    image = repository.find_image(name)
    if not image:
        log.error("Image not found: %s", name)
        exit(1)

    #if image.mode != "normal":
    if len(image.snapshots):
        log.error("You can't modify this image as you have "
                  "already made snapshots with it!")
        log.error("Please vmcloak-clone it and update the clone, "
                  "or delete the snapshots.")
        log.error("Number of snapshots: %s", len(image.snapshots))
        exit(1)

    attr = image.attr()
    attr.update(user_attr)

    vm = image.platform.create_vm(image.name, attr, False)
    vm.start_vm(visible=vm_visible)
    wait_for_host(attr["ipaddr"], attr["port"])
    return image

@click.group(invoke_without_command=True)
@click.option("-u", "--user", help="Drop privileges to user.")
@click.option("-v", "--verbose", is_flag=True, help="Verbose logging.")
def main(user, verbose):
    user and drop_privileges(user)
    if verbose:
        log.setLevel(logging.INFO)

@main.command()
@click.argument("name")
@click.argument("outname")
def clone(name, outname):
    """Clone an image"""
    session = Session()

    image = session.query(Image).filter_by(name=name).first()
    if not image:
        log.error("Image not found: %s", name)
        exit(1)

    outpath = os.path.join(image_path, "%s.vdi" % outname)

    m = image.VM()
    m.clone_hd(image.path, outpath)

    # Retain all fields but update the mode, name & path.
    make_transient(image)
    image.id = None
    image.mode = "normal"
    image.name = outname
    image.path = outpath

    session.add(image)
    session.commit()

@main.command()
@click.argument("name")
@click.option("--winxp", is_flag=True, help="This is a Windows XP instance.")
@click.option("--win7x86", is_flag=True, help="This is a Windows 7 32-bit instance.")
@click.option("--win7x64", is_flag=True, help="This is a Windows 7 64-bit instance.")
@click.option("--win81x86", is_flag=True, help="This is a Windows 8.1 32-bit instance.")
@click.option("--win81x64", is_flag=True, help="This is a Windows 8.1 64-bit instance.")
@click.option("--win10x86", is_flag=True, help="This is a Windows 10 32-bit instance.")
@click.option("--win10x64", is_flag=True, help="This is a Windows 10 64-bit instance.")
@click.option("--product", help="Windows 7 product version.")
@click.option("--vm", default="virtualbox", help="Virtual Machinery.")
@click.option("--iso-mount", help="Mounted ISO Windows installer image.")
@click.option("--serial-key", help="Windows Serial Key.")
@click.option("--ip", default="192.168.56.2", help="Guest IP address.")
@click.option("--port", default=8000, help="Port to run the Agent on.")
@click.option("--adapter", default="vboxnet0", help="Network adapter.")
@click.option("--netmask", default="255.255.255.0", help="Guest IP address.")
@click.option("--gateway", default="192.168.56.1", help="Guest IP address.")
@click.option("--dns", default="8.8.8.8", help="DNS Server.")
@click.option("--cpus", default=1, help="CPU count.")
@click.option("--ramsize", type=int, help="Memory size")
@click.option("--vramsize", default=16, help="Video memory size")
@click.option("--hddsize", type=int, default=256, help="HDD size *1024")
@click.option("--tempdir", default=iso_dst_path, help="Temporary directory to build the ISO file.")
@click.option("--resolution", default="1024x768", help="Screen resolution.")
@click.option("--vm-visible", is_flag=True, help="Start the Virtual Machine in GUI mode.")
@click.option("--vrde", is_flag=True, help="Enable the VirtualBox Remote Display Protocol.")
@click.option("--vrde-port", default=3389, help="Specify the VRDE port.")
@click.option("--python-version", default="2.7.6", help="Which Python version do we install on the guest?")
@click.option("-d", "--debug", is_flag=True, help="Install Virtual Machine in debug mode.")
def init(name, winxp, win7x86, win7x64, win81x86, win81x64, win10x86, win10x64,
         product, vm, iso_mount, serial_key, ip, port, adapter, netmask,
         gateway, dns, cpus, ramsize, vramsize, hddsize, tempdir, resolution,
         vm_visible, vrde, vrde_port, python_version, debug):
    """Create a new image"""
    if debug:
        vrde = True
        log.setLevel(logging.DEBUG)

    session = Session()
    image = session.query(Image).filter_by(name=name).first()
    if image:
        log.error("Image already exists: %s", name)
        exit(1)

    if vm not in VMCLOAK_VM_MODES:
        log.error("Only VirtualBox Machinery or iso is supported at this point.")
        exit(1)

    if winxp:
        osversion = "winxp"
        ramsize = ramsize or 1024
    elif win7x86:
        ramsize = ramsize or 1024
        osversion = "win7x86"
    elif win7x64:
        ramsize = ramsize or 2048
        osversion = "win7x64"
    elif win81x86:
        ramsize = ramsize or 2048
        osversion = "win81x86"
    elif win81x64:
        ramsize = ramsize or 2048
        osversion = "win81x64"
    elif win10x86:
        ramsize = ramsize or 2048
        osversion = "win10x86"
    elif win10x64:
        ramsize = ramsize or 2048
        osversion = "win10x64"
    else:
        log.error(
            "Please provide one of --winxp, --win7x86, --win7x64, "
            "--win81x86, --win81x64, --win10x86, --win10x64."
        )
        exit(1)
    h = get_os(osversion)()

    mount = h.pickmount(iso_mount)
    if not mount:
        log.error("Please specify --iso-mount to a directory containing the "
                  "mounted Windows Installer ISO image.")
        log.info("Refer to the documentation on mounting an .iso image.")
        exit(1)

    if not h.set_serial_key(serial_key):
        exit(1)

    h.configure(tempdir=tempdir, product=product)

    reso_width, reso_height = resolution.split("x")

    bootstrap = tempfile.mkdtemp(prefix="vmcloak", dir=tempdir)

    vmcloak_dir = os.path.join(bootstrap, "vmcloak")
    os.mkdir(vmcloak_dir)

    # Download the Python dependency and set it up for bootstrapping the VM.
    d = Python(i=Image(osversion=osversion), h=h, version=python_version)
    d.download()
    shutil.copy(d.filepath, vmcloak_dir)

    settings = dict(
        GUEST_IP=ip,
        AGENT_PORT=port,
        GUEST_MASK=netmask,
        GUEST_GATEWAY=gateway,
        DNSSERVER=dns,
        DEBUG="yes" if debug else "no",
        RESO_WIDTH=reso_width,
        RESO_HEIGHT=reso_height,
        INTERFACE=h.interface,
        PYTHONINSTALLER=d.exe["filename"],
        PYTHONWINDOW=d.exe["window_name"],
        PYTHONPATH=d.exe["install_path"],
    )

    # Write the configuration values for bootstrap.bat.
    with open(os.path.join(vmcloak_dir, "settings.bat"), "wb") as f:
        for key, value in settings.items():
            print("set %s=%s" % (key, value), file=f)

    iso_path = os.path.join(tempdir, "%s.iso" % name)
    hdd_path = os.path.join(image_path, "%s.vdi" % name)

    if not h.buildiso(mount, iso_path, bootstrap, tempdir):
        shutil.rmtree(bootstrap)
        exit(1)

    shutil.rmtree(bootstrap)

    p = repository.platform(vm)
    m = p.VM(name)

    if vm == "virtualbox":
        m.create_vm()
        m.os_type(osversion)
        m.cpus(cpus)
        m.mouse("usbtablet")
        m.ramsize(ramsize)
        m.vramsize(vramsize)
        m.create_hd(hdd_path, hddsize * 1024)
        m.attach_iso(iso_path)
        m.hostonly(nictype=h.nictype, adapter=adapter)

        if vrde:
            m.vrde(port=vrde_port)

        log.info("Starting the Virtual Machine %r to install Windows.", name)
        m.start_vm(visible=vm_visible)

        m.wait_for_state(shutdown=True)

        m.detach_iso()
        os.unlink(iso_path)

        m.remove_hd()
        m.compact_hd(hdd_path)
        m.delete_vm()
    else:
        # TODO
        log.info("You can find your deployment ISO image at %s", iso_path)

    log.info("Added image %r to the repository.", name)
    session.add(Image(name=name, path=hdd_path, osversion=osversion,
                      servicepack="%s" % h.service_pack, mode="normal",
                      ipaddr=ip, port=port, adapter=adapter,
                      netmask=netmask, gateway=gateway,
                      cpus=cpus, ramsize=ramsize, vramsize=vramsize, vm="%s" % vm))
    session.commit()

@main.command()
@click.argument("name")
@click.argument("dependencies", nargs=-1)
@click.option("--vm-visible", is_flag=True)
@click.option("--vrde", is_flag=True, help="Enable the VirtualBox Remote Display Protocol.")
@click.option("--vrde-port", default=3389, help="Specify the VRDE port.")
@click.option("-r", "--recommended", is_flag=True, help="Install recommended packages.")
@click.option("-d", "--debug", is_flag=True, help="Install applications in debug mode.")
def install(name, dependencies, vm_visible, vrde, vrde_port, recommended, debug):
    """Install dependencies on an image"""
    user_attr = {}
    if debug:
        vrde = True
        log.setLevel(logging.DEBUG)
    if vrde:
        user_attr["vrde"] = vrde_port

    image = init_image_vm(name, vm_visible, user_attr)
    m = image.VM()
    h = get_os(image.osversion)

    a = Agent(image.ipaddr, image.port)
    a.ping()

    settings = {}
    deps = []

    # Include all recommended dependencies if requested.
    for dependency in vmcloak.dependencies.plugins:
        if recommended and dependency.recommended:
            deps.append((dependency.name, dependency.default))

    # Fetch the configuration settings off of the arguments.
    for dependency in dependencies:
        if "." in dependency and "=" in dependency:
            key, value = dependency.split("=", 1)
            settings[key.strip()] = value.strip()
        elif ":" in dependency:
            dependency, version = dependency.split(":", 1)
            deps.append((dependency, version))
        else:
            deps.append((dependency, None))

    for dependency, version in deps:
        if dependency not in vmcloak.dependencies.names:
            log.error("Unknown dependency %s..", dependency)
            break

        if version:
            log.info("Installing dependency %s %s..", dependency, version)
        else:
            log.info("Installing dependency %s..", dependency)

        try:
            # TODO Recursive install function.
            d = vmcloak.dependencies.names[dependency]

            # Check if there are any "childs" for dependencies.
            if d.depends:
                depends = d.depends
                if isinstance(depends, basestring):
                    depends = [depends]

                for depend in depends:
                    if ":" in depend:
                        depend, dversion = depend.split(":", 1)
                    else:
                        dversion = None

                    if depend in dependencies:
                        index = dependencies.index(depend)
                        if dversion:
                            log.error(
                                "You specified %s. Will be reinstalling "
                                "as: %s %s",
                                dependencies[index], depend, dversion
                            )
                        else:
                            log.error(
                                "You specified %s. Will be reinstalling "
                                "as: %s", dependencies[index], depend
                            )

                    if dversion:
                        log.info("Installing child dependency %s %s..", depend, dversion)
                    else:
                        log.info("Installing child dependency %s..", depend)

                    # Install dependency child before dependency itself.
                    dd = vmcloak.dependencies.names[depend]
                    dd(h, m, a, image, dversion, settings).run()

                # Reboot the VM as we expect most dependencies to be related
                # to KB installs.
                a.reboot()
                time.sleep(10)
                wait_for_host(image.ipaddr, image.port)

            d(h, m, a, image, version, settings).run()
        except DependencyError:
            log.error("The dependency %s returned an error..", dependency)
            break

    if image.vm == "virtualbox":
        a.shutdown()
        m.wait_for_state(shutdown=True)

        m.remove_hd()
        m.compact_hd(image.path)
        m.delete_vm()
    else:
        a.reboot()

@main.command()
@click.argument("name")
@click.option("--vm-visible", is_flag=True)
@click.option("--vrde", is_flag=True, help="Enable the VirtualBox Remote Display Protocol.")
@click.option("--vrde-port", default=3389, help="Specify the VRDE port.")
@click.option("-d", "--debug", is_flag=True, help="Install applications in debug mode.")
def modify(name, vm_visible, vrde, vrde_port, debug):
    user_attr = {}
    if debug:
        vrde = True
        log.setLevel(logging.DEBUG)
    if vrde:
        user_attr["vrde"] = vrde_port

    image = init_image_vm(name, vm_visible, user_attr)
    log.info("The Virtual Machine has booted and is ready to be modified!")
    log.info("When you shut it down, all changes will be saved.")

    vm = image.VM()
    vm.wait_for_state(shutdown=True)
    vm.remove_hd()
    vm.compact_hd(image.path)
    vm.delete_vm()

@main.command()
@click.argument("vmname")
@click.argument("cuckoo")
@click.argument("tags", required=False, default="")
def register(vmname, cuckoo, tags):
    snapshot = repository.find_snapshot(vmname)
    if not snapshot:
        log.error("Snapshot not found: %s", vmname)
        exit(1)

    # TODO Add snapshot.port & snapshot.adapter to the configuration.
    # But those options will require various changes in Cuckoo as well.
    register_cuckoo(snapshot.ipaddr, tags, vmname, cuckoo)

def do_snapshot(image, vmname, attr, vm_visible, interactive):
    vm = image.platform.create_vm(vmname, attr, True)

    vm.start_vm(visible=vm_visible)

    wait_for_host(image.ipaddr, image.port)
    a = Agent(image.ipaddr, image.port)
    a.ping()

    # Assign a new hostname.
    hostname = attr.get("hostname") or random_string(8, 16)
    a.hostname(hostname)
    a.reboot()
    a.kill()

    # Wait for the reboot to kick in.
    time.sleep(10)
    wait_for_host(image.ipaddr, image.port)
    a.ping()

    if attr.get("resolution"):
        width, height = attr["resolution"].split("x")
        a.resolution(width, height)

    if interactive:
        a.upload("C:\\vmcloak\\interactive.txt",
                 "Please make your final changes to this VM. When you're"
                 "done, close this window and we'll create a snapshot.")

        log.info("You've started the snapshot creation in interactive mode!")
        log.info("Please make your last changes to the VM.")
        log.info("When you're done close the spawned notepad process in the VM to take the final snapshot.")
        a.execute("notepad.exe C:\\vmcloak\\interactive.txt", async=False)

    a.remove("C:\\vmcloak")
    h = get_os(image.osversion)
    a.static_ip(attr["ipaddr"], attr["netmask"], attr["gateway"], h.interface)
    vm.snapshot("vmcloak", "Snapshot created by VMCloak.")
    vm.stop_vm()

    # Create a database entry for this snapshot.
    return Snapshot(image_id=image.id, vmname=vmname, hostname=hostname,
                    ipaddr=attr["ipaddr"], port=attr["port"])

def _if_defined(attr, k, v):
    if v is not None:
        attr[k] = v

@main.command()
@click.argument("name")
@click.argument("vmname")
@click.argument("ipaddr", required=False, default="192.168.56.101")
@click.option("--resolution", help="Screen resolution.")
@click.option("--ramsize", type=int, help="Amount of virtual memory to assign.")
@click.option("--cpus", type=int, help="Amount of CPUs to assign.")
@click.option("--hostname", help="Hostname for this VM.")
@click.option("--adapter", help="Hostonly adapter for this VM.")
@click.option("--vm-visible", is_flag=True, help="Start the Virtual Machine in GUI mode.")
@click.option("--count", type=int, help="The amount of snapshots to make.")
@click.option("--vrde", is_flag=True, help="Enable the VirtualBox Remote Display Protocol.")
@click.option("--vrde-port", default=3389, help="Specify the VRDE port.")
@click.option("--interactive", is_flag=True, help="Enable interactive snapshot mode.")
@click.option("-d", "--debug", is_flag=True, help="Make snapshot in debug mode.")
@click.option("--com1", is_flag=True, help="Enable COM1 for this VM.")
def snapshot(name, vmname, ipaddr, resolution, ramsize, cpus, hostname,
             adapter, vm_visible, count, vrde, vrde_port, interactive, debug,
             com1):
    """Create one or more snapshots from an image"""
    if debug:
        log.setLevel(logging.DEBUG)

    session = Session()

    if adapter:
        log.error(
            "Specifying a different adapter is not yet supported for "
            "snapshots (this will require detaching the current adapter and "
            "attaching a new one after the static IP address has been "
            "updated or so)."
        )
        exit(1)

    image = session.query(Image).filter_by(name=name).first()
    if not image:
        log.error("Image not found: %s", name)
        exit(1)

    # From now on this image is multiattach.
    image.mode = "multiattach"
    session.commit()

    attr = image.attr()
    attr["ipaddr"] = ipaddr
    _if_defined(attr, "adapter", adapter)
    _if_defined(attr, "cpus", cpus)
    _if_defined(attr, "hostname", hostname)
    _if_defined(attr, "ramsize", ramsize)
    _if_defined(attr, "resolution", resolution)
    if vrde:
        attr["vrde"] = vrde_port

    if not count:
        if com1:
            attr["serial"] = os.path.join(vms_path, vmname, "%s.com1" % vmname)
        snapshot = do_snapshot(image, vmname, attr, vm_visible, interactive)
        session.add(snapshot)
    else:
        if hostname:
            log.error(
                "You specified a hostname, but this is not supported when "
                "creating multiple snapshots at once."
            )
            exit(1)

        for x in xrange(count):
            name = "%s%d" % (vmname, x + 1)
            if com1:
                attr["serial"] = os.path.join(vms_path, name, "%s.com1" % name)
            attr["hostname"] = random_string(8, 16)
            snapshot = do_snapshot(image, name, attr, vm_visible, interactive)
            session.add(snapshot)

            # TODO Implement some limits to make sure that the IP address does
            # not "exceed" its provided subnet (and thus also require the user
            # to specify an IP range, rather than an IP address).
            ipaddr = ipaddr_increase(ipaddr)
            attr["ipaddr"] = ipaddr
            hostname = random_string(8, 16)

    session.commit()

@main.command()
@click.argument("name")
@click.argument("filepath", type=click.Path(writable=True))
def export(name, filepath):
    if not filepath.endswith((".ova", ".ovf")):
        log.error("The exported file should be either .ova or .ovf")
        exit(1)

    session = Session()

    image = session.query(Image).filter_by(name=name).first()
    if not image:
        log.error("Image not found: %s", name)
        exit(1)

    if image.mode != "normal":
        log.error("You can't export this image as you have already made "
                  "snapshots with it!")
        log.error("Please vmcloak clone it and export the clone.")
        exit(1)

    m, h = initvm(image)

    m.export(filepath)

    m.remove_hd()
    m.compact_hd(image.path)
    m.delete_vm()

@main.command()
@click.argument("ipaddr")
@click.argument("port", required=False, default=8000)
def zer0m0n(ipaddr, port):
    log.setLevel(logging.INFO)

    log.info("Checking if we can reach the VM..")
    a = Agent(ipaddr, port)

    try:
        status = a.ping().json()
    except requests.RequestException:
        log.error("Couldn't reach the VM, is it up-and-running? Aborting..")
        return

    if not isinstance(status, dict) or status.get("message") != "Cuckoo Agent!":
        log.error("Agent in VM isn't the new Cuckoo Agent? Aborting..")
        return

    h = Windows7x64()
    log.info("Patching zer0m0n-related files.")
    vmcloak.dependencies.names["zer0m0n"](a=a, h=h).run()
    log.info("Good to go, now *reboot* and make a new *snapshot* of your VM!")

###

@main.command()
@click.argument("name")
def delvm(name):
    """Remove VM and delete all its files
    Will not remove the base image"""
    is_snapshot, vm = repository.find_vm(name)
    if not vm:
        print("Not found:", name)
        exit(1)
    try:
        vm.stop_vm()
    except CommandError:
        log.debug("Could not stop VM; maybe it wasn't running")
    if not is_snapshot:
        vm.remove_hd() # Detach
    vm.delete_vm()
    repository.remove_snapshot(name)

@main.command()
@click.argument("name")
def delimg(name):
    """Delete an image"""
    image = repository.find_image(name)
    if not image:
        print("Not found:", name)
        exit(1)
    if image.snapshots:
        print("Image", name, "still has snapshots. Aborting.")
        exit(1)
    try:
        image.platform.remove_hd(image.path)
    finally:
        if not os.path.exists(image.path):
            repository.remove_image(name)

@main.command()
@click.argument("name")
def start(name):
    """Start a snapshot or VM"""
    obj = repository.any_from_name(name)
    platform = obj.platform
    if isinstance(obj, Image):
        vm = platform.create_vm_for_image(name, obj)
    else:
        vm = obj.VM()
    vm.start_vm()
    # TODO: this conflicts with "modify"

@main.command("import")
def _import():
    """Import images and snapshots
    Can also be used to fix paths"""
    # TODO: make deletion of
    repository.import_all()

###

@main.group("list")
def _list():
    pass

@_list.command("images")
def list_images():
    for img in repository.list_images():
        print("*", img.name, img.platform.name)

@_list.command("snapshots")
def list_snapshots():
    snaps = repository.list_snapshots()
    snaps.sort(key=lambda snap: (snap.image.name, snap.vmname))
    parent = None
    for snap in snaps:
        if snap.image.name != parent:
            parent = snap.image.name
            print(parent, " (", snap.platform.name, ")", sep="")
        print("-", snap.vmname)

def list_dependencies():
    print("Name", "version", "target", "sha1")
    print()
    for name, d in sorted(vmcloak.dependencies.names.items()):
        if d.exes:
            versionlen = max(len(exe.get("version", "None")) for exe in d.exes)
        else:
            versionlen = 4
        print(name)
        for exe in d.exes:
            v = exe.get("version", "None")
            print("  *" if d.default and d.default == v else "   ", end=" ")
            print(exe.get("version", "None").ljust(versionlen), end=" ")
            print(exe.get("target"), exe.get("sha1", "?sha1?"))
        print()

@_list.command("dependencies")
def _list_dependencies():
    list_dependencies()

@_list.command("deps")
def _list_deps():
    list_dependencies()
