# Copyright (C) 2014-2015 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import logging

from vmcloak.abstract import Dependency
from vmcloak.exceptions import DependencyError

log = logging.getLogger(__name__)

class Resolution(Dependency):
    name = "resolution"

    def init(self):
        if not self.version or "x" not in self.version:
            log.error("Please specify a resolution.")
            raise DependencyError

        width, height = self.version.split("x")
        self.width, self.height = width, height

    def run(self):
        self.a.resolution(self.width, self.height)
