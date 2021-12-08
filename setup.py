# Copyright (C) 2014-2018 Jurriaan Bremer.
# Copyright (C) 2018-2021 Hatching B.V.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

from setuptools import setup

setup(
    name="VMCloak",
    version="1.0",
    author="Hatching B.V.",
    author_email="info@hatching.io",
    url="https://github.com/hatching/vmcloak",
    python_requires=">=3.6",
    packages=[
        "vmcloak",
        "vmcloak.data",
        "vmcloak.data.bootstrap",
        "vmcloak.data.hwconf",
    ],
    scripts=[
        # "bin/vmcloak-gethwconf",
        "bin/vmcloak-iptables",
        # "bin/vmcloak-killvbox",
        # "bin/vmcloak-removevms",
        # "bin/vmcloak-vboxnet0",
        "bin/vmcloak-qemubridge"
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
        "click",
        "jinja2",
        "pefile>=2019.4.18, <2019.5.0"
        "pyyaml>=5.1",
        "sqlalchemy>=1.4, <1.5",
        "alembic>=1.7.4, <1.8",
        "requests>=2.22.0, <3",
        "psutil>=5.4.8, <6"
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
        "docs": [
            "sphinx",
            "sphinx-rtd-theme"
        ]
    },
)
