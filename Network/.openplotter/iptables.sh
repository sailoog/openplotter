#!/bin/sh
internet=$1
router=$2
sudo iptables -F
sudo iptables -t nat -A POSTROUTING -o "${internet}" -j MASQUERADE
sudo iptables -A FORWARD -i "${internet}" -o "${router}" -m state --state RELATED,ESTABLISHED -j ACCEPT
sudo iptables -A FORWARD -i "${router}" -o "${internet}" -j ACCEPT
