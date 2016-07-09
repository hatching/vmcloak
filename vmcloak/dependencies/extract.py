# Copyright (C) 2014-2016 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import logging
import os.path

from vmcloak.abstract import Dependency

log = logging.getLogger(__name__)

class Extract(Dependency):
    name = "extract"

    def init(self):
        self.zip = None
        self.dir = None

    def check(self):
        if not self.zip or not os.path.isfile(self.zip):
            log.error("Please provide zip file to extract.")
            return False

        if not self.dir:
            log.error("Please provide %USERPROFILE% folder to extract to.")
            return False

    def run(self):
        dirpath = os.path.join(self.a.environ("USERPROFILE"), self.dir)
        self.a.extract(dirpath, self.zip)
