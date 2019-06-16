#!/bin/bash
#echo "copies and renames files to .openplotter/Network."
#echo "Example: bash copy_main.sh br0 wlan9 00:00:00:00:00:00 5 e"
bridge=$1
AP=$2
mac=$3
GHz=$4
extern=$5

targetfolder=~/.openplotter/Network
loadfolder=~/.config/openplotter/Network

rm -rf $targetfolder
mkdir $targetfolder
mkdir $targetfolder/.openplotter
mkdir $targetfolder/hostapd
mkdir $targetfolder/network
mkdir $targetfolder/network/interfaces.d
mkdir $targetfolder/udev
mkdir $targetfolder/udev/rules.d

#echo $bridge
#echo $AP
#echo $mac
#echo $GHz
#echo $extern

if [ "$AP" = "none" ]; then
	bash "${loadfolder}/hostname_dot_local.sh" "n"
	cp "${loadfolder}/dhcpcd_default.conf" "${targetfolder}/dhcpcd.conf"
	cp "${loadfolder}/network/interfaces_standard" "${targetfolder}/network/interfaces"	
else
	bash "${loadfolder}/hostname_dot_local.sh" "y"
	cp "${loadfolder}/udev/rules.d/11-openplotter-usb0.rules" "${targetfolder}/udev/rules.d/11-openplotter-usb0.rules"
	cp "${loadfolder}/.openplotter/iptables.sh" "${targetfolder}/.openplotter/iptables.sh"
	cp "${loadfolder}/.openplotter/start-ap-managed-wifi.sh" "${targetfolder}/.openplotter/start-ap-managed-wifi.sh"
	cp "${loadfolder}/network/interfaces.d/ap_wlan9" "${targetfolder}/network/interfaces.d/ap"

	if [ "$GHz" = "5" ]; then
		cp "${loadfolder}/hostapd/hostapd_5.conf" "${targetfolder}/hostapd/hostapd.conf"
	fi
	if [ "$GHz" = "2.4" ]; then
		cp "${loadfolder}/hostapd/hostapd_2_4.conf" "${targetfolder}/hostapd/hostapd.conf"
	fi

	if [ "$bridge" = "br0" ]; then
		bash "${loadfolder}/hostapd_Bridge.sh" y
		cp "${loadfolder}/dnsmasq_br0.conf" "${targetfolder}/dnsmasq.conf"
		cp "${loadfolder}/dhcpcd_br0_wlan9.conf" "${targetfolder}/dhcpcd.conf"
		cp "${loadfolder}/network/interfaces_bridge_wlan9_eth0" "${targetfolder}/network/interfaces"
		bash "${loadfolder}/set-router.sh" "br0"
	else
		bash "${loadfolder}/hostapd_Bridge.sh" n
		cp "${loadfolder}/dnsmasq_wlan9.conf" "${targetfolder}/dnsmasq.conf"
		cp "${loadfolder}/dhcpcd_wlan9.conf" "${targetfolder}/dhcpcd.conf"
		cp "${loadfolder}/network/interfaces_standard" "${targetfolder}/network/interfaces"
		bash "${loadfolder}/set-router.sh" "wlan9"
	fi


	if [ "$AP" = "wlan9" ]; then
		cp "${loadfolder}/udev/rules.d/72-AP_intern_wireless_wlan.rules" "${targetfolder}/udev/rules.d/72-wireless.rules"
		if [ "$bridge" = "br0" ]; then
			cp "${loadfolder}/.openplotter/start1-bridge.sh" "${targetfolder}/.openplotter/start1.sh"
		else
			cp "${loadfolder}/.openplotter/start1.sh" "${targetfolder}/.openplotter/start1.sh"
		fi
	fi	

	if [ "$AP" = "uap" ]; then
		cp "${loadfolder}/udev/rules.d/72-AP_intern_wireless_uap.rules" "${targetfolder}/udev/rules.d/72-wireless.rules"
		if [ "$bridge" = "br0" ]; then
			cp "${loadfolder}/.openplotter/start1-bridge-uap.sh" "${targetfolder}/.openplotter/start1.sh"
		else
			cp "${loadfolder}/.openplotter/start1-uap.sh" "${targetfolder}/.openplotter/start1.sh"
		fi
	fi

	if [ "$extern" = "e" ]; then
		echo 'SUBSYSTEM=="net", ACTION=="add", ATTR{address}=="'"${mac}"'", NAME="wlan9"' > "${targetfolder}/udev/rules.d/72-wireless.rules"
	fi
fi
#sleep 3
