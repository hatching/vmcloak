#!/usr/bin/env python
"""Script that copies all files from one directory to a lowercase directory."""
import os
import shutil
import sys


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print 'Usage: python %s <src> <dst>' % sys.argv[0]
        exit(1)

    prefix = len(sys.argv[1])
    for dirpath, dirnames, filenames in os.walk(sys.argv[1]):
        for dirname in dirnames:
            os.mkdir(os.path.join(sys.argv[2],
                                  dirpath[prefix+1:].lower(),
                                  dirname.lower()))

        for fname in filenames:
            path = os.path.join(dirpath, fname)[prefix+1:]
            shutil.copyfile(os.path.join(sys.argv[1], path),
                            os.path.join(sys.argv[2], path.lower()))
