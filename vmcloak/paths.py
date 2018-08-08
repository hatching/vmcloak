# Copyright (C) 2014-2018 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import logging
import os

log = logging.getLogger(__name__)

PATHS = {
    "genisoimage": [
        "/usr/bin/genisoimage",
        "/usr/pkg/bin/genisoimage",
        "/usr/bin/mkisofs",
        "/usr/local/bin/mkisofs",
        "/usr/pkg/bin/mkisofs",
    ],
    "vboxmanage": [
        "/usr/bin/VBoxManage",
        "/usr/local/bin/VBoxManage",
    ],
}

INSTALL = {
    "genisoimage": {
        "Linux": "apt-get install genisoimage",
        "NetBSD": "pkgin install cdrkit",
    },
    "vboxmanage": {
        "Linux": "apt-get install virtualbox",
    },
}

def get_path(app):
    """Returns the path to an application."""
    for path in PATHS[app]:
        if os.path.isfile(path):
            return path

    log.error("No executable path found for %s!", app)
    log.info("In order to install it, run %r",
             INSTALL[app].get(os.uname()[0], "?"))
