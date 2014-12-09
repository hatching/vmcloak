#!/usr/bin/env python
# Copyright (C) 2014 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import logging
import os
import subprocess
import sys

try:
    import requests
    import requests_toolbelt
    HAVE_REQUESTS = True
except ImportError:
    HAVE_REQUESTS = False


from vmcloak.abstract import VM
from vmcloak.data.config import VBOX_CONFIG
from vmcloak.exceptions import CommandError
from vmcloak.rand import random_mac

log = logging.getLogger(__name__)


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
                cmd += ['--' + k.rstrip('_'), str(v)]

        try:
            ret = subprocess.check_output(cmd)
        except Exception as e:
            log.error('[-] Error running command: %s', e)
            raise CommandError

        return ret.strip()

    def vminfo(self, element=None):
        ret = {}
        lines = self._call('showvminfo', self.name, machinereadable=True)
        for line in lines.split('\n'):
            key, value = line.split('=', 1)

            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            elif value.isdigit():
                value = int(value)

            if key.startswith('"') and key.endswith('"'):
                key = key[1:-1]

            ret[key] = value
        return ret if element is None else ret.get(element)

    def api_status(self):
        if not os.path.isfile(self.vboxmanage):
            log.error('VBoxManage not found!')
            return False

        return True

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
        self._call('createhd', filename=self.hdd_path, size=fsize)
        self._call('storagectl', self.name, name='IDE', add='ide')
        self._call('storageattach', self.name, storagectl='IDE',
                   type_='hdd', device=0, port=0, medium=self.hdd_path)

    def attach_hd(self, path):
        self._call('storagectl', self.name, name='IDE', add='ide')
        self._call('storageattach', self.name, storagectl='IDE',
                   type_='hdd', device=0, port=0, medium=path)

    def immutable_hd(self):
        self._call('modifyhd', self.hdd_path, type_='immutable', compact=True)

    def remove_hd(self):
        self._call('storagectl', self.name, portcount=0,
                   name='IDE', remove=True)

    def cpus(self, count):
        self._call('modifyvm', self.name, cpus=count, ioapic='on')

    def attach_iso(self, iso):
        self._call('storageattach', self.name, storagectl='IDE',
                   type_='dvddrive', port=1, device=0, medium=iso)

    def detach_iso(self):
        self._call('storageattach', self.name, storagectl='IDE',
                   type_='dvddrive', port=1, device=0, medium='emptydrive')

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
            log.error('Have you configured %s?', adapter)
            log.info('Please refer to the documentation to configure it.')
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
                          type_='gui' if visible else 'headless')

    def snapshot(self, label, description=''):
        return self._call('snapshot', self.name, 'take', label,
                          description=description, live=True)

    def stopvm(self):
        return self._call('controlvm', self.name, 'poweroff')

    def list_settings(self):
        return self._call('getextradata', self.name, 'enumerate')

    def vrde(self, vrde):
        vrde = 'on' if vrde else 'off'
        return self._call('modifyvm', self.name, vrde=vrde)


class VBoxRPC(VM):
    FIELDS = VBOX_CONFIG
    vm_dir_required = False
    data_dir_required = False

    def __init__(self, *args, **kwargs):
        self.url = kwargs.pop('url')
        self.auth = kwargs.pop('auth')

        VM.__init__(self, *args, **kwargs)

        if not HAVE_REQUESTS:
            sys.exit('Please install requests and requests-toolbelt: '
                     'sudo pip install requests requests-toolbelt')

    def _query(self, *args, **kwargs):
        url = os.path.join(self.url, 'api', *args)
        headers = {
            'user-agent': 'VBoxRPC/0.1',
        }

        r = requests.get(url, auth=self.auth, params=kwargs.get('params'),
                         headers=headers)
        return r.json()

    def api_status(self):
        try:
            self._query('api-status')
            return True
        except Exception as e:
            log.error('Error connecting to the API: %s %s', e.args, e.message)
            return False

    def create_vm(self):
        return self._query('createvm', self.name)

    def delete_vm(self):
        self._query('deletevm', self.name)

    def ramsize(self, ramsize):
        return self._query('ramsize', self.name, '%s' % ramsize)

    def os_type(self, os, sp):
        return self._query('os-type', self.name, os)

    def create_hd(self, disksize):
        return self._query('create-hdd', self.name, '%s' % disksize)

    def cpus(self, count):
        log.warning('VBoxRPC.cpus() has not been implemented yet')

    def attach_iso(self, iso):
        url = os.path.join(self.url, 'api', 'push-iso', '%s.iso' % self.name)

        # And now we wait.
        m = requests_toolbelt.MultipartEncoder(fields={
            'file': ('file', open(iso, 'rb'), ' application/iso-image'),
        })

        requests.post(url, auth=self.auth, data=m,
                      headers={'content-type': m.content_type})

        return self._query('attach-iso', self.name, '%s.iso' % self.name)

    def detach_iso(self):
        return self._query('detach-iso', self.name)

    def set_field(self, key, value):
        return self._query('extra-data', self.name,
                           params={'key': key, 'value': value})

    def modify_mac(self, macaddr=None, index=1):
        if macaddr is None:
            macaddr = random_mac()

        # VBoxManage prefers MAC addresses without colons.
        vbox_mac = macaddr.replace(':', '')
        self._query('mac-address', self.name,
                    'macaddress%d' % index, vbox_mac)
        return macaddr

    def hostonly(self, macaddr=None):
        index = self.network_index() + 1

        if os.name == 'posix':
            adapter = 'vboxnet0'
        else:
            adapter = 'VirtualBox Host-Only Ethernet Adapter'

        # Ensure our hostonly interface is actually up and running.
        if adapter not in self._query('hostonlyifs')['content']:
            log.error('Have you configured %s?', adapter)
            log.info('Please refer to the documentation to configure it.')
            return False

        nic = {
            'nic%d' % index: 'hostonly',
            'nictype%d' % index: 'Am79C973',
            'nicpromisc%d' % index: 'allow-all',
            'hostonlyadapter%d' % index: adapter,
        }

        for key, value in nic.items():
            self._query('nic', self.name, key, value)

        return self.modify_mac(macaddr, index)

    def bridged(self, interface, macaddr=None):
        index = self.network_index() + 1

        nic = {
            'nic%d' % index: 'bridged',
            'nictype%d' % index: 'Am79C973',
            'nicpromisc%d' % index: 'allow-all',
            'bridgeadapter%d' % index: interface,
        }

        for key, value in nic.items():
            self._query('nic', self.name, key, value)

        return self.modify_mac(macaddr, index)

    def nat(self, macaddr=None):
        index = self.network_index() + 1

        nic = {
            'nic%d' % index: 'nat',
            'nictype%d' % index: 'Am79C973',
            'nicpromisc%d' % index: 'allow-all',
        }

        for key, value in nic.items():
            self._query('nic', self.name, key, value)

        return self.modify_mac(macaddr, index)

    def hwvirt(self, enable=True):
        """Enable or disable the usage of Hardware Virtualization."""
        self._query('hwvirt', self.name, 'on' if enable else 'off')

    def start_vm(self, visible=False):
        return self._query('startvm', self.name)

    def snapshot(self, label, description=''):
        return self._query('snapshot', self.name, label,
                           params={'description': description})

    def stopvm(self):
        return self._query('stopvm', self.name)

    def vrde(self, vrde):
        vrde = 'on' if vrde else 'off'
        return self._query('modifyvm', self.name, vrde=vrde)


def initialize_vm(m, s, clone=False):
    log.debug('Creating VM %r.', s.vmname)
    log.debug(m.create_vm())

    m.ramsize(s.ramsize)
    m.os_type(os='xp', sp=3)

    if not clone:
        log.debug('Creating Harddisk.')
        m.create_hd(s.hdsize)

        log.debug('Temporarily attaching DVD-Rom unit for the ISO installer.')
        m.attach_iso(m.iso_path)

    log.debug('Randomizing Hardware.')
    m.init_vm(profile=s.hwconfig_profile)

    log.debug('Setting CPU count to %d', s.cpu_count)
    m.cpus(s.cpu_count)

    log.debug('Checking VirtualBox hostonly network.')
    if not m.hostonly(macaddr=s.hostonly_macaddr):
        exit(1)

    if s.nat:
        m.nat()

    if s.bridged:
        m.bridged(s.bridged, macaddr=s.bridged_macaddr)

    if s.hwvirt is not None:
        if s.hwvirt:
            log.debug('Enabling Hardware Virtualization.')
        else:
            log.debug('Disabling Hardware Virtualization.')
        m.hwvirt(s.hwvirt)

    if s.vrde:
        m.vrde(True)
