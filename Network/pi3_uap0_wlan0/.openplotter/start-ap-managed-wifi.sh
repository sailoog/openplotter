#!/bin/sh
sleep 25
sudo ifdown --force wlan0
sleep 4
sudo rm -f /var/run/wpa_supplicant/wlan0
#PID=`pgrep -f uap0`
#kill $PID

sudo ifup --force wlan0
#sudo iptables -t nat -A POSTROUTING -s 10.10.10.0/24 ! -d 10.10.10.0/24 -j MASQUERADE
sudo iptables -t nat -A POSTROUTING -o wlan0 -j MASQUERADE
sudo iptables -A FORWARD -i wlan0 -o uap0 -m state --state RELATED,ESTABLISHED -j ACCEPT
sudo iptables -A FORWARD -i uap0 -o wlan0 -j ACCEPT
sudo systemctl restart dnsmasq
