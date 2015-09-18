# Copyright (C) 2014-2015 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import os.path
import re

from vmcloak.constants import VMCLOAK_ROOT

def valid_serial_key(serial_key):
    """Determines whether `serial_key` has a valid encoding."""
    parts = serial_key.split('-')
    if len(parts) != 5:
        return False

    for part in parts:
        if not re.match('[A-Z0-9]{5}$', part):
            return False

    return True

def valid_keyboard_layout(kblayout):
    kblayout_txt = os.path.join(VMCLOAK_ROOT, 'data', 'winxp',
                                'keyboard_layout_values.txt')
    for layout in open(kblayout_txt, 'rb'):
        if layout.strip() == kblayout:
            return True
