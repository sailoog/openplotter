#!/bin/sh
sleep 22
sudo ifdown --force br0
sleep 4
sudo ifup --force br0
sleep 2
sudo systemctl restart dnsmasq
