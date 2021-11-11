VM Creation
===========

This page describes how to:

* Create analysis VMs for Cuckoo 3 using VMCloak.
* Install software/modify the VM.
* Import created VMs into Cuckoo 3.

These make the assumption that we are creating QEMU VMs. This is the default Cuckoo 3 machinery module and is currently
the only virtualization platform VMCloak supports. VirtualBox support is
temporarily disabled.

Prerequisites
-------------

All steps mentioned in :ref:`qemu-networking` have been performed. These are
required to start the VM creation process.

1. Preparing the OS ISO
-----------------------

We must have the install ISO before we can install an OS. Let's start with
retrieving one. Cuckoo 3 and VMCloak (currently) support Windows 7 and 10.

Cuckoo 3 uses a new kernel driver. At the moment this supports the following OS versions:

* Windows 10 1703 (No updates).
* Windows 7 SP1 (No updates).

1.1 OS ISO downloading
^^^^^^^^^^^^^^^^^^^^^^

VMCloak can retrieve these needed OS ISOs for us with it ``vmcloak isodownload`` tool.

.. code-block:: bash

  vmcloak isodownload --help

    Usage: vmcloak isodownload [OPTIONS]

      Download the recommended operating system ISOs for Cuckoo 3. These are
      specific OS versions/builds.

    Options:
      --download-to TEXT  The filepath to write the ISO to. Will go to
                          /home/cuckoo/.vmcloak/iso otherwise.
      --win7x64           The recommended Windows 7 x64 ISO for Cuckoo 3
      --win10x64          The recommended Windows 10 x64 ISO for Cuckoo 3

Download an ISO. The download can take a while.

.. code-block:: bash

  vmcloak isodownload --win10x64 /home/cuckoo/win10x64.iso


1.2 Mounting the ISO
^^^^^^^^^^^^^^^^^^^^

In order to mount a Windows Installer ISO image a directory should be created
with **root**, and then the image should be mounted on that directory, with
root as well. The following bash snippet depicts how to setup an ISO mount on
a Ubuntu/Debian system.

.. code-block:: bash

    sudo mkdir /mnt/win10x64
    sudo mount -o loop,ro /home/cuckoo/win10x64.iso /mnt/win10x64

2. Creating an image
--------------------

An image is the disk where we install the chosen OS on. Any dependencies we choose are also installed on this.
When we have made all modification we want, we make the VMs from this image. After this, the image must not be edited.

2.1 Installing the OS
^^^^^^^^^^^^^^^^^^^^^

Image creation and OS installation is done using the ``vmcloak init`` command.
This command will start the install of the OS. It will perform a full installation, set some generic settings
such as disabling Windows defender, and add the Cuckoo agent.

See the example below for its help page.

.. code-block:: bash

    vmcloak init --help

    Usage: vmcloak init [OPTIONS] NAME ADAPTER

      Create a new image with 'name' attached to network (bridge) 'adapter'.

    Options:
      --python-version TEXT  Python version to install on VM.
      --product TEXT         Windows 7 product version.
      --serial-key TEXT      Windows Serial Key.
      --iso-mount TEXT       Mounted ISO Windows installer image.
      --win10x64             This is a Windows 10 64-bit instance.
      --win7x64              This is a Windows 7 64-bit instance.
      --vrde-port INTEGER    Specify the remote display port.
      --vrde                 Enable the remote display (RDP or VNC).
      --vm-visible           Start the Virtual Machine in GUI mode.
      --resolution TEXT      Screen resolution.  [default: 1024x768]
      --tempdir TEXT         Temporary directory to build the ISO file.  [default:
                             /home/cuckoo/.vmcloak/iso]
      --hddsize INTEGER      HDD size in GB  [default: 256]
      --ramsize INTEGER      Memory size
      --cpus INTEGER         CPU count.  [default: 1]
      --dns2 TEXT            Secondary DNS server.  [default: 8.8.4.4]
      --dns TEXT             DNS Server.  [default: 8.8.8.8]
      --gateway TEXT         Guest default gateway IP address (IP of bridge
                             interface)
      --network TEXT         The network to use in CIDR notation. Example:
                             192.168.30.0/24. Uses VM platform default if not
                             given.
      --port INTEGER         Port to run the Agent on.  [default: 8000]
      --ip TEXT              Guest IP address to use
      --iso TEXT             Specify install ISO to use.
      --vm TEXT              Virtual Machinery.  [default: qemu]


We tell VMCloak to add listening VNC port (see :ref:`qemu-vnc`) so that we can connect to the install in case it takes a long time.
The install might be frozen, etc. We will be making an image called 'win10base' on bridge 'qemubr0'.

.. code-block:: bash

  vmcloak --debug init --win10x64 --hddsize 128 --cpus 2 --ramsize 4096 --network 192.168.30.0/24 --vm qemu --vrde --vrde-port 1 --ip 192.168.30.2 --iso-mount /mnt/win10x64 win10base qemubr0

This command can take a long time to complete depending on your system (20-60 minutes).

When the command finishes, the image should be available in the list of images.
View the list of images and their attributes using:

.. code-block:: bash

  vmcloak list images


3. Installing software (dependencies)
-------------------------------------

Software/dependencies can be installed on a finished image. A 'dependency' is what VMCloak uses to refer to a
component that performs a (configuration) change or installs software.

All dependencies and their versions can be viewed with the ``vmcloak list deps`` command.
Not all dependencies are available for Windows 10 and 7 x64.

To view what software is already installed on the image, run ``vmcloak list images``.

3.1 Installing recommended dependencies
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The installation of dependecies will be performed using the ``vmcloak install`` command.
This command starts the given image and installs the specified dependencies on it.

See the example below for the help page:

.. code-block:: bash

    vmcloak install --help
    Usage: vmcloak install [OPTIONS] NAME [DEPENDENCIES]...

    Install dependencies on an image. Dependency settings are specified using
    name.setting=value. Multiple settings per dependency can be given.

    Options:
      --vm-visible
      --vrde               Enable the VirtualBox Remote Display Protocol.
      --vrde-port INTEGER  Specify the VRDE port.
      --force-reinstall    Reinstall even if already installed by VMCloak.
      --no-machine-start   Do not try to start the machine. Assume it is somehow
                           already started and reachable.
      -r, --recommended    Install and perform recommended software and
                           configuration changes for the OS.

In this example we will be using the ``--recommended`` flag.
This will install the dependencies that are recommended for Cuckoo 3 for the OS of the image.

In this case that will install/configure: ie11, .NET, Java, VC redistributables 2013-2019, Edge,
update (Let's encrypt) root certs, Adobe PDF, a wallpaper, OS optimization (stopping updates,
removing unneeded components), and disable unneeded services such as Cortana. This can all be
viewed afterwards with the list image command.

.. code-block:: bash

  vmcloak --debug install win10base --recommended

This command can take a long time to complete depending on your system.
After this command has completed the installed software can be viewed using. ``vmcloak list images``.

3.2 Installing other dependencies
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

VMCloak supports multiple dependencies. One of these is Microsoft Office.

To install office, you must provide the following settings to the install command: an isopath, a (valid) serialkey, and a version.

**Product activation**

Office can be difficult with activation. VMCloak can activate it, but for this the VM must have internet (iptables traffic forwarding) access.
It is recommended that internet to a VM is disabled after the installation and activation of Office completes.
Activation has not been tested with newer versions of Office. You might need to manually activate it using the ``vmcloak modify`` command and VNC. See :ref:`vmcreation-manualchanges`.

If VMCloak should activate Office, the activate=1 option must be provided.

Example of an Office 2010 install command:

.. code-block:: bash

    vmcloak --debug install win10base office office.version=2010 office.isopath=/home/cuckoo/office2010.iso office.serialkey=XXXXX-XXXXX-XXXXX-XXXXX-XXXXX office.activate=1


.. _vmcreation-manualchanges:

3.3 Manual changes
^^^^^^^^^^^^^^^^^^

It is possible to make manual changes to the VM. This can be useful for performing things such as adding random files,
verifying everything meets your requirements, etc. This step can be skipped if there is nothing that needs to be done.

To do this, we use the ``vmcloak modify`` command. This starts the image and waits for it to be shut down.
The ``--vrde`` in combination with ``--vrde-port`` <vnc port offset> arguments can be used to enable VNC. QEMU adds 5900 to the port specified.
So that means that ``--vrde-port 1`` will result in the VNC port being 5901.

See the help page example below:

.. code-block:: bash

    vmcloak modify --help
    Usage: vmcloak modify [OPTIONS] NAME

      Start the given image name to apply manual changes

    Options:
      --vm-visible
      --vrde               Enable the VirtualBox Remote Display Protocol.
      --vrde-port INTEGER  Specify the VRDE port.
      --iso-path TEXT      Path to an iso file to attach as a drive to the
                           machine.

4. Snapshot creation
--------------------

We are creating the actual analysis VMs in this step. We do this with the ``vmcloak snapshot``.
This command will create one or more VMs that each have their own name, IP, disk, and a memory snapshot made of a
running VM with the correct IP. The disk, memory snapshot, and VM info JSON file are stored in a directory named after
the VM in ``VMCLOAKCWD/vms/<virtual machinery>/<name>``

**VM JSON file**

The VM json file contains the VM specifications and exact QEMU startup arguments. You can add extra arguments here if needed.
Be careful with this, as changing devices (or their buses) can break the memory snapshot.

Previously created snapshots can be listed with the ``vmcloak list snapshot`` command.

See the help page example below:

.. code-block:: bash

    vmcloak snapshot --help
    Usage: vmcloak snapshot [OPTIONS] NAME VMNAME [IP]

      Create one or more snapshots from an image

    Options:
      --resolution TEXT    Screen resolution.
      --ramsize INTEGER    Amount of virtual memory to assign. Same as image if
                           not specified.
      --cpus INTEGER       Amount of CPUs to assign. Same as image if not
                           specified.
      --hostname TEXT      Hostname for this VM.
      --vm-visible         Start the Virtual Machine in GUI mode.
      --count INTEGER      The amount of snapshots to make.  [default: 1]
      --vrde               Enable the VirtualBox Remote Display Protocol.
      --vrde-port INTEGER  Specify the VRDE port.
      --interactive        Enable interactive snapshot mode.
      --nopatch            Do not patch the image to be able to load Threemon

In this example we will create 5 snapshots with the same amount of ram and cpus as the image.
To do this, the ``--count`` argument is used. VMCloak will automatically increment VM names and IPs.
VMCloak will only use IPs that are not in use by other images/snapshots yet. It keeps track of this because it remembers
what ``--network`` was specified at image creation.

The snapshot command will perform final changes on the image such as patching Windows.
This patching is required so Cuckoo 3 can load its kernel monitor.

.. code-block:: bash

  vmcloak --debug snapshot --count 5 win10base win10vm_ 192.168.30.10

The command will take a while. It will boot the image, change its IP and hostname, reboot and make a snapshot. And it does this for
every snapshot.

5. VM importing in Cuckoo 3.
----------------------------

Cuckoo 3 can import VMs created by VMCloak. So we do not have to manually
edit configs or add them one by one.

To do this, Cuckoo 3 needs to know the path where the VM files are stored. It uses a
JSON file to retrieve all information about each VM. The VMs are stored in the VMCLOAKCWD.
This is located at ``$USERHOME/.vmcloak``. VMs are in the child dir ``vms/<virtual machinery name``.

That means the VMs we created are located in ``$USERHOME/.vmcloak/vms/qemu``.

First, verify your VMs were all created.

.. code-block:: bash

    vmcloak list snapshots
    win10base 192.168.30.2(qemubr0) (QEMU)
    - win10vm_1 192.168.30.10
    - win10vm_2 192.168.30.11
    - win10vm_3 192.168.30.12
    - win10vm_4 192.168.30.13
    - win10vm_5 192.168.30.14

The importing to Cuckoo will do done using Cuckoo's ``cuckoo machine import`` command.
See its help page below

.. code-block:: bash

    cuckoo machine import --help
    Usage: cuckoo machine import [OPTIONS] MACHINERY_NAME VMS_PATH [MACHINE_NAMES]...

    Import all or 'machine names' from the specified VMCloak vms path to the
    specified machinery module.


We need to run the following command to tell Cuckoo to import the VMs. In this example our user is called 'cuckoo'.

.. code-block:: bash

  cuckoo machine import qemu /home/cuckoo/.vmcloak/vms/qemu

After this command, you might also want to remove the example VM, so that Cuckoo can be started.

.. code-block::

  cuckoo machine delete qemu example1

The VMs are now usable by Cuckoo 3. Cuckoo does need to be restarted to discover them.
