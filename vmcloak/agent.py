# Copyright (C) 2014-2015 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import requests

from vmcloak.misc import wait_for_host

class Agent(object):
    def __init__(self, ipaddr, port):
        self.ipaddr = ipaddr
        self.port = port

    def get(self, method, *args, **kwargs):
        """Wrapper around GET requests."""
        url = "http://%s:%s%s" % (self.ipaddr, self.port, method)
        return requests.get(url, *args, **kwargs)

    def post(self, method, **kwargs):
        """Wrapper around POST requests."""
        url = "http://%s:%s%s" % (self.ipaddr, self.port, method)
        return requests.post(url, data=kwargs)

    def postfile(self, method, files, **kwargs):
        """Wrapper around POST requests with attached files."""
        url = "http://%s:%s%s" % (self.ipaddr, self.port, method)
        return requests.post(url, files=files, data=kwargs)

    def ping(self):
        return self.get("/")

    def static_ip(self, ipaddr, netmask, gateway):
        """Change the IP address of this machine."""
        command = \
            "netsh interface ip set address " \
            "name=\"Local Area Connection\" static " \
            "%s %s %s 1" % (ipaddr, netmask, gateway)
        try:
            requests.post("http://%s:%s/execute" % (self.ipaddr, self.port),
                          data={"command": command}, timeout=10)
        except requests.exceptions.ReadTimeout:
            pass

        # Now wait until the Agent is reachable on the new IP address.
        wait_for_host(ipaddr, self.port)
        self.ipaddr = ipaddr
