# Copyright (C) 2014-2016 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

from vmcloak.abstract import Dependency


class Python(Dependency):
    name = "python"
    default = "2.7.6"
    exes = [
        {
            "arch": "amd64",
            "version": "2.7.6",
            "urls": [
                "https://www.python.org/ftp/python/2.7.6/python-2.7.6.amd64.msi",
            ],
            "sha1": "405290650b85042f389a8fbf06549c35458afd05",
            "filename": "python-2.7.6.amd64.msi",
            "window_name": "Python 2.7.6 (64-bit) Setup",
            "install_path": "C:\\Python27",
        },
        {
            "arch": "x86",
            "version": "2.7.6",
            "urls": [
                "https://www.python.org/ftp/python/2.7.6/python-2.7.6.msi",
                "https://cuckoo.sh/vmcloak/python-2.7.6.msi",
            ],
            "sha1": "c5d71f339f7edd70ecd54b50e97356191347d355",
            "filename": "python-2.7.6.msi",
            "window_name": "Python 2.7.6 Setup",
            "install_path": "C:\\Python27",
        },
        {
            "arch": "amd64",
            "version": "2.7.13",
            "urls": [
                "https://www.python.org/ftp/python/2.7.13/python-2.7.13.amd64.msi",
            ],
            "sha1": "d9113142bae8829365c595735e1ad1f9f5e2894c",
            "filename": "python-2.7.13.amd64.msi",
            "window_name": "Python 2.7.13 (64-bit) Setup",
            "install_path": "C:\\Python27",
        },
        {
            "arch": "x86",
            "version": "2.7.13",
            "urls": [
                "https://www.python.org/ftp/python/2.7.13/python-2.7.13.msi",
            ],
            "sha1": "7e3b54236dbdbea8fe2458db501176578a4d59c0",
            "filename": "python-2.7.13.msi",
            "window_name": "Python 2.7.13 Setup",
            "install_path": "C:\\Python27",
        },
    ]

    def run(self):
        """There are no installation procedures for this dependency as it is
        setup by default when installing a new Virtual Machine. In the end,
        Python is required for running both the Agent as well as Cuckoo's
        Analyzer anyway."""

class Python27(Python, Dependency):
    """Backwards compatibility."""
    name = "python27"
    recommended = False
