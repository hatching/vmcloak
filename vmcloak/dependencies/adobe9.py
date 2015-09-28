# Copyright (C) 2014-2015 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import time

from vmcloak.abstract import Dependency

class Adobe9(Dependency):
    name = "adobe9"
    exes = [
        {
            "url": "http://cuckoo.sh/vmcloak/AdbeRdr90_en_US.exe",
            "sha1": "8faabd08289b9a88023f71136f13fc4bd3290ef0",
        },
    ]

    def run(self):
        self.upload_dependency("C:\\adobe9.exe")
        self.a.execute("C:\\adobe9.exe", async=True)

        # For some reason clicking buttons for Adobe9 is a bit random
        # sometimes so for now we resort to starting a couple background
        # clicking instances as well.
        self.a.click("Adobe Reader 9 - Setup", "&Next >")

        time.sleep(1)
        self.a.click_async("Adobe Reader 9 - Setup", "&Next >")

        time.sleep(1)
        self.a.click_async("Adobe Reader 9 - Setup", "&Next >")

        self.a.click("Adobe Reader 9 - Setup", "&Install")

        time.sleep(1)
        self.a.click_async("Adobe Reader 9 - Setup", "&Install")

        self.a.click("Adobe Reader 9 - Setup", "&Finish")

        # Wait until adobe9.exe is no longer running.
        self.wait_process_exit("adobe9.exe")

        self.a.remove("C:\\adobe9.exe")
