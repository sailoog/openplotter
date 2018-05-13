#!/bin/sh
sleep 22
sudo ifdown --force wlan0
sudo ifdown --force br0
sleep 4
sudo rm -f /var/run/wpa_supplicant/wlan0
sudo ifup --force br0
sleep 1
sudo ifup --force wlan0
sudo systemctl restart dhcpcd
sudo iptables -t nat -A POSTROUTING -o wlan0 -j MASQUERADE
sudo iptables -A FORWARD -i wlan0 -o br0 -m state --state RELATED,ESTABLISHED -j ACCEPT
sudo iptables -A FORWARD -i br0 -o wlan0 -j ACCEPT
sleep 1
sudo systemctl restart dnsmasq
