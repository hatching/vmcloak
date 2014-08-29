#!/usr/bin/env python
# Copyright (C) 2014 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(
    name='VMCloak',
    version='0.1.0',
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
        'bin/vmcloak-deps',
        'bin/vmcloak-gethwconf',
    ],
    url='http://pypi.python.org/pypi/vmcloak/',
    license='docs/LICENSE.txt',
    description='Automated Virtual Machine Generation and Cloaking '
                'for Cuckoo Sandbox.',
    include_package_data=True,
    install_requires=[
        'lockfile',
        'sphinx',
        'sphinxcontrib-programoutput',
        'jinja2',  # Required on BSD systems for unknown reasons.
    ],
)
