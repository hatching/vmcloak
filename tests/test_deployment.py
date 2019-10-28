#!/usr/bin/env python
import random
import jinja2
import os
import logging

from string import ascii_letters
from vmcloak.repository import Image, Session, Snapshot
from vmcloak.vm import VMWare
from vmcloak.constants import VMCLOAK_ROOT
from vmcloak.main import do_snapshot
from vmcloak.misc import wait_for_host
from vmcloak.agent import Agent
from vmcloak.dependencies.pillow import Pillow
from vmcloak.dependencies.vcredist import VcRedist
from vmcloak.winxp import WindowsXPx86, WindowsXPx64
from vmcloak.win7 import Windows7x86, Windows7x64
from vmcloak.win81 import Windows81x86, Windows81x64
from vmcloak.win10 import Windows10x86, Windows10x64

logging.basicConfig()
log = logging.getLogger("vmcloak")
log.setLevel(logging.DEBUG)

session = Session()
vmware_machines = dict()
vbox_machines = dict()

def genname(osversion):
    rand_str = ''.join(random.choice(ascii_letters) for _ in range(5))
    return osversion + "_" + rand_str

def template_parser(tpl_name, mode, config):
    temp_loader = jinja2.FileSystemLoader(searchpath=os.path.join(VMCLOAK_ROOT,
                                                    "data/template"))
    env = jinja2.Environment(loader=temp_loader)
    template = env.get_template("%s.conf"%tpl_name)
    content = template.render(mode=mode, machines=config)
    with open(os.path.expanduser('~/.cuckoo/conf/%s.conf'%tpl_name), 'w') as f:
        f.write(content)

def config_writer():
    handlers = {
        "winxpx86": WindowsXPx86,
        "winxpx64": WindowsXPx64,
        "win7x86": Windows7x86,
        "win7x64": Windows7x64,
        "win81x86": Windows81x86,
        "win81x64": Windows81x64,
        "win10x86": Windows10x86,
        "win10x64": Windows10x64,
    }

    images = session.query(Image).all()

    for image in images:
        ipaddr = image.ipaddr
        machinery = image.vm
        name = image.name
        h = handlers[image.osversion]
        snapshots = session.query(Snapshot).filter_by(image_id=image.id)

        if machinery == "vmware":
            vmx_path = image.config
            if not os.path.exists(vmx_path):
                continue
            vm = VMWare(vmx_path, name=name)
            snapshots = vm.list_snapshots()
            if not snapshots:
                snapshot = genname(name)

                vm.start_vm(visible=True)

                wait_for_host(image.ipaddr, image.port)

                a = Agent(image.ipaddr, image.port)
                a.ping()

                Pillow(a=a, h=h).run()
                VcRedist(a=a, h=h, version="2015u2").run()

                vm.snapshot(snapshot)

                vm.stop_vm()
                vm.wait_for_state(shutdown=True)

                snapshots = vm.list_snapshots()
                #TODO: change ipaddr of each snapshot from default one
            vmware_machines[name] = {'ipaddr': ipaddr,
                                    'snapshot': snapshots[0],
                                    'vmx_path': vmx_path}
        if machinery == "virtualbox":
            if not snapshots:
                snapshot = do_snapshot(image, name)
                vbox_machines[name] = {'snapshot': snapshot,
                                        'ipaddr': ipaddr}

    if vmware_machines:
        template_parser("vmware", "nogui", vmware_machines)
    if vbox_machines:
        template_parser("virtualbox", "headless", vbox_machines)

if __name__ == '__main__':
    config_writer()
