# Copyright (C) 2018 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import os.path

from vmcloak.abstract import Dependency
from vmcloak.constants import VMCLOAK_ROOT

# TODO Following only works on 32-bit Python versions.
REG = "C:\\Windows\\sysnative\\reg.exe"
RUN = "HKEY_LOCAL_MACHINE\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"

class Modified(Dependency):
    name = "modified"
    description = "Add the agent for Cuckoo Modified"

    bind_ip = "0.0.0.0"
    bind_port = "8001"

    def run(self):
        # Usage (changing port): "vmcloak install master modified:8002".
        port = self.version or self.bind_port

        agent = os.path.join(VMCLOAK_ROOT, "data", "modified_agent.py")
        self.a.upload("C:\\modified_agent.py", open(agent, "rb").read())

        # Use same Python instance as main agent.
        r = self.a.execute("%s query %s /v Agent" % (REG, RUN))
        python = None
        lines = r.json()["stdout"].split("\r\n")
        for line in lines:
            parts = line.split()
            if parts[:2] == ["Agent", "REG_SZ"]:
                python = parts[2]
                break
        if not python:
            raise ValueError("Could not determine Python interpreter to use")

        cmd = "%s C:\\modified_agent.py %s %s" % (python, self.bind_ip, port)
        self.a.execute(
            '%s add %s /v AgentModified /t REG_SZ /d "%s" /f' %
            (REG, RUN, cmd)
        )
