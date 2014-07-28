#!/usr/bin/env python
# Copyright (C) 2014 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import os
import logging
import shutil

from vmcloak.misc import ini_read_dict

log = logging.getLogger()

DEPS_DIR = os.path.join(os.getenv('HOME'), '.vmcloak', 'deps')



class DependencyWriter(object):
    def __init__(self, bootstrap_path):
        self.bootstrap = bootstrap_path
        self.repo = ini_read_dict(os.path.join(DEPS_DIR, 'repo.ini'))

        self.installed = []
        self.f = open(os.path.join(bootstrap_path, 'deps.bat'), 'wb')

    def add(self, dependency):
        if dependency not in self.repo:
            log.error('Dependency %s not found!', dependency)
            exit(1)

        if dependency in self.installed:
            log.debug('Dependency %s has already been handled.', dependency)
            return

        kw = self.repo[dependency]

        fname = kw.pop('filename')
        arguments = kw.pop('arguments', '')
        depends = kw.pop('dependencies', '')
        marker = kw.pop('marker', None)
        flags = []
        cmds = []

        for flag in kw.pop('flags', '').split():
            if flag.strip():
                flags.append(flag.strip())

        idx = 0
        while 'cmd%d' % idx in kw:
            cmds.append(kw.pop('cmd%d' % idx))
            idx += 1

        # Not used by us.
        kw.pop('description', None)

        if kw:
            log.error('Found one or more remaining value(s) in the '
                      'configuration, please it fix before continuing..')
            log.info('Remaining value(s): %s', kw)
            exit(1)

        for dep in depends.split():
            if dep.strip():
                self.add(dep.strip())

        self.installed.append(dependency)

        print>>self.f, 'echo Installing..', fname
        if marker:
            print>>self.f, 'if exist "%s" (' % marker
            print>>self.f, '  echo Dependency already installed!'
            print>>self.f, ') else ('

        if 'background' in flags:
            print>>self.f, '  start C:\\vmcloak\\deps\\%s' % fname, arguments
        else:
            print>>self.f, '  C:\\vmcloak\\deps\\%s' % fname, arguments

        for cmd in cmds:
            if cmd.startswith('click'):
                print>>self.f, '  C:\\%s' % cmd
            else:
                print>>self.f, '  %s' % cmd

        if marker:
            print>>self.f, ')'

        shutil.copy(os.path.join('deps', 'files', fname),
                    os.path.join(self.bootstrap, 'deps', fname))

    def write(self):
        self.f.close()
