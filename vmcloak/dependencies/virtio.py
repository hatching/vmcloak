from vmcloak.abstract import Dependency

class Virtio(Dependency):
    name = "virtio"
    default = "0.1.96-1"
    exes = [{
        "version": "0.1.96-1",
        "urls": [
            "https://fedorapeople.org/groups/virt/virtio-win/direct-downloads/stable-virtio/virtio-win.iso"
        ],
        "sha1": "4f37af23d97855caf37c534854bf008bbe2e8b74",
        "filename": "virtio-win.iso",
    }]

    def run(self):
        pass
