#!/usr/bin/env python
"""Script that modifies an INI file."""
import sys


def read_ini(path):
    ret, cur = {}, None
    buf = open(path, 'rb').read()

    # UTF-16 BOM
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
            ret[cur].append('%s = %s' % (a.strip(), b.strip()))
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


def ini_merge(data, ini2):
    mode, data2 = read_ini(ini2)
    for section in data2:
        for value in data2[section]:
            if section not in data:
                data[section] = [value]
                continue

            off = value.find('=')
            # TODO For now we only support key = value lines.
            if off < 0:
                continue

            for idx, row in enumerate(data[section]):
                if len(row) > off and row[:off] == value[:off]:
                    data[section][idx] = value
                    break
            else:
                data[section].append(value)


actions = {
    'add': (ini_add, 2),
    'merge': (ini_merge, 1),
}


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print 'Usage: python %s <ini> <action> [args..]' % sys.argv[0]
        print 'Actions:'
        print '    add <section> <value>'
        print '    merge <ini2>'
        exit(1)

    path, action = sys.argv[1:3]
    mode, data = read_ini(path)

    if action not in actions:
        print '%s is not a valid action' % action
        exit(1)

    if len(sys.argv) - 3 != actions[action][1]:
        print 'Invalid argument count', len(sys.argv) - 3,
        print 'instead of', actions[action][1]
        exit(1)

    actions[action][0](data, *sys.argv[3:])

    write_ini(path, mode, data)
