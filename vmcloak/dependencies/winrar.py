# Copyright (C) 2016-2018 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

from vmcloak.abstract import Dependency

class Winrar(Dependency):
    name = "winrar"
    default = "5.31"
    exes = [{
        "version": "5.31",
        "arch": "amd64",
        "urls": [
            "http://rarlab.com/rar/winrar-x64-531.exe",
            "https://cuckoo.sh/vmcloak/winrar-x64-531.exe",
        ],
        "sha1": "48add5a966ed940c7d88456caf7a5f5c2a6c27a7",
    }, {
        "version": "5.31",
        "arch": "x86",
        "urls": [
            "http://rarlab.com/rar/wrar531.exe"
            "https://cuckoo.sh/vmcloak/wrar531.exe",
        ],
        "sha1": "e19805a1738975aeec19a25a4e461d52eaf9b231",
    }, {
        "version": "5.40",
        "arch": "amd64",
        "urls": [
            "http://rarlab.com/rar/winrar-x64-540.exe",
        ],
        "sha1": "22ac3a032f37ce5dabd0673f401f3d0307f21b74",
    }, {
        "version": "5.40",
        "arch": "x86",
        "urls": [
            "http://rarlab.com/rar/wrar540.exe"
        ],
        "sha1": "211a19ca4ec3c7562c9844fe6c42e66a521b8bd4",
    }]

    def run(self):
        self.upload_dependency("C:\\%s" % self.filename)
        self.a.execute("C:\\%s /S" % self.filename)
        self.a.remove("C:\\%s" % self.filename)
