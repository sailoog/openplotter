#!/bin/sh
sleep 22
sudo ifdown --force wlan0
sudo rm -f /var/run/wpa_supplicant/wlan0
sleep 4

sudo ifup --force wlan0
sudo iptables -t nat -A POSTROUTING -o wlan0 -j MASQUERADE
sudo iptables -A FORWARD -i wlan0 -o uap0 -m state --state RELATED,ESTABLISHED -j ACCEPT
sudo iptables -A FORWARD -i uap0 -o wlan0 -j ACCEPT
sudo systemctl restart dnsmasq
sudo systemctl restart dhcpcd
