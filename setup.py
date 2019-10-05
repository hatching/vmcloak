# Copyright (C) 2014-2018 Jurriaan Bremer.
# Copyright (C) 2018-2019 Hatching B.V.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

from setuptools import setup

setup(
    name="VMCloak",
    version="0.4.8",
    author="Hatching B.V.",
    author_email="info@hatching.io",
    url="https://github.com/hatching/vmcloak",
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
        "sqlalchemy==1.3.9",
        "alembic>=1.0.7, <1.1",
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
