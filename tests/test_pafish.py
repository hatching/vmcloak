#!/usr/bin/env python2
# Copyright (C) 2019 Mohsen Ahmadi.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.
import socket
import os
import time
import logging
import requests
import posixpath
import urlparse
import json

from vmcloak.repository import Image, Session, Snapshot, deps_path
from vmcloak.agent import Agent
from vmcloak.misc import wait_for_host
from vmcloak.vm import VMWare, VirtualBox

logging.basicConfig()
log = logging.getLogger("vmcloak")
log.setLevel(logging.DEBUG)

PAFISH_URL = "https://raw.githubusercontent.com/a0rtega/pafish/master/pafish.exe"

def download(url):
    path = urlparse.urlsplit(url).path
    fname = posixpath.basename(path)
    filename = os.path.join(deps_path, fname)
    if os.path.exists(filename):
        return filename
    r = requests.get(url, allow_redirects=True)
    open(filename, 'wb').write(r.content)
    return filename

def file_exist(agent, path):
    a = agent
    # python escape % using %%!
    cmd = """for %%I in (%s) do @echo %%~zI"""%path
    cnt = 0
    while True:
        if cnt > 10:
            return False
        r = a.execute(cmd, shell=True)
        cnt += 1
        stdout = json.loads(r.content)['stdout'].strip()
        if "ECHO" in stdout or stdout == "0":
            time.sleep(3)
        else:
            return True

def test_pafish():
    session = Session()
    images = session.query(Image).all()
    pafish_path = download(PAFISH_URL)
    pafish = open(pafish_path, 'rb')
    COMMAND = """C:\\Windows\\System32\\cmd.exe /c echo \\n | C:\\pafish.exe 1> %s 2>&1;"""
    pfish_gpath = "C:\\pafish.exe"

    for image in images:
        ipaddr = image.ipaddr
        port = image.port
        backend = image.vm
        name = image.name
        hostname = socket.gethostname()
        report_name = "_".join([hostname, backend, name]) + ".log"
        report_path = "C:\\%s"%report_name

        if backend == "vmware":
            vmx_path = image.config
            log.debug(vmx_path)
            if vmx_path is None:
                continue
            if not os.path.exists(vmx_path):
                continue
            vm = VMWare(vmx_path, name=name)

            snapshot_list = vm.list_snapshots()
            if snapshot_list:
                vm.restore_snapshot(label=snapshot_list[0])
            else:
                vm.start_vm(visible=False)

        elif backend == "virtualbox":
            vm = VirtualBox(name=name)

            snapshots = session.query(Snapshot).filter_by(image_id=image.id).all()
            if snapshots:
                vm.restore_snapshot(label=snapshot_list[0])
            else:
                vm.start_vm(visible=False)

        elif backend == "kvm":
            pass

        wait_for_host(ipaddr, port)

        a = Agent(ipaddr, port)
        a.ping()
        log.debug("--- got ping back from agent...")

        a.upload(pfish_gpath,pafish)
        pafish.seek(0)
        if file_exist(a, pfish_gpath):
            log.debug("--- pafish uploaded successfully to the %s..."%hostname)
        command = COMMAND%report_path
        a.execute(command, async="true")

        if file_exist(a, report_path):
            opath = os.path.join("pafish", report_name)
            open(opath, 'wb').write(a.retrieve(report_path))

        vm.stop_vm()
        vm.wait_for_state(shutdown=True)


if __name__ == "__main__":
    dir_ = os.path.join(os.path.abspath('.'), "pafish")
    if not os.path.exists(dir_):
        os.makedirs(dir_)
    test_pafish()
