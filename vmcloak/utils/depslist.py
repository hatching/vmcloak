#!/usr/bin/env python
# Copyright (C) 2014 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import os.path

from vmcloak.misc import ini_read_dict

VMCLOAK_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


if __name__ == '__main__':
    deps = ini_read_dict(os.path.join(VMCLOAK_ROOT, 'deps', 'repo.ini'))
    print '%-16s: %s' % ('dependency', 'description')
    print '-----------------------------'
    print
    for dep, info in sorted(deps.items()):
        print '%-16s: %s' % (dep, info['description'])
