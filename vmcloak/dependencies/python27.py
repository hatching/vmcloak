# Copyright (C) 2014-2016 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

from vmcloak.abstract import Dependency

class Python27(Dependency):
    name = "python27"
    exes = [
        {
            "url": "https://cuckoo.sh/vmcloak/python-2.7.6.msi",
            "sha1": "c5d71f339f7edd70ecd54b50e97356191347d355",
        },
    ]

    def run(self):
        """There are no installation procedures for this dependency as it is
        setup by default when installing a new Virtual Machine. In the end,
        Python is required for running both the Agent as well as Cuckoo's
        Analyzer anyway."""
