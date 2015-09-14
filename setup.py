#!/usr/bin/env python
# Copyright (C) 2014-2015 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

from setuptools import setup


setup(
    name='VMCloak',
    version='0.2.13',
    author='Jurriaan Bremer',
    author_email='jurriaanbremer@gmail.com',
    packages=[
        'vmcloak',
        'vmcloak.data',
        'vmcloak.data.bootstrap',
        'vmcloak.data.hwconf',
    ],
    scripts=[
        'bin/vmcloak',
        'bin/vmcloak-bird',
        'bin/vmcloak-clone',
        'bin/vmcloak-deps',
        'bin/vmcloak-gethwconf',
        'bin/vmcloak-iptables',
        'bin/vmcloak-killvbox',
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
        # Libraries to build the documentation.
        'sphinx',

        # Required on BSD systems for unknown reasons.
        'jinja2',
    ],
)
