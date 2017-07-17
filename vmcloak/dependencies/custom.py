# Copyright (C) 2014-2016 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.
# Custom Dependency submitted by Marc Ohm.

import os.path

from vmcloak.abstract import Dependency

class Custom(Dependency):
    name = "custom"
    
    def init(self):
        self.exepath = None
        self.params = None

    def check(self):    
        if not self.exepath or not os.path.isfile(self.exepath):
            log.error("Please provide the path to the exe file.")
            return False

    def run(self):
        self.a.upload(
            "C:\\setup.exe",
            open(self.exepath, "rb").read()
        )
        self.a.execute("C:\\setup.exe " + self.params if self.params else "")
        self.a.remove("C:\\setup.exe")
