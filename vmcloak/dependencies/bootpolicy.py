# Copyright (C) 2018 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.
# Chrome Dependency submitted by Jason Lewis.

from vmcloak.abstract import Dependency

class BootPolicy(Dependency):
    name = "bootpolicy"
    description = "Remove the 30 second timeout when starting a VM after hard poweroff"

    # Also enable debug mode
    debug = "0"

    def run(self):
        if self.debug == "1":
            self.a.execute("bcdedit /debug on")

        self.a.execute("bcdedit /set {current} bootstatuspolicy ignoreallfailures")
