# Copyright (C) 2014-2018 Jurriaan Bremer.
# Copyright (C) 2018 Hatching B.V.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import click
import logging
import os.path
import shutil
import subprocess
import tempfile
import time

from sqlalchemy.orm.session import make_transient

from vmcloak import repository
import vmcloak.dependencies

from vmcloak.agent import Agent
from vmcloak.constants import VMCLOAK_ROOT
from vmcloak.dependencies import Python, ThreemonPatch, Finalize
from vmcloak.install import DependencyInstaller, InstallError, find_recipe
from vmcloak.misc import (
    wait_for_agent, drop_privileges, download_file, filename_from_url
)
from vmcloak.rand import random_string
from vmcloak.repository import (
    image_path, Session, Image, Snapshot, iso_dst_path, db_migratable,
    SCHEMA_VERSION, IPNet, conf_path
)
from vmcloak.ostype import get_os

logging.basicConfig(format="%(asctime)s %(name)s %(levelname)s: %(message)s")
log = logging.getLogger("vmcloak")
log.setLevel(logging.INFO)

@click.group(invoke_without_command=True)
@click.option("-u", "--user", help="Drop privileges to user.")
@click.option("-q", "--quiet", help="Only show log warnings or higher")
@click.option("-d", "--debug", is_flag=True, help="Enable debugging.")
@click.pass_context
def main(ctx, user, quiet, debug):
    ctx.meta["debug"] = debug
    user and drop_privileges(user)
    if quiet:
        log.setLevel(logging.WARNING)
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
    if os.path.exists(outpath):
        log.error(f"Outpath: {outpath} already exists.")
        exit(1)

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
    click.option("--ip", help="Guest IP address to use"),
    click.option("--port", default=8000, help="Port to run the Agent on.", show_default=True),
    click.option("--network", help="The network to use in CIDR notation. Example: 192.168.30.0/24. Uses VM platform default if not given."),
    click.option("--gateway", help="Guest default gateway IP address (IP of bridge interface is used if none is given)"),
    click.option("--dns", default="8.8.8.8", help="DNS Server.", show_default=True),
    click.option("--dns2", default="8.8.4.4", help="Secondary DNS server.", show_default=True),
    click.option("--cpus", default=1, help="CPU count.", show_default=True),
    click.option("--ramsize", type=int, help="Memory size"),
    click.option("--vramsize", default=16, help="Video memory size"),
    click.option("--hddsize", type=int, default=256, help="HDD size in GB", show_default=True),
    click.option("--tempdir", default=iso_dst_path, help="Temporary directory to build the ISO file.", show_default=True),
    click.option("--resolution", default="1024x768", help="Screen resolution.", show_default=True),
    click.option("--vm-visible", is_flag=True, help="Start the Virtual Machine in GUI mode."),
    click.option("--vrde", is_flag=True, help="Enable the remote display (RDP or VNC)."),
    click.option("--vrde-port", default=3389, help="Specify the remote display port."),
    # click.option("--paravirtprovider", default="default", help="Select paravirtprovider for Virtualbox none|default|legacy|minimal|hyperv|kvm")
]

_iso_attributes = [
    # TODO: use something like --os winX
    # click.option("--winxp", is_flag=True, help="This is a Windows XP instance."), # Comment all non-x64 OS for now until we test them with new VMCloak.
    # click.option("--win7x86", is_flag=True, help="This is a Windows 7 32-bit instance."),  # Comment all non-x64 OS for now until we test them with new VMCloak.
    click.option("--win7x64", is_flag=True, help="This is a Windows 7 64-bit instance."),
    # click.option("--win81x86", is_flag=True, help="This is a Windows 8.1 32-bit instance."),  # Comment all non-x64 OS for now until we test them with new VMCloak.
    click.option("--win81x64", is_flag=True, help="This is a Windows 8.1 64-bit instance."),
    # click.option("--win10x86", is_flag=True, help="This is a Windows 10 32-bit instance."),  # Comment all non-x64 OS for now until we test them with new VMCloak.
    click.option("--win10x64", is_flag=True, help="This is a Windows 10 64-bit instance."),
    click.option("--iso-mount", help="Mounted ISO Windows installer image."),
    click.option("--serial-key", help="Windows Serial Key."),
    click.option("--product", help="Windows 7 product version."),
    click.option("--python-version", help="Python version to install on VM."),
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

# Comment all non-x64 windows OSes for now until we test them with new VMCloak.
def os_from_attr(attr):
    ramsize = attr["ramsize"]
    # if attr["winxp"]:
    #     osversion = "winxp"
    #     ramsize = ramsize or 1024
    # elif attr["win7x86"]:
    #     ramsize = ramsize or 1024
    #     osversion = "win7x86"
    if attr["win7x64"]:
        ramsize = ramsize or 2048
        osversion = "win7x64"
    # elif attr["win81x86"]:
    #     ramsize = ramsize or 2048
    #     osversion = "win81x86"
    elif attr["win81x64"]:
        ramsize = ramsize or 2048
        osversion = "win81x64"
    # elif attr["win10x86"]:
    #     ramsize = ramsize or 2048
    #     osversion = "win10x86"
    elif attr["win10x64"]:
        ramsize = ramsize or 2048
        osversion = "win10x64"
    else:
        # log.error(
        #     "Please provide one of --winxp, --win7x86, --win7x64, "
        #     "--win81x86, --win81x64, --win10x86, --win10x64."
        # )
        log.error("Please provide one of --win7x64, --win81x64, --win10x64.")
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

    for k in ("network", "gateway", "ip"):
        if not attr.get(k):
            log.error(f"Missing option '{k}'")
            exit(1)

    ipnet = _get_network(None, attr)
    ip = _get_ip(ipnet, attr)
    log.info(f"Image IP: {ip}. Image network: {ipnet}")

    attr["gateway"] = ipnet.bridge_ip
    attr["netmask"] = ipnet.netmask
    attr["ip"] = ip

    _create_iso(iso_path, attr)

def _create_iso(iso_path, attr):
    try:
        if not _ip_in_network(attr["ip"], attr["gateway"], attr["netmask"]):
            log.error(
                f"IP {attr['ip']} not in same network as gateway "
                f"{attr['gateway']}/{attr['netmask']}"
            )
            exit(1)
    except ValueError as e:
        log.error(f"Invalid ip: {e}")
        exit(1)

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
    d = Python(h=h, i=Image(osversion=attr["osversion"]), version=attr.get("python_version"))
    d.download()
    shutil.copy(d.filepath, vmcloak_dir)

    # Prepare settings
    reso_width, reso_height = attr["resolution"].split("x")
    attr["reso_width"] = reso_width
    attr["reso_height"] = reso_height

    env_vars = dict(
        GUEST_IP=attr["ip"],
        AGENT_PORT=attr["port"],
        GUEST_MASK=attr["netmask"],
        GUEST_GATEWAY=attr["gateway"],
        DNSSERVER=attr["dns"],
        DNSERVER2=attr["dns2"],
        DEBUG="yes" if attr["debug"] else "no",
        RESO_WIDTH=attr["reso_width"],
        RESO_HEIGHT=attr["reso_height"],
        INTERFACE=h.interface,
        PYTHONINSTALLER=d.exe["filename"],
        PYTHONWINDOW=d.exe["window_name"],
        PYTHONPATH=d.exe["install_path"]
    )

    # Now try building the ISO
    try:
        if not h.buildiso(mount, iso_path, bootstrap, h.tempdir,
                          env_vars=env_vars):
            exit(1)
    finally:
        shutil.rmtree(bootstrap)

    log.info("Created ISO: %s", iso_path)

def _get_network(platform, attrs):
    network_str = attrs["network"]
    bridge_ip = attrs["gateway"]
    bridge_interface = attrs.get("adapter")
    if network_str:
        try:
            return IPNet(
                network_str, bridge_ip=bridge_ip,
                bridge_interface=bridge_interface
            )
        except ValueError as e:
            log.error(f"Invalid network setting: {e}")
            exit(1)

    if not platform:
        log.error(
            "No platform specified to find defaults for network settings."
        )
        exit(1)

    ipnet = platform.default_net
    try:
        if bridge_interface:
            ipnet.set_bridge_interface(bridge_interface)
        if bridge_ip:
            ipnet.set_bridge_ip(bridge_ip)
    except ValueError as e:
        log.error(f"Invalid adapter/bridge: {e}")
        exit(1)

    return ipnet

def _get_ip(ipnet, attr):
    if attr.get("ip"):
        ip = attr["ip"]
        try:
            ipnet.check_ip_usable(ip)
        except (ValueError, KeyError) as e:
            log.error(f"Cannot use IP '{ip}'. {e}")
            exit(1)
    else:
        try:
            ip = ipnet.get_ips(count=1)[0]
        except (ValueError, KeyError) as e:
            log.error(f"Failed to get IP in network: {ipnet}. {e}")
            exit(1)

    return ip

@main.command()
@click.argument("name")
@click.argument("adapter")
@_add_install_attr
@click.option("--iso", help="Specify install ISO to use.")
@click.option("--vm", default="qemu", help="Virtual Machinery.", show_default=True)
@click.pass_context
def init(ctx, name, adapter, iso, vm, **attr):
    """Create a new image with 'name' attached to network (bridge)
    'adapter'."""
    attr["debug"] = ctx.meta["debug"]
    if attr["vrde"] or attr["debug"]:
        attr["vrde"] = attr["vrde_port"]

    if vm.lower() != "qemu":
        log.error("VMCloak temporarily only supports QEMU vm creation.")
        exit(1)

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

    attr["adapter"] = adapter
    ipnet = _get_network(p, attr)
    ip = _get_ip(ipnet, attr)
    log.info(f"Image IP: {ip}. Image network: {ipnet}")

    attr["gateway"] = ipnet.bridge_ip
    attr["netmask"] = ipnet.netmask
    attr["ip"] = ip

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
                      # paravirtprovider=attr["paravirtprovider"],
                      mac=attr["mac"]))
    session.commit()

def _do_install(image, dependencies, attrs={}, skip_installed=True,
                no_machine_start=False):
    try:
        installer = DependencyInstaller(image, dependencies, attrs)
    except InstallError as e:
        log.error(f"Install failed: {e}")
        return False

    success = False
    try:
        installer.prepare(no_machine_start=no_machine_start)
        success = installer.install_all(skip_installed=skip_installed)
    except InstallError as e:
        log.exception(f"Fatal error during installation process. {e}")
        return False
    finally:
        installer.finish(do_shutdown=True)

    installed = ""
    for name, versions in installer.installed.items():
        for v in versions:
            if installed:
                installed += ", "
            installed += f"{name}={v or 'No version/default'}"

    if installed:
        log.debug(f"Installed: {installed}")

    return success

@main.command()
@click.argument("name")
@click.argument("dependencies", nargs=-1)
@click.option("--vm-visible", is_flag=True)
@click.option("--vrde", is_flag=True, help="Enable the VirtualBox Remote Display Protocol.")
@click.option("--vrde-port", default=3389, help="Specify the VRDE port.")
@click.option("--force-reinstall", is_flag=True, help="Reinstall even if already installed by VMCloak.")
@click.option("--no-machine-start", is_flag=True, help="Do not try to start the machine. Assume it is somehow already started and reachable.")
@click.option("-r", "--recommended", is_flag=True, help="Install and perform recommended software and configuration changes for the OS.")
@click.option("-d", "--debug", is_flag=True, help="Install applications in debug mode.")
@click.pass_context
def install(ctx, name, dependencies, vm_visible, vrde, vrde_port,
            force_reinstall, no_machine_start, recommended, debug):
    """Install dependencies on an image. Dependency settings are specified
    using name.setting=value. Multiple settings per dependency can be given."""
    user_attr = {"vm_visible": vm_visible}
    if vrde or ctx.meta["debug"]:
        user_attr["vrde"] = vrde_port

    image = repository.find_image(name)
    if not image:
        log.error("Image not found: %s", name)
        exit(1)

    if image.vm and image.vm.lower() != "qemu":
        log.error(
            "VMCloak temporarily only supports QEMU vm creation. "
            f"The image is for: {image.vm}"
        )
        exit(1)

    if image.mode != "normal":
        log.error(
            "Image is already in use for snapshots. You can no longer "
            "modify it."
        )
        exit(1)

    try:
        image.network
    except ValueError as e:
        log.error(f"Image IP network error: {e}")
        exit(1)

    recom_deps = []
    if recommended:
        try:
            recom_deps = find_recipe(image.osversion)
            log.info(f"Using recommended packages: {recom_deps}")
        except InstallError as e:
            log.error(f"Failed to use recommended dependencies. {e}")
            exit(1)

    # Install any recommendations first.
    if recom_deps:
        recom_deps.extend(dependencies)
        dependencies = recom_deps

    if not dependencies:
        log.error("No dependencies given to install")
        exit(1)

    if not _do_install(image, dependencies, user_attr,
                       skip_installed=not force_reinstall,
                       no_machine_start=no_machine_start):
        exit(1)


@main.command()
@click.argument("name")
@click.option("--vm-visible", is_flag=True)
@click.option("--vrde", is_flag=True, help="Enable the VirtualBox Remote Display Protocol.")
@click.option("--vrde-port", default=3389, help="Specify the VRDE port.")
@click.option("--iso-path", help="Path to an iso file to attach as a drive to the machine.")
@click.pass_context
def modify(ctx, name, vm_visible, vrde, vrde_port, iso_path):
    """Start the given image name to apply manual changes"""
    user_attr = {"vm_visible": vm_visible}
    if vrde or ctx.meta["debug"]:
        user_attr["vrde"] = vrde_port

    if iso_path and not os.path.exists(iso_path):
        log.error("Iso path does not exist")
        exit(1)

    image = repository.find_image(name)
    if not image:
        log.error("Image not found: %s", name)
        exit(1)

    if image.vm and image.vm.lower() != "qemu":
        log.error(
            "VMCloak temporarily only supports QEMU vm creation. "
            f"The image is for: {image.vm}"
        )
        exit(1)

    if image.mode != "normal":
        log.error(
            "Image is already in use for snapshots. You can no "
            "longer modify it."
        )
        exit(1)

    try:
        image.network
    except ValueError as e:
        log.error(f"Image IP network error: {e}")
        exit(1)

    p = image.platform
    p.start_image_vm(image, user_attr)
    if iso_path:
        vm = image.VM()
        vm.attach_iso(iso_path)
    try:
        log.warning("The Virtual Machine has booted and is ready to be modified!")
        log.warning("When you shut it down, all changes will be saved.")
        p.wait_for_shutdown(image.name)
    except ValueError as e:
        log.error(f"Error during image shutdown: {e}")
    finally:
        p.remove_vm_data(image.name)

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
    try:
        wait_for_agent(a, timeout=600)
    except OSError as e:
        log.error(f"VM online wait timeout. {e}")
        exit(1)

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
        a.execute("notepad.exe C:\\vmcloak\\interactive.txt", cucksync=False)

    a.remove("C:\\vmcloak")
    h = get_os(image.osversion)
    a.static_ip(attr["ip"], attr["netmask"], attr["gateway"], h.interface)

    log.debug("Creating snapshot")
    p.create_snapshot(vmname)
    p.create_machineinfo_dump(vmname, image)

    # Create a database entry for this snapshot.
    return Snapshot(image_id=image.id, vmname=vmname, hostname=hostname,
                    ipaddr=attr["ip"], port=attr["port"])

def _if_defined(attr, k, v):
    if v is not None:
        attr[k] = v

def _ip_in_network(ip, gateway_ip, netmask):
    from ipaddress import ip_network, ip_address

    return ip_address(ip) in ip_network(f"{gateway_ip}/{netmask}",
                                        strict=False)

def vm_iter(count, name, iplist, port):
    if not count or count == 1:
        yield name, iplist[0], port
    else:
        for i in range(count):
            yield "%s%s" % (name, i + 1), iplist[i], port + i

def _do_final_changes(nopatch, image, attr):
    deps = []
    # If the OS is supported by threemon and it is not patched, patch it.
    if not nopatch and image.osversion in ("win10x64", "win8164", "win7x64"):
        if not image.dependency_installed(ThreemonPatch.name):
            log.info("Image not patched for Threemon yet. Starting patching.")
            deps.append(ThreemonPatch.name)

    if not image.dependency_installed(Finalize.name):
        deps.append(Finalize.name)

    if not deps:
        return

    if not _do_install(image, deps, attr):
        log.error(
            f"Failed to finalize image. Snapshot creation aborted. "
            f"Missing one of: {deps}"
        )
        exit(1)


_ISOS = {
    "win7x64":("36ae90defbad9d9539e649b193ae573b77a71c83","https://hatching.dev/hatchvm/win7ultimate.iso"),
    "win10x64": ("ce8005a659e8df7fe9b080352cb1c313c3e9adce", "https://hatching.dev/hatchvm/Win10_1703_English_x64.iso")
}
@main.command()
@click.option("--download-to", help=f"The filepath to write the ISO to. Will go to {iso_dst_path} otherwise.")
@click.option("--win7x64", is_flag=True, help="The recommended Windows 7 x64 ISO for Cuckoo 3")
@click.option("--win10x64", is_flag=True, help="The recommended Windows 10 x64 ISO for Cuckoo 3")
def isodownload(win7x64, win10x64, download_to):
    """Download the recommended operating system ISOs for Cuckoo 3. These are
    specific OS versions/builds."""
    if not win7x64 and not win10x64:
        log.error("One OS flag must be provided. See --help")
        exit(1)

    if win7x64:
        name = "win7x64"
    elif win10x64:
        name = "win10x64"
    else:
        log.error("Invalid choice")
        exit(1)

    expected_sha1, url = _ISOS[name]
    if download_to:
        iso_path = download_to
    else:
        iso_path = os.path.join(conf_path, filename_from_url(url))

    log.info(f"Downloading ISO for {name} to {iso_path}")
    success, sha1 = download_file(url, iso_path)
    if not success:
        log.error("ISO download failed")
    else:
        log.info(f"ISO downloaded to: {iso_path}")
        if sha1 != expected_sha1:
            log.error(
                f"Download success, but expected sha1 "
                f"'{expected_sha1}' does not match calculated sha1 '{sha1}'"
            )


@main.command()
@click.argument("name")
@click.option("--vm", default="qemu", help="Virtual Machinery.")
def cleanup(name, vm):
    p = repository.platform(vm)
    p.remove_vm_data(name)

@main.command()
@click.argument("name")
@click.argument("vmname")
@click.argument("ip", required=False)
@click.option("--resolution", help="Screen resolution.")
@click.option("--ramsize", type=int, help="Amount of virtual memory to assign. Same as image if not specified.")
@click.option("--cpus", type=int, help="Amount of CPUs to assign. Same as image if not specified.")
@click.option("--hostname", help="Hostname for this VM.")
# @click.option("--adapter", help="Hostonly adapter for this VM.")
@click.option("--vm-visible", is_flag=True, help="Start the Virtual Machine in GUI mode.")
@click.option("--count", type=int, help="The amount of snapshots to make.", default=1, show_default=True)
# @click.option("--share", help="Add shared folder")
@click.option("--vrde", is_flag=True, help="Enable the VirtualBox Remote Display Protocol.")
@click.option("--vrde-port", default=3389, help="Specify the VRDE port.")
@click.option("--interactive", is_flag=True, help="Enable interactive snapshot mode.")
@click.option("--com1", is_flag=True, help="Enable COM1 for this VM.")
@click.option("--nopatch", is_flag=True, help="Do not patch the image to be able to load threemon")
@click.pass_context
def snapshot(ctx, name, vmname, ip, resolution, ramsize, cpus, hostname,
             vm_visible, count, vrde, vrde_port, interactive,
             com1, nopatch):
    """Create one or more snapshots from an image"""
    if count and hostname:
        log.error(
            "You specified a hostname, but this is not supported when "
            "creating multiple snapshots at once."
        )
        exit(1)

    image = repository.find_image(name)
    if not image:
        log.error("Image not found: %s", name)
        exit(1)

    if image.vm and image.vm.lower() != "qemu":
        log.error(
            "VMCloak temporarily only supports QEMU vm creation. "
            f"The image is for: {image.vm}"
        )
        exit(1)

    if ip:
        try:
            if not _ip_in_network(ip, image.gateway, image.netmask):
                log.error(
                    f"IP {ip} not in same network as gateway "
                    f"{image.gateway}/{image.netmask}"
                )
                exit(1)
        except ValueError as e:
            log.error(f"Invalid ip: {e}")
            exit(1)

    try:
        image.network
    except ValueError as e:
        log.error(f"Image IP network error: {e}")
        exit(1)

    attr = image.attr()
    if vrde or ctx.meta["debug"]:
        attr["vrde"] = vrde_port

    # Perform final changes such patching for kernel monitor and
    # disabling services that were still needed during the image
    # creation/install phase.
    _do_final_changes(nopatch, image, attr)

    # From now on this image is multiattach.

    ses = Session()
    try:
        ses.query(Image).filter_by(name=name).update(
            {"mode": "multiattach"}, synchronize_session=False
        )
        ses.commit()
    finally:
        ses.close()

    # Copy properties from image and replace snapshot-specific ones
    p = image.platform
    attr["imgpath"] = attr.pop("path")
    # attr["ip"] = ip
    attr["vm_visible"] = vm_visible
    _if_defined(attr, "cpus", cpus)
    _if_defined(attr, "hostname", hostname)
    _if_defined(attr, "ramsize", ramsize)
    _if_defined(attr, "resolution", resolution)
    # _if_defined(attr, "share", share)

    try:
        iplist = image.network.get_ips(
            count=count, start_offset=10, start_ip=ip
        )
    except (ValueError, KeyError) as e:
        log.error(f"Network error: {e}")
        exit(1)

    # TODO: must detect adapter change, because changing it requires booting
    # the old adapter (or use IPv6-LL)
    # _if_defined(attr, "adapter", adapter)

    for vmname, ip, port in vm_iter(count, vmname, iplist, vrde_port):
        vmdir = p.prepare_snapshot(vmname, attr)
        if not vmdir:
            log.warning("Not creating %r because it exists", vmname)
            continue

        log.info(f"Creating snapshot: '{vmname}' with IP '{ip}'")
        if not os.path.exists(vmdir):
            os.makedirs(vmdir)
        if "vrde" in attr:
            attr["vrde"] = port
        if com1:
            attr["serial"] = os.path.join(vmdir, "%s.com1" % vmname)
        if not hostname:
            attr["hostname"] = random_string(8, 16)
        attr["ip"] = ip
        new_snapshot = _snapshot(image, vmname, attr, interactive)
        ses = Session()
        try:
            ses.add(new_snapshot)
            ses.commit()
        finally:
            ses.close()

        log.info(f"Snapshot '{vmname}' created")

    log.info("Finished creating snapshots")

# XXX Comment until we tested vbox, libvirt, qemu support with this
# in newer versions.
# @main.command()
# @click.argument("name")
# @click.argument("filepath", type=click.Path(writable=True))
# def export(name, filepath):
#     if not filepath.endswith((".ova", ".ovf")):
#         log.error("The exported file should be either .ova or .ovf")
#         exit(1)
#
#     session = Session()
#     image = session.query(Image).filter_by(name=name).first()
#     if not image:
#         log.error("Image not found: %s", name)
#         exit(1)
#
#     if image.vm != "virtualbox":
#         log.error("Only VirtualBox VMs can be exported.")
#         exit(1)
#
#     if image.mode != "normal":
#         log.error("You can't export this image as you have already made "
#                   "snapshots with it!")
#         log.error("Please vmcloak clone it and export the clone.")
#         exit(1)
#
#     image.platform.export_vm(image, filepath)

# @main.command()
# @click.argument("name")
# def restore(name):
#     """Restore snapshot"""
#     snapshot = repository.find_snapshot(name)
#     if not snapshot:
#         log.error("Snapshot not found: %s", name)
#         exit(1)
#     log.info("Restoring %s to vmcloak snapshot", name)
#     p = snapshot.platform
#     p.restore_snapshot(name, "vmcloak")

# @main.command()
# @click.argument("ip")
# @click.argument("port", required=False, default=8000)
# def zer0m0n(ip, port):
#     log.setLevel(logging.INFO)
#
#     log.info("Checking if we can reach the VM..")
#     a = Agent(ip, port)
#
#     try:
#         status = a.ping().json()
#     except requests.RequestException:
#         log.error("Couldn't reach the VM, is it up-and-running? Aborting..")
#         return
#
#     if not isinstance(status, dict) or status.get("message") != "Cuckoo Agent!":
#         log.error("Agent in VM isn't the new Cuckoo Agent? Aborting..")
#         return
#
#     h = get_os("win7x64")
#     log.info("Patching zer0m0n-related files.")
#     vmcloak.dependencies.names["zer0m0n"](a=a, h=h).run()
#     log.info("Good to go, now *reboot* and make a new *snapshot* of your VM!")

@main.command()
@click.option("--revision", default="head", help="Migrate to a certain revision")
def migrate(revision):
    """Perform database migration needed by VMCloak after updates."""
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

# @main.command("import")
# def _import():
#     """Import images and snapshots
#     Can also be used to fix paths"""
#     repository.import_all()

# List things:
@main.group("list")
def _list():
    pass

@_list.command("images")
def list_images():
    for img in repository.list_images():
        print("*", img.name, "|", img.platform.name,"|",
              img.ipaddr, "|","Adapter:", img.adapter)
        installed = img.installed
        if not installed:
            continue

        for dep, version in sorted(img.installed, key=lambda k: k[0]):
            print("\t", "-", dep, f"| version={version}" if version else "")

@_list.command("snapshots")
def list_snapshots():
    snaps = repository.list_snapshots()
    snaps.sort(key=lambda snap: (snap.image.name, snap.vmname))
    parent = None
    for snap in snaps:
        if snap.image.name != parent:
            parent = snap.image.name
            print(parent, f"{snap.image.ipaddr}({snap.image.adapter})",
                  f"({snap.platform.name})")
        print("-", snap.vmname, snap.ipaddr)

def list_dependencies(name_only=False):
    print("Name", "version", "target", "sha1", "arch")
    print()
    for name, d in sorted(vmcloak.dependencies.names.items()):
        if d.exes:
            versionlen = max(len(exe.get("version", "None")) for exe in d.exes)
        else:
            versionlen = 4

        print(name)
        if name_only:
            continue

        for exe in d.exes:
            v = exe.get("version", "None")
            print(
                name, "*" if d.default and d.default == v else "",
                exe.get("version", "None") + " "*(versionlen - len(v)),
                exe.get("target"), exe.get("sha1", "None"),
                exe.get("arch", ""),
            )
        print("----"*5)

@_list.command("deps")
@click.option("--name-only", is_flag=True, help="Only list the names of existing dependencies")
def _list_deps(name_only):
    list_dependencies(name_only)
