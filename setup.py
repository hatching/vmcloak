#!/usr/bin/env python
# Copyright (C) 2014-2015 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

from setuptools import setup


setup(
    name='VMCloak',
    version="0.3.13",
    author='Jurriaan Bremer',
    author_email="jbr@cuckoo.sh",
    packages=[
        'vmcloak',
        'vmcloak.data',
        'vmcloak.data.bootstrap',
        'vmcloak.data.hwconf',
    ],
    scripts=[
        'bin/vmcloak',
        'bin/vmcloak-init',
        'bin/vmcloak-snapshot',
        'bin/vmcloak-install',
        'bin/vmcloak-modify',
        'bin/vmcloak-clone',
        'bin/vmcloak-gethwconf',
        'bin/vmcloak-iptables',
        'bin/vmcloak-killvbox',
        'bin/vmcloak-register',
        'bin/vmcloak-removevms',
        'bin/vmcloak-vboxnet0',
    ],
    url='http://vmcloak.org/',
    license='GPLv3',
    description='Automated Virtual Machine Generation and Cloaking '
                'for Cuckoo Sandbox.',
    include_package_data=True,
    package_data={
        'vmcloak.data': ['*.*'],
        'vmcloak.data.bootstrap': ['*.*'],
        'vmcloak.data.winxp': ['*.*'],
        'vmcloak.data.win7': ['*.*'],
    },
    install_requires=[
        'requests',
        'sqlalchemy',
        'sphinx',
        'jinja2',
    ],
)
