#This script automatically configures elements that are used for sandboxes

from vmcloak.abstract import Dependency

class Windows_Cleanup(Dependency):
    name = "windows_cleanup"
    def run(self):

        if self.i.osversion == "winxp":
	      #disable system restore
            self.a.execute("reg add \"HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\SystemRestore\" /v DisableSR /t REG_DWORD /d 1 /f")
       	    self.a.execute("reg add \"HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Services\\sr\" /v Start /t REG_DWORD /d 4 /f")

	      #if self.i.osversion == "win7":

        #if self.i.osversion == "win7x64":
