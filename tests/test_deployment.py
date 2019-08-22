#!/usr/bin/env python
import random
import jinja2
import os

from string import ascii_letters
from vmcloak.repository import Image, Session, Snapshot
from vmcloak.vm import VMWare
from vmcloak.constants import VMCLOAK_ROOT
from vmcloak.main import do_snapshot

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
    images = session.query(Image).all()

    for image in images:
        ipaddr = image.ipaddr
        machinery = image.vm
        name = image.name
        snapshots = session.query(Snapshot).filter_by(image_id=image.id)

        if machinery == "vmware":
            vmx_path = image.config
            if not os.path.exists(vmx_path):
                continue
            vm = VMWare(vmx_path, name=name)
            snapshots = vm.list_snapshots()
            if not snapshots:
                snapshot = genname(name)
                vm.snapshot(snapshot)
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
