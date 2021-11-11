# Copyright (C) 2021 Hatching B.V.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

# Disable all non-vital services after the reboot
# This list is based on blackviper's collection of services that can safely be disabled:
# http://www.blackviper.com/service-configurations/black-vipers-windows-10-service-configurations/

Write-Host "Disabling all non-vital Windows 10 services"
$errs = 0
Foreach ($servicename in ("PrintNotify", "WpnUserService", "OneSyncSvc", "WdBoot", "WdFilter", "WdNisDrv", "WdNisSvc", "WinDefend", "DiagTrack", "DoSvc", "TimeBrokerSvc", "TokenBroker", "Sense", "SecurityHealthService", "wscsvc", "dmwappushservice", "AJRouter", "ALG", "AppMgmt", "bthserv", "PeerDistSvc", "CertPropSvc", "dmwappushservice", "MapsBroker", "Fax", "lfsvc", "HvHost", "vmickvpexchange", "vmicguestinterface", "vmicshutdown", "vmicheartbeat", "vmicvmsession", "vmicrdv", "vmictimesync", "vmicvss", "irmon", "SharedAccess", "iphlpsvc", "IpxlatCfgSvc", "MSiSCSI", "SmsRouter", "NaturalAuthentication", "NetTcpPortSharing", "Netlogon", "NcdAutoSetup", "CscService", "SEMgrSvc", "PhoneSvc", "SessionEnv", "TermService", "UmRdpService", "RpcLocator", "RetailDemo", "SensorDataService", "SensrSvc", "SensorService", "ScDeviceEnum", "SCPolicySvc", "SNMPTRAP", "TabletInputService", "WebClient", "FrameServer", "wcncsvc", "wisvc", "WMPNetworkSvc", "icssvc", "WinRM", "workfolderssvc", "WwanSvc", "XblAuthManager", "XblGameSave", "XboxNetApiSvc", "WFDSConMgrSvc")) {
If (Test-Path HKLM:\SYSTEM\CurrentControlSet\Services\$servicename) {
    $shhh = reg add "HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\$servicename" /v "Start" /t REG_DWORD /d 4 /f
    $start = (Get-ItemProperty -Path HKLM:\SYSTEM\CurrentControlSet\Services\$servicename -ErrorAction SilentlyContinue).Start
    If ($start -ne "4") {
      Write-Host "Failed to disable service $servicename"
      $errs += 1
    }
 }
}

If ($errs -ne 0) {
    exit 1
}
