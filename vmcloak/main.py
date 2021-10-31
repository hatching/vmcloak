# Copyright (C) 2014-2018 Jurriaan Bremer.
# Copyright (C) 2018 Hatching B.V.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

from __future__ import print_function

import click
import logging
import os.path
import requests
import shutil
import subprocess
import tempfile
import time

from sqlalchemy.orm.session import make_transient

from vmcloak import repository
import vmcloak.dependencies

from vmcloak.agent import Agent
from vmcloak.constants import VMCLOAK_ROOT
from vmcloak.dependencies import Python
from vmcloak.exceptions import DependencyError
from vmcloak.misc import wait_for_agent, register_cuckoo, drop_privileges
from vmcloak.misc import ipaddr_increase
from vmcloak.rand import random_string
from vmcloak.repository import (
    image_path, Session, Image, Snapshot, iso_dst_path, db_migratable,
    SCHEMA_VERSION
)
from vmcloak.ostype import get_os

logging.basicConfig(format="%(asctime)s %(name)s %(levelname)s: %(message)s")
log = logging.getLogger("vmcloak")
log.setLevel(logging.WARNING)

@click.group(invoke_without_command=True)
@click.option("-u", "--user", help="Drop privileges to user.")
@click.option("-v", "--verbose", is_flag=True, help="Verbose logging.")
@click.option("-d", "--debug", is_flag=True, help="Enable debugging.")
@click.pass_context
def main(ctx, user, verbose, debug):
    ctx.meta["debug"] = debug
    user and drop_privileges(user)
    if verbose:
        log.setLevel(logging.INFO)
    if debug:
        log.setLevel(logging.DEBUG)

    if db_migratable():
        log.error(
            "Database schema version mismatch. Expected: '%s'. "
            "Optionally make a backup and then apply automatic database "
            "migration by using: 'vmcloak migrate'" % SCHEMA_VERSION
        )

        if ctx.invoked_subcommand != "migrate":
            exit(1)

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

    p = image.platform
    outpath = os.path.join(image_path, "%s.%s" % (outname, p.disk_format))

    p.clone_disk(image, outpath)

    # Retain all fields but update the mode, name & path.
    make_transient(image)
    image.id = None
    image.mode = "normal"
    image.name = outname
    image.path = outpath

    session.add(image)
    session.commit()

_vm_attributes = [
    click.option("--adapter", help="Specify network adapter/bridge to use."),
    click.option("--ip", default="192.168.56.2", help="Guest IP address."),
    click.option("--port", default=8000, help="Port to run the Agent on."),
    click.option("--netmask", default="255.255.255.0", help="Guest IP address."),
    click.option("--gateway", default="192.168.56.1", help="Guest IP address."),
    click.option("--dns", default="8.8.8.8", help="DNS Server."),
    click.option("--cpus", default=1, help="CPU count."),
    click.option("--ramsize", type=int, help="Memory size"),
    click.option("--vramsize", default=16, help="Video memory size"),
    click.option("--hddsize", type=int, default=256, help="HDD size *1024"),
    click.option("--tempdir", default=iso_dst_path, help="Temporary directory to build the ISO file."),
    click.option("--resolution", default="1024x768", help="Screen resolution."),
    click.option("--vm-visible", is_flag=True, help="Start the Virtual Machine in GUI mode."),
    click.option("--vrde", is_flag=True, help="Enable the remote display (RDP or VNC)."),
    click.option("--vrde-port", default=3389, help="Specify the remote display port."),
    click.option("--paravirtprovider", default="default", help="Select paravirtprovider for Virtualbox none|default|legacy|minimal|hyperv|kvm")
]

_iso_attributes = [
    # TODO: use something like --os winX
    click.option("--winxp", is_flag=True, help="This is a Windows XP instance."),
    click.option("--win7x86", is_flag=True, help="This is a Windows 7 32-bit instance."),
    click.option("--win7x64", is_flag=True, help="This is a Windows 7 64-bit instance."),
    click.option("--win81x86", is_flag=True, help="This is a Windows 8.1 32-bit instance."),
    click.option("--win81x64", is_flag=True, help="This is a Windows 8.1 64-bit instance."),
    click.option("--win10x86", is_flag=True, help="This is a Windows 10 32-bit instance."),
    click.option("--win10x64", is_flag=True, help="This is a Windows 10 64-bit instance."),
    click.option("--iso-mount", help="Mounted ISO Windows installer image."),
    click.option("--serial-key", help="Windows Serial Key."),
    click.option("--product", help="Windows 7 product version."),
    click.option("--python-version", default="2.7.13", help="Python version to install on VM."),
]

def _add_install_attr(func):
    for attr in _vm_attributes:
        func = attr(func)
    for attr in _iso_attributes:
        func = attr(func)
    return func

def _add_snapshot_attr(func):
    for attr in _vm_attributes:
        func = attr(func)
    return func

def os_from_attr(attr):
    ramsize = attr["ramsize"]
    if attr["winxp"]:
        osversion = "winxp"
        ramsize = ramsize or 1024
    elif attr["win7x86"]:
        ramsize = ramsize or 1024
        osversion = "win7x86"
    elif attr["win7x64"]:
        ramsize = ramsize or 2048
        osversion = "win7x64"
    elif attr["win81x86"]:
        ramsize = ramsize or 2048
        osversion = "win81x86"
    elif attr["win81x64"]:
        ramsize = ramsize or 2048
        osversion = "win81x64"
    elif attr["win10x86"]:
        ramsize = ramsize or 2048
        osversion = "win10x86"
    elif attr["win10x64"]:
        ramsize = ramsize or 2048
        osversion = "win10x64"
    else:
        log.error(
            "Please provide one of --winxp, --win7x86, --win7x64, "
            "--win81x86, --win81x64, --win10x86, --win10x64."
        )
        exit(1)
    attr["ramsize"] = ramsize
    attr["osversion"] = osversion
    return get_os(osversion)


@main.command()
@click.argument("iso_path")
@_add_install_attr
@click.pass_context
def createiso(ctx, iso_path, **attr):
    """Create new ISO install image"""
    attr["debug"] = ctx.meta["debug"]
    _create_iso(iso_path, attr)

def _create_iso(iso_path, attr):
    # Prepare OS
    h = os_from_attr(attr)
    h.configure(tempdir=attr["tempdir"], product=attr["product"])

    if not h.set_serial_key(attr["serial_key"]):
        exit(1)
    mount = h.pickmount(attr["iso_mount"])
    if not mount:
        log.error("Please specify --iso-mount to a directory containing the "
                  "mounted Windows Installer ISO image.")
        log.info("Refer to the documentation on mounting an .iso image.")
        exit(1)

    bootstrap = tempfile.mkdtemp(prefix="vmcloak", dir=h.tempdir)
    vmcloak_dir = os.path.join(bootstrap, "vmcloak")
    os.mkdir(vmcloak_dir)

    # Download the Python dependency and set it up for bootstrapping the VM.
    d = Python(h=h, i=Image(osversion=attr["osversion"]), version=attr["python_version"])
    d.download()
    shutil.copy(d.filepath, vmcloak_dir)

    # Prepare settings
    reso_width, reso_height = attr["resolution"].split("x")
    attr["reso_width"] = reso_width
    attr["reso_height"] = reso_height

    settings = dict(
        GUEST_IP=attr["ip"],
        AGENT_PORT=attr["port"],
        GUEST_MASK=attr["netmask"],
        GUEST_GATEWAY=attr["gateway"],
        DNSSERVER=attr["dns"],
        DEBUG="yes" if attr["debug"] else "no",
        RESO_WIDTH=attr["reso_width"],
        RESO_HEIGHT=attr["reso_height"],
        INTERFACE=h.interface,
        PYTHONINSTALLER=d.exe["filename"],
        PYTHONWINDOW=d.exe["window_name"],
        PYTHONPATH=d.exe["install_path"],
    )

    # Write the configuration values for bootstrap.bat.
    with open(os.path.join(vmcloak_dir, "settings.bat"), "wb") as f:
        for key, value in settings.items():
            print("set %s=%s" % (key, value), file=f)

    # Now try building the ISO
    try:
        if not h.buildiso(mount, iso_path, bootstrap, h.tempdir):
            exit(1)
    finally:
        shutil.rmtree(bootstrap)

    log.info("Created ISO: %s", iso_path)

@main.command()
@click.argument("name")
@_add_install_attr
@click.option("--iso", help="Specify install ISO to use.")
@click.option("--vm", default="virtualbox", help="Virtual Machinery.")
@click.pass_context
def init(ctx, name, iso, vm, **attr):
    """Create a new image"""
    attr["debug"] = ctx.meta["debug"]
    if attr["vrde"] or attr["debug"]:
        attr["vrde"] = attr["vrde_port"]

    try:
        p = repository.platform(vm)
    except ImportError:
        log.error("Platform %r is not supported at this point.", vm)
        exit(1)

    session = Session()
    image = session.query(Image).filter_by(name=name).first()
    if image:
        log.error("Image already exists: %s", name)
        exit(1)

    h = os_from_attr(attr)

    if not iso:
        iso_path = os.path.join(attr["tempdir"], "%s.iso" % name)
        _create_iso(iso_path, attr)
        remove_iso = True
    else:
        iso_path = iso
        remove_iso = False

    try:
        attr["path"] = os.path.join(image_path, "%s.%s" % (name, p.disk_format))

        # Create new image from ISO
        p.create_new_image(name, os, iso_path, attr)
    except:
        log.exception("Failed to create %r:", name)
        return
    finally:
        p.remove_vm_data(name)
        if remove_iso:
            os.remove(iso_path)

    log.info("Added image %r to the repository.", name)
    session.add(Image(name=name,
                      path=attr["path"],
                      osversion=attr["osversion"],
                      servicepack="%s" % h.service_pack,
                      mode="normal",
                      ipaddr=attr["ip"],
                      port=attr["port"],
                      adapter=attr["adapter"],
                      netmask=attr["netmask"],
                      gateway=attr["gateway"],
                      cpus=attr["cpus"],
                      ramsize=attr["ramsize"],
                      vramsize=attr["vramsize"],
                      vm="%s" % vm,
                      paravirtprovider=attr["paravirtprovider"]))
    session.commit()

@main.command()
@click.argument("name")
@click.argument("dependencies", nargs=-1)
@click.option("--vm-visible", is_flag=True)
@click.option("--vrde", is_flag=True, help="Enable the VirtualBox Remote Display Protocol.")
@click.option("--vrde-port", default=3389, help="Specify the VRDE port.")
@click.option("-r", "--recommended", is_flag=True, help="Install recommended packages.")
@click.option("-d", "--debug", is_flag=True, help="Install applications in debug mode.")
@click.pass_context
def install(ctx, name, dependencies, vm_visible, vrde, vrde_port, recommended, debug):
    """Install dependencies on an image"""

    user_attr = {"vm_visible": vm_visible}
    if vrde or ctx.meta["debug"]:
        user_attr["vrde"] = vrde_port

    image = repository.find_image(name)
    if not image:
        log.error("Image not found: %s", name)
        exit(1)

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

    p = image.platform
    m = p.VM(image.name)
    h = get_os(image.osversion)
    p.start_image_vm(image, user_attr)
    try:
        a = Agent(image.ipaddr, image.port)
        wait_for_agent(a)

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

                # Check if there are any child dependencies.
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
                    wait_for_agent(a)

                d(h, m, a, image, version, settings).run()
            except DependencyError:
                log.error("The dependency %s returned an error..", dependency)
                break

        a.shutdown()
        p.wait_for_shutdown(image.name, 30)
    finally:
        p.remove_vm_data(image.name)

@main.command()
@click.argument("name")
@click.option("--vm-visible", is_flag=True)
@click.option("--vrde", is_flag=True, help="Enable the VirtualBox Remote Display Protocol.")
@click.option("--vrde-port", default=3389, help="Specify the VRDE port.")
@click.pass_context
def modify(ctx, name, vm_visible, vrde, vrde_port):
    user_attr = {"vm_visible": vm_visible}
    if vrde or ctx.meta["debug"]:
        user_attr["vrde"] = vrde_port

    image = repository.find_image(name)
    p = image.platform
    p.start_image_vm(image, user_attr)
    try:
        log.warning("The Virtual Machine has booted and is ready to be modified!")
        log.warning("When you shut it down, all changes will be saved.")
        p.wait_for_shutdown(image.name)
    finally:
        p.remove_vm_data(image.name)

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

def _snapshot(image, vmname, attr, interactive):
    log.info("Creating snapshot %s (%s)", vmname, attr["ip"])
    p = image.platform
    p.create_snapshot_vm(image, vmname, attr)

    a = Agent(image.ipaddr, image.port)
    wait_for_agent(a)

    # Assign a new hostname.
    hostname = attr.get("hostname") or random_string(8, 16)
    a.hostname(hostname)
    a.reboot()
    a.kill()

    # Wait for the reboot to kick in.
    time.sleep(10)
    wait_for_agent(a)

    #if attr.get("resolution"):
    #    width, height = attr["resolution"].split("x")
    #    a.resolution(width, height)

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
    a.static_ip(attr["ip"], attr["netmask"], attr["gateway"], h.interface)

    p.create_snapshot(vmname)

    # Create a database entry for this snapshot.
    return Snapshot(image_id=image.id, vmname=vmname, hostname=hostname,
                    ipaddr=attr["ip"], port=attr["port"])

def _if_defined(attr, k, v):
    if v is not None:
        attr[k] = v

def vm_iter(count, name, ip, port):
    if not count:
        yield name, ip, port
    else:
        for i in range(count):
            yield "%s%s" % (name, i + 1), ip, port + i
            # TODO Implement some limits to make sure that the IP address does
            # not "exceed" its provided subnet (and thus also require the user
            # to specify an IP range, rather than an IP address).
            ip = ipaddr_increase(ip)

@main.command()
@click.argument("name")
@click.option("--vm", default="virtualbox", help="Virtual Machinery.")
def cleanup(name, vm):
    p = repository.platform(vm)
    p.remove_vm_data(name)

@main.command()
@click.argument("name")
@click.argument("vmname")
@click.argument("ip", required=False, default="192.168.56.101")
@click.option("--resolution", help="Screen resolution.")
@click.option("--ramsize", type=int, help="Amount of virtual memory to assign.")
@click.option("--cpus", type=int, help="Amount of CPUs to assign.")
@click.option("--hostname", help="Hostname for this VM.")
@click.option("--adapter", help="Hostonly adapter for this VM.")
@click.option("--vm-visible", is_flag=True, help="Start the Virtual Machine in GUI mode.")
@click.option("--count", type=int, help="The amount of snapshots to make.")
@click.option("--share", help="Add shared folder")
@click.option("--vrde", is_flag=True, help="Enable the VirtualBox Remote Display Protocol.")
@click.option("--vrde-port", default=3389, help="Specify the VRDE port.")
@click.option("--interactive", is_flag=True, help="Enable interactive snapshot mode.")
@click.option("--com1", is_flag=True, help="Enable COM1 for this VM.")
@click.pass_context
def snapshot(ctx, name, vmname, ip, resolution, ramsize, cpus, hostname,
             adapter, vm_visible, count, share, vrde, vrde_port, interactive,
             com1):
    """Create one or more snapshots from an image"""

    if adapter:
        log.error(
            "Specifying a different adapter is not yet supported for "
            "snapshots (this will require detaching the current adapter and "
            "attaching a new one after the static IP address has been "
            "updated or so)."
        )
        exit(1)

    if count and hostname:
        log.error(
            "You specified a hostname, but this is not supported when "
            "creating multiple snapshots at once."
        )
        exit(1)

    session = Session()
    image = session.query(Image).filter_by(name=name).first()
    if not image:
        log.error("Image not found: %s", name)
        exit(1)

    # From now on this image is multiattach.
    image.mode = "multiattach"
    session.commit()

    # Copy properties from image and replace snapshot-specific ones
    p = image.platform
    attr = image.attr()
    attr["imgpath"] = attr.pop("path")
    attr["ip"] = ip
    attr["vm_visible"] = vm_visible
    _if_defined(attr, "cpus", cpus)
    _if_defined(attr, "hostname", hostname)
    _if_defined(attr, "ramsize", ramsize)
    _if_defined(attr, "resolution", resolution)
    _if_defined(attr, "share", share)

    # TODO: must detect adapter change, because changing it requires booting
    # the old adapter (or use IPv6-LL)
    _if_defined(attr, "adapter", adapter)

    if vrde or ctx.meta["debug"]:
        attr["vrde"] = vrde_port

    for vmname, ip, port in vm_iter(count, vmname, attr["ip"], vrde_port):
        vmdir = p.prepare_snapshot(vmname, attr)
        if not vmdir:
            log.warning("Not creating %r because it exists", vmname)
            continue
        if not os.path.exists(vmdir):
            os.makedirs(vmdir)
        if "vrde" in attr:
            attr["vrde"] = port
        if com1:
            attr["serial"] = os.path.join(vmdir, "%s.com1" % vmname)
        if not hostname:
            attr["hostname"] = random_string(8, 16)
        attr["ip"] = ip
        snapshot = _snapshot(image, vmname, attr, interactive)
        session.add(snapshot)

    session.commit()

# XXX
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

    if image.vm != "virtualbox":
        log.error("Only VirtualBox VMs can be exported.")
        exit(1)

    if image.mode != "normal":
        log.error("You can't export this image as you have already made "
                  "snapshots with it!")
        log.error("Please vmcloak clone it and export the clone.")
        exit(1)

    image.platform.export_vm(image, filepath)

@main.command()
@click.argument("name")
def restore(name):
    """Restore snapshot"""
    snapshot = repository.find_snapshot(name)
    if not snapshot:
        log.error("Snapshot not found: %s", name)
        exit(1)
    log.info("Restoring %s to vmcloak snapshot", name)
    p = snapshot.platform
    p.restore_snapshot(name, "vmcloak")

@main.command()
@click.argument("ip")
@click.argument("port", required=False, default=8000)
def zer0m0n(ip, port):
    log.setLevel(logging.INFO)

    log.info("Checking if we can reach the VM..")
    a = Agent(ip, port)

    try:
        status = a.ping().json()
    except requests.RequestException:
        log.error("Couldn't reach the VM, is it up-and-running? Aborting..")
        return

    if not isinstance(status, dict) or status.get("message") != "Cuckoo Agent!":
        log.error("Agent in VM isn't the new Cuckoo Agent? Aborting..")
        return

    h = get_os("win7x64")
    log.info("Patching zer0m0n-related files.")
    vmcloak.dependencies.names["zer0m0n"](a=a, h=h).run()
    log.info("Good to go, now *reboot* and make a new *snapshot* of your VM!")

@main.command()
@click.option("--revision", default="head", help="Migrate to a certain revision")
def migrate(revision):
    log.setLevel(logging.INFO)

    if not db_migratable():
        log.info("Database schema is already at the latest version")
        exit(0)

    try:
        subprocess.check_call(
            ["alembic", "upgrade", "%s" % revision],
            cwd=os.path.join(VMCLOAK_ROOT, "data", "db_migration")
        )
    except subprocess.CalledProcessError as e:
        log.exception("Database migration failed: %s", e)
        exit(1)
    log.info("Database migration successful!")

@main.command()
@click.argument("name")
def delvm(name):
    """Remove VM and delete all its files
    Will not remove the base image"""
    is_snapshot, obj = repository.find_vm(name)
    if not obj:
        print("Not found:", name)
        exit(1)
    obj.platform.remove_vm_data(name)
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
    image.platform.remove_vm_data(name)
    try:
        log.info("Removing image %s", image.path)
        image.platform.remove_hd(image.path)
    finally:
        repository.remove_image(name)

@main.command("import")
def _import():
    """Import images and snapshots
    Can also be used to fix paths"""
    repository.import_all()

# List things:
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
    print("Name", "version", "target", "sha1", "arch")
    print()
    for name, d in sorted(vmcloak.dependencies.names.items()):
        if d.exes:
            versionlen = max(len(exe.get("version", "None")) for exe in d.exes)
        else:
            versionlen = 4

        print(name)
        for exe in d.exes:
            v = exe.get("version", "None")
            print("  *" if d.default and d.default == v else "   ")
            print(exe.get("version", "None") + " "*(versionlen - len(v)))
            print(exe.get("target"), exe.get("sha1", "None"))
            print(exe.get("arch", ""))
        print()

def list_vms():
    session = Session()
    vms = []
    try:
        vms = session.query(Snapshot).all()
    finally:
        session.close()

    for vm in vms:
        print(vm.vmname, vm.ipaddr)

@_list.command("dependencies")
def _list_dependencies():
    list_dependencies()

@_list.command("deps")
def _list_deps():
    list_dependencies()

@_list.command("vms")
def _list_vms():
    list_vms()
