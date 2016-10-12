# Copyright (C) 2016 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import pytest
import sys

from vmcloak.paths import get_path

@pytest.mark.skipif(sys.platform != "linux2", reason="Not Linux")
def test_path1():
    assert get_path("vboxmanage") == "/usr/bin/VBoxManage"

@pytest.mark.skipif(sys.platform != "Darwin", reason="Not Mac OS X")
def test_path2():
    assert get_path("vboxmanage") == "/usr/local/bin/VBoxManage"
