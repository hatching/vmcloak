# Copyright (C) 2016 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import os
import pytest
import tempfile

from vmcloak.swarm import Swarm
from vmcloak.exceptions import SwarmError

def f(filename):
    return Swarm(os.path.join("tests", "files", "%s.swarm" % filename))

def tmp(content):
    fd, filepath = tempfile.mkstemp()
    os.write(fd, content)
    os.close(fd)
    return filepath

def test_invalid():
    with pytest.raises(SwarmError):
        Swarm(tmp("")).load()

    with pytest.raises(SwarmError):
        Swarm(tmp("a:\nb")).load()

    with pytest.raises(SwarmError):
        Swarm(tmp("- foo\n- bar")).load()

    with pytest.raises(SwarmError):
        Swarm(tmp("a: b")).load()

    s = Swarm(tmp("""
dep1:
  - 1.0
  - 2.0

dep2:
  os:winxp:
    - 1.0
  os:win7x64:
    - 2.0

dep3:
  os:winxp:
    - serialkey: ABCD
      isopath: EFGH
      version: 1.2.3

vm1:
  os: winxp
  deps:
    - dep1
    - dep2
    - dep3:
      - version: 1.2.3

matrix:
  - vm1
"""))
    s.read_swarm()
    s.parse_matrix()
    assert s.machines == {
        "vm1": {
            "os": "winxp",
            "isomount": "/mnt/winxp",
            "deps": [
                [
                    {
                        "dependency": "dep1",
                        "os": None,
                        "version": "1.0",
                    },
                    {
                        "dependency": "dep1",
                        "os": None,
                        "version": "2.0",
                    },
                ],
                [
                    {
                        "dependency": "dep2",
                        "os": "winxp",
                        "version": "1.0",
                    },
                    {
                        "dependency": "dep2",
                        "os": "win7x64",
                        "version": "2.0",
                    },
                ],
                [
                    {
                        "dependency": "dep3",
                        "os": "winxp",
                        "version": "1.2.3",
                        "serialkey": "ABCD",
                        "isopath": "EFGH",
                    },
                ],
            ],
        },
    }
    s.interpret_machines()
    assert s.machines == {
        "vm1": {
            "os": "winxp",
            "isomount": "/mnt/winxp",
            "deps": [
                [
                    {
                        "dependency": "dep1",
                        "os": None,
                        "version": "1.0",
                    },
                    {
                        "dependency": "dep1",
                        "os": None,
                        "version": "2.0",
                    },
                ],
                [
                    {
                        "dependency": "dep2",
                        "os": "winxp",
                        "version": "1.0",
                    },
                ],
                [
                    {
                        "dependency": "dep3",
                        "os": "winxp",
                        "version": "1.2.3",
                        "serialkey": "ABCD",
                        "isopath": "EFGH",
                    },
                ],
            ],
        },
    }

    s = Swarm(tmp("""
matrix:
  winxp0:
    os: winxp
    count: 20
"""))
    s.read_swarm()
    s.parse_matrix()
    assert s.machines == {
        "winxp0": {
            "os": "winxp",
            "isomount": "/mnt/winxp",
            "count": 20,
            "deps": [],
        },
    }
