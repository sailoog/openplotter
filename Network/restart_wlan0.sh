#!/bin/bash
sudo dhclient -r wlan0
sudo ifdown wlan0
sudo ifup wlan0
sudo dhclient -v wlan0