import json
import os.path
import tempfile

import vmcloak

dirpath = tempfile.mkdtemp()

# To be populated by the user of the unittests.
config = json.load(open(os.path.expanduser("~/.vmcloak/config.json"), "rb"))

def call(function, *args):
    """Invokes click command."""
    return function.main(args, standalone_mode=False)

def genname(osversion):
    return "%s-%s" % (osversion, os.path.basename(dirpath))

def test_winxp():
    ip, port = "192.168.56.103", 13337

    name, snapshot = genname("winxp"), genname("winxp-snapshot")
    call(
        vmcloak.main.init, name, "--winxp", "--port", port,
        "--tempdir", dirpath, "--serial-key", config["winxp"]["serialkey"]
    )
    call(vmcloak.main.snapshot, name, snapshot, ip)

    m = vmcloak.vm.VirtualBox(snapshot)
    m.restore_snapshot()
    m.start_vm()

    vmcloak.misc.wait_for_host(ip, port)

    a = vmcloak.agent.Agent(ip, port)
    print a.environ()
