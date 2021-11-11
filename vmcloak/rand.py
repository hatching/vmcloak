# Copyright (C) 2014-2016 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import random
import string

def random_string(minimum, maximum=None):
    if maximum is None:
        maximum = minimum

    count = random.randint(minimum, maximum)
    return "".join(random.choice(string.ascii_letters) for x in range(count))

_system_macs = set()

def _get_system_macs():
    """Discover system interface mac addresses."""
    global _system_macs

    if _system_macs:
        return _system_macs

    from psutil import net_if_addrs
    try:
        from socket import AF_LINK
        family_link = AF_LINK
    except ImportError:
        # Attribute is af_packet on Linux
        from socket import AF_PACKET
        family_link = AF_PACKET

    for _, if_addrs in net_if_addrs().items():
        for nicaddrs in if_addrs:
            if nicaddrs.family != family_link:
                continue

            _system_macs.add(nicaddrs.address.lower())

    return _system_macs


def random_mac():
    """Generates a random MAC address."""
    values = [random.randint(0, 15) for _ in range(12)]

    # At least for VirtualBox there's a limitation for the second character,
    # as outlined in the following thread. Thus we handle this.
    # https://forums.virtualbox.org/viewtopic.php?p=85316
    values[1] = int(random.choice("02468ace"), 16)

    return "%x%x:%x%x:%x%x:%x%x:%x%x:%x%x" % tuple(values)

def random_vendor_mac():
    skip_macs = _get_system_macs()
    # Prefixes from a few commonly used desktop and laptop vendors.
    vendor_prefixes = [
        "94:b8:6d", "B8:03:05", "E8:2A:EA", "A4:11:94", "8C:16:45",
        "C8:7E:75", "10:1D:C0", "78:9E:D0", "00:16:17", "00:1F:CF",
        "00:0A:F7", "D4:01:29", "00:E0:4C", "00:19:3C", "00:17:A4",
        "00:06:5B", "A4:BA:DB"
    ]
    random.shuffle(vendor_prefixes)
    prefix = random.choice(vendor_prefixes).lower()

    # Try a maximum amount of times and then fall back to the regular
    # mac generator.
    for _ in range(20):
        rand_mac = prefix
        for _ in range(3):
            rand_mac += f":{random.randint(0, 255):02x}"

        if rand_mac in skip_macs:
            continue

        return rand_mac

    return random_mac()

def random_serial(length=None):
    if length is None:
        length = random.randint(8, 20)

    return "".join(random.choice(string.uppercase + string.digits)
                   for _ in range(length))

def random_uuid():
    value = random_serial(32)
    return "-".join((value[:8], value[8:12], value[12:16],
                     value[16:20], value[20:32]))
