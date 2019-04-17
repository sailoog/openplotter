#!/bin/bash
#echo "Activates or disables hostapd.conf bridge setting."
#echo "Example to activate bridge: bash hostapd_Bridge.sh y"
#echo "Example to disable bridge: bash hostapd_Bridge.sh n"
response=$1
oldline=$(grep -F 'bridge=' ~/.openplotter/Network/hostapd/hostapd.conf)

if [[ "$response" =~ ^([yY][eE][sS]|[yY])+$ ]]
then
	sudo sed -i "s/${oldline}/bridge=br0/g" ~/.openplotter/Network/hostapd/hostapd.conf
else
	sudo sed -i "s/${oldline}/#bridge=br0/g" ~/.openplotter/Network/hostapd/hostapd.conf
fi
