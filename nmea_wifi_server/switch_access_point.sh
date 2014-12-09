#!/bin/bash
#
# Switch wifi connection (access point/DHCP client) script for SailPi project.
# by sailoog.com
#
# http://campus.sailoog.com/course/view.php?id=9
#
###################################################

#set default values
TYPE=SERVER
SSID=OpenPlotter
PASSWORD=openplotter
CHIPSET=regular
DRIVER=nl80211

if [[ -n $(lsusb | grep RTL8188CUS) ]]; then
	CHIPSET=RTL8188CUS
	DRIVER=rtl871xdrv
fi

if [[ -n $(lsusb | grep RTL8192CU) ]]; then
	CHIPSET=RTL8192CU
	DRIVER=rtl871xdrv
fi

# Get Input from User
clear
echo "==========================================================="
echo "$DRIVER driver for $CHIPSET chipset it will be used."
echo "==========================================================="
echo "Please answer the following questions."
echo "Hitting return will continue with the default option."
echo "==========================================================="
echo

read -p "Do you want to set OpenPlotter as a SERVER or CLIENT? [$TYPE]: " -e t1
if [ -n "$t1" ]; then TYPE="$t1";fi

if [ "$TYPE" = "SERVER" ]; then

read -p "SSID [$SSID]: " -e t1
if [ -n "$t1" ]; then SSID="$t1";fi

read -p "PASSWORD [$PASSWORD]: " -e t1
if [ -n "$t1" ]; then PASSWORD="$t1";fi

fi

# Get confirmation
clear
echo "===================================================="
echo "If you answer yes the computer will reboot!!!"
echo "Save your work."
echo "===================================================="
echo

read -p "Do you wish to continue and Setup RPi as $TYPE? (y/n) " RESP

if [ "$RESP" = "y" ]; then
	
if [ "$TYPE" = "SERVER" ]; then
cat <<EOF > /etc/network/interfaces
#created by $0
auto lo
iface lo inet loopback
iface eth0 inet dhcp
allow-hotplug wlan0
iface wlan0 inet static
address 192.168.42.1
netmask 255.255.255.0
#iface wlan0 inet manual
#wpa-roam /etc/wpa_supplicant/wpa_supplicant.conf
#iface default inet dhcp
up iptables-restore < /etc/iptables.ipv4.nat
EOF
cat <<EOF > /etc/hostapd/hostapd.conf
#created by $0
interface=wlan0
driver=$DRIVER
ssid=$SSID
channel=6
wmm_enabled=1
wpa=1
wpa_passphrase=$PASSWORD
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
auth_algs=1
macaddr_acl=0
EOF
cp -f /home/pi/.config/openplotter/nmea_wifi_server/$CHIPSET/hostapd /usr/sbin/hostapd
chmod 755 /usr/sbin/hostapd
fi

if [ "$TYPE" = "CLIENT" ]; then
cat <<EOF > /etc/network/interfaces
#created by $0
auto lo
iface lo inet loopback
iface eth0 inet dhcp
allow-hotplug wlan0
#iface wlan0 inet static
#address 192.168.42.1
#netmask 255.255.255.0
iface wlan0 inet manual
wpa-roam /etc/wpa_supplicant/wpa_supplicant.conf
iface default inet dhcp
up iptables-restore < /etc/iptables.ipv4.nat
EOF
fi

clear
echo "===================================================="
echo "SETUP COMPLETE"
echo "Rebooting..."
echo "===================================================="
ifdown --force wlan0;
ifup wlan0;
reboot

else
clear
echo "===================================================="
echo "SETUP ABORTED"
echo "Exiting..."
echo "===================================================="
exit 0
fi
