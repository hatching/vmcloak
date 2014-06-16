#!/usr/bin/env python
"""Script that modifies an INI file."""
import sys


def read_ini(path):
    ret, cur = {}, None
    for line in open(path, 'rb'):
        line = line.strip()
        if not line:
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
    return ret


def write_ini(path, data):
    f = open(path, 'wb')
    for key in sorted(data.keys()):
        print>>f, '[%s]' % key
        for value in sorted(data[key]):
            print>>f, value
        print>>f


if __name__ == '__main__':
    if len(sys.argv) != 5:
        print 'Usage: python %s <ini> <action> <section> <value>' % sys.argv[0]
        print 'Actions: add'
        exit(1)

    path, action, section, value = sys.argv[1:]
    data = read_ini(path)

    if action == 'add':
        if section not in data:
            data[section] = []

        data[section].append(value)

    write_ini(path, data)
