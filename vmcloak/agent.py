# Copyright (C) 2014-2018 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.
from __future__ import print_function
from vmcloak.misc import wait_for_host

import io
import time
import re
import logging
import requests
import matplotlib.pyplot as plt
import pandas as pd


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

    def execute(self, command, async=False):
        """Execute a command."""
        log.debug("Executing command in VM: %s", command)
        if async:
            return self.post("/execute", command=command, async="true")
        else:
            return self.post("/execute", command=command)

    def execpy(self, filepath, async=False):
        """Execute a Python file."""
        if async:
            return self.post("/execpy", filepath=filepath, async="true")
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
        self.execute("shutdown -s -t 0", async=True)

    def reboot(self):
        """Reboot the machine."""
        self.execute("shutdown -r -t 0", async=True)

    def kill(self):
        """Kill the Agent."""
        self.get("/kill")

    def killprocess(self, process_name):
        """Terminate a process."""
        self.execute("taskkill /F /IM %s" % process_name)

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

        try:
            session = requests.Session()
            session.trust_env = False
            session.proxies = None
            session.post(
                "http://%s:%s/execute" % (self.ipaddr, self.port),
                data={"command": command}, timeout=5
            )
        except requests.exceptions.ReadTimeout:
            pass

        # Now wait until the Agent is reachable on the new IP address.
        wait_for_host(ipaddr, self.port)
        self.ipaddr = ipaddr

    def dns_server(self, ipaddr):
        """Set the IP address of the DNS server."""
        command = \
            "netsh interface ip set dns " \
            "name=\"Local Area Connection\" static %s" % ipaddr
        self.execute(command)

    def upload(self, filepath, contents):
        """Upload a file to the Agent."""
        if isinstance(contents, basestring):
            contents = io.BytesIO(str(contents))
        self.postfile("/store", {"file": contents}, filepath=filepath)

    def process_utilization(self, process="*", interval=2, samples=10,
                            output="C:\process.csv"):
        """Read performance counter for process object."""
        RE_PROC = r'\"\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}\.\d{3}\",(.*)\r\n'
        config = ["\Process({process})\ID Process",
                "\Process({process})\% Processor Time"]
        counters_string = ' '.join("\"%s\""%c.format(**{"process": process}) for c in config)
        command = "typeperf -si {si} -sc {sc} -f CSV -y -o {o} {counters}".format(**{"si": interval,
                                                                "sc":samples,
                                                                "o":output,
                                                                "counters": counters_string})
        self.execute(command, async=True)
        time.sleep(interval*samples)
        content = self.retrieve(output)
        data_list = re.findall(RE_PROC, content)
        process_list = re.findall(r'Process\(([\w#]+)\)\\ID Process', content)
        process_count = len(process_list)
        process_PID = data_list[0].split(',')[:process_count]
        cpu_usage = {p:[] for p in process_list}
        cpu_list = []

        for sample in range(1, samples-1):
            cpu_list = [ d.replace('\"', '') for d in
                        data_list[sample].split(',')[process_count:] ]
            for process, t in zip(process_list, cpu_list):
                cpu_usage[process].append(t)

        cpu_usage['x'] = range(1,samples-1)
        df = pd.DataFrame(cpu_usage)
        plt.ylabel("Processor time")
        plt.xlabel("Samples per second")
        for p in process_list:
            plt.plot('x', p, data=df, marker='o', markerfacecolor='blue',
                     markersize=12, color='skyblue', linewidth=4)
        plt.legend()
        plt.savefig("cpu_usage.png", dpi=100)
        #plt.show()
        return cpu_usage

    def disk_utilization(self, interval=2, samples=10,
                            output="C:\hdd.csv"):
        """Read performance counter for physical disk object."""
        ret = dict()
        r = re.compile(r'\"\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}\.\d{3}\",\"(?P<read>\d+\.\d+|\d+)\",\"(?P<write>\d+\.\d+|\d+)\"\r\n')
        config = ["\PhysicalDisk(0 C:)\Disk Read Bytes/sec",
                  "\PhysicalDisk(0 C:)\Disk Write Bytes/sec"]
        counters_string = ' '.join("\"%s\""%c for c in config)
        command = "typeperf -si {si} -sc {sc} -f CSV -y -o {o} {counters}".format(**{"si": interval,
                                                                "sc":samples,
                                                                "o":output,
                                                                "counters": counters_string})
        self.execute(command, async=True)
        time.sleep(interval*samples)
        content = self.retrieve(output)
        ret['read'] = [m.group('read') for m in r.finditer(content)]
        ret['write'] = [m.group('write') for m in r.finditer(content)]
        return ret

    def memory_utilization(self, interval=2, samples=10,
                            output="C:\memory.csv"):
        """Read performance counter for memory object."""
        ret = dict()
        r = re.compile(r'\"\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}\.\d{3}\",\"(?P<commit>\d+)\",\"(?P<avail>\d+)\"\,\"(?P<cache>\d+)\"\r\n')
        config = ["\Memory\Committed Bytes",
                  "\Memory\Available Bytes",
                  "\Memory\Cache Bytes"]
        counters_string = ' '.join("\"%s\""%c for c in config)
        command = "typeperf -si {si} -sc {sc} -f CSV -y -o {o} {counters}".format(**{"si": interval,
                                                                "sc":samples,
                                                                "o":output,
                                                                "counters": counters_string})
        self.execute(command, async=True)
        time.sleep(interval*samples)
        content = self.retrieve(output)
        ret['commit'] = [m.group('commit') for m in r.finditer(content)]
        ret['available'] = [m.group('avail') for m in r.finditer(content)]
        ret['cache'] = [m.group('cache') for m in r.finditer(content)]
        return ret


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
            (window_title, button_name), async=True
        )

    def resolution(self, width, height):
        """Set the screen resolution of this Virtual Machine."""
        self.execute(
            "C:\\Python27\\python.exe C:\\vmcloak\\resolution.py %s %s" %
            (width, height)
        )
