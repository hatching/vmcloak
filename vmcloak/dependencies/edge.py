from vmcloak.abstract import Dependency

class Edge(Dependency):
    name = "edge"
    
    def run(self):
        self.a.execute(
            "reg add \"HKEY_LOCAL_MACHINE\\Software\\"
            "Microsoft\\Windows\\CurrentVersion\\"
            "Policies\\System\" "
            "/v FilterAdministratorToken /t REG_DWORD /d 1 /f"
        )
        self.a.execute(
            "reg add \"HKEY_LOCAL_MACHINE\\Software\\"
            "Microsoft\\Windows\\CurrentVersion\\"
            "Policies\\System\\UIPI\" "
            "/v \"\" /t REG_SZ /d \"1\" /f"
        )

