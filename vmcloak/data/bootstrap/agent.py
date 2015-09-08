# Copyright (C) 2010-2014 Cuckoo Foundation.
# Copyright (C) 2014-2015 Jurriaan Bremer.
# This file is part of Cuckoo Sandbox - http://www.cuckoosandbox.org
# See the file 'docs/LICENSE' for copying permission.

import ctypes
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

def delete_key(rootkey, subkey, key):
    h = CreateKeyEx(rootkey, subkey, 0, KEY_ALL_ACCESS)
    DeleteValue(h, key)
    h.Close()

def update_key(rootkey, subkey, key, value):
    h = CreateKeyEx(rootkey, subkey, 0, KEY_ALL_ACCESS)
    SetValueEx(h, key, 0, REG_SZ, value)
    h.Close()

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

        # Remove this file and its associated registry key as we're about
        # to execute a sample.
        if s['vmmode'] != 'longterm':
            os.unlink(os.path.abspath(__file__))
            delete_key(HKEY_LOCAL_MACHINE,
                       'Software\\Microsoft\\Windows\\CurrentVersion\\Run',
                       'Agent')

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
    s = json.loads(sys.argv[1].decode('base64'))

    require_reboot = False

    # Attempt to connect to the host machine.
    if 'host_ip' in s and 'host_port' in s:
        sock = None
        while not sock:
            try:
                addr = s['host_ip'], s['host_port']
                sock = socket.create_connection(addr, 1)
            except socket.error:
                time.sleep(0.1)
                continue

        # Connect to the host machine. In case this is a bird, also
        # receive the new IP address, mask, and gateway.
        if s['vmmode'] == 'bird':
            # Retrieve the configuration for this clone.
            conf = json.loads(sock.recv(0x10000))

            # Update the VM mode to whatever vmcloak informs us to.
            s['vmmode'] = conf['vmmode']

            sock.close()

            args = [
                "netsh", "interface", "ip", "set", "address",
                "name=Local Area Connection", "static",
                conf["ip"], conf["netmask"], conf["gateway"], "1",
            ]
            subprocess.Popen(args).wait()

            if "hostname" in conf:
                # For excellent reasons (?) this only works when passed along
                # as shell command, so here we go.
                subprocess.call(
                    'wmic computersystem where name="%s" '
                    'call rename name="%s"' % (
                        os.getenv("COMPUTERNAME"), conf["hostname"]
                    ),
                    shell=True
                )

                require_reboot = True
        else:
            sock.close()

        del s['host_ip']
        del s['host_port']

    # Update the registry to reflect any changes to IP addresses, i.e., the
    # Virtual Machine connected to the host.
    value = '"%s" "%s" %s' % (sys.executable,
                              os.path.abspath(__file__),
                              json.dumps(s).encode('base64'))
    update_key(HKEY_LOCAL_MACHINE,
               'Software\\Microsoft\\Windows\\CurrentVersion\\Run',
               'Agent', value)

    # On some systems a "System Settings Change" message box pops up after
    # having installed everything. It requires us to reboot, so here goes.
    # (Notably the Cuckoo human.py will click it for us otherwise which
    # results in rebooting before the sample is able to achieve persistence,
    # generally speaking).
    if ctypes.windll.user32.FindWindowA(None, 'System Settings Change'):
        require_reboot = True

    # This should be further improved. Namely, per-instance changes to the
    # registry etc (although it would be easier to do that as a kernel driver).
    if require_reboot:
        subprocess.Popen(['shutdown', '-r', '-t', '0']).wait()

    try:
        if not BIND_IP:
            BIND_IP = socket.gethostbyname(socket.gethostname())

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
