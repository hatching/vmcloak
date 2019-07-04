#!/bin/bash
# Copyright (C) 2014-2015 Mohsen Ahmadi.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.
set -e

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 
   exit 1
fi

VM_PATH="/etc/vmware/networking"
PATTERN="enabled"
KEY_DIR=$HOME/.vmware/keys/
PUB_KEY="MOK.der"
PRV_KEY="MOK.priv"
DRIVERS=(vmmon vmnet)
SBOOT=$(mokutil --sb-state | grep -q $PATTERN && echo $?)
SIGN="/usr/src/linux-headers-$(uname -r)/scripts/sign-file"

iface() {
    local result=$(cat /sys/class/net/$1/operstate)
    local stat=1
    if [ $result = "unknown" ] && [ $? ]; then
        stat=0
    else
        stat=1
    fi
    return $stat
}

valid_ip ()
{
    local  ip=$1
    local  stat=1

    if [[ $ip =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]; then
        OIFS=$IFS
        IFS='.'
        ip=($ip)
        IFS=$OIFS
        [[ ${ip[0]} -le 255 && ${ip[1]} -le 255 \
            && ${ip[2]} -le 255 && ${ip[3]} -le 255 ]]
        stat=$?
    fi
    return $stat
}


usage () {
    echo "Usage: $0 --nat [subnet] [netmask] --hostonly [subnet] [netmask]"
    echo "    $0 --nat 192.168.57.0 255.255.255.0 --hostonly 192.168.45.0 255.255.255.0"
    echo
    echo "Defaults to:"
    echo "    nat: 192.168.156.0 255.255.255.0"
    echo "    hostonly: 192.168.19.0 255.255.255.0"
    exit
}

signfile () {
    local DRIVER=$1
    local MOD_PATH=$(modinfo -n $DRIVER)
    $($SIGN sha256 "$KEY_DIR/$PRV_KEY" "$KEY_DIR/$PUB_KEY" $MOD_PATH)
    $(modprobe -q $DRIVER)
}

secureboot () {
    local STAT=1
    if [ $SBOOT ]; then
        echo "Secure Boot is enabled!"
        echo "Generating key-pair using openssl to sign drivers..."
        if [ ! -d $KEY_DIR ]; then
            mkdir -p $KEY_DIR && pushd ${KEY_DIR}
        else
            pushd ${KEY_DIR}
        fi
        $(openssl req -new -x509 -newkey rsa:2048 -keyout $PRV_KEY \
            -outform DER -out $PUB_KEY -nodes -days 36500 -subj "/CN=VMware/")

        popd

        for drvname in "${DRIVERS[@]}"; do
            echo "Signing/loading the $drvname driver."
            $(signfile $drvname)
            if [ ! $? -eq 0 ]; then echo "Couldn't sign/load $drvname driver."; fi
        done

        $(/etc/init.d/vmware restart)
    fi
}

function substitude () {
    $(sed -i 's/\(${1}[[:space:]]\)[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}/\1${2}/g' $VM_PATH)
}

declare -A items
items[VNET_1_HOSTONLY_NETMASK]=$HOSTONLY_MASK
items[VNET_1_HOSTONLY_SUBNET]=$HOSTONLY_SUBNET
items[VNET_8_HOSTONLY_NETMASK]=$NAT_MASK
items[VNET_8_HOSTONLY_SUBNET]=$NAT_SUBNET

# Only create a new hostonly interface if it does not already exist.
if ! iface "vmnet1"; then
    secureboot
fi

while [ "$#" -gt 0 ]; do
    case "$1" in
        --nat)
            # check subnet validity
            if valid_ip $2; then
                NAT_SUBNET=$2
            else
                NAT_SUBNET="192.168.156.0"
            fi
            # check submask validity
            if valid_ip $3; then
                NAT_MASK=$3
            else
                NAT_MASK="255.255.255.0"
            fi
            shift 3
          ;;
          --hostonly)
            # check subnet validity
            if valid_ip $2; then
                HOSTONLY_SUBNET=$2
            else
                HOSTONLY_SUBNET="192.168.19.0"
            fi
            # check submask validity
            if valid_ip $3; then
                HOSTONLY_MASK=$3
            else
                HOSTONLY_MASK="255.255.255.0"
            fi
            shift 3
          ;;
        --) # end argument parsing
          shift
          break
          ;;
        -h|--help) # preserve positional arguments
          usage
          ;;
        -*|--*=) # unsupported flags
          echo "Error: Unsupported flag $1" >&2
          exit 1
          ;;
        *)
          usage
          ;;
    esac
done

# set subnet & mask for hostonly and nat ifaces
for i in ${!items[@]}; do
    substitude $i ${items[$i]}
done

vmware-networks --stop
vmware-networks --start
