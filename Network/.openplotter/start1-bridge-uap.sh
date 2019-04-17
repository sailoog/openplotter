#!/bin/sh
sleep 22
sudo ifdown --force wlan0
sudo ifdown --force br0
sleep 4
#sudo rm -f /var/run/wpa_supplicant/wlan0
sudo ifup --force br0
sleep 1
sudo ifup --force wlan0
sleep 2
sudo systemctl restart dnsmasq
sudo systemctl restart dhcpcd
