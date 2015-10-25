# Silent install of Firefox 41
# https://download-installer.cdn.mozilla.net/pub/firefox/releases/41.0.2/win32/en-US/Firefox%20Setup%2041.0.2.exe
# file was renamed Firefox_Setup_41.0.2.exe to avoid issues with spaces.

from vmcloak.abstract import Dependency

class Firefox_41(Dependency):
    name = "firefox_41"
    exes = [
        {
            "url": "http://cuckoo.sh/vmcloak/Firefox_Setup_41.0.2.exe",
            "sha1": "c5118ca76f0cf6ecda5d2b9292bf191525c9627a",
        },
    ]

    def run(self):
        self.upload_dependency("C:\\Firefox_Setup_41.0.2.exe")
        self.a.execute("C:\\Firefox_Setup_41.0.2.exe -ms")
        self.a.remove("C:\\Firefox_Setup_41.0.2.exe")
