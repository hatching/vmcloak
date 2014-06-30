from ConfigParser import ConfigParser
import os.path
import shutil


DEPS = []


def add_dependency(f, deps_repo, dependency):
    conf = ConfigParser()
    conf.read(deps_repo)

    d = dependency.strip()
    if d not in conf.sections():
        print '[-] Dependency %s not found!' % d
        exit(1)

    kw = dict(conf.items(d))
    fname = kw.pop('filename')
    arguments = kw.pop('arguments', '')
    depends = kw.pop('dependencies', None)
    marker = kw.pop('marker', None)
    flags = []
    cmds = []

    for flag in kw.pop('flags', '').split(','):
        if flag.strip():
            flags.append(flag.strip())

    idx = 0
    while 'cmd%d' % idx in kw:
        cmds.append(kw.pop('cmd%d' % idx))
        idx += 1

    # Not used by us.
    kw.pop('description', None)

    if kw:
        print '[-] Found an unused value in the configuration,'
        print '[-] please fix before continuing..'
        print '[-] Remaining values:', kw
        exit(1)

    if depends:
        for dep in depends.split(','):
            add_dependency(f, deps_repo, dep)

    if d not in DEPS:
        DEPS.append(d)

        print>>f, 'echo Installing..', fname
        if marker:
            print>>f, 'if exist "%s" (' % marker
            print>>f, 'echo Dependency already installed!'
            print>>f, ') else ('

        if 'background' in flags:
            print>>f, 'start C:\\dependencies\\%s' % fname, arguments
        else:
            print>>f, 'C:\\dependencies\\%s' % fname, arguments

        for cmd in cmds:
            if cmd.startswith('click'):
                print>>f, 'C:\\%s' % cmd
            else:
                print>>f, cmd

        if marker:
            print>>f, ')'

        shutil.copy(os.path.join('deps', 'files', fname),
                    os.path.join('bootstrap', 'dependencies', fname))
