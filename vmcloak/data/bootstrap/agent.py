# Copyright (C) 2010-2014 Cuckoo Foundation.
# This file is part of Cuckoo Sandbox - http://www.cuckoosandbox.org
# See the file 'docs/LICENSE' for copying permission.

import json
import os
import platform
import random
import socket
import string
import sys
import time
import subprocess
from ConfigParser import RawConfigParser
from SimpleXMLRPCServer import SimpleXMLRPCServer
from StringIO import StringIO
from _winreg import CreateKeyEx, DeleteValue, SetValueEx
from _winreg import HKEY_LOCAL_MACHINE, KEY_ALL_ACCESS, REG_SZ
from zipfile import ZipFile

BIND_IP = "0.0.0.0"
BIND_PORT = 8000

STATUS_INIT = 0x0001
STATUS_RUNNING = 0x0002
STATUS_COMPLETED = 0x0003
STATUS_FAILED = 0x0004
CURRENT_STATUS = STATUS_INIT

ERROR_MESSAGE = ""
ANALYZER_FOLDER = ""
RESULTS_FOLDER = ""

class ObjectDict(object):
    def __init__(self, d):
        self.__dict__ = d


class Agent:
    """Cuckoo agent, it runs inside guest."""

    def __init__(self):
        self.system = platform.system().lower()
        self.analyzer_path = ""
        self.analyzer_pid = 0

    def _initialize(self):
        global ERROR_MESSAGE
        global ANALYZER_FOLDER

        if not ANALYZER_FOLDER:
            random.seed(time.time())
            container = "".join(random.choice(string.ascii_lowercase) for x in range(random.randint(5, 10)))

            if self.system == "windows":
                system_drive = os.environ["SYSTEMDRIVE"] + os.sep
                ANALYZER_FOLDER = os.path.join(system_drive, container)
            elif self.system == "linux" or self.system == "darwin":
                ANALYZER_FOLDER = os.path.join(os.environ["HOME"], container)
            else:
                ERROR_MESSAGE = "Unable to identify operating system"
                return False

            try:
                os.makedirs(ANALYZER_FOLDER)
            except OSError as e:
                ERROR_MESSAGE = e
                return False

        return True

    def get_status(self):
        """Get current status.
        @return: status.
        """
        return CURRENT_STATUS

    def get_error(self):
        """Get error message.
        @return: error message.
        """
        return str(ERROR_MESSAGE)

    def add_malware(self, data, name):
        """Get analysis data.
        @param data: analysis data.
        @param name: file name.
        @return: operation status.
        """
        global ERROR_MESSAGE
        data = data.data

        if self.system == "windows":
            root = os.environ["TEMP"]
        elif self.system == "linux" or self.system == "darwin":
            root = "/tmp"
        else:
            ERROR_MESSAGE = "Unable to write malware to disk because of " \
                            "failed identification of the operating system"
            return False

        file_path = os.path.join(root, name)

        try:
            with open(file_path, "wb") as malware:
                malware.write(data)
        except IOError as e:
            ERROR_MESSAGE = "Unable to write malware to disk: {0}".format(e)
            return False

        return True

    def add_config(self, options):
        """Creates analysis.conf file from current analysis options.
        @param options: current configuration options, dict format.
        @return: operation status.
        """
        global ERROR_MESSAGE

        if type(options) != dict:
            return False

        config = RawConfigParser()
        config.add_section("analysis")

        try:
            for key, value in options.items():
                # Options can be UTF encoded.
                if isinstance(value, basestring):
                    try:
                        value = value.encode("utf-8")
                    except UnicodeEncodeError:
                        pass

                config.set("analysis", key, value)

            config_path = os.path.join(ANALYZER_FOLDER, "analysis.conf")

            with open(config_path, "wb") as config_file:
                config.write(config_file)
        except Exception as e:
            ERROR_MESSAGE = str(e)
            return False

        return True

    def add_analyzer(self, data):
        """Add analyzer.
        @param data: analyzer data.
        @return: operation status.
        """
        data = data.data

        if not self._initialize():
            return False

        try:
            zip_data = StringIO()
            zip_data.write(data)

            with ZipFile(zip_data, "r") as archive:
                archive.extractall(ANALYZER_FOLDER)
        finally:
            zip_data.close()

        self.analyzer_path = os.path.join(ANALYZER_FOLDER, "analyzer.py")

        return True

    def execute(self):
        """Execute analysis.
        @return: analyzer PID.
        """
        global ERROR_MESSAGE
        global CURRENT_STATUS

        if not self.analyzer_path or not os.path.exists(self.analyzer_path):
            return False

        try:
            proc = subprocess.Popen([sys.executable, self.analyzer_path],
                                    cwd=os.path.dirname(self.analyzer_path))
            self.analyzer_pid = proc.pid
        except OSError as e:
            ERROR_MESSAGE = str(e)
            return False

        CURRENT_STATUS = STATUS_RUNNING

        return self.analyzer_pid

    def complete(self, success=True, error="", results=""):
        """Complete analysis.
        @param success: success status.
        @param error: error status.
        """
        global ERROR_MESSAGE
        global CURRENT_STATUS
        global RESULTS_FOLDER

        if success:
            CURRENT_STATUS = STATUS_COMPLETED
        else:
            if error:
                ERROR_MESSAGE = str(error)

            CURRENT_STATUS = STATUS_FAILED

        RESULTS_FOLDER = results

        return True

if __name__ == "__main__":
    # Load the configuration values.
    s = ObjectDict(json.loads(sys.argv[1].decode('base64')))

    # Attempt to connect to the host machine.
    if hasattr(s, 'host_ip') and hasattr(s, 'host_port'):
        sock = None
        while not sock:
            try:
                sock = socket.create_connection((s.host_ip, s.host_port), 1)
            except socket.error:
                continue

        # Connect to the host machine. In case this is a bird, also
        # receive the new IP address, mask, and gateway.
        if s.vmmode == 'bird':
            # Retrieve the static IP address that we're supposed to use.
            ip_address, ip_mask, ip_gateway = sock.recv(256).split()

            sock.close()

            args = [
                "netsh", "interface", "ip", "set", "address",
                "name=Local Area Connection", "static",
                ip_address, ip_mask, ip_gateway, "1",
            ]
            subprocess.Popen(args).wait()
        else:
            sock.close()

    h = CreateKeyEx(HKEY_LOCAL_MACHINE,
                    "Software\\Microsoft\\Windows\\CurrentVersion\\Run",
                    0, KEY_ALL_ACCESS)

    if s.vmmode == 'normal':
        # In normal mode we remove the entry in Run from the registry.
        DeleteValue(h, 'Agent')
    else:
        # In bird mode we modify it so that the agent is aware that no new
        # IP address has to be assigned and goes straight to listening for
        # the host to connect.
        settings = dict(vmmode=s.vmmode)
        value = 'C:\\Python27\\Pythonw.exe "%s" %s' % (
            os.path.abspath(__file__), json.dumps(settings).encode('base64'))
        SetValueEx(h, 'Agent', 0, REG_SZ, value)

    h.Close()

    try:
        if not BIND_IP:
            BIND_IP = socket.gethostbyname(socket.gethostname())

        # Remove this file if we're in normal mode.
        if s.vmmode == 'normal':
            os.unlink(os.path.abspath(__file__))

        print("[+] Starting agent on %s:%s ..." % (BIND_IP, BIND_PORT))

        # Disable DNS lookup, by Scott D.
        def FakeGetFQDN(name=""):
            return name
        socket.getfqdn = FakeGetFQDN

        server = SimpleXMLRPCServer((BIND_IP, BIND_PORT), allow_none=True)
        server.register_instance(Agent())
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
