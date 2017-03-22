#!/bin/bash
echo
echo "CLOSING OPENCPN..."
echo
pkill -9 opencpn
echo
echo "UPDATING PACKAGES..."
echo
sudo apt-get update
echo
echo "INSTALLING OPENCPN..."
echo
sudo apt-get install opencpn
echo
echo "EDITING OPENCPN MENU..."
echo
sudo bash -c 'echo -e "[Desktop Entry]\nName=OpenCPN\nComment=Open source chart plotter / navigator\nExec=opencpn\nIcon=opencpn\nStartupNotify=true\nCategories=OpenPlotter\nTerminal=false\nType=Application\nVersion=1.0" > /usr/share/applications/opencpn.desktop'
echo
read -p "FINISHED PRESS ENTER TO EXIT"
