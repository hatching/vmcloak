# Copyright (C) 2014-2015 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import logging
import os

log = logging.getLogger(__name__)

PATHS = {
    'wget': [
        '/usr/bin/wget',
        '/usr/local/bin/wget',
        '/usr/pkg/bin/wget'
    ],
    'genisoimage': [
        '/usr/bin/genisoimage',
        '/usr/pkg/bin/genisoimage',
        '/usr/bin/mkisofs',
        '/usr/local/bin/mkisofs',
        '/usr/pkg/bin/mkisofs',
    ],
}

INSTALL = {
    'wget': {
        'Linux': 'apt-get install wget',
        'NetBSD': 'pkgin install wget',
    },
    'genisoimage': {
        'Linux': 'apt-get install genisoimage',
        'NetBSD': 'pkgin install cdrkit',
    },
}

def get_path(app):
    """Returns the path to an application."""
    for path in PATHS[app]:
        if os.path.isfile(path):
            return path

    log.error('No executable path found for %s!', app)
    log.info('In order to install it, run %r',
             INSTALL[app].get(os.uname()[0], '?'))
