# Copyright (C) 2014-2016 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

from vmcloak.abstract import Dependency


class VcRedist(Dependency):
    # all latest versions can be found on:
    # https://support.microsoft.com/en-us/kb/2977003
    name = "vcredist"
    description = "Visual studio redistributable packages"
    default = "2005sp1"

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
            "urls": [
                "https://download.microsoft.com/download/d/3/4/d342efa6-3266-4157-a2ec-5174867be706/vcredist_x86.exe",
            ],
            "sha1": "47fba37de95fa0e2328cf2e5c8ebb954c4b7b93c"
        },
        {
            "version": "2005",
            "arch": "amd64",
            "urls": [
                "https://download.microsoft.com/download/9/1/4/914851c6-9141-443b-bdb4-8bad3a57bea9/vcredist_x64.exe",
            ],
            "sha1": "90a3d2a139c1a106bfccd98cbbd7c2c1d79f5ebe"
        },
        {
            "version": "2005sp1",
            "arch": "x86",
            "urls": [
                "https://download.microsoft.com/download/e/1/c/e1c773de-73ba-494a-a5ba-f24906ecf088/vcredist_x86.exe",
                "https://cuckoo.sh/vmcloak/vcredist_2005_x86.exe",
            ],
            "sha1": "7dfa98be78249921dd0eedb9a3dd809e7d215c8d"
        },
        {
            "version": "2005sp1",
            "arch": "amd64",
            "urls": [
                "https://download.microsoft.com/download/d/4/1/d41aca8a-faa5-49a7-a5f2-ea0aa4587da0/vcredist_x64.exe",
                "https://cuckoo.sh/vmcloak/vcredist_2005_x64.exe",
            ],
            "sha1": "756f2c773d4733e3955bf7d8f1e959a7f5634b1a"
        },
        {
            "version": "2008",
            "arch": "x86",
            "urls": [
                "https://download.microsoft.com/download/d/d/9/dd9a82d0-52ef-40db-8dab-795376989c03/vcredist_x86.exe",
            ],
            "sha1": "56719288ab6514c07ac2088119d8a87056eeb94a"
        },
        {
            "version": "2008",
            "arch": "amd64",
            "url": "https://download.microsoft.com/download/d/2/4/d242c3fb-da5a-4542-ad66-f9661d0a8d19/vcredist_x64.exe",
            "sha1": "5580072a056fdd50cdf93d470239538636f8f3a9"
        },
        {
            "version": "2008sp1",
            "arch": "x86",
            "urls": [
                "https://download.microsoft.com/download/d/d/9/dd9a82d0-52ef-40db-8dab-795376989c03/vcredist_x86.exe",
                "https://cuckoo.sh/vmcloak/vcredist_2008_x86.exe",
            ],
            "sha1": "6939100e397cef26ec22e95e53fcd9fc979b7bc9"
        },
        {
            "version": "2008sp1",
            "arch": "amd64",
            "urls": [
                "https://cuckoo.sh/vmcloak/vcredist_2008_x64.exe",
                "https://download.microsoft.com/download/2/d/6/2d61c766-107b-409d-8fba-c39e61ca08e8/vcredist_x64.exe",
            ],
            "sha1": "13674c43652b941dafd2049989afce63cb7c517b"
        },
        {
            "version": "2010",
            "arch": "x86",
            "urls": [
                "https://download.microsoft.com/download/5/B/C/5BC5DBB3-652D-4DCE-B14A-475AB85EEF6E/vcredist_x86.exe",
            ],
            "sha1": "372d9c1670343d3fb252209ba210d4dc4d67d358"
        },
        {
            "version": "2010",
            "arch": "amd64",
            "urls": [
                "https://download.microsoft.com/download/3/2/2/3224B87F-CFA0-4E70-BDA3-3DE650EFEBA5/vcredist_x64.exe",
            ],
            "sha1": "b330b760a8f16d5a31c2dc815627f5eb40861008"
        },
        {
            "version": "2010sp1",
            "arch": "x86",
            "urls": [
                "https://download.microsoft.com/download/C/6/D/C6D0FD4E-9E53-4897-9B91-836EBA2AACD3/vcredist_x86.exe",
                "https://cuckoo.sh/vmcloak/vcredist_2010_x86.exe",
            ],
            "sha1": "b84b83a8a6741a17bfb5f3578b983c1de512589d"
        },
        {
            "version": "2010sp1",
            "arch": "amd64",
            "urls": [
                "https://download.microsoft.com/download/A/8/0/A80747C3-41BD-45DF-B505-E9710D2744E0/vcredist_x64.exe",
                "https://cuckoo.sh/vmcloak/vcredist_2010_x64.exe",
            ],
            "sha1": "027d0c2749ec5eb21b031f46aee14c905206f482"
        },
        {
            "version": "2012u4",
            "arch": "x86",
            "urls": [
                "https://download.microsoft.com/download/1/6/B/16B06F60-3B20-4FF2-B699-5E9B7962F9AE/VSU_4/vcredist_x86.exe",
            ],
            "sha1": "96b377a27ac5445328cbaae210fc4f0aaa750d3f"
        },
        {
            "version": "2012u4",
            "arch": "amd64",
            "urls": [
                "https://download.microsoft.com/download/1/6/B/16B06F60-3B20-4FF2-B699-5E9B7962F9AE/VSU_4/vcredist_x64.exe",
            ],
            "sha1": "1a5d93dddbc431ab27b1da711cd3370891542797"
        },
        {
            "version": "2013",
            "arch": "x86",
            "urls": [
                "https://download.microsoft.com/download/2/E/6/2E61CFA4-993B-4DD4-91DA-3737CD5CD6E3/vcredist_x86.exe",
                "https://cuckoo.sh/vmcloak/vcredist_2013_x86.exe",
            ],
            "sha1": "df7f0a73bfa077e483e51bfb97f5e2eceedfb6a3"
        },
        {
            "version": "2013",
            "arch": "amd64",
            "urls": [
                "https://download.microsoft.com/download/2/E/6/2E61CFA4-993B-4DD4-91DA-3737CD5CD6E3/vcredist_x64.exe",
                "https://cuckoo.sh/vmcloak/vcredist_2013_x64.exe",
            ],
            "sha1": "8bf41ba9eef02d30635a10433817dbb6886da5a2"
        },
        {
            "version": "2013u5",
            "arch": "x86",
            "urls": [
                "http://download.microsoft.com/download/0/5/6/056dcda9-d667-4e27-8001-8a0c6971d6b1/vcredist_x86.exe",
            ],
            "sha1": "2a07a32330d5131665378836d542478d3e7bd137"
        },
        {
            "version": "2013u5",
            "arch": "amd64",
            "urls": [
                "http://download.microsoft.com/download/0/5/6/056dcda9-d667-4e27-8001-8a0c6971d6b1/vcredist_x64.exe",
            ],
            "sha1": "261c2e77d288a513a9eb7849cf5afca6167d4fa2"
        },
        {
            "version": "2015",
            "arch": "x86",
            "urls": [
                "https://download.microsoft.com/download/9/3/F/93FCF1E7-E6A4-478B-96E7-D4B285925B00/vc_redist.x86.exe",
                "https://cuckoo.sh/vmcloak/vcredist_2015_x86.exe",
            ],
            "sha1": "bfb74e498c44d3a103ca3aa2831763fb417134d1"
        },
        {
            "version": "2015",
            "arch": "amd64",
            "urls": [
                "https://download.microsoft.com/download/9/3/F/93FCF1E7-E6A4-478B-96E7-D4B285925B00/vc_redist.x64.exe",
                "https://cuckoo.sh/vmcloak/vcredist_2015_x64.exe",
            ],
            "sha1": "3155cb0f146b927fcc30647c1a904cd162548c8c"
        },
        {
            "version": "2015u3",
            "arch": "x86",
            "urls": [
                "https://download.microsoft.com/download/6/A/A/6AA4EDFF-645B-48C5-81CC-ED5963AEAD48/vc_redist.x86.exe",
            ],
            "sha1": "72211bd2e7dfc91ea7c8fac549c49c0543ba791b"
        },
        {
            "version": "2015u3",
            "arch": "amd64",
            "urls": [
                "https://download.microsoft.com/download/6/A/A/6AA4EDFF-645B-48C5-81CC-ED5963AEAD48/vc_redist.x64.exe",
            ],
            "sha1": "10b1683ea3ff5f36f225769244bf7e7813d54ad0"
        },
    ]

    def run(self):
        # Get the installation parameters required to start
        # an unattended install
        param = self.install_params[self.version.split("u")[0].split("sp")[0]]

        self.upload_dependency("C:\\vcredist.exe")
        self.a.execute("C:\\vcredist.exe %s" % param)
        self.a.remove("C:\\vcredist.exe")
