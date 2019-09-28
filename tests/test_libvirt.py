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

def test_winx786():
    """ Test windows 7 X86 """
    config = json.load(open(os.path.expanduser("~/.vmcloak/config/win7x86.json"), "rb"))
    machinery = 'kvm'
    names = config.keys()

    for name in names:
        start_time = time.time()
        win_conf = config[name]
        ip = win_conf["network"]["ip"]
        port = win_conf["network"]["port"]
        dns = win_conf["network"]["dns"]
        mac = win_conf["network"]["mac"] if 'mac' in win_conf["network"].keys() else None
        iso = win_conf["iso"]
        ramsize = win_conf["config"]["ram_size"]
        vramsize = win_conf["config"]["vram_size"]
        gateway = win_conf["network"]["gateway"]
        extra_config = win_conf["extraConfig"][machinery]
        #except KeyError as e:
        #    vars()[e.args[0]] = None

        call(
            main.init, name,"--vm", machinery,"--win7x86",
            "--ip",  ip, "--port", port, "--ramsize", ramsize,
            "--tempdir", dirpath, "--iso-mount", iso, "--vramsize", vramsize ,
            "--dns", dns, "--mac", mac, "--gateway", gateway, "--debug",
            "--extra-config", extra_config
        )

        image = session.query(Image).filter_by(name=name).first()
        m = vm.KVM(image.config, name=image.name)
        m.create_vm()
        m.start_vm(visible=True)

        misc.wait_for_host(ip, port)

        ## Very basic integrity checking of the VM.
        a = agent.Agent(ip, port)
        assert a.environ()["SYSTEMDRIVE"] == "C:"

        a.shutdown()
        m.wait_for_state(shutdown=True)
        print("--- %s seconds to finish %s installation ---" % (time.time() - start_time, name))

def test_winxpx86():
    """ Test windows XP X86 """
    name, _ = genname("winxpx86"), genname("winxpx86-snapshot")
    machinery = 'kvm'
    win_conf = config["winxpx86"]
    ip = win_conf["network"]["ip"]
    port = win_conf["network"]["port"]
    dns = win_conf["network"]["dns"]
    mac = win_conf["network"]["mac"]
    serialkey = win_conf["serialkey"]
    iso = win_conf["iso"]
    ramsize = win_conf["config"]["ram_size"]
    vramsize = win_conf["config"]["vram_size"]
    gateway = win_conf["network"]["gateway"]
    extra_config = win_conf["extraConfig"][machinery]
    #hdd_vdev = config["winxpx86"]["config"]["hdd_vdev"]

    call(
        main.init, name,"--vm", machinery,"--winxpx86",
        "--ip",  ip, "--port", port, "--ramsize", ramsize,
        "--tempdir", dirpath, "--serial-key", serialkey,
        "--iso-mount", iso, "--vramsize", vramsize ,
        "--dns", dns, "--mac", mac, "--gateway", gateway, "--debug",
        "--extra-config", extra_config
    )

    image = session.query(Image).filter_by(name=name).first()
    m = vm.KVM(image.config, name=image.name)
    m.create_vm()
    m.start_vm(visible=True)

    # sleep
    time.sleep(7)

    misc.wait_for_host(ip, port)

    ## Very basic integrity checking of the VM.
    a = agent.Agent(ip, port)
    assert a.environ()["SYSTEMDRIVE"] == "C:"

    a.shutdown()
    m.wait_for_state(shutdown=True)


if __name__ == "__main__":
    test_winx786()
