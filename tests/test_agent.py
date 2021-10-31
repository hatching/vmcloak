# Copyright (C) 2017 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

from vmcloak.agent import Agent

class TestAgent(object):
    def setup(self):
        self.a = Agent("localhost", 8000)

    def test_upload(self):
        def none(*args, **kwargs):
            pass

        self.a.postfile = none
        self.a.upload("/tmp/hello", "contents")
        self.a.upload("/tmp/hello", "contents")
