# Copyright (C) 2014-2018 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import io
import logging
import requests

from vmcloak.misc import wait_for_agent

log = logging.getLogger(__name__)

class Agent(object):
    def __init__(self, ipaddr, port):
        self.ipaddr = ipaddr
        self.port = port

    def get(self, method, *args, **kwargs):
        """Wrapper around GET requests."""
        url = "http://%s:%s%s" % (self.ipaddr, self.port, method)
        session = requests.Session()
        session.trust_env = False
        session.proxies = None
        return session.get(url, *args, **kwargs)

    def post(self, method, **kwargs):
        """Wrapper around POST requests."""
        url = "http://%s:%s%s" % (self.ipaddr, self.port, method)
        session = requests.Session()
        session.trust_env = False
        session.proxies = None
        return session.post(url, data=kwargs)

    def postfile(self, method, files, **kwargs):
        """Wrapper around POST requests with attached files."""
        url = "http://%s:%s%s" % (self.ipaddr, self.port, method)
        session = requests.Session()
        session.trust_env = False
        session.proxies = None
        return session.post(url, files=files, data=kwargs)

    def ping(self):
        """Ping the machine."""
        return self.get("/", timeout=5)

    def environ(self, value=None, default=None):
        """Obtain one or all environment variable(s)."""
        environ = self.get("/environ").json()["environ"]
        return environ if value is None else environ.get(value, default)

    def execute(self, command, cucksync=False):
        """Execute a command."""
        log.debug("Executing command in VM: %s", command)
        if cucksync:
            return self.post("/execute", command=command, cucksync="true")
        else:
            resp = self.post("/execute", command=command).json()
            return {
                "exit_code": resp.get("exit_code"), "error": resp.get("error"),
                "stdout": resp.get("stdout"), "stderr": resp.get("stderr")
            }

    def execpy(self, filepath, cucksync=False):
        """Execute a Python file."""
        if cucksync:
            return self.post("/execpy", filepath=filepath, cucksync="true")
        else:
            return self.post("/execpy", filepath=filepath)

    def remove(self, path):
        """Remove a file or entire directory."""
        self.post("/remove", path=path)

    def extract(self, dirpath, zipfile):
        """Extract a zip file to folder."""
        zipfile = open(zipfile, "rb")
        self.postfile("/extract", {"zipfile": zipfile}, dirpath=dirpath)

    def shutdown(self):
        """Power off the machine."""
        # Use 1 second timer with cucksync to prevent the machine from shutting
        # down while a response is being sent or before it is sent.
        self.execute("shutdown -s -t 1", cucksync=True)

    def reboot(self):
        """Reboot the machine."""
        # Use 1 second timer with cucksync to prevent the machine from shutting
        # down while a response is being sent or before it is sent.
        self.execute("shutdown -r -t 1", cucksync=True)

    def kill(self):
        """Kill the Agent."""
        self.get("/kill")

    def killprocess(self, process_name, force=True):
        """Terminate a process."""
        cmd = f"taskkill /IM {process_name}"
        if force:
            cmd += " /F"
        self.execute(cmd)

    def hostname(self, hostname):
        """Assign a new hostname."""
        cmdline = "wmic computersystem where name=\"%(oldname)s\" " \
            "call rename name=\"%(newname)s\""
        args = dict(oldname=self.environ("COMPUTERNAME"), newname=hostname)

        # self.execute(cmdline % args, shell=True)
        self.execute(cmdline % args)

    def static_ip(self, ipaddr, netmask, gateway, interface):
        """Change the IP address of this machine."""
        command = (
            "netsh interface ip set address name=\"%s\" static %s %s %s 1"
        ) % (interface, ipaddr, netmask, gateway)
        log.debug("Executing command in VM: %s", command)
        try:
            session = requests.Session()
            session.trust_env = False
            session.proxies = None
            session.post(
                "http://%s:%s/execute" % (self.ipaddr, self.port),
                data={"command": command}, timeout=5
            )
        except requests.exceptions.ConnectionError:
            pass

        # Now wait until the Agent is reachable on the new IP address.
        self.ipaddr = ipaddr
        log.debug(
            f"Waiting for agent to be reachable on: {self.ipaddr}:{self.port}"
        )
        wait_for_agent(self)

    def dns_server(self, ipaddr):
        """Set the IP address of the DNS server."""
        command = \
            "netsh interface ip set dns " \
            "name=\"Local Area Connection\" static %s" % ipaddr
        self.execute(command)

    def upload(self, filepath, contents):
        """Upload a file to the Agent."""
        if isinstance(contents, str):
            contents = io.BytesIO(contents.encode())
        self.postfile("/store", {"file": contents}, filepath=filepath)

    def retrieve(self, filepath):
        """Retrieve a file from the Agent."""
        return self.post("/retrieve", filepath=filepath).content

    def click(self, window_title, button_name):
        """Identify a window by its title and click one of its buttons."""
        log.debug(
            "Clicking window '%s' button '%s'", window_title, button_name
        )
        self.execute(
            "C:\\vmcloak\\click.exe \"%s\" \"%s\"" %
            (window_title, button_name)
        )

    def click_async(self, window_title, button_name):
        """Identify a window by its title and click one of its buttons
        asynchronously. This is mostly used in cases where the click may or
        may not be required, leaving the clicking process hanging."""
        log.debug(
            "Clicking (async) window '%s' button '%s'",
            window_title, button_name
        )
        self.execute(
            "C:\\vmcloak\\click.exe \"%s\" \"%s\"" %
            (window_title, button_name), cucksync=True
        )

    def resolution(self, width, height):
        """Set the screen resolution of this Virtual Machine."""
        self.execute(
            "C:\\Python3\\python.exe C:\\vmcloak\\resolution.py %s %s" %
            (width, height)
        )
