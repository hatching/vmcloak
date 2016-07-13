# Copyright (C) 2014-2016 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import json
import logging
import os

from vmcloak.constants import VMCLOAK_ROOT

log = logging.getLogger(__name__)
HWCONF_PATH = os.path.join(VMCLOAK_ROOT, "data", "hwconf")

def load_hwconf(profile, dirpath=HWCONF_PATH):
    ret = {}

    if profile is not None:
        files = ["%s.json" % profile]
    else:
        # Load profiles that ship with VMCloak.
        files = os.listdir(dirpath)

        # Load local profiles.
        local_hwconf = os.path.join(os.getenv("HOME"),
                                    ".config", "vmcloak", "hwconf")

        if os.path.exists(local_hwconf):
            for fname in os.listdir(local_hwconf):
                files.append(os.path.join(local_hwconf, fname))

    for fname in files:
        if not fname.endswith(".json"):
            continue

        conf = json.load(open(os.path.join(dirpath, fname), "rb"))
        for key, value in conf.items():
            if key not in ret:
                ret[key] = []

            if isinstance(value, list):
                ret[key].extend(value)
            else:
                ret[key].append(value)

    return ret
