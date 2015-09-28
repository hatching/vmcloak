# Copyright (C) 2014-2015 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

from vmcloak.abstract import Dependency

class DnsServer(Dependency):
    name = "dns"

    def run(self):
        self.a.dns_server(self.version)
