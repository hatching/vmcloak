# Copyright (C) 2014-2015 Jurriaan Bremer.
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
    exes = [
        {
            "url": "https://cuckoo.sh/vmcloak/wic_x86_enu.exe",
            "sha1": "53c18652ac2f8a51303deb48a1b7abbdb1db427f",
        },
    ]

    def run(self):
        self.upload_dependency("C:\\wic.exe")
        self.a.execute("C:\\wic.exe /passive /norestart")
        self.a.remove("C:\\wic.exe")
