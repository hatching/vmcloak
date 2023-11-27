Requirements
============

In order to run VMCloak you'll at the very least require the following
software:

* Python 3.6 or higher (tested with 3.11).
* mkisofs *or* genisoimage
* QEMU 2.11 or higher (tested with 8.1.3).
* **root** access to :ref:`mount the Windows Installer ISO image <conf-mounted-iso>`


..
    Note:
    VirtualBox support is temporarily disabled.

    To create a :ref:`Hardware Profile <hwconfig-create>` **root** is required as
    well, as well as the following tools:

    * dmidecode
    * lshw
