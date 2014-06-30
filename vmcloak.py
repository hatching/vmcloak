#!/usr/bin/env python
# Copyright (C) 2010-2014 Cuckoo Sandbox Developers.
# This file is part of Cuckoo Sandbox - http://www.cuckoosandbox.org
# See the file 'docs/LICENSE' for copying permission.

import argparse
import logging
import os.path
import socket
import subprocess
import tempfile
import time

from lib.conf import Configuration, configure_winnt_sif, vboxmanage_path
from lib.conf import check_keyboard_layout
from lib.deps import Dependency
from lib.vm import VirtualBox


logging.basicConfig(level=logging.INFO)
log = logging.getLogger()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('vmname', type=str, help='Name of the Virtual Machine.')
    parser.add_argument('--cuckoo', type=str, help='Directory where Cuckoo is located.')
    parser.add_argument('--basedir', type=str, help='Base directory for the virtual machine and its associated files.')
    parser.add_argument('--vm', type=str, help='Virtual Machine Software (VirtualBox.)')
    parser.add_argument('--list', action='store_true', help='List the cloaked settings for a VM.')
    parser.add_argument('--delete', action='store_true', help='Completely delete a Virtual Machine and its associated files.')
    parser.add_argument('--ramsize', type=int, help='Available virtual memory (in MB) for this virtual machine.')
    parser.add_argument('--resolution', type=str, help='Virtual Machine resolution.')
    parser.add_argument('--hdsize', type=int, help='Maximum size (in MB) of the dynamically allocated harddisk.')
    parser.add_argument('--iso-mount', type=str, help='Mounted ISO Windows installer image.')
    parser.add_argument('--host-ip', type=str, help='Static IP address to bind to on the Host.')
    parser.add_argument('--hostonly-ip', type=str, help='Static IP address to use on the Guest for the hostonly network.')
    parser.add_argument('--hostonly-mask', type=str, help='Static IP address mask to use on the Guest for the hostonly network.')
    parser.add_argument('--hostonly-gateway', type=str, help='Static IP address gateway to use on the Guest for the hostonly network.')
    parser.add_argument('--hostonly-macaddr', type=str, help='Mac address for the hostonly interface.')
    parser.add_argument('--bridged', type=str, help='Network interface for the bridged network.')
    parser.add_argument('--bridged-ip', type=str, help='Static IP address to use on the Guest for the bridged network.')
    parser.add_argument('--bridged-mask', type=str, help='Static IP address mask to use on the Guest for the bridged network.')
    parser.add_argument('--bridged-gateway', type=str, help='Static IP address gateway to use on the Guest for the bridged network.')
    parser.add_argument('--bridged-macaddr', type=str, help='Mac address for the bridged interface.')
    parser.add_argument('--hwvirt', action='store_true', default=None, help='Explicitly enable Hardware Virtualization.')
    parser.add_argument('--no-hwvirt', action='store_false', default=None, dest='hwvirt', help='Explicitly disable Hardware Virtualization.')
    parser.add_argument('--serial-key', type=str, help='Windows Serial Key.')
    parser.add_argument('--tags', type=str, help='Cuckoo Tags for the Virtual Machine.')
    parser.add_argument('--no-register-cuckoo', action='store_false', default=True, dest='register_cuckoo', help='Explicitly disable registering the Virtual Machine with Cuckoo upon completion.')
    parser.add_argument('--vboxmanage', type=str, help='Path to VBoxManage.')
    parser.add_argument('--dependencies', type=str, help='Comma-separated list of all dependencies in the Virtual Machine.')
    parser.add_argument('--vm-visible', action='store_true', default=None, help='Explicitly enable Hardware Virtualization.')
    parser.add_argument('--keyboard-layout', type=str, help='Keyboard Layout within the Virtual Machine.')
    parser.add_argument('-s', '--settings', type=str, action='append', help='Configuration file with various settings.')

    defaults = dict(
        vm='virtualbox',
        ramsize=1024,
        resolution='1024x768',
        hdsize=256*1024,
        host_ip='192.168.56.1',
        hostonly_ip='192.168.56.101',
        hostonly_mask='255.255.255.0',
        hostonly_gateway='192.168.0.1',
        bridged_mask='255.255.255.0',
        tags='',
        vboxmanage='/usr/bin/VBoxManage',
        vm_visible=False,
        keyboard_layout='US',
    )

    args = parser.parse_args()
    s = Configuration()

    for settings in args.settings:
        s.from_file(settings)

    s.from_args(args)
    s.from_defaults(defaults)

    if not s.cuckoo and s.register_cuckoo:
        print '[-] To register the Virtual Machine with Cuckoo'
        print '[-] please provide the Cuckoo directory.'
        print '[x] To disable registering please provide --no-register-cuckoo'
        print '[x] or register-cuckoo = false in the configuration.'
        exit(1)

    if not s.basedir:
        print '[-] Please provide the base directory for the VM.'
        exit(1)

    if s.vm == 'virtualbox':
        m = VirtualBox(s.vmname, s.basedir,
                       vboxmanage=vboxmanage_path(s))
    else:
        print '[-] Only VirtualBox is supported as of now'
        exit(1)

    if s.list:
        print m.list_settings()
        exit(0)

    if s.delete:
        print '[x] Unregistering and deleting the VM and its associated files'
        m.delete_vm()
        exit(0)

    if not s.iso_mount or not os.path.isdir(s.iso_mount):
        print '[-] Please specify the path to a mounted '
        print '[-] Windows Installer ISO image.'
        exit(1)

    # Make sure the dependencies repository is available.
    deps_repo = os.path.join('deps', 'repo.ini')
    if not os.path.exists(deps_repo):
        print '[x] Please run "git submodule update --init" first!'
        exit(1)

    print '[x] Checking whether the keyboard layout is valid.'
    if not check_keyboard_layout(s.keyboard_layout):
        print '[-] Invalid keyboard layout:', s.keyboard_layout
        print '[-] Please use one provided in data/keyboard_layout_values.txt.'
        exit(1)

    try:
        # TODO This should be part of m.hostonly().
        print '[x] Ensuring vboxnet0 is running.'
        subprocess.check_call(['./utils/vboxnet.sh', vboxmanage_path(s)])
    except OSError as e:
        print '[-] Is ./utils/vboxnet.sh executable?'
        print e
        exit(1)

    print '[x] Static Host IP', s.host_ip
    print '[x] Static Guest hostonly IP', s.hostonly_ip
    print '[x] Static Guest bridged IP', s.bridged_ip
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((s.host_ip, 0))
    sock.listen(1)
    _, port = sock.getsockname()

    print '[x] Configuring WINNT.SIF'
    buf = configure_winnt_sif(os.path.join('data', 'winnt.sif'), s)
    if not buf:
        print '[-] Error configuring WINNT.SIF'
        exit(1)

    # Write the WINNT.SIF file.
    _, winntsif = tempfile.mkstemp(suffix='.sif')
    open(winntsif, 'wb').write(buf)

    settings_bat = dict(
        HOSTONLYIP=s.hostonly_ip,
        HOSTONLYMASK=s.hostonly_mask,
        HOSTONLYGATEWAY=s.hostonly_gateway,
        BRIDGED='yes' if s.bridged else 'no',
        BRIDGEDIP=s.bridged_ip,
        BRIDGEDMASK=s.bridged_mask,
        BRIDGEDGATEWAY=s.bridged_gateway,
    )

    settings_py = dict(
        HOST_IP=s.host_ip,
        HOST_PORT=port,
        RESOLUTION=s.resolution,
    )

    bootstrap = tempfile.mkdtemp()

    # Write the configuration values for bootstrap.bat.
    with open(os.path.join(bootstrap, 'settings.bat'), 'wb') as f:
        for key, value in settings_bat.items():
            print>>f, 'set %s=%s' % (key, value)

    # Write the configuration values for bootstrap.py.
    with open(os.path.join(bootstrap, 'settings.py'), 'wb') as f:
        for key, value in settings_py.items():
            print>>f, '%s = %r' % (key, value)

    # TODO Make sure the deps repository is up-to-date.

    os.mkdir(os.path.join(bootstrap, 'dependencies'))

    deps = Dependency(deps_repo, os.path.join(bootstrap, 'dependencies.bat'))

    deps.add('python27')

    for d in s.dependencies.split(','):
        if d.strip():
            deps.add(d.strip())

    deps.write()

    # The image directory doesn't exist yet, probably.
    if not os.path.exists(os.path.join(s.basedir, s.vmname)):
        os.mkdir(os.path.join(s.basedir, s.vmname))

    iso_path = os.path.join(s.basedir, s.vmname, 'image.iso')

    # Create the ISO file.
    print '[x] Creating ISO file.'
    try:
        subprocess.check_call(['./utils/buildiso.sh',
                               s.iso_mount, winntsif, iso_path, bootstrap])
    except OSError as e:
        print '[-] Is ./utils/buildiso.sh executable?'
        print e
        exit(1)
    except subprocess.CalledProcessError as e:
        print '[-] Error creating ISO file.'
        print e
        exit(1)

    print '[x] Creating VM'
    print m.create_vm()

    m.ramsize(s.ramsize)
    m.os_type(os='xp', sp=3)

    print '[x] Creating Harddisk'
    m.create_hd(s.hdsize)

    print '[x] Temporarily attaching DVD-Rom unit for the ISO installer'
    m.attach_iso(iso_path)

    print '[x] Randomizing Hardware'
    m.init_vm()

    print '[x] Initially configuring Hostonly network'
    m.hostonly(macaddr=s.hostonly_macaddr, index=1)

    if s.bridged:
        m.bridged(s.bridged, macaddr=s.bridged_macaddr, index=2)

    if s.hwvirt is not None:
        if s.hwvirt:
            print '[x] Enabling Hardware Virtualization'
        else:
            print '[x] Disabling Hardware Virtualization'
        m.hwvirt(s.hwvirt)

    print '[!] Starting the Virtual Machine to install Windows'
    print m.start_vm(visible=s.vm_visible)

    print '[x] Waiting for the Virtual Machine to connect back'
    print '[!] This may take up to 30 minutes'
    t = time.time()

    guest, _ = sock.accept()
    print '[x] It took %d seconds to install Windows!' % (time.time() - t)

    print '[x] Setting the resolution to %s' % s.resolution
    if ord(guest.recv(1)):
        print '[+] Resolution was set successfully'
    else:
        print '[-] Error setting the resolution'

    print '[x] Detaching the Windows Installation disk.'
    m.detach_iso()

    # Give the system a little bit of time to fully initialize.
    time.sleep(10)

    print '[x] Taking a snapshot of the current state'
    print m.snapshot('vmcloak', 'Snapshot created by VM Cloak.')

    print '[x] Powering off the virtual machine'
    print m.stopvm()

    if s.register_cuckoo:
        print '[x] Registering the VM with Cuckoo.'
        try:
            machine_py = os.path.join(s.cuckoo, 'utils', 'machine.py')
            subprocess.check_call([machine_py, '--add',
                                   '--ip', s.hostonly_ip,
                                   '--platform', 'windows',
                                   '--tags', s.tags,
                                   '--snapshot', 'vmcloak',
                                   s.vmname],
                                  cwd=s.cuckoo)
        except OSError as e:
            print '[-] Is $CUCKOO/utils/machine.py executable?'
            print e
            exit(1)
        except subprocess.CalledProcessError as e:
            print '[-] Error registering the VM.'
            print e
            exit(1)

    print '[!] Virtual Machine created successfully.'

if __name__ == '__main__':
    main()
