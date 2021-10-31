# Copyright (C) 2018 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

from vmcloak.abstract import Dependency

WMIC = "C:\\Windows\\sysnative\\wbem\\wmic.exe"
BCDEDIT = "C:\\Windows\\sysnative\\bcdedit.exe"


class BootPolicy(Dependency):
    name = "bootpolicy"
    description = "Remove the 30 second timeout when starting a VM after hard poweroff"

    # Also enable debug mode
    debug = "0"

    def run(self):
        if self.debug == "1":
            self.a.execute("%s /debug on" % BCDEDIT)
            self.a.execute("%s RecoverOS set AutoReboot = false" % WMIC)
            # Disable memory dump
            self.a.execute("%s RecoverOS set DebugInfoType = 0" % WMIC)

        self.a.execute("%s /timeout 1" % BCDEDIT)
        self.a.execute("%s /set {current} bootstatuspolicy ignoreallfailures" % BCDEDIT)
