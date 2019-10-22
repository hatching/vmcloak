# Copyright (C) 2019 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

from vmcloak.abstract import Dependency

class ACPIShutdown(Dependency):
    """Tells Windows that to do if an ACPI shutdown signal (power button) is
    sent. These settings tell Windows to shut down."""
    name = "acpishutdown"

    def run(self):
        # Tell Windows to shut down if the power button is clicked when it
        # is running on the battery
        self.a.execute(
            "c:\\Windows\\System32\\powercfg.exe "
            "-setdcvalueindex SCHEME_CURRENT "
            "4f971e89-eebd-4455-a8de-9e59040e7347 "
            "7648efa3-dd9c-4e3e-b566-50f929386280 3"
        )
        # Tell Windows to shut down if the power button is clicked when it is
        # not running from the battery
        self.a.execute(
            "c:\\Windows\\System32\\powercfg.exe "
            "-setacvalueindex SCHEME_CURRENT "
            "4f971e89-eebd-4455-a8de-9e59040e7347 "
            "7648efa3-dd9c-4e3e-b566-50f929386280 3"
        )
