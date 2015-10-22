#silent install of chrome. installer is the standalone version
#https://dl.google.com/dl/chrome/install/googlechromestandaloneenterprise.msi

from vmcloak.abstract import Dependency

class Chrome(Dependency):
    name = "chrome"
    exes = [
        {
            "url": "http://cuckoo.sh/vmcloak/googlechromestandaloneenterprise.msi",
            "sha1": "5b1fdc38cc8995792c37abcc81f3957d578d2593",
        },
    ]

    def run(self):
        self.upload_dependency("C:\\googlechromestandaloneenterprise.msi")
        self.a.execute("Msiexec /q /I C:\\googlechromestandaloneenterprise.msi")
        self.a.remove("C:\\googlechromestandaloneenterprise.msi")
