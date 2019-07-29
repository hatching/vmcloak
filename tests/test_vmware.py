#!/usr/bin/env python
import os.path
import tempfile
import shutil

from vmcloak.vm import VMware

dirpath = tempfile.mkdtemp()

def test_vmware():
    vmx_path = os.path.join(dirpath, "test.vmx")
    vmdk_path = os.path.join(dirpath, "test.vmdk")
    iso_path = "/media/pwnslinger/D268B33068B31269/winxp/sp2_x86/WXPSP2Home.iso"
    vm = VMware(vmx_path, name="test")
    vm.create_vm()
    vm.os_type("winxp")
    vm.ramsize(5396)
    vm.create_hd(vmdk_path)
    #vm.vramsize()
    vm.attach_iso(iso_path)
    vm.hostonly()
    vm.enableparavirt()
    vm.remotedisplay(password="thisisatestpasswd")
    vm.start_vm()
    if vm.isrunning():
        vm.stop_vm()
    shutil.rmtree(dirpath)

if __name__ == '__main__':
    test_vmware()
