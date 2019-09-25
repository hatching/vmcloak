# Copyright (C) 2017 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

from vmcloak.agent import Agent
from vmcloak.misc import wait_for_host
import os
import ntpath

HOST = "192.168.122.3"
PORT = 8000

class TestAgent(object):
    def setup(self):
        self.a = Agent(HOST, PORT)
        assert self.a.environ()["SYSTEMDRIVE"] == "C:"
        #self.a.ping()

    def test_upload(self):
        def none(*args, **kwargs):
            pass

        self.a.postfile = none
        self.a.upload("/tmp/hello", "contents")
        self.a.upload("/tmp/hello", u"contents")

    def test_download(self, filename, path):
        data = self.a.retrieve(filename)
        name = ntpath.basename(filename)
        out = os.path.join(os.path.abspath(path), name)
        with open(out, 'wb') as f:
            f.write(data)

    def process_info(self):
        self.a.process_utilization()

    def hdd_info(self):
        self.a.disk_utilization()

    def memory_info(self):
        self.a.memory_utilization()

if __name__ == '__main__':
    wait_for_host(HOST, PORT)
    ta = TestAgent()
    ta.setup()
    #ta.test_download('C:\info.csv','.')
    #ta.process_info()
    #ta.hdd_info()
    #ta.memory_info()
