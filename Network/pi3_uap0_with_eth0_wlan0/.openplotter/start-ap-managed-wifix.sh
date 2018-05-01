#!/bin/sh
var=`ls /sys/class/net | grep uap0`
if [ "$var" == "uap0" ];then
	sleep 30
	sudo ifdown --force wlan0
	sleep 2
	sudo ifup --force wlan0
	sleep 2
	sudo systemctl restart dnsmasq
fi
sudo iptables -t nat -A POSTROUTING -s 10.10.10.0/24 ! -d 10.10.10.0/24 -j MASQUERADE
#sudo iptables -t nat -A POSTROUTING -o wlan0 -j MASQUERADE
#sudo iptables -A FORWARD -i wlan0 -o uap0 -m state --state RELATED,ESTABLISHED -j ACCEPT
#sudo iptables -A FORWARD -i uap0 -o wlan0 -j ACCEPT
