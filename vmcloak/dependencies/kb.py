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
            "url": "http://download.microsoft.com/download/6/C/A/6CA15546-A46C-4333-B405-AB18785ABB66/Windows6.1-KB2729094-v2-x64.msu",
            "sha1": "e1a3ecc5030a51711f558f90dd1db52e24ce074b",
        },
        {
            "version": "2731771",
            "url": "http://download.microsoft.com/download/9/F/E/9FE868F6-A0E1-4F46-96E5-87D7B6573356/Windows6.1-KB2731771-x64.msu",
            "sha1": "98dba6673cedbc2860c76b9686e895664d463347",
        },
        {
            "version": "2533623",
            "url": "http://download.microsoft.com/download/F/1/0/F106E158-89A1-41E3-A9B5-32FEB2A99A0B/Windows6.1-KB2533623-x64.msu",
            "sha1": "8a59ea3c7378895791e6cdca38cc2ad9e83bebff",
        },
        {
            "version": "2670838",
            "url": "http://download.microsoft.com/download/1/4/9/14936FE9-4D16-4019-A093-5E00182609EB/Windows6.1-KB2670838-x64.msu",
            "sha1": "9f667ff60e80b64cbed2774681302baeaf0fc6a6",
        },
        {
            "version": "2786081",
            "url": "http://download.microsoft.com/download/1/8/F/18F9AE2C-4A10-417A-8408-C205420C22C3/Windows6.1-KB2786081-x64.msu",
            "sha1": "dc63b04c58d952d533c40b185a8b555b50d47905",
        },
    ]

    def run(self):
        self.upload_dependency("C:\\setup.msu")
        # wusa.exe needs wuauserv
        self.a.execute("sc config wuauserv start= auto")

        time.sleep(1)
        self.a.execute("wusa.exe C:\\setup.msu /quiet /norestart")

        self.a.remove("C:\\setup.msu")
        
        # disable wuauserv again
        self.a.execute("sc config wuauserv start= disabled")
        self.a.execute("net stop wuauserv")