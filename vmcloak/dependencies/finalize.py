# Copyright (C) 2021 Hatching B.V.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import logging

from vmcloak.abstract import Dependency

log = logging.getLogger(__name__)

_finalize_windows_ps = """
Set-Service trustedinstaller -StartupType Disabled
Set-Service wuauserv -StartupType Disabled
Get-Service clr_optimization_v* | Set-Service -StartupType Disabled
"""

class Finalize(Dependency):
    name = "finalize"

    def _finalize_windows(self):
        log.debug(
            "Disabling trustedinstaller, wuauserv, and clr optimization "
            "services"
        )
        self.run_powershell_strings(_finalize_windows_ps)

    def run(self):
        if self.i.name in ("win10x64", "win7x64", "win7x86"):
            self._finalize_windows()
