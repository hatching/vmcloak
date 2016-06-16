# Copyright (C) 2014-2016 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import os.path
import time

from vmcloak.abstract import Dependency

class KB(Dependency):
    name = "KB"
    exes = [
        {
            "version": "2729094",
            "target": "win7x64",
            "url": "http://download.microsoft.com/download/6/C/A/6CA15546-A46C-4333-B405-AB18785ABB66/Windows6.1-KB2729094-v2-x64.msu",
            "sha1": "e1a3ecc5030a51711f558f90dd1db52e24ce074b",
        },
        {
            "version": "2731771",
            "target": "win7x64",
            "url": "http://download.microsoft.com/download/9/F/E/9FE868F6-A0E1-4F46-96E5-87D7B6573356/Windows6.1-KB2731771-x64.msu",
            "sha1": "98dba6673cedbc2860c76b9686e895664d463347",
        },
        {
            "version": "2533623",
            "target": "win7x64",
            "url": "http://download.microsoft.com/download/F/1/0/F106E158-89A1-41E3-A9B5-32FEB2A99A0B/Windows6.1-KB2533623-x64.msu",
            "sha1": "8a59ea3c7378895791e6cdca38cc2ad9e83bebff",
        },
        {
            "version": "2670838",
            "target": "win7x64",
            "url": "http://download.microsoft.com/download/1/4/9/14936FE9-4D16-4019-A093-5E00182609EB/Windows6.1-KB2670838-x64.msu",
            "sha1": "9f667ff60e80b64cbed2774681302baeaf0fc6a6",
        },
        {
            "version": "2786081",
            "target": "win7x64",
            "url": "http://download.microsoft.com/download/1/8/F/18F9AE2C-4A10-417A-8408-C205420C22C3/Windows6.1-KB2786081-x64.msu",
            "sha1": "dc63b04c58d952d533c40b185a8b555b50d47905",
        },
        {
            "version": "2639308",
            "target": "win7x64",
            "url": "http://download.microsoft.com/download/9/1/C/91CC3B0D-F58B-4B36-941D-D810A8FF6805/Windows6.1-KB2639308-x64.msu",
            "sha1": "67eedaf061e02d503028d970515d88d8fe95579d",
        },
        {
            "version": "2834140",
            "target": "win7x64",
            "url": "https://download.microsoft.com/download/5/A/5/5A548BFE-ADC5-414B-B6BD-E1EC27A8DD80/Windows6.1-KB2834140-v2-x64.msu",
            "sha1": "3db9d9b3dc20515bf4b164821b721402e34ad9d6",
        },
        {
            "version": "2882822",
            "target": "win7x64",
            "url": "https://download.microsoft.com/download/6/1/4/6141BFD5-40FD-4148-A3C9-E355338A9AC8/Windows6.1-KB2882822-x64.msu",
            "sha1": "ec92821f6ee62ac9d2f74e847f87be0bf9cfcb31",
        },
        {
            "version": "2888049",
            "target": "win7x64",
            "url": "https://download.microsoft.com/download/4/1/3/41321D2E-2D08-4699-A635-D9828AADB177/Windows6.1-KB2888049-x64.msu",
            "sha1": "fae6327b151ae04b56fac431e682145c14474c69",
        },
    ]

    def run(self):
        self.upload_dependency("C:\\setup.msu")
        self.a.execute("sc config wuauserv start= auto")
        time.sleep(1)
        self.a.execute("wusa.exe C:\\setup.msu /quiet /norestart")

        self.a.remove("C:\\setup.msu")
        
        self.a.execute("sc config wuauserv start= disabled")
        self.a.execute("net stop wuauserv")
