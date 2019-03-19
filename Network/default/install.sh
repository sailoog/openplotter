#!/bin/sh
sudo cp dhcpcd.conf /etc
sudo cp sysctl.conf /etc
sudo cp .openplotter/start-ap-managed-wifi.sh ~/.openplotter
sudo cp network/interfaces /etc/network

if [ -e /etc/network/interfaces.d/ap ]
then
    sudo rm /etc/network/interfaces.d/ap
fi

if [ -e /etc/network/interfaces.d/station ]
then
    sudo rm /etc/network/interfaces.d/station
fi

if [ -e /etc/udev/rules.d/72-static-name.rules ]
then
    sudo rm /etc/udev/rules.d/72-static-name.rules
fi

if [ -e /etc/udev/rules.d/90-wireless.rules ]
then
    sudo rm /etc/udev/rules.d/90-wireless.rules
fi

if [ -e /lib/dhcpcd/10-wpa_supplicant ]
then
    sudo mv /lib/dhcpcd/10-wpa_supplicant /lib/dhcpcd/dhcpcd-hooks
fi

if [ -e /etc/udev/rules.d/11-openplotter-usb0.rules ]
then
    sudo rm /etc/udev/rules.d/11-openplotter-usb0.rules
fi

sudo systemctl disable dnsmasq
sudo systemctl disable hostapd

/bin/bash delete_hostname_dot_local.sh