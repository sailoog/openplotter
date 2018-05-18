#!/bin/sh
sleep 30
sudo ifdown --force wlan0
sudo ifdown --force br0
sleep 4
sudo rm -f /var/run/wpa_supplicant/wlan0
sudo ifup --force br0
sleep 2
sudo ifup --force wlan0
sudo iptables -t nat -A POSTROUTING -o wlan0 -j MASQUERADE
sudo iptables -A FORWARD -i wlan0 -o br0 -m state --state RELATED,ESTABLISHED -j ACCEPT
sudo iptables -A FORWARD -i br0 -o wlan0 -j ACCEPT
sudo systemctl restart dnsmasq
