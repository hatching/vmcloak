#!/usr/bin/env python
# Copyright (C) 2010-2014 Cuckoo Sandbox Developers.
# This file is part of Cuckoo Sandbox - http://www.cuckoosandbox.org
# See the file 'docs/LICENSE' for copying permission.

import argparse
import logging
import os.path
import random
import socket
import string
import subprocess
import sys
import time


logging.basicConfig(level=logging.INFO)
log = logging.getLogger()


CONFIG = dict(
    bios=[
    ],
    system=[
    ],
    board=[
    ],
    chassis=[
    ],
    harddisk=[
    ],
)


def random_string(minimum, maximum=None):
    if maximum is None:
        maximum = minimum

    count = random.randint(minimum, maximum)
    return ''.join(random.choice(string.ascii_letters) for x in xrange(count))


def random_mac():
    """Generates a random MAC address."""
    values = [random.randint(0, 15) for _ in xrange(12)]

    # At least for VirtualBox there's a limitation for the second character,
    # as outlined in the following thread. Thus we handle this.
    # https://forums.virtualbox.org/viewtopic.php?p=85316
    values[1] = int(random.choice('02468ace'), 16)

    return '%x%x:%x%x:%x%x:%x%x:%x%x:%x%x' % tuple(values)


def random_serial(length=None):
    if length is None:
        length = random.randint(8, 20)

    return ''.join(random.choice(string.uppercase + string.digits)
                   for _ in xrange(length))


class VM(object):
    FIELDS = {}

    def __init__(self, name, basedir):
        self.name = name
        self.basedir = basedir

    def create_vm(self):
        """Create a new Virtual Machine."""
        raise

    def delete_vm(self):
        """Delete an existing Virtual Machine and its associated files."""
        raise

    def ramsize(self, ramsize):
        """Modify the amount of RAM available for this Virtual Machine."""
        raise

    def os_type(self, os, sp):
        """Set the OS type to the OS and the Service Pack."""
        raise

    def create_hd(self, fsize):
        """Create a harddisk."""
        raise

    def attach_iso(self, iso):
        """Attach a ISO file as DVDRom."""
        raise

    def set_field(self, key, value):
        """Set a specific field of a Virtual Machine."""
        raise

    def modify_mac(self, mac=None):
        """Modify the MAC address of a Virtual Machine."""
        raise

    def hostonly(self, index=0):
        """Configure a Hostonly adapter for the Virtual Machine."""
        raise

    def start_vm(self):
        """Start the associated Virtual Machine."""
        raise

    def list_settings(self):
        """List all settings of a Virtual Machine."""
        raise

    def init_vm(self):
        """Initialize fields as specified by `FIELDS`."""
        def _init_vm(path, fields):
            for key, value in fields.items():
                key = path + '/' + key
                if isinstance(value, dict):
                    _init_vm(key, value)
                else:
                    if isinstance(value, tuple):
                        k, v = value
                        if not CONFIG[k]:
                            value = 'To be filled by O.E.M.'
                        else:
                            if k not in config:
                                config[k] = random.choice(CONFIG[k])

                            value = config[k][v]

                            # Some values are dynamically generated.
                            if callable(value):
                                value = value()

                    print '[+] Setting %r to %r' % (key, value)
                    ret = self.set_field(key, value)
                    if ret:
                        print ret

        config = {}
        _init_vm('', self.FIELDS)


class VirtualBox(VM):
    FIELDS = {
        'VBoxInternal/Devices/pcbios/0/Config': dict(

            # http://blog.prowling.nu/2012/08/modifying-virtualbox-settings-for.html
            DmiBIOSVendor=('bios', 'vendor'),
            DmiBIOSVersion=('bios', 'version'),
            DmiBIOSReleaseDate=('bios', 'release_date'),
            # DmiBIOSReleaseMajor=
            # DmiBIOSReleaseMinor=
            # DmiBIOSFirmwareMajor=
            # DmiBIOSFirmwareMinor=

            DmiSystemVendor=('system', 'vendor'),
            DmiSystemProduct=('system', 'product'),
            DmiSystemVersion=('system', 'version'),
            DmiSystemSerial=('system', 'serial'),
            DmiSystemSKU=('system', 'sku'),
            DmiSystemFamily=('system', 'family'),
            DmiSystemUuid=('system', 'uuid'),

            # http://blog.prowling.nu/2012/10/modifying-virtualbox-settings-for.html
            DmiBoardVendor=('board', 'vendor'),
            DmiBoardProduct=('board', 'product'),
            DmiBoardVersion=('board', 'version'),
            DmiBoardSerial=('board', 'serial'),
            DmiBoardAssetTag=('board', 'asset'),
            DmiBoardLocInChass=('board', 'location'),

            DmiChassisVendor=('chassis', 'vendor'),
            DmiChassisVersion=('chassis', 'version'),
            DmiChassisSerial=('chassis', 'serial'),
            DmiChassisAssetTag=('chassis', 'asset'),
        ),
        'VBoxInternal/Devices/piix3ide/0/Config': {
            'Port0': dict(

                # http://downloads.cuckoosandbox.org/slides/blackhat.pdf, Page 82
                # https://forums.virtualbox.org/viewtopic.php?f=1&t=48718
                # ATAPIProductId='',
                # ATAPIRevision='',
                # ATAPIVendorId='',
            ),
            'PrimaryMaster': dict(

                # http://blog.prowling.nu/2012/08/modifying-virtualbox-settings-for.html
                SerialNumber=('harddisk', 'serial'),
                FirmwareRevision=('harddisk', 'revision'),
                ModelNumber=('harddisk', 'model'),
            ),
        },
    }

    def __init__(self, *args, **kwargs):
        VM.__init__(self, *args, **kwargs)

        self.CONF_PATH = os.path.join(CUCKOO_ROOT, 'conf', 'virtualbox.conf')

        try:
            self.vboxmanage = Config(self.CONF_PATH).virtualbox.path
        except:
            log.error('Unable to locate VBoxManage path, please '
                      'configure conf/virtualbox.conf properly.')
            exit(1)

        if not os.path.isfile(self.vboxmanage):
            log.error('The configured VBoxManage path does not exist, '
                      'please configure conf/virtualbox.conf properly.')
            exit(1)

    def _call(self, *args, **kwargs):
        cmd = [self.vboxmanage] + list(args)

        for k, v in kwargs.items():
            if v is None or v is True:
                cmd += ['--' + k]
            else:
                cmd += ['--' + k, str(v)]

        try:
            ret = subprocess.check_output(cmd)
        except Exception as e:
            print '[-] Error running command:', e
            return

        return ret

    def create_vm(self):
        return self._call('createvm', name=self.name,
                          basefolder=self.basedir, register=True)

    def delete_vm(self):
        return self._call('unregistervm', self.name, delete=True)

    def ramsize(self, ramsize):
        return self._call('modifyvm', self.name, memory=ramsize)

    def os_type(self, os, sp):
        operating_systems = {
            'xp': 'WindowsXP',
        }
        return self._call('modifyvm', self.name, ostype=operating_systems[os])

    def create_hd(self, fsize):
        ctlname = 'IDE Controller'
        path = os.path.join(self.basedir, self.name, '%s.vdi' % self.name)
        self._call('createhd', filename=path, size=fsize)
        self._call('storagectl', self.name, name=ctlname, add='ide')
        self._call('storageattach', self.name, storagectl=ctlname,
                   type='hdd', device=0, port=0, medium=path)

    def attach_iso(self, iso):
        ctlname = 'IDE Controller'
        self._call('storageattach', self.name, storagectl=ctlname,
                   type='dvddrive', port=1, device=0, medium=iso)
        self._call('modifyvm', self.name, boot1='dvd')

    def set_field(self, key, value):
        return self._call('setextradata', self.name, key, value)

    def modify_mac(self, macaddr=None):
        if macaddr is None:
            macaddr = random_mac()

        # VBoxManage prefers MAC addresses without colons.
        vbox_mac = macaddr.replace(':', '')

        self._call('modifyvm', self.name, macaddress1=vbox_mac)
        return macaddr

    def hostonly(self, index=0):
        if os.name == 'posix':
            adapter = 'vboxnet0'
        else:
            adapter = 'VirtualBox Host-Only Ethernet Adapter'

        self._call('modifyvm', self.name,
                   nic1='hostonly',
                   nictype1='Am79C973',
                   nicpromisc1='allow-all',
                   hostonlyadapter1=adapter)

    def start_vm(self):
        return self._call('startvm', self.name)

    def list_settings(self):
        return self._call('getextradata', self.name, 'enumerate')


def configure_winnt_sif(path, args):
    values = {
        'PRODUCTKEY': args.serial_key,
        'COMPUTERNAME': random_string(8, 16),
        'FULLNAME': '%s %s' % (random_string(4, 8), random_string(4, 10)),
        'ORGANIZATION': '',
        'WORKGROUP': random_string(4, 8),
    }

    buf = open(path, 'rb').read()
    for key, value in values.items():
        buf = buf.replace('%%%s%%' % key, value)
    return buf


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('vmname', type=str, help='Name of the Virtual Machine.')
    parser.add_argument('--cuckoo', type=str, required=True, help='Directory where Cuckoo is located.')
    parser.add_argument('--basedir', type=str, required=True, help='Base directory for the virtual machine and its associated files.')
    parser.add_argument('--vm', type=str, default='virtualbox', help='Virtual Machine Software (VirtualBox.)')
    parser.add_argument('--list', action='store_true', help='List the cloaked settings for a VM.')
    parser.add_argument('--delete', action='store_true', help='Completely delete a Virtual Machine and its associated files.')
    parser.add_argument('--ramsize', type=int, default=1024, help='Available virtual memory (in MB) for this virtual machine.')
    parser.add_argument('--resolution', type=str, default='1024x768', help='Virtual Machine resolution.')
    parser.add_argument('--hdsize', type=int, default=256*1024, help='Maximum size (in MB) of the dynamically allocated harddisk.')
    parser.add_argument('--iso', type=str, help='ISO Windows installer.')
    parser.add_argument('--serial-key', type=str, help='Windows Serial Key.')

    args = parser.parse_args()

    sys.path.append(args.cuckoo)
    from lib.cuckoo.common.config import Config
    from lib.cuckoo.common.constants import CUCKOO_ROOT

    if args.vm == 'virtualbox':
        m = VirtualBox(args.vmname, args.basedir)
    else:
        print '[-] Only VirtualBox is supported as of now'
        exit(1)

    if args.list:
        print m.list_settings()
        exit(0)

    if args.delete:
        print '[x] Unregistering and deleting the VM and its associated files'
        m.delete_vm()
        exit(0)

    if not args.iso:
        print '[-] Please specify a Windows Installer ISO image'
        exit(1)

    print '[x] Configuring WINNT.SIF'
    buf = configure_winnt_sif('winnt.sif', args)
    if not buf:
        print '[-] Error configuring WINNT.SIF'
        exit(1)

    # Write the WINNT.SIF file.
    open(os.path.join('nlite', 'winnt.sif'), 'wb').write(buf)

    print '[x] Creating VM'
    print m.create_vm()

    m.ramsize(args.ramsize)
    m.os_type(os='xp', sp=3)

    print '[x] Creating Harddisk'
    m.create_hd(args.hdsize)

    print '[x] Temporarily attaching DVD-Rom unit for the ISO installer'
    m.attach_iso(args.iso)

    print '[x] Randomizing Hardware'
    m.init_vm()

    print '[x] Randomizing the MAC address:',
    print m.modify_mac()

    print '[x] Initially configuring Hostonly network'
    m.hostonly()

    print '[!] Starting the Virtual Machine to install Windows'
    print m.start_vm()

    print '[x] Waiting for the Virtual Machine to connect back'
    print '[!] This may take up to 30 minutes'
    t = time.time()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('192.168.56.1', 61453))
    s.listen(1)

    c, a = s.accept()
    print '[x] It took %d seconds to install Windows!' % (time.time() - t)

    try:
        width, height = [int(x) for x in args.resolution.split('x')]
    except:
        print '[-] Invalid resolution specified'
        exit(1)

    print '[x] Setting the resolution to %dx%d' % (width, height)
    c.send(args.resolution)
    if ord(c.recv(1)):
        print '[+] Resolution was set successfully'
    else:
        print '[-] Error setting the resolution'
