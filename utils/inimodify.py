#!/usr/bin/env python
# Copyright (C) 2014 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

"""Script that modifies an INI file."""

import os.path
import sys


def read_ini(path):
    ret, cur = {}, None

    if os.path.exists(path):
        buf = open(path, 'rb').read()
    else:
        buf = ''

    # UTF-16 Byte Order Mark ("BOM")
    mode = 'utf16' if buf[:2] == '\xff\xfe' else 'latin1'
    buf = buf.decode(mode)

    for line in buf.split('\n'):
        line = line.strip()
        if not line or line[0] == ';':
            continue

        if line[0] == '[' and ']' in line:
            cur = line[1:line.index(']')]
            ret[cur] = []
            continue

        if '=' not in line:
            ret[cur].append(line)
        else:
            a, b = line.split('=', 1)
            ret[cur].append('%s=%s' % (a.strip(), b.strip()))
    return mode, ret


def write_ini(path, mode, data):
    lines = ['']
    for key in sorted(data.keys()):
        lines.append('[%s]' % key)
        for value in sorted(data[key]):
            lines.append(value)
        lines.append('')
    open(path, 'wb').write('\r\n'.join(lines).encode(mode))


def ini_add(data, section, value):
    if section not in data:
        data[section] = []

    if value not in data[section]:
        data[section].append(value)


def ini_delete(data, section, value):
    if section not in data:
        return

    for idx, row in enumerate(data[section]):
        if row == value:
            del data[section][idx]


def ini_merge(data, ini2, overwrite=True):
    mode, data2 = read_ini(ini2)
    for section in data2:
        for value in data2[section]:
            if section not in data:
                data[section] = [value]
                continue

            off = value.find('=')
            # If this line is not a key = value entry, then
            # we take the entire line.
            if off < 0:
                off = len(value)

            for idx, row in enumerate(data[section]):
                if len(row) > off and row[:off] == value[:off]:
                    if overwrite:
                        data[section][idx] = value
                    break
            else:
                data[section].append(value)


actions = {
    'add': (ini_add, 2),
    'delete': (ini_delete, 2),
    'merge': (ini_merge, 1),
}


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print 'Usage: python %s <ini> <action> [args..]' % sys.argv[0]
        print 'Actions:'
        print '    add <section> <value>'
        print '    delete <section> <value>'
        print '    merge <ini2> [--overwrite]'
        exit(1)

    path, action = sys.argv[1:3]
    mode, data = read_ini(path)

    if action not in actions:
        print '%s is not a valid action' % action
        exit(1)

    argc = actions[action][1]
    if len(sys.argv) - 3 < argc:
        print 'Invalid argument count', len(sys.argv) - 3,
        print 'instead of', argc
        exit(1)

    d = dict(overwrite=False)

    for arg in sys.argv[3+argc:]:
        assert arg[:2] == '--'
        d[arg[2:]] = True

    actions[action][0](data, *sys.argv[3:3+argc], **d)

    write_ini(path, mode, data)
