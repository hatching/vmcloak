#!/usr/bin/env python
# Copyright (C) 2014-2015 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

from __future__ import absolute_import
import logging
import os.path
import random
import shutil
import subprocess
import tempfile

from vmcloak.conf import load_hwconf
from vmcloak.constants import VMCLOAK_ROOT
from vmcloak.misc import copytreelower, copytreeinto
from vmcloak.paths import get_path
from vmcloak.rand import random_serial, random_uuid

log = logging.getLogger(__name__)

class Machinery(object):
    FIELDS = {}
    vm_dir_required = True
    data_dir_required = True

    def __init__(self, name, vm_dir=None, data_dir=None, temp_dir=None):
        self.name = name
        self.vm_dir = vm_dir
        self.data_dir = data_dir

        self.network_idx = 0

        if self.vm_dir_required and not vm_dir:
            log.error('Please provide --vm-dir a directory for the '
                      'associated VM files.')
            log.info('Optionally this directory can be put into tmpfs for '
                     'improved speed.')
            exit(1)

        if self.data_dir_required and not data_dir:
            log.error('Please provide --data-dir a directory for the '
                      'harddisk and .iso files for the virtual machine.')
            log.info('It is recommended to store this directory on a regular '
                     'harddisk or SSD - not in tmpfs.')
            exit(1)

        if data_dir:
            self.iso_path = os.path.join(self.data_dir, '%s.iso' % self.name)
        else:
            _, self.iso_path = tempfile.mkstemp(suffix='.iso', dir=temp_dir)

    def vminfo(self, element=None):
        """Returns a dictionary with all available information for the
        Virtual Machine."""
        raise

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

    def immutable_hd(self):
        """Make a harddisk immutable or normal."""
        raise

    def remove_hd(self):
        """Remove a harddisk."""
        raise

    def cpus(self, count):
        """Set the number of CPUs to assign to this Virtual Machine."""
        raise

    def attach_iso(self, iso):
        """Attach a ISO file as DVDRom drive."""
        raise

    def detach_iso(self):
        """Detach the ISO file in the DVDRom drive."""
        raise

    def set_field(self, key, value):
        """Set a specific field of a Virtual Machine."""
        raise

    def modify_mac(self, mac=None):
        """Modify the MAC address of a Virtual Machine."""
        raise

    def network_index(self):
        """Get the index for the next network interface."""
        ret = self.network_idx
        self.network_idx += 1
        return ret

    def hostonly(self, macaddr=None, index=1):
        """Configure a hostonly adapter for the Virtual Machine."""
        raise

    def nat(self, macaddr=None, index=1):
        """Configure NAT for the Virtual Machine."""
        raise

    def hwvirt(self, enable=True):
        """Enable or disable the usage of Hardware Virtualization."""
        raise

    def start_vm(self, visible=False):
        """Start the associated Virtual Machine."""
        raise

    def snapshot(self, label):
        """Take a snapshot of the associated Virtual Machine."""
        raise

    def stopvm(self):
        """Stop the associated Virtual Machine."""
        raise

    def list_settings(self):
        """List all settings of a Virtual Machine."""
        raise

    def init_vm(self, profile):
        """Initialize fields as specified by `FIELDS`."""
        hwconf = load_hwconf(profile=profile)

        def _init_vm(path, fields):
            for key, value in fields.items():
                key = path + '/' + key
                if isinstance(value, dict):
                    _init_vm(key, value)
                else:
                    if isinstance(value, tuple):
                        k, v = value
                        if k not in hwconf or not hwconf[k]:
                            value = 'To be filled by O.E.M.'
                        else:
                            if k not in config:
                                config[k] = random.choice(hwconf[k])

                            value = config[k][v]

                            # Some values have to be generated randomly.
                            if value is not None:
                                if value.startswith('<SERIAL>'):
                                    length = int(value.split()[-1])
                                    value = random_serial(length)
                                elif value.startswith('<UUID>'):
                                    value = random_uuid()

                    if value is None:
                        value = "To be filled by O.E.M."

                    log.debug('Setting %r to %r.', key, value)
                    ret = self.set_field(key, value)
                    if ret:
                        log.debug(ret)

        config = {}
        _init_vm('', self.FIELDS)

class OperatingSystem(object):
    # Short name for this OS.
    name = None

    # Service Pack that is likely being used.
    service_pack = None

    # Default directory where the original ISO is mounted.
    mount = None

    # The Network Interface Card Type.
    nictype = None

    # Directory where to store the vmcloak bootstrap files.
    osdir = None

    # Additional arguments for genisoimage.
    genisoargs = []

    def __init__(self):
        self.data_path = os.path.join(VMCLOAK_ROOT, 'data')
        self.path = os.path.join(self.data_path, self.name)
        self.serial_key = None

        if self.name is None:
            raise Exception('Name has to be provided for OS handler')

        if self.osdir is None:
            raise Exception('OSDir has to be provided for OS handler')

    def configure(self, s):
        """Configure the setup with settings provided by the user."""
        self.s = s

    def isofiles(self, outdir, tmp_dir=None):
        """Abstract method for writing additional files to the newly created
        ISO file."""

    def set_serial_key(self, serial_key):
        """Abstract method for checking a serial key if provided and otherwise
        use a default serial key if available."""

    def buildiso(self, mount, newiso, bootstrap, tmp_dir=None):
        """Builds an ISO file containing all our modifications."""
        outdir = tempfile.mkdtemp(dir=tmp_dir)

        # Copy all files to our temporary directory as mounted iso files are
        # read-only and we need lowercase (aka case-insensitive) filepaths.
        copytreelower(mount, outdir)

        # Copy the boot image.
        shutil.copy(os.path.join(self.path, 'boot.img'), outdir)

        # Allow the OS handler to write additional files.
        self.isofiles(outdir, tmp_dir)

        os.makedirs(os.path.join(outdir, self.osdir, 'vmcloak'))

        data_bootstrap = os.path.join(self.data_path, 'bootstrap')
        for fname in os.listdir(data_bootstrap):
            shutil.copy(os.path.join(data_bootstrap, fname),
                        os.path.join(outdir, self.osdir, 'vmcloak', fname))

        copytreeinto(bootstrap, os.path.join(outdir, self.osdir))

        isocreate = get_path('genisoimage')
        if not isocreate:
            log.error('Either genisoimage or mkisofs is required!')
            shutil.rmtree(outdir)
            return False

        args = [
            isocreate, '-quiet', '-b', 'boot.img', '-o', newiso,
        ] + self.genisoargs + [outdir]

        try:
            # TODO Properly suppress the ISO-9660 warning.
            subprocess.check_call(args)
        except subprocess.CalledProcessError as e:
            log.error('Error creating ISO file: %s', e)
            shutil.rmtree(outdir)
            return False

        shutil.rmtree(outdir)
        return True
