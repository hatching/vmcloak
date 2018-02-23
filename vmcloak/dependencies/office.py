# Copyright (C) 2014-2018 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import logging
import os.path

from vmcloak.abstract import Dependency

log = logging.getLogger(__name__)

config = """
<Configuration Product="ProPlus">
    <Display Level="basic" CompletionNotice="no" SuppressModal="yes" AcceptEula="yes" />
    <PIDKEY Value="%(serial_key)s" />
    <Setting Id="AUTO_ACTIVATE" Value="%(activate)s" />
</Configuration>
"""

officever = {
    "2016": "16.0",
    "2013": "15.0",
    "2010": "14.0",
    "2007": "12.0",
    "2003": "11.0",
}

class Office(Dependency):
    name = "office"
    default = "2010"

    def init(self):
        self.isopath = None
        self.serialkey = None
        self.activate = None

    def check(self):
        if not self.serialkey:
            log.error("Please provide a serial key for Office.")
            return False

        if not self.isopath or not os.path.isfile(self.isopath):
            log.error("Please provide the Office installer ISO file.")
            return False

        if not self.activate:
            self.activate = 0
            log.info("Defaulting activate to False")
            return True
        elif self.activate not in ["0", "1"]:
            log.error(
                "Please keep activate value 0 or 1. You had %s.",
                self.activate
            )
            return False

    def run(self):
        if self.i.vm == "virtualbox":
            self.disable_autorun()
            self.m.attach_iso(self.isopath)

        self.a.upload(
            "C:\\config.xml",
            config % dict(serial_key=self.serialkey, activate=self.activate)
        )
        self.a.execute("D:\\setup.exe /config C:\\config.xml")

        # Wait until setup.exe is no longer running.
        self.wait_process_exit("setup.exe")

        self.a.remove("C:\\config.xml")

        # disable first use popup
        self.a.execute(
            "REG ADD \"HKEY_CURRENT_USER\\Software\\"
            "Microsoft\\Office\\%s\\Common\\General\" "
            "/v ShownFirstRunOptin /t REG_DWORD /d 1 /f" %
            officever[self.version]
        )

        # dont report office binary files (pub/doc/xls/etc) to MS if validation failed
        # https://blogs.technet.microsoft.com/office2010/2009/12/16/office-2010-file-validation/
        self.a.execute(
            "REG ADD \"HKEY_CURRENT_USER\\Software\\"
            "Microsoft\\Office\\%s\\Common\\Security\\FileValidation\" "
            "/v DisableReporting /t REG_DWORD /d 1 /f" %
            officever[self.version]
        )

        # Disable all privacy settings in all Office products
        # https://social.technet.microsoft.com/Forums/office/en-US/0db3e246-04b6-4948-a98c-4459fb65b1f9/privacy-options-in-access-2010?forum=officeitproprevious
        # https://msdn.microsoft.com/en-us/library/office/aa205294(v=office.11).aspx
        # https://www.stigviewer.com/stig/microsoft_office_system_2007/2014-01-07/finding/V-17740
        self.a.execute(
            "REG ADD \"HKEY_CURRENT_USER\\Software\\"
            "Microsoft\\Office\\%s\\Common\\Internet\" "
            "/v UseOnlineContent /t REG_DWORD /d 0 /f" %
            officever[self.version]
        )
        self.a.execute(
            "REG ADD \"HKEY_CURRENT_USER\\Software\\"
            "Microsoft\\Office\\%s\\Common\\Internet\" "
            "/v UseOnlineAppDetect /t REG_DWORD /d 0 /f" %
            officever[self.version]
        )
        self.a.execute(
            "REG ADD \"HKEY_CURRENT_USER\\Software\\"
            "Microsoft\\Office\\%s\\Common\\Internet\" "
            "/v IDN_AlertOff /t REG_DWORD /d 1 /f" %
            officever[self.version]
        )
        self.a.execute(
            "REG ADD \"HKEY_CURRENT_USER\\Software\\"
            "Microsoft\\Office\\%s\\Common\\Research\\Options\" "
            "/v NoDiscovery /t REG_DWORD /d 1 /f" %
            officever[self.version]
        )
        self.a.execute(
            "REG ADD \"HKEY_CURRENT_USER\\Software\\"
            "Microsoft\\Office\\%s\\Common\\Research\\Options\" "
            "/v DiscoveryNeedOptIn /t REG_DWORD /d 1 /f" %
            officever[self.version]
        )
        # dont use online dictionaries
        self.a.execute(
            "REG ADD \"HKEY_CURRENT_USER\\Software\\"
            "Microsoft\\Office\\%s\\Common\\Research\\Translation\" "
            "/v UseOnline /t REG_DWORD /d 0 /f" %
            officever[self.version]
        )
        self.a.execute(
            "REG ADD \"HKEY_CURRENT_USER\\Software\\"
            "Microsoft\\Office\\%s\\Common\" "
            "/v UpdateReliabilityData /t REG_DWORD /d 0 /f" %
            officever[self.version]
        )

        # disable activeX warnings, disable AX safe mode
        # https://www.greyhathacker.net/?p=948
        self.a.execute(
            "REG ADD \"HKEY_CURRENT_USER\\Software\\"
            "Microsoft\\Office\\Common\\Security\" "
            "/v DisableAllActiveX /t REG_DWORD /d 0 /f"
        )
        self.a.execute(
            "REG ADD \"HKEY_CURRENT_USER\\Software\\"
            "Microsoft\\Office\\Common\\Security\" "
            "/v UFIControls /t REG_DWORD /d 1 /f"
        )

        # disable Protected View for all office products files
        for product in ["Access", "Excel", "Outlook", "PowerPoint", "Publisher", "Word"]:
            self.a.execute(
                "REG ADD \"HKEY_CURRENT_USER\\Software\\"
                "Microsoft\\Office\\%s\\%s\\Security\\ProtectedView\" "
                "/v DisableAttachmentsInPV /t REG_DWORD /d 1 /f" %
                (officever[self.version], product)
            )
            self.a.execute(
                "REG ADD \"HKEY_CURRENT_USER\\Software\\"
                "Microsoft\\Office\\%s\\%s\\Security\\ProtectedView\" "
                "/v DisableInternetFilesInPV /t REG_DWORD /d 1 /f" %
                (officever[self.version], product)
            )
            self.a.execute(
                "REG ADD \"HKEY_CURRENT_USER\\Software\\"
                "Microsoft\\Office\\%s\\%s\\Security\\ProtectedView\" "
                "/v DisableUnsafeLocationsInPV /t REG_DWORD /d 1 /f" %
                (officever[self.version], product)
            )

        for product in ["Excel", "Powerpoint", "Word"]:
            # disable DEP and macro warnings
            self.a.execute(
                "REG ADD \"HKEY_CURRENT_USER\\Software\\"
                "Microsoft\\Office\\%s\\%s\\Security\" "
                "/v EnableDEP /t REG_DWORD /d 0 /f" %
                (officever[self.version], product)
            )
            self.a.execute(
                "REG ADD \"HKEY_CURRENT_USER\\Software\\"
                "Microsoft\\Office\\%s\\%s\\Security\" "
                "/v VBAWarnings /t REG_DWORD /d 1 /f" %
                (officever[self.version], product)
            )
            self.a.execute(
                "REG ADD \"HKEY_CURRENT_USER\\Software\\"
                "Microsoft\\Office\\%s\\%s\\Security\" "
                "/v AccessVBOM /t REG_DWORD /d 1 /f" %
                (officever[self.version], product)
            )

            # Dont show warnings for files from the network
            self.a.execute(
                "REG ADD \"HKEY_CURRENT_USER\\Software\\"
                "Microsoft\\Office\\%s\\%s\\Security\\Trusted Locations\" "
                "/v AllowNetworkLocations /t REG_DWORD /d 1 /f" %
                (officever[self.version], product)
            )

        # Dont block older Word documents
        self.a.execute(
            "REG ADD \"HKEY_CURRENT_USER\\Software\\"
            "Microsoft\\Office\\%s\\Word\\Security\\FileBlock\" "
            "/v OpenInProtectedView /t REG_DWORD /d 2 /f" %
            officever[self.version]
        )
        self.a.execute(
            "REG ADD \"HKEY_CURRENT_USER\\Software\\"
            "Microsoft\\Office\\%s\\Word\\Security\\FileBlock\" "
            "/v Word2Files /t REG_DWORD /d 0 /f" %
            officever[self.version]
        )
        self.a.execute(
            "REG ADD \"HKEY_CURRENT_USER\\Software\\"
            "Microsoft\\Office\\%s\\Word\\Security\\FileBlock\" "
            "/v Word60Files /t REG_DWORD /d 0 /f" %
            officever[self.version]
        )
        self.a.execute(
            "REG ADD \"HKEY_CURRENT_USER\\Software\\"
            "Microsoft\\Office\\%s\\Word\\Security\\FileBlock\" "
            "/v Word95Files /t REG_DWORD /d 0 /f" %
            officever[self.version]
        )

        # Dont block older Excel documents
        self.a.execute(
            "REG ADD \"HKEY_CURRENT_USER\\Software\\"
            "Microsoft\\Office\\%s\\Excel\\Security\\FileBlock\" "
            "/v OpenInProtectedView /t REG_DWORD /d 2 /f" %
            officever[self.version]
        )
        self.a.execute(
            "REG ADD \"HKEY_CURRENT_USER\\Software\\"
            "Microsoft\\Office\\%s\\Word\\Security\\FileBlock\" "
            "/v XL2Macros /t REG_DWORD /d 0 /f" %
            officever[self.version]
        )
        self.a.execute(
            "REG ADD \"HKEY_CURRENT_USER\\Software\\"
            "Microsoft\\Office\\%s\\Word\\Security\\FileBlock\" "
            "/v XL2Worksheets /t REG_DWORD /d 0 /f" %
            officever[self.version]
        )
        self.a.execute(
            "REG ADD \"HKEY_CURRENT_USER\\Software\\"
            "Microsoft\\Office\\%s\\Word\\Security\\FileBlock\" "
            "/v XL3Macros /t REG_DWORD /d 0 /f" %
            officever[self.version]
        )
        self.a.execute(
            "REG ADD \"HKEY_CURRENT_USER\\Software\\"
            "Microsoft\\Office\\%s\\Word\\Security\\FileBlock\" "
            "/v XL3Worksheets /t REG_DWORD /d 0 /f" %
            officever[self.version]
        )
        self.a.execute(
            "REG ADD \"HKEY_CURRENT_USER\\Software\\"
            "Microsoft\\Office\\%s\\Word\\Security\\FileBlock\" "
            "/v XL4Macros /t REG_DWORD /d 0 /f" %
            officever[self.version]
        )
        self.a.execute(
            "REG ADD \"HKEY_CURRENT_USER\\Software\\"
            "Microsoft\\Office\\%s\\Word\\Security\\FileBlock\" "
            "/v XL4Workbooks /t REG_DWORD /d 0 /f" %
            officever[self.version]
        )
        self.a.execute(
            "REG ADD \"HKEY_CURRENT_USER\\Software\\"
            "Microsoft\\Office\\%s\\Word\\Security\\FileBlock\" "
            "/v XL4Worksheets /t REG_DWORD /d 0 /f" %
            officever[self.version]
        )

        # Allow data connections without warnings in Excel
        # https://www.experts-exchange.com/questions/28247804/Enable-Data-Connections-for-all-users.html
        self.a.execute(
            "REG ADD \"HKEY_CURRENT_USER\\Software\\"
            "Microsoft\\Office\\%s\\Excel\\Security\" "
            "/v DataConnectionWarnings /t REG_DWORD /d 0 /f" %
            officever[self.version]
        )

        # auto update workbook links
        # https://support.microsoft.com/en-us/help/826921/how-to-control-the-startup-message-about-updating-linked-workbooks-in-excel
        self.a.execute(
            "REG ADD \"HKEY_CURRENT_USER\\Software\\"
            "Microsoft\\Office\\%s\\Excel\\Security\" "
            "/v WorkbookLinkWarnings /t REG_DWORD /d 0 /f" %
            officever[self.version]
        )

        # Enable macros in Outlook
        self.a.execute(
            "REG ADD \"HKEY_CURRENT_USER\\Software\\"
            "Microsoft\\Office\\%s\\Outlook\\Security\" "
            "/v Level /t REG_DWORD /d 1 /f" %
            officever[self.version]
        )

        # disable AV Notification in outlook
        # https://www.slipstick.com/developer/change-programmatic-access-options/
        self.a.execute(
            "REG ADD \"HKEY_LOCAL_MACHINE\\SOFTWARE\\"
            "Wow6432Node\\Microsoft\\Office\\%s\\Outlook\\Security\" "
            "/v ObjectModelGuard /t REG_DWORD /d 2 /f" %
            officever[self.version]
        )

        if self.i.vm == "virtualbox":
            self.m.detach_iso()

class Office2007(Office, Dependency):
    """Backwards compatibility."""
    name = "office2007"
