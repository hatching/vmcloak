# Silent install of Chrome using the standalone installer.
# https://dl.google.com/dl/chrome/install/googlechromestandaloneenterprise.msi

from vmcloak.abstract import Dependency

class Chrome(Dependency):
    name = "chrome"
    exes = [
        {
            "url": "http://cuckoo.sh/vmcloak/googlechromestandaloneenterprise.msi",
            "sha1": "a0ade494dda8911eeb68c9294c2dd0e3229d8f02",
        },
    ]

    def run(self):
        self.upload_dependency("C:\\googlechromestandaloneenterprise.msi")
        self.a.execute("Msiexec /q /I C:\\googlechromestandaloneenterprise.msi")
        self.a.remove("C:\\googlechromestandaloneenterprise.msi")
