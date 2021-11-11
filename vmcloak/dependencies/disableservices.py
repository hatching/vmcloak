# Copyright (C) 2021 Hatching B.V.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import logging
from pathlib import Path

from vmcloak.abstract import Dependency
from vmcloak.exceptions import DependencyError

log = logging.getLogger(__name__)

class DisableServices(Dependency):
    name = "disableservices"
    must_reboot = True

    disable_scripts = {
        "win10": Path(
            Dependency.data_path, "win10", "scripts", "disableservices.ps1"
        ),
        "win7": Path(
            Dependency.data_path, "win7", "scripts", "disableservices.ps1"
        ),
    }

    def run(self):
        disable_script = self.disable_scripts.get(self.h.name)
        if not disable_script:
            raise DependencyError(
                f"OS: {self.h.name} has no service disable script available."
            )

        res = self.run_powershell_file(str(disable_script))
        exit_code = res.get("exit_code")
        if exit_code:
            log.debug(
                f"Service disable return non-zero exit code. {exit_code}. "
                f"Stderr={res.get('stderr')}. stdout={res.get('stdout')}. "
            )
