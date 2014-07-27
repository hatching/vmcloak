#!/usr/bin/env python
# Copyright (C) 2014 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import os
import subprocess

from data.config import VBOX_CONFIG
from lib.abstract import VM
from lib.rand import random_mac


class VirtualBox(VM):
    FIELDS = VBOX_CONFIG

    def __init__(self, *args, **kwargs):
        self.vboxmanage = kwargs.pop('vboxmanage')
        VM.__init__(self, *args, **kwargs)

        self.hdd_path = os.path.join(self.data_dir, '%s.vdi' % self.name)

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
            exit(1)

        return ret.strip()

    def create_vm(self):
        return self._call('createvm', name=self.name,
                          basefolder=self.vm_dir, register=True)

    def delete_vm(self):
        self._call('unregistervm', self.name, delete=True)

    def ramsize(self, ramsize):
        return self._call('modifyvm', self.name, memory=ramsize)

    def os_type(self, os, sp):
        operating_systems = {
            'xp': 'WindowsXP',
        }
        return self._call('modifyvm', self.name, ostype=operating_systems[os])

    def create_hd(self, fsize):
        ctlname = 'IDE Controller'
        self._call('createhd', filename=self.hdd_path, size=fsize)
        self._call('storagectl', self.name, name=ctlname, add='ide')
        self._call('storageattach', self.name, storagectl=ctlname,
                   type='hdd', device=0, port=0, medium=self.hdd_path)

    def attach_iso(self, iso):
        ctlname = 'IDE Controller'
        self._call('storageattach', self.name, storagectl=ctlname,
                   type='dvddrive', port=1, device=0, medium=iso)

    def detach_iso(self):
        ctlname = 'IDE Controller'
        self._call('storageattach', self.name, storagectl=ctlname,
                   type='dvddrive', port=1, device=0, medium='emptydrive')

    def set_field(self, key, value):
        return self._call('setextradata', self.name, key, value)

    def modify_mac(self, macaddr=None, index=1):
        if macaddr is None:
            macaddr = random_mac()

        # VBoxManage prefers MAC addresses without colons.
        vbox_mac = macaddr.replace(':', '')

        mac = {'macaddress%d' % index: vbox_mac}
        self._call('modifyvm', self.name, **mac)
        return macaddr

    def hostonly(self, macaddr=None):
        index = self.network_index() + 1

        if os.name == 'posix':
            adapter = 'vboxnet0'
        else:
            adapter = 'VirtualBox Host-Only Ethernet Adapter'

        # Ensure our hostonly interface is actually up and running.
        if adapter not in self._call('list', 'hostonlyifs'):
            print '[-] Have you configured %s?' % adapter
            print '[!] Please refer to the documentation to configure it.'
            return False

        nic = {
            'nic%d' % index: 'hostonly',
            'nictype%d' % index: 'Am79C973',
            'nicpromisc%d' % index: 'allow-all',
            'hostonlyadapter%d' % index: adapter,
        }
        self._call('modifyvm', self.name, **nic)
        return self.modify_mac(macaddr, index)

    def bridged(self, interface, macaddr=None):
        index = self.network_index() + 1

        nic = {
            'nic%d' % index: 'bridged',
            'nictype%d' % index: 'Am79C973',
            'nicpromisc%d' % index: 'allow-all',
            'bridgeadapter%d' % index: interface,
        }
        self._call('modifyvm', self.name, **nic)
        return self.modify_mac(macaddr, index)

    def nat(self, macaddr=None):
        index = self.network_index() + 1

        nic = {
            'nic%d' % index: 'nat',
            'nictype%d' % index: 'Am79C973',
            'nicpromisc%d' % index: 'allow-all',
        }
        self._call('modifyvm', self.name, **nic)
        return self.modify_mac(macaddr, index)

    def hwvirt(self, enable=True):
        """Enable or disable the usage of Hardware Virtualization."""
        self._call('modifyvm', self.name, hwvirtex='on' if enable else 'off')

    def start_vm(self, visible=False):
        return self._call('startvm', self.name,
                          type='gui' if visible else 'headless')

    def snapshot(self, label, description=''):
        return self._call('snapshot', self.name, 'take', label,
                          description=description, live=True)

    def stopvm(self):
        return self._call('controlvm', self.name, 'poweroff')

    def list_settings(self):
        return self._call('getextradata', self.name, 'enumerate')
