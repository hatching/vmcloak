# Copyright (C) 2014-2016 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import requests
import logging

from StringIO import StringIO

from vmcloak.misc import wait_for_host

log = logging.getLogger(__name__)

class Agent(object):
    def __init__(self, ipaddr, port):
        self.ipaddr = ipaddr
        self.port = port
        self._system = None
        self.ping()

    @property
    def system(self):
        if not self._system:
            self._system = self.get("/system").json()["system"].lower()
        return self._system

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
        """Ping the machine."""
        return self.get("/", timeout=5)

    def environ(self, value=None, default=None):
        """Obtain one or all environment variable(s)."""
        environ = self.get("/environ").json()["environ"]
        return environ if value is None else environ.get(value, default)

    def execute(self, command, async=False):
        """Execute a command."""
        if async:
            return self.post("/execute", command=command, async="true")
        else:
            return self.post("/execute", command=command)

    def remove(self, path):
        """Remove a file or entire directory."""
        self.post("/remove", path=path)

    def extract(self, dirpath, zipfile):
        """Extract a zip file to folder."""
        zipfile = open(zipfile, "rb")
        self.postfile("/extract", {"zipfile": zipfile}, dirpath=dirpath)

    def shutdown(self):
        """Power off the machine."""
        if self.system == "linux":
            self.execute("poweroff", async=True)
        else:
            self.execute("shutdown -s -t 0", async=True)

    def reboot(self):
        """Reboot the machine."""
        if self.system == 'linux':
            self.execute("reboot", async=True)
        else:
            self.execute("shutdown -r -t 0", async=True)

    def kill(self):
        """Kill the Agent."""
        self.get("/kill")

    def killprocess(self, process_name):
        """Terminate a process."""
        if self.system == "linux":
            self.execute("pkill -9 %s" % process_name)
        else:
            self.execute("taskkill /F /IM %s" % process_name)

    def hostname(self, hostname):
        """Assign a new hostname."""
        if self.system == 'linux':
            cmdline = "hostname %(newname)s; echo '%(newname)s' > /etc/hostname"
            args = dict(newname=hostname)
        else:
            cmdline = "wmic computersystem where name=\"%(oldname)s\" " \
                "call rename name=\"%(newname)s\""
            args = dict(oldname=self.environ("COMPUTERNAME"), newname=hostname)

        # self.execute(cmdline % args, shell=True)
        self.execute(cmdline % args)

    def static_ip(self, ipaddr, netmask, gateway, interface):
        """Change the IP address of this machine."""
        if self.system == 'linux':
            command = (
                "IFACE=`ip route ls | grep '^default' | cut -f 5 -d ' '`; export IFACE; ifconfig $IFACE %s netmask %s; route add default dev $IFACE"
            ) % (ipaddr, netmask, gateway)
        else:
            command = (
                "netsh interface ip set address name=\"%s\" static %s %s %s 1"
            ) % (interface, ipaddr, netmask, gateway)

        try:
            requests.post("http://%s:%s/execute" % (self.ipaddr, self.port),
                          data={"command": command}, timeout=5)
        except requests.exceptions.ReadTimeout:
            pass

        # Now wait until the Agent is reachable on the new IP address.
        wait_for_host(ipaddr, self.port)
        self.ipaddr = ipaddr

    def dns_server(self, ipaddr):
        """Set the IP address of the DNS server."""
        if self.system == "linux":
            command = "echo '%s' > /etc/resolv.conf" % (ipaddr,)
        else:
            command = \
                "netsh interface ip set dns " \
                "name=\"Local Area Connection\" static %s" % ipaddr
        self.execute(command)

    def upload(self, filepath, contents):
        """Upload a file to the Agent."""
        if isinstance(contents, basestring):
            contents = StringIO(contents)
        self.postfile("/store", {"file": contents}, filepath=filepath)

    def click(self, window_title, button_name, async=False):
        """Identify a window by its title and click one of its buttons.
           Async is mostly used in cases where the click may or
           may not be required, leaving the clicking process hanging."""
        if self.system == "windows":
            log.debug("Clicking window '%s' button '%s'", window_title, button_name)
            self.execute("C:\\vmcloak\\click.exe \"%s\" \"%s\"" % (
                window_title, button_name), async=async)
        else:
            log.warning("Cannot 'click' on non-windows platforms!")

    def click_async(self, window_title, button_name):
        self.click(window_title, button_name, async=True)

    def resolution(self, width, height):
        """Set the screen resolution of this Virtual Machine."""
        if self.system == "windows":
            self.execute("C:\\Python27\\python.exe C:\\vmcloak\\resolution.py "
                         "%s %s" % (width, height))
        else:
            log.warning("Cannot change resolution on non-windows platform")
