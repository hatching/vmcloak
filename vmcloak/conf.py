#!/usr/bin/env python
# Copyright (C) 2014-2015 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import ConfigParser
import json
import logging
import os

from vmcloak.constants import VMCLOAK_ROOT

log = logging.getLogger(__name__)
HWCONF_PATH = os.path.join(VMCLOAK_ROOT, 'data', 'hwconf')

class Configuration(object):
    def __init__(self):
        self.conf = {}

    def _process_value(self, value):
        if isinstance(value, str) and value.startswith('~'):
            return os.getenv('HOME') + value[1:]
        if value in ('true', 'True', 'on', 'yes', 'enable'):
            return True
        if value in ('false', 'False', 'off', 'no', 'disable'):
            return False
        return value

    def from_args(self, args):
        for key, value in args._get_kwargs():
            if key not in self.conf or value:
                self.conf[key] = self._process_value(value)

    def from_file(self, path):
        p = ConfigParser.ConfigParser()
        p.read(path)
        for key in p.options('vmcloak'):
            self.conf[key.replace('-', '_')] = \
                self._process_value(p.get('vmcloak', key))

    def from_defaults(self, defaults):
        for key, value in defaults.items():
            if key in self.conf and self.conf[key] is None:
                self.conf[key] = self._process_value(value)

    def __getattr__(self, key):
        return self.conf[key]

    def apply_types(self, types):
        for k, v in self.conf.items():
            if k not in types:
                continue

            try:
                self.conf[k] = types[k](v)
            except ValueError:
                log.critical('Flag %r should be an %r.', k, types[k].__name__)
                exit(1)

def vboxmanage_path(s):
    if os.path.isfile(s.vboxmanage):
        return s.vboxmanage

    if not s.cuckoo or not os.path.isdir(s.cuckoo):
        log.error('Please provide your Cuckoo root directory.')
        log.info('Or provide the path to the VBoxManage executable.')
        return

    conf_path = os.path.join(s.cuckoo, 'conf', 'virtualbox.conf')

    try:
        from lib.cuckoo.common.config import Config
        vboxmanage = Config(conf_path).virtualbox.path
    except:
        log.error('Unable to locate VBoxManage path, please '
                  'configure $CUCKOO/conf/virtualbox.conf properly.')
        exit(1)

    if not vboxmanage or not os.path.isfile(vboxmanage):
        log.error('The configured VBoxManage path in Cuckoo does not '
                  'exist, please configure $CUCKOO/conf/virtualbox.conf '
                  'properly.')
        exit(1)

    return vboxmanage

def load_hwconf(profile, dirpath=HWCONF_PATH):
    ret = {}

    if profile is not None:
        files = ['%s.json' % profile]
    else:
        # Load profiles that ship with VMCloak.
        files = os.listdir(dirpath)

        # Load local profiles.
        local_hwconf = os.path.join(os.getenv('HOME'),
                                    '.config', 'vmcloak', 'hwconf')

        if os.path.exists(local_hwconf):
            for fname in os.listdir(local_hwconf):
                files.append(os.path.join(local_hwconf, fname))

    for fname in files:
        if not fname.endswith('.json'):
            continue

        conf = json.load(open(os.path.join(dirpath, fname), 'rb'))
        for key, value in conf.items():
            if key not in ret:
                ret[key] = []

            if isinstance(value, list):
                ret[key].extend(value)
            else:
                ret[key].append(value)

    return ret
