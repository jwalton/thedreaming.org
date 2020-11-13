---
title: "Ubuntu - Wake from bluetooth keyboard"
tags:
  - ubutnu
  - bluetooth
  - kodi
---

I recently installed Ubuntu on an old Mac Mini, and I ran into a problem where I couldn't get a bluetooth keyboard to wake the device (actually a Harmony Hub remote, but it presents itself as a bluetooth keyboard).  I did some digging and found [this offline page](https://web.archive.org/web/20130807055107/http://bernaerts.dyndns.org/linux/220-ubuntu-resume-usb-hid) which describes a method for enabling wake-from-suspend for USB devices.  This is an attempt at slightly simplifying this.

<!--more-->

Quoting from that page:

> Under SYSFS, a typical USB device connexion chain will ressemble something like /sys/devices/pci0000:00/0000:00:1d.0/usb5/5-0:1.0.
>
> To be able to resume your computer with this USB device, you will need to have a wake-up power supply on every active device of the chain. In this way, even with the computer suspended, a minimum power will be supplied to the devices, so that they can send the wake-up signal.
>
> With SYSFS, the power supply of an active device is controlled by its ./power/wakeup file. By simply writing enabled in that file, you are configuring it to get the wakeup power supply during suspended mode.
>
> As an example, to enable wakeup power supply for the root PCI bus we need to write enabled in /sys/devices/pci0000:00/0000:00:1d.0/power/wakeup
>
> `sudo sh -c "echo enabled > /sys/devices/pci0000:00/0000:00:1d.0/power/wakeup"`
>
> So to enable a USB device to be used to resume your computer, you simply need to enable every active device on the connexion chain from the PCI bus till the device itself.
>
> It's as simple as that.

## Find USB Devices

Your bluetooth adapter probably shows up as a USB device:

```sh
$ lsusb
Bus 002 Device 005: ID 05ac:8242 Apple, Inc. Built-in IR Receiver
Bus 002 Device 008: ID 05ac:828a Apple, Inc.
Bus 002 Device 004: ID 0a5c:4500 Broadcom Corp. BCM2046B1 USB 2.0 Hub (part of BCM2046 Bluetooth)
Bus 002 Device 003: ID 0424:2512 Microchip Technology, Inc. (formerly SMSC) USB 2.0 Hub
Bus 003 Device 002: ID 046d:c52b Logitech, Inc. Unifying Receiver
...
```

These are the devices I found on my machine.  Below are two scripts which I stole from Nicolas Bernaerts's website, since it's down (mainly I posted them here so I can find them again if I need to).  Create these two files, run `sudo apt install zenity` if you don't have it installed already, and then run `/usr/local/sbin/select-resume-devices` from a terminal window.  Note that you need to run this from the desktop because the script uses zenity to display a dialog to let you pick which devices to enable.  Once you pick devices, this will write a file named `/etc/udev/rules.d/90-hid-wakeup-enable.rules` which will configure these devices at boot time.  After you run the script, you need to reboot for changes to take effect.

In my case, I tried enabling sleep for the "Apple, Inc." device and the BCM2046B1 Hub, and this fixed my problem.  Probably I only needed to enable one of them, but I had to reboot for this change to take effect, and I'm too lazy to figure out which one I really need.  :P  Note that in my case, to enable wake for the bluetooth hub, I had to modify this line in `select-resume-devices`:

```diff
+LIST_DEVICE=(`lsusb | grep -v "0000:0000" | sed 's/^.*[0-9a-f]\:[0-9a-f]* \(.*\)$/\1/g'`)
-LIST_DEVICE=(`lsusb | grep -v "0000:0000" | grep -iv "hub" | sed 's/^.*[0-9a-f]\:[0-9a-f]* \(.*\)$/\1/g'`)
```

Here are the scripts:

/usr/local/sbin/enable-wakeup:

```bash
#!/bin/bash
#
# Script to enable a USB devices to be used to resume computer from sleep
#
# Depends on udevadm package
# 09/05/2012 - V1.0 by Nicolas Bernaerts

# if device has been removed, exit
[ "$ACTION" = "remove" ] && exit 0

# set PATH as it is not set for udev scripts
PATH="/usr/sbin:/usr/bin:/sbin:/bin"

# set device SYSFS path
DEVICE_SYSFS="/sys$1"
CURRENT_SYSFS=$DEVICE_SYSFS

# get device product and vendor name from parent SYSFS
DEVICE_VENDOR=`udevadm info --query=all -p "$CURRENT_SYSFS/../" | grep "ID_VENDOR_ID=" | cut -d "=" -f 2`
DEVICE_PRODUCT=`udevadm info --query=all -p "$CURRENT_SYSFS/../" | grep "ID_MODEL_ID=" | cut -d "=" -f 2`
DEVICE_LABEL=`lsusb | grep "${DEVICE_VENDOR}:${DEVICE_PRODUCT}" | sed 's/^.*[0-9a-f]\:[0-9a-f]* \(.*\)$/\1/g'`

# loop thru the SYSFS path, up to PCI bus
CARRY_ON=1
while [ $CARRY_ON -eq 1 ]
do
  # get the first three letters of current SYSFS folder
  FIRST_LETTERS=`basename $CURRENT_SYSFS | sed 's/^\(...\).*$/\1/g'`

  # if current SYSFS is PCI bus, stop the loop
  if [ "$FIRST_LETTERS" = "pci" ] || [ "$FIRST_LETTERS" = "/" ] ; then
    CARRY_ON=0

  # else,
  else
    # if possible, enable wakeup for current SYSFS
    WAKEUP_FILE="${CURRENT_SYSFS}/power/wakeup"
    if [ -f $WAKEUP_FILE ]; then
      echo "enabled" > $WAKEUP_FILE
    fi

    # go to father directory of current SYSFS
    CURRENT_SYSFS=`dirname $CURRENT_SYSFS`
  fi
done

# log the action
LOG_HEADER="USB device ${DEVICE_VENDOR}:${DEVICE_PRODUCT}"
logger "${LOG_HEADER} - Description : ${DEVICE_LABEL}"
logger "${LOG_HEADER} - SysFS path  : ${DEVICE_SYSFS}"
logger "${LOG_HEADER} - Device is enabled to handle suspend/resume"
```

/usr/local/sbin/select-resume-devices:

```bash
#!/bin/bash
#
# Script to create resume udev rules for USB devices
#
# Depends on zenity
# 09/05/2012 - V1.0 by Nicolas Bernaerts

# udev file to generate
UDEV_FILE="/etc/udev/rules.d/90-hid-wakeup-enable.rules"

# set separator as CR
IFS=$'\n'

# list all USB devices, excluding root & hubs
LIST_DEVICE=(`lsusb | grep -v "0000:0000" | grep -iv "hub" | sed 's/^.*[0-9a-f]\:[0-9a-f]* \(.*\)$/\1/g'`)

# loop thru the devices array to generate zenity parameter
for DEVICE in "${LIST_DEVICE[@]}"
do
  # if needed, remove [xxx] from device name as it gives trouble with grep
  DEVICE=`echo "$DEVICE" | sed 's/\[.*\]//g'`

  # add it to the parameters list
  ARR_PARAMETER=( FALSE ${DEVICE} ${ARR_PARAMETER[@]} )
done

# display the dialog box to choose devices
TITLE="Wakeup - Enable USB devices"
TEXT="Please, select USB devices you want to use to resume your computer"
CHOICE=`zenity --list --width=600 --height=250 --text=$TEXT --title=$TITLE --checklist --column "Select" --column "Device name" "${ARR_PARAMETER[@]}"`

# slit the device choice into an array
IFS="|" read -a ARR_CHOICE <<< "$CHOICE"

# if at least one device has been selected, initialise udev rules file
[ ${#ARR_CHOICE[@]} -gt 0 ] && echo "# udev rule for USB wake-up of selected devices" > $UDEV_FILE
[ ${#ARR_CHOICE[@]} -gt 0 ] && echo "#" >> $UDEV_FILE

# loop thru the selected devices to create udev rules
for DEVICE_NAME in "${ARR_CHOICE[@]}"
do
  # get current device data
  DEVICE_DATA=`lsusb | grep "${DEVICE_NAME}" | sed 's/^.*ID \([0-9a-f]*\):\([0-9a-f]*\).*$/\1|\2/g'`
  DEVICE_VENDOR=`echo $DEVICE_DATA | cut -d"|" -f1`
  DEVICE_PRODUCT=`echo $DEVICE_DATA | cut -d"|" -f2`

  # create udev rule for current device
  DEVICE_RULE="SUBSYSTEM==\"usb\", ATTRS{idVendor}==\"$DEVICE_VENDOR\", ATTRS{idProduct}==\"$DEVICE_PRODUCT\" RUN+=\"/usr/local/sbin/enable-wakeup \$env{DEVPATH}\" "

  # add udev rule for current device
  echo "# ${DEVICE_NAME}" >> $UDEV_FILE
  echo ${DEVICE_RULE} >> $UDEV_FILE
done

# if at least one device has been selected, display notification
TITLE="USB resume enabled"
TEXT="Your USB devices are resume enabled.\nTo finalize configuration you have to do one of these actions :\n- replug USB devices\n- reboot the computer"
[ ${#ARR_CHOICE[@]} -gt 0 ] && notify-send --icon=media-eject $TITLE $TEXT
```
