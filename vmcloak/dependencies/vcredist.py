# Copyright (C) 2014-2016 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

from vmcloak.abstract import Dependency

class VcRedist(Dependency):
    name = "vcredist"
    description = "Visual studio redistributable packages"
    default = "2005"

    install_params = {
        "2005": "/q:a",
        "2008": "/qb",
        "2010": "/passive /norestart",
        "2012": "/passive /norestart",
        "2013": "/passive /norestart",
        "2015": "/passive /norestart",
    }

    exes = [
        {
            "version": "2005",
            "arch": "x86",
            "url": "https://cuckoo.sh/vmcloak/vcredist_2005_x86.exe",
            "sha1": "7dfa98be78249921dd0eedb9a3dd809e7d215c8d"
        },
        {
            "version": "2005",
            "arch": "amd64",
            "url": "https://cuckoo.sh/vmcloak/vcredist_2005_x64.exe",
            "sha1": "756f2c773d4733e3955bf7d8f1e959a7f5634b1a"
        },
        {
            "version": "2008",
            "arch": "x86",
            "url": "https://cuckoo.sh/vmcloak/vcredist_2008_x86.exe",
            "sha1": "6939100e397cef26ec22e95e53fcd9fc979b7bc9"
        },
        {
            "version": "2008",
            "arch": "amd64",
            "url": "https://cuckoo.sh/vmcloak/vcredist_2008_x64.exe",
            "sha1": "13674c43652b941dafd2049989afce63cb7c517b"
        },
        {
            "version": "2010",
            "arch": "x86",
            "url": "https://cuckoo.sh/vmcloak/vcredist_2010_x86.exe",
            "sha1": "b84b83a8a6741a17bfb5f3578b983c1de512589d"
        },
        {
            "version": "2010",
            "arch": "amd64",
            "url": "https://cuckoo.sh/vmcloak/vcredist_2010_x64.exe",
            "sha1": "027d0c2749ec5eb21b031f46aee14c905206f482"
        },
        {
            "version": "2012",
            "arch": "x86",
            "url": "https://cuckoo.sh/vmcloak/vcredist_2012_x86.exe",
            "sha1": "7d6f654c16f9ce534bb2c4b1669d7dc039c433c9"
        },
        {
            "version": "2012",
            "arch": "amd64",
            "url": "https://cuckoo.sh/vmcloak/vcredist_2012_x64.exe",
            "sha1": "c4ac45564e801e1bfd87936cac8a76c5754cdbd4"
        },
        {
            "version": "2013",
            "arch": "x86",
            "url": "https://cuckoo.sh/vmcloak/vcredist_2013_x86.exe",
            "sha1": "df7f0a73bfa077e483e51bfb97f5e2eceedfb6a3"
        },
        {
            "version": "2013",
            "arch": "amd64",
            "url": "https://cuckoo.sh/vmcloak/vcredist_2013_x64.exe",
            "sha1": "8bf41ba9eef02d30635a10433817dbb6886da5a2"
        },
        {
            "version": "2015",
            "arch": "x86",
            "url": "https://cuckoo.sh/vmcloak/vcredist_2015_x86.exe",
            "sha1": "bfb74e498c44d3a103ca3aa2831763fb417134d1"
        },
        {
            "version": "2015",
            "arch": "amd64",
            "url": "https://cuckoo.sh/vmcloak/vcredist_2015_x64.exe",
            "sha1": "3155cb0f146b927fcc30647c1a904cd162548c8c"
        },
    ]

    def run(self):
        # Get the installation parameters required to start
        # an unattended install
        param = self.install_params[self.version]

        self.upload_dependency("C:\\vcredist.exe")
        self.a.execute("C:\\vcredist.exe %s" % param)
        self.a.remove("C:\\vcredist.exe")
