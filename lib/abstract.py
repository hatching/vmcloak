from __future__ import absolute_import
import random

from data.config import HW_CONFIG


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

    def hostonly(self, index=1):
        """Configure a hostonly adapter for the Virtual Machine."""
        raise

    def bridged(self, interface, index=1):
        """Configure a bridged adapter for the Virtual Machine."""
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
                        if not HW_CONFIG[k]:
                            value = 'To be filled by O.E.M.'
                        else:
                            if k not in config:
                                config[k] = random.choice(HW_CONFIG[k])

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
