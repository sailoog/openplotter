#!/bin/bash
echo
echo "DOWNLOADING PACKAGES LIST..."
echo
sudo apt-get update
echo
echo "UPDATING PACKAGES..."
echo
sudo apt-get upgrade -y
echo
echo "UPGRADING SYSTEM..."
echo
sudo apt-get dist-upgrade -y
echo
echo "FINISHED, PRESS ENTER TO EXIT."
read -p "PLEASE REBOOT SYSTEM."

