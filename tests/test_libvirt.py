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

def test_winxpx86():
    """ Test windows XP X86 """
    name, _ = genname("winxpx86"), genname("winxpx86-snapshot")
    win_conf = config["winxpx86"]
    ip = win_conf["network"]["ip"]
    port = win_conf["network"]["port"]
    dns = win_conf["network"]["dns"]
    mac = win_conf["network"]["mac"]
    serialkey = win_conf["serialkey"]
    iso = win_conf["iso"]
    ramsize = win_conf["config"]["ram_size"]
    vramsize = win_conf["config"]["vram_size"]
    #hdd_vdev = config["winxpx86"]["config"]["hdd_vdev"]
    machinery = 'kvm'

    call(
        main.init, name,"--vm", machinery,"--winxpx86",
        "--ip",  ip, "--port", port, "--ramsize", ramsize,
        "--tempdir", dirpath, "--serial-key", serialkey,
        "--iso-mount", iso, "--vramsize", vramsize ,
        "--dns", dns, "--mac", mac, "--debug"
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


if __name__ == "__main__":
    test_winxpx86()
