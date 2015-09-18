# Copyright (C) 2014-2015 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import requests

class Agent(object):
    def __init__(self, ipaddr, port):
        self.ipaddr = ipaddr
        self.port = port

    def get(self, method, *args, **kwargs):
        url = "http://%s:%s%s" % (self.ipaddr, self.port, method)
        return requests.get(url, *args, **kwargs)

    def post(self, method, **kwargs):
        url = "http://%s:%s%s" % (self.ipaddr, self.port, method)
        return requests.post(url, data=kwargs)

    def postfile(self, method, files, **kwargs):
        url = "http://%s:%s%s" % (self.ipaddr, self.port, method)
        return requests.post(url, files=files, data=kwargs)
