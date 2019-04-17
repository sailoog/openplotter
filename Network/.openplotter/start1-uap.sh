#!/bin/sh
sleep 24
sudo ifdown --force wlan0
sleep 4
sudo ifup --force wlan0
sleep 2
sudo systemctl restart dnsmasq
sudo systemctl restart dhcpcd
