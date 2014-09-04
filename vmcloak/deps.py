#!/usr/bin/env python
# Copyright (C) 2014 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import logging
import os
import shutil
import subprocess

from vmcloak.misc import ini_read_dict, sha1_file
from vmcloak.paths import get_path

log = logging.getLogger()

DEPS_DIR = os.path.join(os.getenv('HOME'), '.vmcloak', 'deps')
DEPS_REPO = 'git://github.com/jbremer/vmcloak-deps.git'


class DependencyManager(object):
    def __init__(self):
        self.conf = {}
        self.repo = {}
        self.urls = {}
        self.files_repo = None
        self.files_dir = None

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
        if os.path.isdir(DEPS_DIR) and not self.repo:
            self.conf = ini_read_dict(os.path.join(DEPS_DIR, 'conf.ini'))
            self.repo = ini_read_dict(os.path.join(DEPS_DIR, 'repo.ini'))

            self.urls = self._read_conf_file(
                os.path.join(DEPS_DIR, 'urls.txt'))
            self.hashes = self._read_conf_file(
                os.path.join(DEPS_DIR, 'hashes.txt'))

            self.files_repo = self.conf['vmcloak-files']['git']
            self.files_dir = os.path.join(DEPS_DIR, 'files')

    def init(self):
        """Initializes the dependency repository."""
        if not os.path.isdir(DEPS_DIR):
            try:
                log.info('Cloning vmcloak-deps.')
                subprocess.check_call([get_path('git'), 'clone',
                                       DEPS_REPO, DEPS_DIR])
            except subprocess.CalledProcessError as e:
                log.error('Error cloning vmcloak-deps: %s.', e)
                return False

        self._load_config()

        if not os.path.isdir(self.files_dir):
            files_git = os.path.join(DEPS_DIR, 'files')

            try:
                log.info('Setting up vmcloak-files.')
                subprocess.check_call([get_path('git'), 'init', files_git])
                subprocess.check_call([get_path('git'), 'remote', 'add',
                                       'origin', self.files_repo],
                                      cwd=files_git)
            except subprocess.CalledProcessError as e:
                log.error('Error setting up vmcloak-files directory: %s', e)
                return False

        return True

    def update(self):
        """Updates the dependency repository."""
        if not self._check():
            return False

        try:
            log.info('Updating vmcloak-deps.')
            subprocess.check_call([get_path('git'), 'pull',
                                   'origin', 'master'],
                                  cwd=DEPS_DIR)
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

        fname = self.repo[dependency]['filename']
        filepath = os.path.join(DEPS_DIR, 'files', fname)

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

        filepath = os.path.join(DEPS_DIR, 'files', info['filename'])

        if self.available(dependency):
            log.info('Dependency %r has already been fetched.', dependency)
            return True

        if info['filename'] in self.urls:
            url = self.urls[info['filename']]

            # TODO We have to check the sha1sum of the downloaded binary.

            # Using wget seems the easiest as it shows the progress.
            # TODO Should we be using a Python library for this?
            try:
                log.debug('Fetching dependency %r: %s.',
                          dependency, info['filename'])
                subprocess.check_call([get_path('wget'), '-O', filepath, url,
                                       '--no-check-certificate'])
            except subprocess.CalledProcessError as e:
                log.warning('Error downloading %s: %s.', info['filename'], e)
                return False
        else:
            url = self.conf['vmcloak-files']['raw'] % info['filename']

            # Using wget seems the easiest as it shows the progress.
            # TODO Should we be using a Python library for this?
            try:
                log.debug('Fetching dependency %r: %s.',
                          dependency, info['filename'])
                subprocess.check_call([get_path('wget'), '-O', filepath, url,
                                       '--no-check-certificate'])
            except subprocess.CalledProcessError as e:
                log.warning('Error downloading %s: %s.', info['filename'], e)
                return False

        if not self.available(dependency):
            return False

        return True

    def fetch_all(self):
        """Fetch all dependencies at once."""
        if not self._check():
            return False

        self._load_config()

        try:
            log.info('Cloning the vmcloak-files repository.')
            subprocess.check_call([get_path('git'), 'pull',
                                   'origin', 'master'],
                                  cwd=self.files_dir)
        except subprocess.CalledProcessError as e:
            log.error('Error fetching vmcloak-files repository: %s', e)
            return False

        return True

    def _check(self):
        """Checks whether the dependency repository has been initialized."""
        if not os.path.isdir(DEPS_DIR):
            log.debug('Initializing the vmcloak-deps repository.')
            self.init()
            return False

        return True


class DependencyWriter(object):
    def __init__(self, bootstrap_path):
        self.bootstrap = bootstrap_path

        self.installed = []
        self.f = open(os.path.join(bootstrap_path, 'deps.bat'), 'wb')

        self.dm = DependencyManager()

        # Make sure the dependency repository is available.
        self.dm.init()

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
                print>>self.f, '  C:\\vmcloak\\%s' % cmd
            else:
                print>>self.f, '  %s' % cmd

        if marker:
            print>>self.f, ')'

        shutil.copy(os.path.join(DEPS_DIR, 'files', fname),
                    os.path.join(self.bootstrap, 'deps', fname))
        return True

    def write(self):
        self.f.close()
