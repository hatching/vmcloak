#!/usr/bin/env python
from __future__ import print_function
import random
import jinja2
import os
import logging
import time

from string import ascii_letters
from vmcloak.repository import Image, Session, Snapshot
from vmcloak.vm import KVM
from vmcloak.constants import VMCLOAK_ROOT
from vmcloak.main import do_snapshot
from vmcloak.misc import wait_for_host
from vmcloak.agent import Agent
from vmcloak.dependencies.pillow import Pillow
from vmcloak.winxp import WindowsXPx86, WindowsXPx64
from vmcloak.win7 import Windows7x86, Windows7x64
from vmcloak.win81 import Windows81x86, Windows81x64
from vmcloak.win10 import Windows10x86, Windows10x64

logging.basicConfig()
log = logging.getLogger("vmcloak")
log.setLevel(logging.DEBUG)

session = Session()
kvm_machines = dict()
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
        port = image.port
        machinery = image.vm
        name = image.name
        h = handlers[image.osversion]
        snapshots = session.query(Snapshot).filter_by(image_id=image.id)

        if machinery == "kvm":
            start_time = time.time()
            domain_path = image.config
            if not os.path.exists(domain_path):
                continue
            vm =KVM(domain_path, name=name)
            vm.create_vm()
            snapshots = vm.list_snapshots()
            if not snapshots:
                snapshot = genname(name)

                vm.start_vm(visible=True)

                wait_for_host(ipaddr, port)

                a = Agent(ipaddr, port)
                a.ping()

                Pillow(a=a, h=h).run()

                vm.snapshot(snapshot)

                vm.stop_vm()
                vm.wait_for_state(shutdown=True)

                snapshots = vm.list_snapshots()
                #TODO: change ipaddr of each snapshot from default one
            kvm_machines[name] = {'ipaddr': ipaddr,
                                    'snapshot': snapshots[0]}
            print("--- %s seconds to finish %s config deployement ---" % (time.time() - start_time, name))
        if machinery == "virtualbox":
            if not snapshots:
                snapshot = do_snapshot(image, name)
                vbox_machines[name] = {'snapshot': snapshot,
                                        'ipaddr': ipaddr}

    if kvm_machines:
        template_parser("kvm", "qemu:///system", kvm_machines)
    if vbox_machines:
        template_parser("virtualbox", "headless", vbox_machines)

if __name__ == '__main__':
    config_writer()
