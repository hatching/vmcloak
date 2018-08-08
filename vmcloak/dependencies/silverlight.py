# Copyright (C) 2016-2018 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

from vmcloak.abstract import Dependency

class Silverlight(Dependency):
    name = "silverlight"
    default = "5.0.61118.0"
    exes = [{
        "arch": "x86",
        "version": "5.0.61118.0",
        "urls": [
            "https://download.microsoft.com/download/5/5/7/55748E53-D673-4225-8072-4C7A377BB513/runtime/Silverlight.exe"
        ],
        "sha1": "f0c3c1bce3802addca966783a33db1b668261fb5",
    }, {
        "arch": "amd64",
        "version": "5.0.61118.0",
        "urls": [
            "https://download.microsoft.com/download/5/5/7/55748E53-D673-4225-8072-4C7A377BB513/runtime/Silverlight_x64.exe"
        ],
        "sha1": "c98499e2a2f9ac0f8b70d301e3dee4d4cc4a5f86",
    }, {
        "arch": "x86",
        "version": "5.1.40620.0",
        "urls": [
            "https://download.microsoft.com/download/5/A/4/5A4F7D41-D714-42B4-9F5F-A2B0B985CBAC/40620.00/Silverlight.exe",
        ],
        "sha1": "45f07952e2e6cf8bd972a733aacb213871d086f1",
    }, {
        "arch": "amd64",
        "version": "5.1.40620.0",
        "urls": [
            "https://download.microsoft.com/download/5/A/4/5A4F7D41-D714-42B4-9F5F-A2B0B985CBAC/40620.00/Silverlight_x64.exe",
        ],
        "sha1": "56ade2a82b7083383c9e4453af1da0301b48ac53",
    }, {
        "arch": "x86",
        "version": "5.1.50709.0",
        "urls": [
            "https://download.microsoft.com/download/7/7/6/7765A6A5-4B02-41DE-B7AF-067C92C581BD/50709.00/Silverlight.exe",
        ],
        "sha1": "6e7c5e763ec6dba646adec4a0bcbd88059750658",
    }, {
        "arch": "amd64",
        "version": "5.1.50709.0",
        "urls": [
            "https://download.microsoft.com/download/7/7/6/7765A6A5-4B02-41DE-B7AF-067C92C581BD/50709.00/Silverlight_x64.exe",
        ],
        "sha1": "0222ec109d882a612d65c8ef8daa04af2f72f8fa",
    }, {
        "arch": "x86",
        "version": "5.1.50905.0",
        "urls": [
            "https://download.microsoft.com/download/8/6/A/86AC5F63-A0C9-4868-8CC5-C653B189E4B6/50905.00/Silverlight.exe",
        ],
        "sha1": "97b56d4e390241ae1baabe65d41e4080270bcb1b",
    }, {
        "arch": "amd64",
        "version": "5.1.50905.0",
        "urls": [
            "https://download.microsoft.com/download/8/6/A/86AC5F63-A0C9-4868-8CC5-C653B189E4B6/50905.00/Silverlight_x64.exe",
        ],
        "sha1": "16712886955bab475549184015d425e3091a6357",
    }, {
        "arch": "x86",
        "version": "5.1.50906.0",
        "urls": [
            "https://download.microsoft.com/download/3/F/5/3F5B3DEC-A698-4B6A-8BB9-A1A554EA103C/50906.00/Silverlight.exe",
        ],
        "sha1": "7a811b061f742479d2e25ce5ac1a9908f5745bf1",
    }, {
        "arch": "amd64",
        "version": "5.1.50906.0",
        "urls": [
            "https://download.microsoft.com/download/3/F/5/3F5B3DEC-A698-4B6A-8BB9-A1A554EA103C/50906.00/Silverlight_x64.exe",
        ],
        "sha1": "d10a077bf0043a846f2f2a75962c2e068a060f10",
    }]

    def run(self):
        self.upload_dependency("C:\\setup.exe")
        self.a.execute("C:\\setup.exe /q /doNotRequireDRMPrompt /noupdate")
        self.a.remove("C:\\setup.exe")
