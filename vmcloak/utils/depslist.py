#!/usr/bin/env python
# Copyright (C) 2014 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

from ConfigParser import ConfigParser
import os.path


VMCLOAK_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


def read_ini(path):
    c = ConfigParser()
    c.read(path)
    return dict((section, dict(c.items(section)))
                for section in c.sections())

if __name__ == '__main__':
    deps = read_ini(os.path.join(VMCLOAK_ROOT, 'deps', 'repo.ini'))
    print '%-16s: %s' % ('dependency', 'description')
    print '-----------------------------'
    print
    for dep, info in sorted(deps.items()):
        print '%-16s: %s' % (dep, info['description'])
