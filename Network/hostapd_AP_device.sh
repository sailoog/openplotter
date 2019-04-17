#!/bin/bash
#echo "Change hostapd.conf interface=[device]."
#echo "Example for wlan1 as AP: bash hostapd_AP_device.sh wlan1"
devicename=$1
newline="interface=${devicename}"

oldline=$(grep -F 'interface=' ~/.openplotter/Network/hostapd/hostapd.conf)
  
sudo sed -i "s/${oldline}/${newline}/g" ~/.openplotter/Network/hostapd/hostapd.conf
