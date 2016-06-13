# Silent install of Winrar

from vmcloak.abstract import Dependency

class Winrar(Dependency):
    name = "winrar"
    exes = [
        {
            "url": "http://www.rarlab.com/rar/winrar-x64-531.exe",
            "sha1": "48add5a966ed940c7d88456caf7a5f5c2a6c27a7",
        },
    ]

    def run(self):
        self.upload_dependency("C:\\winrar.exe")
        self.a.execute("C:\\winrar.exe /S")
        self.a.remove("C:\\winrar.exe")
