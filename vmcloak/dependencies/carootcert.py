# Copyright (C) 2021 Hatching B.V.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import logging
from pathlib import Path

from vmcloak.abstract import Dependency
from vmcloak.exceptions import DependencyError

log = logging.getLogger(__name__)

class CaRootCert(Dependency):
    name = "carootcert"
    files = [
        {
            # Let's encrypt root certificate. Their 'old' one expired in 2021.
            "urls": ["https://letsencrypt.org/certs/isrgrootx1.der"],
            "sha1": "cabd2a79a1076a31f21d253635cb039d4329a5e8",
            "filename": "isrgrootx1.der",
            "description": "Let's encrypt CA ISRG root."
        },
        {
            # Certificate needed to install some updates and dotnet packages.
            # See https://docs.microsoft.com/en-us/archive/blogs/vsnetsetup/a-certificate-chain-could-not-be-built-to-a-trusted-root-authority-2
            "urls": [
                "https://hatching.io/hatchvm/MicRooCerAut2011_2011_03_22.crt",
                "https://www.microsoft.com/pki/certs/MicRooCerAut2011_2011_03_22.crt"
            ],
            "sha1": "8f43288ad272f3103b6fb1428485ea3014c0bcfe",
            "filename": "MicRooCerAut2011_2011_03_22.crt",
            "description": "Microsoft root certificate"
        }
    ]

    def run(self):
        for ca_cert in self.files:
            ca_cert_path = Path(self.deps_path, ca_cert["filename"])
            winpath = f"c:\\{ca_cert_path.name}"

            self.upload_file(ca_cert_path, winpath)
            try:
                log.debug(
                    f"Adding {ca_cert_path.name} to certificate store. "
                    f"{ca_cert.get('description')}"
                )
                res = self.a.execute(
                    "c:\\Windows\\System32\\certutil.exe "
                    f"-addstore root {winpath}"
                )
                if res.get("exit_code", 0):
                    raise DependencyError(
                        f"Failed to install CA root certificate: "
                        f"{ca_cert_path}. Description: "
                        f"{ca_cert.get('description')}"
                        f"Certutil: stdout={res.get('stdout')}. "
                        f"Stderr={res.get('stderr')}"
                    )
            finally:
                self.a.remove(winpath)
