# Copyright (C) 2014-2016 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import click
import logging
import os.path
import shutil
import tempfile
import time

from sqlalchemy.orm.session import make_transient

import vmcloak.dependencies

from vmcloak.agent import Agent
from vmcloak.dependencies import Python27
from vmcloak.exceptions import DependencyError
from vmcloak.misc import wait_for_host, register_cuckoo, drop_privileges
from vmcloak.misc import ipaddr_increase
from vmcloak.rand import random_string
from vmcloak.repository import image_path, Session, Image, Snapshot, iso_dst_path
from vmcloak.winxp import WindowsXP
from vmcloak.win7 import Windows7x86, Windows7x64
from vmcloak.win81 import Windows81x86, Windows81x64
from vmcloak.win10 import Windows10x86, Windows10x64
from vmcloak.vm import VirtualBox
from vmcloak.constants import VMCLOAK_VM_MODES

logging.basicConfig()
log = logging.getLogger("vmcloak")
log.setLevel(logging.ERROR)

def initvm(image, name=None, multi=False, ramsize=None, vramsize=None, cpus=None):
    handlers = {
        "winxp": WindowsXP,
        "win7x86": Windows7x86,
        "win7x64": Windows7x64,
        "win81x86": Windows81x86,
        "win81x64": Windows81x64,
        "win10x86": Windows10x86,
        "win10x64": Windows10x64,
    }

    h = handlers[image.osversion]
    m = None

    if image.vm == "virtualbox":
        m = VirtualBox(name=name or image.name)
        m.create_vm()
        m.os_type(image.osversion)
        m.cpus(cpus or image.cpus)
        m.mouse("usbtablet")
        m.ramsize(ramsize or image.ramsize)
        m.vramsize(vramsize or image.vramsize)
        m.attach_hd(image.path, multi=multi)
        # Ensure the slot is at least allocated for by an empty drive.
        m.detach_iso()
        m.hostonly(nictype=h.nictype, adapter=image.adapter)

    return m, h

@click.group(invoke_without_command=True)
@click.option("-u", "--user", help="Drop privileges to user.")
def main(user):
    user and drop_privileges(user)

@main.command()
@click.argument("name")
@click.argument("outname")
def clone(name, outname):
    session = Session()

    image = session.query(Image).filter_by(name=name).first()
    if not image:
        log.error("Image not found: %s", name)
        exit(1)

    outpath = os.path.join(image_path, "%s.vdi" % outname)

    m = VirtualBox(None)
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
@click.option("--tempdir", default=iso_dst_path, help="Temporary directory to build the ISO file.")
@click.option("--resolution", default="1024x768", help="Screen resolution.")
@click.option("--vm-visible", is_flag=True, help="Start the Virtual Machine in GUI mode.")
@click.option("-d", "--debug", is_flag=True, help="Install Virtual Machine in debug mode.")
@click.option("-v", "--verbose", is_flag=True, help="Verbose logging.")
def init(name, winxp, win7x86, win7x64, win81x86, win81x64, win10x86,
         win10x64, product, vm, iso_mount, serial_key, ip, port, adapter,
         netmask, gateway, dns, cpus, ramsize, vramsize, tempdir, resolution,
         vm_visible, debug, verbose):
    if verbose:
        log.setLevel(logging.INFO)
    if debug:
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
        h = WindowsXP()
        osversion = "winxp"
        ramsize = ramsize or 1024
    elif win7x86:
        h = Windows7x86()
        ramsize = ramsize or 1024
        osversion = "win7x86"
    elif win7x64:
        h = Windows7x64()
        ramsize = ramsize or 2048
        osversion = "win7x64"
    elif win81x86:
        h = Windows81x86()
        ramsize = ramsize or 2048
        osversion = "win81x86"
    elif win81x64:
        h = Windows81x64()
        ramsize = ramsize or 2048
        osversion = "win81x64"
    elif win10x86:
        h = Windows10x86()
        ramsize = ramsize or 2048
        osversion = "win10x86"
    elif win10x64:
        h = Windows10x64()
        ramsize = ramsize or 2048
        osversion = "win10x64"
    else:
        log.error(
            "Please provide one of --winxp, --win7x86, --win7x64, "
            "--win81x86, --win81x64, --win10x86, --win10x64."
        )
        exit(1)

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
    )

    bootstrap = tempfile.mkdtemp(dir=tempdir)

    vmcloak_dir = os.path.join(bootstrap, "vmcloak")
    os.mkdir(vmcloak_dir)

    # Write the configuration values for bootstrap.bat.
    with open(os.path.join(vmcloak_dir, "settings.bat"), "wb") as f:
        for key, value in settings.items():
            print>>f, "set %s=%s" % (key, value)

    # Download the Python dependency and set it up for bootstrapping the VM.
    d = Python27(i=Image(osversion=osversion))
    d.download()
    shutil.copy(d.filepath, vmcloak_dir)

    iso_path = os.path.join(tempdir, "%s.iso" % name)
    hdd_path = os.path.join(image_path, "%s.vdi" % name)
    m = VirtualBox(name=name)

    if not h.buildiso(mount, iso_path, bootstrap, tempdir):
        shutil.rmtree(bootstrap)
        exit(1)

    shutil.rmtree(bootstrap)

    if vm == "virtualbox":
        m.create_vm()
        m.os_type(osversion)
        m.cpus(cpus)
        m.mouse("usbtablet")
        m.ramsize(ramsize)
        m.vramsize(vramsize)
        m.create_hd(hdd_path)
        m.attach_iso(iso_path)
        m.hostonly(nictype=h.nictype, adapter=adapter)

        log.info("Starting the Virtual Machine %r to install Windows.", name)
        m.start_vm(visible=vm_visible)

        m.wait_for_state(shutdown=True)

        m.detach_iso()
        os.unlink(iso_path)

        m.remove_hd()
        m.compact_hd(hdd_path)
        m.delete_vm()
    else:
        log.info("You can find your deployment ISO image from : %s" % iso_path)

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
@click.option("-r", "--recommended", is_flag=True, help="Install recommended packages.")
@click.option("-d", "--debug", is_flag=True, help="Install applications in debug mode.")
def install(name, dependencies, vm_visible, recommended, debug):
    if debug:
        log.setLevel(logging.DEBUG)

    session = Session()

    image = session.query(Image).filter_by(name=name).first()
    if not image:
        log.error("Image not found: %s", name)
        exit(1)

    if image.mode != "normal":
        log.error("You can't install dependencies in this image as you have "
                  "already made snapshots with it!")
        log.error("Please vmcloak-clone it and update the clone.")
        exit(1)

    m, h = initvm(image)

    if image.vm == "virtualbox":
        m.start_vm(visible=vm_visible)

    wait_for_host(image.ipaddr, image.port)

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
def modify(name, vm_visible):
    session = Session()

    image = session.query(Image).filter_by(name=name).first()
    if not image:
        log.error("Image not found: %s", name)
        exit(1)

    if image.mode != "normal":
        log.error("You can't modify this image as you have already made "
                  "snapshots with it!")
        log.error("Please vmcloak-clone it and modify the clone.")
        exit(1)

    m, h = initvm(image)

    m.start_vm(visible=vm_visible)
    wait_for_host(image.ipaddr, image.port)

    log.info("The Virtual Machine has booted and is ready to be modified!")
    log.info("When you shut it down, all changes will be saved.")

    m.wait_for_state(shutdown=True)

    m.remove_hd()
    m.compact_hd(image.path)
    m.delete_vm()

@main.command()
@click.argument("vmname")
@click.argument("cuckoo")
@click.argument("tags", required=False, default="")
def register(vmname, cuckoo, tags):
    session = Session()

    snapshot = session.query(Snapshot).filter_by(vmname=vmname).first()
    if not snapshot:
        log.error("Snapshot not found: %s", vmname)
        exit(1)

    # TODO Add snapshot.port & snapshot.adapter to the configuration.
    # But those options will require various changes in Cuckoo as well.
    register_cuckoo(snapshot.ipaddr, tags, vmname, cuckoo)

def do_snapshot(image, vmname, ipaddr, resolution, ramsize, cpus,
                hostname, adapter, vm_visible):
    m, h = initvm(image, name=vmname, multi=True, ramsize=ramsize, cpus=cpus)

    m.start_vm(visible=vm_visible)

    wait_for_host(image.ipaddr, image.port)
    a = Agent(image.ipaddr, image.port)
    a.ping()

    # Assign a new hostname.
    a.hostname(hostname)
    a.reboot()
    a.kill()

    # Wait for the reboot to kick in.
    time.sleep(10)
    wait_for_host(image.ipaddr, image.port)
    a.ping()

    if resolution:
        width, height = resolution.split("x")
        a.resolution(width, height)

    a.remove("C:\\vmcloak")
    a.static_ip(ipaddr, image.netmask, image.gateway, h.interface)

    m.snapshot("vmcloak", "Snapshot created by VM Cloak.")
    m.stopvm()

    # Create a database entry for this snapshot.
    snapshot = Snapshot(image_id=image.id, vmname=vmname, ipaddr=ipaddr,
                        port=image.port, hostname=hostname)
    return snapshot

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
@click.option("-d", "--debug", is_flag=True, help="Make snapshot in debug mode.")
def snapshot(name, vmname, ipaddr, resolution, ramsize, cpus, hostname,
             adapter, vm_visible, count, debug):
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

    if not count:
        snapshot = do_snapshot(
            image, vmname, ipaddr, resolution, ramsize, cpus,
            hostname or random_string(8, 16), adapter, vm_visible
        )
        session.add(snapshot)
    else:
        if hostname:
            log.error(
                "You specified a hostname, but this is not supported when "
                "creating multiple snapshots at once."
            )
            exit(1)

        for x in xrange(count):
            snapshot = do_snapshot(
                image, "%s%d" % (vmname, x + 1), ipaddr, resolution,
                ramsize, cpus, hostname, adapter, vm_visible
            )
            session.add(snapshot)

            # TODO Implement some limits to make sure that the IP address does
            # not "exceed" its provided subnet (and thus also require the user
            # to specify an IP range, rather than an IP address).
            ipaddr = ipaddr_increase(ipaddr)
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

def list_dependencies():
    print "Name", "version", "target", "sha1"
    print
    for name, d in sorted(vmcloak.dependencies.names.items()):
        if d.exes:
            versionlen = max(len(exe.get("version", "None")) for exe in d.exes)
        else:
            versionlen = 4

        print name
        for exe in d.exes:
            v = exe.get("version", "None")
            print "  *" if d.default and d.default == v else "   ",
            print exe.get("version", "None") + " "*(versionlen - len(v)),
            print exe.get("target"), exe["sha1"]
        print

@main.group("list")
def _list():
    pass

@_list.command("dependencies")
def _list_dependencies():
    list_dependencies()

@_list.command("deps")
def _list_deps():
    list_dependencies()
