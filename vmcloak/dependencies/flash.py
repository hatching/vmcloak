# Copyright (C) 2014-2016 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import time

from vmcloak.abstract import Dependency

class Flash11(Dependency):
    name = "flash11"
    exes = [
        {
            "url": "http://cuckoo.sh/vmcloak/flashplayer11_4r402_287_winax.msi",
            "sha1": "99fb61ed221df9125698e78d659ee1fc93b97c60",
        },
    ]

    def run(self):
        self.upload_dependency("C:\\flashplayer11_4r402_287_winax.msi")
        self.a.execute("msiexec /i C:\\flashplayer11_4r402_287_winax.msi /passive")

        self.a.remove("C:\\flashplayer11_4r402_287_winax.msi")
        