#!/bin/sh
sudo cp dnsmasq.conf /etc
sudo cp dhcpcd.conf /etc
sudo cp sysctl.conf /etc
sudo cp .openplotter/start-ap-managed-wifi.sh ~/.openplotter
sudo cp hostapd/hostapd.conf /etc/hostapd
sudo cp network/interfaces /etc/network
sudo cp network/interfaces.d/station /etc/network/interfaces.d
sudo cp udev/rules.d/72-static-name.rules /etc/udev/rules.d


if [ -e /etc/network/interfaces.d/ap ]
then
    sudo rm /etc/network/interfaces.d/ap
fi

if [ -e /etc/udev/rules.d/90-wireless.rules ]
then
    sudo rm /etc/udev/rules.d/90-wireless.rules
fi

if [ -e /lib/dhcpcd/dhcpcd-hooks/10-wpa_supplicant ]
then
    sudo mv /lib/dhcpcd/dhcpcd-hooks/10-wpa_supplicant /lib/dhcpcd
fi
