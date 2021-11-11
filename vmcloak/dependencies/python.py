# Copyright (C) 2015-2018 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

from vmcloak.abstract import Dependency

class Python(Dependency):
    name = "python"
    tags = ["python"]
    exes = [
        # {
        #     "arch": "x86",
        #     "version": "2.7.6",
        #     "urls": [
        #         "https://www.python.org/ftp/python/2.7.6/python-2.7.6.msi",
        #         "https://cuckoo.sh/vmcloak/python-2.7.6.msi",
        #     ],
        #     "sha1": "c5d71f339f7edd70ecd54b50e97356191347d355",
        #     "filename": "python-2.7.6.msi",
        #     "window_name": "Python 2.7.6 Setup"
        # }, {
        #     "arch": "x86",
        #     "version": "2.7.13",
        #     "urls": [
        #         "https://www.python.org/ftp/python/2.7.13/python-2.7.13.msi",
        #         "https://cuckoo.sh/vmcloak/python-2.7.13.msi",
        #     ],
        #     "sha1": "7e3b54236dbdbea8fe2458db501176578a4d59c0",
        #     "filename": "python-2.7.13.msi",
        #     "window_name": "Python 2.7.13 Setup"
        # },
        {
            "arch": "amd64",
            "version": "3.7.3",
            "target": "win7x64",
            "urls": [
                "https://www.python.org/ftp/python/3.7.3/python-3.7.3-amd64.exe",
            ],
            "sha1": "bd95399506f362e7618d4f6b5a429ebf44714585",
            "filename": "python-3.7.3-amd64.exe",
            "window_name": "Python 3.7.3 (64-bit) Setup",
            "install_path": "C:\\Python3"
        },
        {
            "arch": "amd64",
            "version": "3.10.0",
            "target": "win10x64",
            "urls": [
                "https://www.python.org/ftp/python/3.10.0/python-3.10.0-amd64.exe",
            ],
            "sha1": "3ee4e92a8ef94c70fb56859503fdc805d217d689",
            "filename": "python-3.10.0-amd64.exe",
            "window_name": "Python 3.10.0 (64-bit) Setup",
            "install_path": "C:\\Python3"
        }

    ]

    def run(self):
        """There are no installation procedures for this dependency as it is
        setup by default when installing a new Virtual Machine. In the end,
        Python is required for running both the Agent as well as Cuckoo's
        Analyzer anyway."""
