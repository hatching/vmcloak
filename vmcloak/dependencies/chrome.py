# Copyright (C) 2014-2016 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.
# Chrome Dependency submitted by Jason Lewis.
# https://dl.google.com/dl/chrome/install/googlechromestandaloneenterprise.msi

from vmcloak.abstract import Dependency

class Chrome(Dependency):
    name = "chrome"
    exes = [
        {
            "url": "https://cuckoo.sh/vmcloak/googlechromestandaloneenterprise.msi",
            "sha1": "a0ade494dda8911eeb68c9294c2dd0e3229d8f02",
        },
    ]

    def run(self):
        self.upload_dependency("C:\\googlechromestandaloneenterprise.msi")
        self.a.execute("Msiexec /q /I C:\\googlechromestandaloneenterprise.msi")
        self.a.remove("C:\\googlechromestandaloneenterprise.msi")
