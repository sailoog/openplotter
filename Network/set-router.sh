#!/bin/bash
#echo "Change start-ap-managed-wifi.sh."
#echo "Example for wlan1 as AP: bash set-router.sh wlan1"
router=$1

oldline=$(grep -F 'router=' ~/.openplotter/Network/.openplotter/start-ap-managed-wifi.sh)
newline="router=${router}"
sudo sed -i "s/${oldline}/${newline}/g" ~/.openplotter/Network/.openplotter/start-ap-managed-wifi.sh

