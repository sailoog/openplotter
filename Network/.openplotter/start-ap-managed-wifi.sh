#!/bin/sh
internet=wlan0
router=
sudo sysctl -w net.ipv4.ip_forward=1
/bin/bash /home/pi/.openplotter/start1.sh
/bin/bash /home/pi/.openplotter/iptables.sh "$internet" "$router"
