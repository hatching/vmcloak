#!/usr/bin/env python
# Copyright (C) 2014-2017 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

from setuptools import setup

setup(
    name="VMCloak",
    version="0.4.5a1",
    author="Jurriaan Bremer",
    author_email="jbr@cuckoo.sh",
    url="http://vmcloak.org/",
    packages=[
        "vmcloak",
        "vmcloak.data",
        "vmcloak.data.bootstrap",
        "vmcloak.data.hwconf",
    ],
    scripts=[
        "bin/vmcloak-gethwconf",
        "bin/vmcloak-iptables",
        "bin/vmcloak-killvbox",
        "bin/vmcloak-removevms",
        "bin/vmcloak-vboxnet0",
    ],
    entry_points={
        "console_scripts": [
            "vmcloak = vmcloak.main:main",
        ],
    },
    license="GPLv3",
    description="Automated Virtual Machine Generation and Cloaking "
                "for Cuckoo Sandbox.",
    include_package_data=True,
    package_data={
        "vmcloak.data": ["*.*"],
        "vmcloak.data.bootstrap": ["*.*"],
        "vmcloak.data.winxp": ["*.*"],
        "vmcloak.data.win7": ["*.*"],
    },
    install_requires=[
        "click==6.6",
        "jinja2==2.9.6",
        "pefile2==1.2.11",
        "pyyaml==3.12",
        "sqlalchemy==1.0.8",
    ],
    extras_require={
        ":sys_platform == 'win32'": [
            "requests>=2.13.0",
        ],
        ":sys_platform == 'darwin'": [
            "requests>=2.13.0",
        ],
        ":sys_platform == 'linux2'": [
            "requests[security]>=2.13.0",
        ],
    },
)
