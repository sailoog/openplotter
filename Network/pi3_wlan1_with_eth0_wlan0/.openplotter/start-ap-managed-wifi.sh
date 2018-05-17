#!/bin/sh
sleep 22
sudo ifdown --force br0
sleep 4
sudo ifup --force br0
sleep 1
sudo iptables -t nat -A POSTROUTING -o wlan0 -j MASQUERADE
sudo iptables -A FORWARD -i wlan0 -o br0 -m state --state RELATED,ESTABLISHED -j ACCEPT
sudo iptables -A FORWARD -i br0 -o wlan0 -j ACCEPT
sleep 1
sudo systemctl restart dnsmasq
