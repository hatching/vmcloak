# Copyright (C) 2016-2018 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import time

from vmcloak.abstract import Dependency

class KB(Dependency):
    name = "kb"
    exes = [{
        "version": "2729094",
        "target": "win7x64",
        "urls": [
            "https://download.microsoft.com/download/6/C/A/6CA15546-A46C-4333-B405-AB18785ABB66/Windows6.1-KB2729094-v2-x64.msu",
            "https://cuckoo.sh/vmcloak/Windows6.1-KB2729094-v2-x64.msu",
        ],
        "sha1": "e1a3ecc5030a51711f558f90dd1db52e24ce074b",
    }, {
        "version": "2729094",
        "target": "win7x86",
        "urls": [
            "https://download.microsoft.com/download/B/6/B/B6BF1D9B-2568-406B-88E8-E4A218DEA90A/Windows6.1-KB2729094-v2-x86.msu",
            "https://cuckoo.sh/vmcloak/Windows6.1-KB2729094-v2-x86.msu",
        ],
        "sha1": "565e7f2a6562ace748c5b6165aa342a11c96aa98",
    }, {
        "version": "2731771",
        "target": "win7x64",
        "urls": [
            "https://download.microsoft.com/download/9/F/E/9FE868F6-A0E1-4F46-96E5-87D7B6573356/Windows6.1-KB2731771-x64.msu",
            "https://cuckoo.sh/vmcloak/Windows6.1-KB2731771-x64.msu",
        ],
        "sha1": "98dba6673cedbc2860c76b9686e895664d463347",
    }, {
        "version": "2731771",
        "target": "win7x86",
        "urls": [
            "https://download.microsoft.com/download/A/0/B/A0BA0A59-1F11-4736-91C0-DFCB06224D99/Windows6.1-KB2731771-x86.msu",
            "https://cuckoo.sh/vmcloak/Windows6.1-KB2731771-x86.msu",
        ],
        "sha1": "86675d2fd327b328793dc179727ce0ce5107a72e",
    }, {
        "version": "2533623",
        "target": "win7x64",
        "urls": [
            "https://download.microsoft.com/download/F/1/0/F106E158-89A1-41E3-A9B5-32FEB2A99A0B/Windows6.1-KB2533623-x64.msu",
            "https://cuckoo.sh/vmcloak/Windows6.1-KB2533623-x64.msu",
        ],
        "sha1": "8a59ea3c7378895791e6cdca38cc2ad9e83bebff",
    }, {
        "version": "2533623",
        "target": "win7x86",
        "urls": [
            "https://download.microsoft.com/download/2/D/7/2D78D0DD-2802-41F5-88D6-DC1D559F206D/Windows6.1-KB2533623-x86.msu",
            "https://cuckoo.sh/vmcloak/Windows6.1-KB2533623-x86.msu",
        ],
        "sha1": "25becc0815f3e47b0ba2ae84480e75438c119859",
    }, {
        "version": "2670838",
        "target": "win7x64",
        "urls": [
            "https://download.microsoft.com/download/1/4/9/14936FE9-4D16-4019-A093-5E00182609EB/Windows6.1-KB2670838-x64.msu",
            "https://cuckoo.sh/vmcloak/Windows6.1-KB2670838-x64.msu",
        ],
        "sha1": "9f667ff60e80b64cbed2774681302baeaf0fc6a6",
    }, {
        "version": "2670838",
        "target": "win7x86",
        "urls": [
            "https://download.microsoft.com/download/1/4/9/14936FE9-4D16-4019-A093-5E00182609EB/Windows6.1-KB2670838-x86.msu",
            "https://cuckoo.sh/vmcloak/Windows6.1-KB2670838-x86.msu",
        ],
        "sha1": "984b8d122a688d917f81c04155225b3ef31f012e",
    }, {
        "version": "2786081",
        "target": "win7x64",
        "urls": [
            "https://download.microsoft.com/download/1/8/F/18F9AE2C-4A10-417A-8408-C205420C22C3/Windows6.1-KB2786081-x64.msu",
            "https://cuckoo.sh/vmcloak/Windows6.1-KB2786081-x64.msu",
        ],
        "sha1": "dc63b04c58d952d533c40b185a8b555b50d47905",
    }, {
        "version": "2786081",
        "target": "win7x86",
        "urls": [
            "https://download.microsoft.com/download/4/8/1/481C640E-D3EE-4ADC-AA48-6D0ED2869D37/Windows6.1-KB2786081-x86.msu",
            "https://cuckoo.sh/vmcloak/Windows6.1-KB2786081-x86.msu",
        ],
        "sha1": "70122aca48659bfb8a06bed08cb7047c0c45c5f4",
    }, {
        "version": "2639308",
        "target": "win7x64",
        "urls": [
            "https://download.microsoft.com/download/9/1/C/91CC3B0D-F58B-4B36-941D-D810A8FF6805/Windows6.1-KB2639308-x64.msu",
            "https://cuckoo.sh/vmcloak/Windows6.1-KB2639308-x64.msu",
        ],
        "sha1": "67eedaf061e02d503028d970515d88d8fe95579d",
    }, {
        "version": "2639308",
        "target": "win7x86",
        "urls": [
            "https://download.microsoft.com/download/3/1/D/31DB4F4F-207D-416E-9A07-FBD9E431F9FB/Windows6.1-KB2639308-x86.msu",
            "https://cuckoo.sh/vmcloak/Windows6.1-KB2639308-x86.msu",
        ],
        "sha1": "96e09ef9caf3907a32315839086b9f576bb46459",
    }, {
        "version": "2834140",
        "target": "win7x64",
        "urls": [
            "https://download.microsoft.com/download/5/A/5/5A548BFE-ADC5-414B-B6BD-E1EC27A8DD80/Windows6.1-KB2834140-v2-x64.msu",
            "https://cuckoo.sh/vmcloak/Windows6.1-KB2834140-v2-x64.msu",
        ],
        "sha1": "3db9d9b3dc20515bf4b164821b721402e34ad9d6",
    }, {
        "version": "2834140",
        "target": "win7x86",
        "urls": [
            "https://download.microsoft.com/download/F/1/4/F1424AD7-F754-4B6E-B0DA-151C7CBAE859/Windows6.1-KB2834140-v2-x86.msu",
            "https://cuckoo.sh/vmcloak/Windows6.1-KB2834140-v2-x86.msu",
        ],
        "sha1": "b57c05e9da2c66e1bb27868c92db177a1d62b2fb",
    }, {
        "version": "2882822",
        "target": "win7x64",
        "urls": [
            "https://download.microsoft.com/download/6/1/4/6141BFD5-40FD-4148-A3C9-E355338A9AC8/Windows6.1-KB2882822-x64.msu",
            "https://cuckoo.sh/vmcloak/Windows6.1-KB2882822-x64.msu",
        ],
        "sha1": "ec92821f6ee62ac9d2f74e847f87be0bf9cfcb31",
    }, {
        "version": "2882822",
        "target": "win7x86",
        "urls": [
            "https://download.microsoft.com/download/7/C/E/7CE5D2A0-3A08-427E-9AA9-8A79E47B87B9/Windows6.1-KB2882822-x86.msu",
            "https://cuckoo.sh/vmcloak/Windows6.1-KB2882822-x86.msu",
        ],
        "sha1": "7fab5b9ca9b5c2395b505d1234ee889941bfb151",
    }, {
        "version": "2888049",
        "target": "win7x64",
        "urls": [
            "https://download.microsoft.com/download/4/1/3/41321D2E-2D08-4699-A635-D9828AADB177/Windows6.1-KB2888049-x64.msu",
            "https://cuckoo.sh/vmcloak/Windows6.1-KB2888049-x64.msu",
        ],
        "sha1": "fae6327b151ae04b56fac431e682145c14474c69",
    }, {
        "version": "2888049",
        "target": "win7x86",
        "urls": [
            "https://download.microsoft.com/download/3/9/D/39D85CA8-7BF3-47C1-9031-FD6E51D8BBEB/Windows6.1-KB2888049-x86.msu",
            "https://cuckoo.sh/vmcloak/Windows6.1-KB2888049-x86.msu",
        ],
        "sha1": "65b4c7a5773fab177d20c8e49d773492e55e8d76",
    }, {
        "version": "2819745",
        "target": "win7x64",
        "url": "https://cuckoo.sh/vmcloak/Windows6.1-KB2819745-x64-MultiPkg.msu",
        "sha1": "5d40d059b9ea7f1d596f608a07cca49e4537dc15",
    }, {
        "version": "2819745",
        "target": "win7x86",
        "url": "https://cuckoo.sh/vmcloak/Windows6.1-KB2819745-x86-MultiPkg.msu",
        "sha1": "378bd9f96b8c898b86bb0c0b92f2c9c000748c5e",
    }, {
        "version": "3109118",
        "target": "win7x64",
        "url": "https://cuckoo.sh/vmcloak/Windows6.1-KB3109118-v4-x64.msu",
        "sha1": "ae0cac3e0571874dbc963dabbfa7d17d45db582c",
    }, {
        "version": "3109118",
        "target": "win7x86",
        "url": "https://cuckoo.sh/vmcloak/Windows6.1-KB3109118-v4-x86.msu",
        "sha1": "378bd9f96b8c898b86bb0c0b92f2c9c000748c5e",
    }]

    def run(self):
        self.upload_dependency("C:\\setup.msu")
        self.a.execute("sc config wuauserv start= auto")
        time.sleep(1)
        self.a.execute("wusa.exe C:\\setup.msu /quiet /norestart")

        self.a.remove("C:\\setup.msu")

        self.a.execute("sc config wuauserv start= disabled")
        self.a.execute("net stop wuauserv")
