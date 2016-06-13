# Copyright (C) 2014-2015 Jurriaan Bremer.
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

    def check(self):
        if not self.zip or not os.path.isfile(self.zip):
            log.error("Please provide zip file to extract.")
            return False

    def run(self):
        self.upload_dependency("C:\\package.zip", self.zip)
        self.a.execute("\"%PROGRAMFILES%\\WinRAR\\Winrar.exe\" x C:\\package.zip *.* \"%USERPROFILE%\Desktop\"")

        self.wait_process_exit("Winrar.exe")
        
        self.a.remove("C:\\package.zip")
