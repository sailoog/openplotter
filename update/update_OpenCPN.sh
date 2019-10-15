#!/bin/bash
echo
echo "CLOSING OPENCPN..."
echo
pkill -9 opencpn
echo
echo "UPDATING PACKAGE LISTS..."
echo
sudo apt-get -qq update
if [ $? -ne 0 ]; then
	echo
	read -p "#### ERROR. ABORTING, PRESS ENTER TO EXIT ####"
	exit 1
fi
echo
echo "UPDATING OPENCPN..."
echo
sudo apt-get -qq install opencpn
if [ $? -ne 0 ]; then
	echo
	read -p "#### ERROR. ABORTING, PRESS ENTER TO EXIT ####"
	exit 1
fi
echo
echo "EDITING OPENCPN MENU..."
echo
sudo bash -c 'echo -e "[Desktop Entry]\nName=OpenCPN\nComment=Open source chart plotter / navigator\nExec=opencpn\nIcon=opencpn\nStartupNotify=true\nCategories=OpenPlotter\nTerminal=false\nType=Application\nVersion=1.0" > /usr/share/applications/opencpn.desktop'
echo
read -p "FINISHED PRESS ENTER TO EXIT"
