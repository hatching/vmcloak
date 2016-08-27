# Copyright (C) 2014-2016 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

from vmcloak.abstract import Dependency

class Winrar(Dependency):
    name = "winrar"
    default = "5.31"
    exes = [
        {
            "version": "5.31_x64",
            "url": "https://cuckoo.sh/vmcloak/winrar-x64-531.exe",
            "sha1": "48add5a966ed940c7d88456caf7a5f5c2a6c27a7",
        },
        {
            "version": "5.31",
            "url": "https://cuckoo.sh/vmcloak/wrar531.exe",
            "sha1": "e19805a1738975aeec19a25a4e461d52eaf9b231",
        },
    ]

    def run(self):
        self.upload_dependency("C:\\%s" % self.filename)
        self.a.execute("C:\\%s /S" % self.filename)
        self.a.remove("C:\\%s" % self.filename)
