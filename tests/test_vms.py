import json
import os.path
import tempfile

from vmcloak import main, misc, agent, vm
from vmcloak.repository import Session, Image

dirpath = tempfile.mkdtemp()

# To be populated by the user of the unittests.
config = json.load(open(os.path.expanduser("~/.vmcloak/config.json"), "rb"))

# Database session.
session = Session()

def call(function, *args):
    """Invokes click command."""
    return function.main(args, standalone_mode=False)

def genname(osversion):
    return "%s-%s" % (osversion, os.path.basename(dirpath))

def test_winxp():
    ip, port = "192.168.56.103", 13337

    name, snapshot = genname("winxp"), genname("winxp-snapshot")
    call(
        main.init, name, "--winxp", "--port", port,
        "--tempdir", dirpath, "--serial-key", config["winxp"]["serialkey"]
    )
    call(main.snapshot, name, snapshot, ip)

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
    ip, port = "192.168.56.104", 13338

    name, snapshot = genname("win7x64"), genname("win7x64-snapshot")
    call(
        main.init, name, "--win7x64", "--port", port, "--tempdir", dirpath,
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

def test_win81x64():
    ip, port = "192.168.56.105", 13339

    name, snapshot = genname("win81x64"), genname("win81x64-snapshot")
    call(
        main.init, name, "--win81x64", "--port", port, "--tempdir", dirpath,
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
        main.init, name, "--win10x64", "--port", port, "--tempdir", dirpath,
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
