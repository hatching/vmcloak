# Copyright (C) 2021 Hatching B.V.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import logging
from pathlib import Path

from vmcloak.abstract import Dependency
from vmcloak.exceptions import DependencyError

log = logging.getLogger(__name__)

class OptimizeOS(Dependency):
    name = "optimizeos"
    must_reboot = True

    optimize_scripts = {
        "win10": Path(
            Dependency.data_path, "win10", "scripts", "optimize.ps1"
        ),
        "win7": Path(
            Dependency.data_path, "win7", "scripts", "optimize.ps1"
        ),
    }

    def run(self):
        optimize_script = self.optimize_scripts.get(self.h.name)
        if not optimize_script:
            raise DependencyError(
                f"OS: {self.h.name} has no optimizing script available."
            )

        res = self.run_powershell_file(str(optimize_script))
        if res.get("exit_code", 0):
            raise DependencyError(
                "OS optimize script returned non-zero exit code."
                f"exit_code={res.get('exit_code')}"
                f"stdout={res.get('stdout')}. "
                f"Stderr={res.get('stderr')}"
            )
