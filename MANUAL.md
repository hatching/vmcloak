## How to make vmcloak working?
----


### Mount ISO images of Windows OS 
----
The first thing you need is to mount the VM ISOs under your `/mnt/` path for
each version of OS. This can be done easily using the script I've already out
under `bin/vmcloak-mount.sh` path. The only thing you might need to change is
the path to VM folder hierarchy variable
(`MEDIA="/media/$USER/D268B33068B31269/windows"`) to yours on the server. 

I've already uploaded the VM hierarchy under `/opt/share/VMS/windows` directory
on hopper server. One needed to be part of the `mimosa` group to get access to the ISO
images. 

```
pwnslinger@jerseyshore:/opt/share/VMS/windows$ tree
.
├── win10
│   ├── x64
│   │   └── Win10_1809Oct_v2_English_x64.iso
│   └── x86
│       └── Win10_1809Oct_v2_English_x32.iso
├── win7
│   ├── x64
│   │   └── win7x64sp1.iso
│   └── x86
│       └── Windows_7_32-bit_Professional_x86.iso
├── win81
│   ├── x64
│   │   └── Win8.1_English_x64.iso
│   └── x86
│       └── Win8.1_English_x32.iso
└── winxp
    ├── x64
    │   ├── SN.txt
    │   └── winxpprox64.iso
    └── x86
        ├── en_windows_xp_professional_with_service_pack_3_x86_cd_vl_x14-73974.iso
        └── Serial.txt
``` 

After you've mounted all the ISO images successfully, then it comes to
generating customized VMs per each OS using `vmcloak` for any of the supported
hypervisor backends (Virtualbox, VMWare so far). 

### Customizing OS and hypervisor parameters 
----
In order to run the tests, you should put your config file which basically is a
JSON file under `$HOME/.vmcloak/config/config.json` path. The structure of this
file is as the following: 

```json
    "winxpx64":
    {
        "serialkey": "FM634-HJ3QK-6QVTY-RJY4R-XCR9J",
        "iso": "/mnt/winxpx64/",
        "network": {
            "ip": "192.168.19.2",
            "port": "8000",
            "netmask": "",
            "gateway": "192.168.19.1",
            "dns": "192.168.19.1",
            "mac": "6C:F0:49:1A:6E:85"
        },
        "config": {
            "ram_size": "1024",
            "cpus": "2",
            "hdd_size": "",
            "hdd_adapter": "buslogic",
            "hdd_vdev": "lsisas1068"
        },
        "extraConfig": {
            "vmware": {
                "hypervisor.cpuid.v0": "FALSE",
                "board-id.reflectHost": "TRUE",
                "hw.model.reflectHost": "TRUE",
                "monitor_control.disable_btseg": "TRUE"
            },
            "virtualbox": {
                "VBoxInternal/Devices/efi/0/Config/DmiBIOSVendor": "Apple Inc.",
                "VBoxInternal/Devices/efi/0/Config/DmiBIOSVersion": "MB52.88Z.0088.B05.0904162222",
                "VBoxInternal/Devices/efi/0/Config/DmiBIOSReleaseDate": "08/10/13",
                "VBoxInternal/Devices/efi/0/Config/DmiBIOSReleaseMajor": "5",
                "VBoxInternal/Devices/efi/0/Config/DmiBIOSReleaseMinor": "9",
                "VBoxInternal/Devices/piix3ide/0/Config/SecondaryMaster/ATAPIRevision": "KAA2",
                "VBoxInternal/Devices/acpi/0/Config/AcpiOemId": "APPLE"
            }
        }
    },
``` 

Then after you set necessary parameters for CPU, RAM, network info, and so on,
then you are ready to boot up the OS through VMCloak. All the necessary test
cases are located under `tests/test_vms_vmware.py` for `vmware` as an example. 

### configure cuckoo sandbox per VMs
----
After a successful run you should be able to see a SQLite database under your
`$HOME/.vmcloak/repository.db` which is basically containing the path and other
metadata for each of the configure VMs. Then, one can use these data to
auto-configure cuckoo machinary based on the already existing VMs. It's
suggested to have a snapshot for each VM (with some modules installed on the OS
like .NET framework, PIL library to take snapshot from desktop during the
malware execution per each generated new window, ...). 

The script under `tests/test_deployment.py` will facilitate this process for you
by taking a snapshot after installing and testing the connectivity of Agent
inside each of the VMs. 
