# Copyright (C) 2014 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import logging
import os.path


log = logging.getLogger(__name__)

PATHS = {
    'git': [
        '/usr/bin/git',
        '/usr/pkg/bin/git'
    ],
    'wget': [
        '/usr/bin/wget',
        '/usr/pkg/bin/wget'
    ],
    'genisoimage': [
        '/usr/bin/genisoimage',
        '/usr/bin/mkisofs',
        '/usr/pkg/bin/mkisofs',
    ],
}


def get_path(app):
    """Returns the path to an application."""
    for path in PATHS[app]:
        if os.path.isfile(path):
            return path

    log.error('No executable path found for %s!', app)
