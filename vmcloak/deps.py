#!/usr/bin/env python
# Copyright (C) 2014-2015 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

from __future__ import absolute_import
import logging
import os
import shutil
import subprocess
import urlparse

from vmcloak.misc import ini_read_dict, sha1_file
from vmcloak.paths import get_path

log = logging.getLogger(__name__)

class DependencyManager(object):
    FILES = 'conf.ini', 'repo.ini', 'hashes.txt'

    def __init__(self, deps_directory=None, deps_repository=None):
        self.conf = {}
        self.repo = {}

        self.deps_directory = deps_directory
        self.deps_repository = deps_repository

        self._load_config()

    def _read_conf_file(self, path):
        ret = {}
        for line in open(path, 'rb'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            key, value = line.split('=', 1)
            ret[key.strip()] = value.strip()
        return ret

    def _load_config(self):
        if os.path.isdir(self.deps_directory) and not self.repo:
            self.conf = \
                ini_read_dict(os.path.join(self.deps_directory, 'conf.ini'))
            self.repo = \
                ini_read_dict(os.path.join(self.deps_directory, 'repo.ini'))

            self.hashes = self._read_conf_file(
                os.path.join(self.deps_directory, 'hashes.txt'))

            files_dir = os.path.join(self.deps_directory, 'files')
            if not os.path.isdir(files_dir):
                os.mkdir(files_dir)

    def _wget(self, filename, url=None, subdir=None):
        if subdir is None:
            path = os.path.join(self.deps_directory, filename)
        else:
            path = os.path.join(self.deps_directory, subdir, filename)

        if url is None:
            url = urlparse.urljoin(self.deps_repository, filename)

        args = get_path('wget'), '-O', path, url, '--no-check-certificate'
        subprocess.check_call(args)

    def init(self, bitsize_64):
        """Initializes the dependency repository."""
        self.bitsize_64 = bitsize_64
        if not os.path.isdir(self.deps_directory):
            os.mkdir(self.deps_directory)
            try:
                log.info('Cloning vmcloak-deps.')
                for fname in self.FILES:
                    self._wget(fname)
            except subprocess.CalledProcessError as e:
                log.error('Error cloning vmcloak-deps: %s.', e)
                return False

        self._load_config()
        return True

    def update(self):
        """Updates the dependency repository."""
        if not self._check():
            return False

        try:
            log.info('Updating vmcloak-deps.')
            for fname in self.FILES:
                self._wget(fname)
        except subprocess.CalledProcessError as e:
            log.error('Error updating the vmcloak-deps repository: %s', e)
            return False

        return True

    def available(self, dependency):
        """Checks whether a dependency is available and whether its integrity
        is correct."""
        self._load_config()

        if dependency not in self.repo:
            log.info('No such dependency: %s.', dependency)
            return False

        if self.bitsize_64 and 'filename64' in self.repo[dependency]:
            fname = self.repo[dependency]['filename64']
        else:
            fname = self.repo[dependency]['filename']

        filepath = os.path.join(self.deps_directory, 'files', fname)

        if not os.path.exists(filepath):
            return False

        sha1 = sha1_file(filepath)
        if sha1 != self.hashes[fname]:
            log.warning('File %s of dependency %r downloaded with '
                        'an incorrect sha1.', fname, dependency)
            os.unlink(filepath)
            return False

        return True

    def fetch(self, dependency):
        """Fetch a single dependency."""
        if not self._check():
            return False

        self._load_config()

        if dependency not in self.repo:
            log.warning('No such dependency: %s.', dependency)
            return False

        info = self.repo[dependency]

        if self.bitsize_64 and 'filename64' in self.repo[dependency]:
            fname = self.repo[dependency]['filename64']
        else:
            fname = self.repo[dependency]['filename']

        if self.available(dependency):
            log.info('Dependency %r has already been fetched.', dependency)
            return True

        url = self.conf['vmcloak-files']['raw'] % info['filename']

        try:
            log.debug('Fetching dependency %r: %s.', dependency, fname)
            self._wget(fname, url=url, subdir='files')
        except subprocess.CalledProcessError as e:
            log.warning('Error downloading %s: %s.', info['filename'], e)
            return False

        if not self.available(dependency):
            return False

        return True

    def _check(self):
        """Checks whether the dependency repository has been initialized."""
        if not os.path.isdir(self.deps_directory):
            log.debug('Initializing the vmcloak-deps repository.')
            self.init()
            return False

        return True

class DependencyWriter(object):
    def __init__(self, dm, bootstrap_path, bitsize_64):
        self.bootstrap = bootstrap_path
        self.bitsize_64 = bitsize_64

        self.installed = []
        self.f = open(os.path.join(bootstrap_path, 'deps.bat'), 'wb')

        self.dm = dm

        # Make sure the dependency repository is available.
        self.dm.init(self.bitsize_64)

        # Copy the repository information from the dependency manager.
        self.repo = self.dm.repo

    def add(self, dependency):
        if dependency not in self.repo:
            log.error('Dependency %s not found!', dependency)
            return False

        if dependency in self.installed:
            log.debug('Dependency %s has already been handled.', dependency)
            return True

        if not self.dm.available(dependency):
            if not self.dm.fetch(dependency):
                return False

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
            if self.bitsize_64 and 'cmd%d_64' % idx in kw:
                cmds.append(kw.pop('cmd%d_64' % idx))
            else:
                cmds.append(kw.pop('cmd%d' % idx))

            kw.pop('cmd%d' % idx, None)
            kw.pop('cmd%d_64' % idx, None)
            idx += 1

        # Not used by us.
        kw.pop('description', None)

        # If this is a 64-bit OS and there's a 64-bit installer available,
        # then use it.
        if self.bitsize_64 and kw.get('filename64'):
            fname = kw.pop('filename64')
        else:
            kw.pop('filename64', None)

        if kw:
            log.error('Found one or more remaining value(s) in the '
                      'configuration, please it fix before continuing..')
            log.info('Remaining value(s): %s', kw)
            exit(1)

        for dep in depends.split():
            if dep.strip():
                self.add(dep.strip())

        log.debug("Added dependency %r (filename %r).", dependency, fname)

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
                print>>self.f, '  C:\\vmcloak\\%s' % cmd
            else:
                print>>self.f, '  %s' % cmd

        if marker:
            print>>self.f, ')'

        if not os.path.isdir(os.path.join(self.bootstrap, 'deps')):
            os.mkdir(os.path.join(self.bootstrap, 'deps'))

        shutil.copy(os.path.join(self.dm.deps_directory, 'files', fname),
                    os.path.join(self.bootstrap, 'deps', fname))
        return True

    def write(self):
        self.f.close()
