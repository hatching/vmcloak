# Copyright (C) 2016 Markus Teufelberger.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

from vmcloak.abstract import Dependency

class Pafish(Dependency):
    name = "pafish"
    default = "058"
    exes = [
        {
            "version": "058",
            "url": "https://github.com/a0rtega/pafish/raw/master/pafish.exe",
            "sha1": "124f46228d1e220d88ae5e9a24d6e713039a64f9",
        },
    ]

    def run(self):
        self.upload_dependency("C:\\%s" % self.filename)
