KVM
===

This document describes how VMCloak supports KVM through libvirt.

Dependencies:

* qemu-kvm
* qemu-utils
* libvirt-daemon-system
* libvirt-clients
* virtinst

Unsupported features:

* Shared directories
* Serial port


Managing KVM as regular user
----------------------------

.. TODO: all URL to official document

In order to be able to manage KVM as a regular user, some Polkit configuration
is required.
One option is to allow all users in the ``kvm`` group to manage VMs,
or you can authorize any another group or user.

On older polkit versions (0.105, found on Debian and Ubuntu), create
``/etc/polkit-1/localauthority/50-local.d/org.libvirt.unix.manage.pkla``
with the following contents:

.. code-block::

    [Allow users in KVM group to manage Virtual Machines]
    Identity=unix-group:kvm
    Action=org.libvirt.unix.manage
    ResultAny=no
    ResultInactive=no
    ResultActive=yes

For newer polkit versions, create
``/etc/polkit-1/rules.d/49-org.libvirt.unix.manager.rules``
with the following contents:

.. code-block::

    // Allow users in kvm group to manage the libvirt
    // daemon without authentication
    polkit.addRule(function(action, subject) {
        if (action.id == "org.libvirt.unix.manage" &&
            subject.isInGroup("kvm")) {
                return polkit.Result.YES;
        }
    });


Networking
----------

VMCloak supports assigning VMs to specific networks via the ``--adapter``
option.
However, it will not create or start networks automatically.


VNC
---

You can use the vrde/vrde-port options to enable VNC.
Note that libvirt requires that the port is above 5900.
