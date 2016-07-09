# Copyright (C) 2014-2016 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import json
import logging
import os

from vmcloak.constants import VMCLOAK_ROOT

log = logging.getLogger(__name__)
HWCONF_PATH = os.path.join(VMCLOAK_ROOT, 'data', 'hwconf')

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
