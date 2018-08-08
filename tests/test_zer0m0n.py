# Copyright (C) 2017 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import hashlib

from vmcloak.dependencies.zer0m0n import Zer0m0n

def patch_file(method, filename):
    blob = open("tests/files/%s" % filename, "rb").read()
    return hashlib.md5(method(blob)).hexdigest()

def patch_winload(filename):
    return patch_file(Zer0m0n().patch_winload, filename)

def patch_ntoskrnl(filename):
    return patch_file(Zer0m0n().patch_ntoskrnl, filename)

def test_winload():
    assert patch_winload("winload.0x4ce7929c.exe") == "8f53e6483ef8af4ffacf48bbeb5b8c56"
    assert patch_ntoskrnl("ntoskrnl.0x4ce7951a.exe") == "d8b4c59189401cd87d72a0f361c441d5"
