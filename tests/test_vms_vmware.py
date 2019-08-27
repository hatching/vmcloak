# Copyright (C) 2016 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.
from __future__ import print_function
import json
import random
import os.path
import tempfile
import time
import pickle

from vmcloak import main, misc, agent, vm
from vmcloak.repository import Session, Image, vms_path
from vmcloak.constants import VMCLOAK_VM_MODES
from string import ascii_letters

dirpath = tempfile.mkdtemp()

# To be populated by the user of the unittests.
config = json.load(open(os.path.expanduser("~/.vmcloak/config/config.json"), "rb"))

# Database session.
session = Session()


def call(function, *args):
    """Invokes click command."""
    return function.main(args, standalone_mode=False)

def genname(osversion):
    rand_str = ''.join(random.choice(ascii_letters) for _ in range(5))
    return osversion + "_" + rand_str

def test_ipaddr_increase():
    assert misc.ipaddr_increase("1.2.3.4") == "1.2.3.5"
    assert misc.ipaddr_increase("192.168.56.101") == "192.168.56.102"

def test_all():
    for winver in config.keys():
        start_time = time.time()
        win_conf = config[winver]
        name = genname(winver)
        ip = win_conf["network"]["ip"]
        port = win_conf["network"]["port"]
        gateway = win_conf["network"]["gateway"]
        dns = win_conf["network"]["dns"]
        mac = win_conf["network"]["mac"]
        iso = win_conf["iso"]
        hdd_vdev = win_conf["config"]["hdd_vdev"]
        cpu = win_conf["config"]["cpus"]
        virts = win_conf["extraConfig"].keys()
        virts.remove('virtualbox')
        extraConfig = ""

        for machinery in virts:
            if machinery in VMCLOAK_VM_MODES:
                for k,v in win_conf["extraConfig"][machinery].items():
                    extraConfig += "{0} = {1}\n".format(k,v)
            if "serialkey" in win_conf.keys():
                serialkey = win_conf["serialkey"]
                call(
                    main.init, name,"--vm", machinery,"--%s"%winver,
                    "--ip",  ip, "--port", port, "--gateway", gateway,
                    "--mac", mac, "--cpus", cpu, "--dns", dns,
                    "--tempdir", dirpath, "--serial-key", serialkey,
                    "--iso-mount", iso, "--hdd-vdev", hdd_vdev,
                    "--extra-config", extraConfig, "--debug"
                )
            else:
                call(
                    main.init, name,"--vm", machinery,"--%s"%winver,
                    "--ip",  ip, "--port", port, "--gateway", gateway,
                    "--mac", mac, "--cpus", cpu,
                    "--tempdir", dirpath, "--iso-mount", iso,
                    "--hdd-vdev", hdd_vdev, "--extra-config", extraConfig, "--debug"
                )

            image = session.query(Image).filter_by(name=name).first()
            m = vm.VMWare(image.config, name=image.name)
            m.start_vm(visible=True)

            misc.wait_for_host(image.ipaddr, image.port)

            ## Very basic integrity checking of the VM.
            a = agent.Agent(image.ipaddr, image.port)
            assert a.environ()["SYSTEMDRIVE"] == "C:"

            cpu_usage = a.process_utilization()
            out = os.path.join(vms_path, name,
                               "cpu_usage.pkl")
            with open(out, 'wb') as f:
                pickle.dump(cpu_usage, f, protocol=pickle.HIGHEST_PROTOCOL)

            a.shutdown()
            m.wait_for_state(shutdown=True)
        print("--- %s seconds to finish %s installation ---" % (time.time() - start_time, winver))

def test_winxpx86():

    name, snapshot = genname("winxpx86"), genname("winxpx86-snapshot")
    ip = config["winxpx86"]["network"]["ip"]
    port = config["winxpx86"]["network"]["port"]
    serialkey = config["winxpx86"]["serialkey"]
    iso = config["winxpx86"]["iso"]
    hdd_vdev = config["winxpx86"]["config"]["hdd_vdev"]
    virts = config["winxpx86"]["extraConfig"].keys()
    virts.remove('virtualbox')
    extraConfig = ""

    for machinery in virts:
        if machinery in VMCLOAK_VM_MODES:
            for k,v in config["winxpx86"]["extraConfig"][machinery].items():
                extraConfig += "{0} = {1}\n".format(k,v)
            call(
                main.init, name,"--vm", machinery,"--winxpx86",
                "--ip",  ip, "--port", port,
                "--tempdir", dirpath, "--serial-key", serialkey,
                "--iso-mount", iso, "--hdd-vdev", hdd_vdev,
                "--extra-config", extraConfig, "--debug"
            )


            image = session.query(Image).filter_by(name=name).first()
            m = vm.VMWare(image.config, name=image.name)
            m.start_vm(visible=True)
            m.install_vmwaretools()
            call(main.snapshot, name, snapshot, ip)

            m = vm.VMWare(snapshot)
            m.restore_snapshot()
            m.start_vm()

            misc.wait_for_host(ip, port)

            ## Very basic integrity checking of the VM.
            a = agent.Agent(ip, port)
            assert a.environ()["SYSTEMDRIVE"] == "C:"

            a.shutdown()
            m.wait_for_state(shutdown=True)

            m.delete_snapshot("vmcloak")
            m.remove_hd()
            m.delete_vm()

            image = session.query(Image).filter_by(name=name).first()
            os.remove(image.path)

def test_winxpx64():

    name, _ = genname("winxpx64"), genname("winxpx64-snapshot")
    ip = config["winxpx64"]["network"]["ip"]
    port = config["winxpx64"]["network"]["port"]
    serialkey = config["winxpx64"]["serialkey"]
    iso = config["winxpx64"]["iso"]
    hdd_vdev = config["winxpx64"]["config"]["hdd_vdev"]
    virts = config["winxpx64"]["extraConfig"].keys()
    virts.remove('virtualbox')
    extraConfig = ""
    #print dirpath

    for machinery in virts:
        if machinery in VMCLOAK_VM_MODES:
            for k,v in config["winxpx64"]["extraConfig"][machinery].items():
                extraConfig += "{0} = {1}\n".format(k,v)
            call(
                main.init, name,"--vm", machinery,"--winxpx64",
                "--ip",  ip, "--port", port,
                "--tempdir", dirpath, "--serial-key", serialkey,
                "--iso-mount", iso, "--hdd-vdev", hdd_vdev,
                "--extra-config", extraConfig, "--debug"
            )
            misc.wait_for_host(ip, port)

            ## Very basic integrity checking of the VM.
            a = agent.Agent(ip, port)
            assert a.environ()["SYSTEMDRIVE"] == "C:"

def test_winxpx64_many():
    ip, port, count = "192.168.56.201", 13400, 10

    name, snapshot = genname("winxpx64"), genname("winxpx64-snapshot")
    call(
        main.init, name, "--winxpx64",
        "--ip", "192.168.56.4", "--port", port,
        "--tempdir", dirpath, "--serial-key", config["winxpx64"]["serialkey"]
    )
    call(main.snapshot, name, snapshot, ip, "--count", count)

    snapshots = []
    for x in range(count):
        snapshots.append([
            "%s%d" % (snapshot, x + 1),
            ip, port,
        ])

        ip = misc.ipaddr_increase(ip)

    # We have to remove the VMs in reverse because of VirtualBox dependencies.
    for snapshot, ip, port in snapshots[::-1]:
        m = vm.VirtualBox(snapshot)
        m.restore_snapshot()
        m.start_vm()

        misc.wait_for_host(ip, port)

        # Very basic integrity checking of the VM.
        a = agent.Agent(ip, port)
        assert a.environ()["SYSTEMDRIVE"] == "C:"

        a.shutdown()
        m.wait_for_state(shutdown=True)

        m.delete_snapshot("vmcloak")
        m.remove_hd()
        m.delete_vm()

    image = session.query(Image).filter_by(name=name).first()
    os.remove(image.path)

def test_win7x64():
    ip, port = "192.168.19.3", 13338

    name, snapshot = genname("win7x64"), genname("win7x64-snapshot")
    call(
        main.init, name, "--vm", "vmware" ,"--win7x64",
        "--ip", ip, "--port", port,
        "--tempdir", dirpath, "--debug"
    )
    call(main.snapshot, name, snapshot, ip)

    m = vm.VMWare(snapshot)
    m.restore_snapshot()
    m.start_vm()

    misc.wait_for_host(ip, port)

    a = agent.Agent(ip, port)
    assert a.environ()["SYSTEMDRIVE"] == "C:"

    a.shutdown()
    m.wait_for_state(shutdown=True)

    m.delete_snapshot("vmcloak")
    m.remove_hd()
    m.delete_vm()

    image = session.query(Image).filter_by(name=name).first()
    os.remove(image.path)

def test_win81x64():
    ip, port = "192.168.56.105", 13339

    name, snapshot = genname("win81x64"), genname("win81x64-snapshot")
    call(
        main.init, name, "--win81x64",
        "--ip", "192.168.56.6", "--port", port,
        "--tempdir", dirpath,
    )
    call(main.snapshot, name, snapshot, ip)

    m = vm.VirtualBox(snapshot)
    m.restore_snapshot()
    m.start_vm()

    misc.wait_for_host(ip, port)

    a = agent.Agent(ip, port)
    assert a.environ()["SYSTEMDRIVE"] == "C:"

    a.shutdown()
    m.wait_for_state(shutdown=True)

    m.delete_snapshot("vmcloak")
    m.remove_hd()
    m.delete_vm()

    image = session.query(Image).filter_by(name=name).first()
    os.remove(image.path)

def test_win10x64():
    ip, port = "192.168.56.106", 13340

    name, snapshot = genname("win10x64"), genname("win10x64-snapshot")
    call(
        main.init, name, "--win10x64",
        "--ip", "192.168.56.7", "--port", port,
        "--tempdir", dirpath,
    )
    call(main.snapshot, name, snapshot, ip)

    m = vm.VirtualBox(snapshot)
    m.restore_snapshot()
    m.start_vm()

    misc.wait_for_host(ip, port)

    a = agent.Agent(ip, port)
    assert a.environ()["SYSTEMDRIVE"] == "C:"

    a.shutdown()
    m.wait_for_state(shutdown=True)

    m.delete_snapshot("vmcloak")
    m.remove_hd()
    m.delete_vm()

    image = session.query(Image).filter_by(name=name).first()
    os.remove(image.path)

if __name__ == "__main__":
    test_all()
