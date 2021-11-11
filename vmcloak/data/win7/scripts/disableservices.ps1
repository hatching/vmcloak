# This list is based on blackviper's collection of services that can safely be disabled:
#http://www.blackviper.com/service-configurations/black-vipers-windows-7-service-pack-1-service-configurations/
$errs = 0
Foreach ($servicename in ("DPS", "clr_optimization_v2.0.50727_32", "clr_optimization_v2.0.50727_64", "AxInstSV", "SensrSvc", "ALG", "AppMgmt", "BDESVC", "bthserv", "PeerDistSvc", "CertPropSvc", "KeyIso", "VaultSvc", "WdiServiceHost", "WdiSystemHost", "TrkWks", "EapHost", "Fax", "fdPHost", "FDResPub", "hkmsvc", "HomeGroupListener", "HomeGroupProvider", "hidserv", "IKEEXT", "UI0Detect", "iphlpsvc", "PolicyAgent", "lltdsvc", "Mcx2Svc", "MSiSCSI", "NetTcpPortSharing", "Netlogon", "napagent", "CscService", "WPCSvc", "PNRPsvc", "p2psvc", "p2pimsvc", "IPBusEnum", "PNRPAutoReg", "WPDBusEnum", "wercplsupport", "PcaSvc", "QWAVE", "SessionEnv", "TermService", "UmRdpService", "RpcLocator", "RemoteRegistry", "SstpSvc", "wscsvc", "SCardSvr", "SCPolicySvc", "SNMPTRAP", "StorSvc", "TabletInputService", "lmhosts", "TapiSrv", "TBS", "WebClient", "WbioSrvc", "idsvc", "WcsPlugInService", "wcncsvc", "WinDefend", "WerSvc", "MpsSvc", "ehRecvr", "ehSched", "WMPNetworkSvc", "FontCache3.0.0.0", "WinRM", "WSearch", "WinHttpAutoProxySvc", "dot3svc", "Wlansvc", "WwanSvc")) {
    Set-Service $servicename -StartupType Disabled -ErrorAction SilentlyContinue
    $start = (Get-ItemProperty -Path HKLM:\SYSTEM\CurrentControlSet\Services\$servicename -ErrorAction SilentlyContinue).Start
    If ($start -ne "4") {
        Write-Host "Failed to disable service $servicename"
        $errs += 1
     }
}

If ($errs -ne 0) {
    exit 1
}
