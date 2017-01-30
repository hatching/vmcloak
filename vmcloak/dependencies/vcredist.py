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
            "sha1": "47fba37de95fa0e2328cf2e5c8ebb954c4b7b93c"
        },
        {
            "version": "2005",
            "arch": "amd64",
            "url": "https://cuckoo.sh/vmcloak/vcredist_2005_x64.exe",
            "sha1": "90a3d2a139c1a106bfccd98cbbd7c2c1d79f5ebe"
        },
        {
            "version": "2008",
            "arch": "x86",
            "url": "https://cuckoo.sh/vmcloak/vcredist_2008_x86.exe",
            "sha1": "56719288ab6514c07ac2088119d8a87056eeb94a"
        },
        {
            "version": "2008",
            "arch": "amd64",
            "url": "https://cuckoo.sh/vmcloak/vcredist_2008_x64.exe",
            "sha1": "5580072a056fdd50cdf93d470239538636f8f3a9"
        },
        {
            "version": "2010",
            "arch": "x86",
            "url": "https://cuckoo.sh/vmcloak/vcredist_2010_x86.exe",
            "sha1": "372d9c1670343d3fb252209ba210d4dc4d67d358"
        },
        {
            "version": "2010",
            "arch": "amd64",
            "url": "https://cuckoo.sh/vmcloak/vcredist_2010_x64.exe",
            "sha1": "b330b760a8f16d5a31c2dc815627f5eb40861008"
        },
        {
            "version": "2012",
            "arch": "x86",
            "url": "https://cuckoo.sh/vmcloak/vcredist_2012_x86.exe",
            "sha1": "96b377a27ac5445328cbaae210fc4f0aaa750d3f"
        },
        {
            "version": "2012",
            "arch": "amd64",
            "url": "https://cuckoo.sh/vmcloak/vcredist_2012_x64.exe",
            "sha1": "1a5d93dddbc431ab27b1da711cd3370891542797"
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
