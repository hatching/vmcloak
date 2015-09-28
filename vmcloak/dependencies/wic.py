# Copyright (C) 2014-2015 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

from vmcloak.abstract import Dependency

class WIC(Dependency):
    name = "wic"
    exes = [
        {
            "url": "http://cuckoo.sh/vmcloak/wic_x86_enu.exe",
            "sha1": "53c18652ac2f8a51303deb48a1b7abbdb1db427f",
        },
    ]

    def run(self):
        self.upload_dependency("C:\\wic.exe")
        self.a.execute("C:\\wic.exe /passive /norestart")
        self.a.remove("C:\\wic.exe")
