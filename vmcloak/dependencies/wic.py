# Copyright (C) 2015-2018 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.
#
# The Windows Imaging Component (WIC) provides WIC-enabled
# applications to display and edit any image format for which
# a WIC-compliant CODEC is installed, and also to read and
# write metadata in image files.

from vmcloak.abstract import Dependency

class WIC(Dependency):
    name = "wic"
    exes = [{
        "arch": "x86",
        "urls": [
            "https://download.microsoft.com/download/f/f/1/ff178bb1-da91-48ed-89e5-478a99387d4f/wic_x86_enu.exe",
            "https://cuckoo.sh/vmcloak/wic_x86_enu.exe",
        ],
        "sha1": "53c18652ac2f8a51303deb48a1b7abbdb1db427f",
    }, {
        "arch": "amd64",
        "urls": [
            "https://download.microsoft.com/download/6/4/5/645FED5F-A6E7-44D9-9D10-FE83348796B0/wic_x64_enu.exe",
        ],
        "sha1": "4bdbf76a7bc96453306c893b4a7b2b8ae6127f67",
    }]

    def run(self):
        self.upload_dependency("C:\\wic.exe")
        self.a.execute("C:\\wic.exe /passive /norestart")
        self.a.remove("C:\\wic.exe")
