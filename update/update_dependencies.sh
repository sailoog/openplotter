#!/bin/bash
cd ~/.config
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
echo "UPDATING PACKAGES..."
echo
sudo apt-get -qq upgrade
if [ $? -ne 0 ]; then
	echo
	read -p "#### ERROR. ABORTING, PRESS ENTER TO EXIT ####"
	exit 1
fi
echo
echo "INSTALLING DEPENDENCIES..."
echo
sudo apt-get -qq install cmake gettext gpsd python-w1thermsensor x11vnc xrdp python-wxgtk3.0 hostapd dnsmasq isc-dhcp-server network-manager network-manager-gnome mpg123 python-gammu gammu mosquitto libusb-1.0-0-dev libfftw3-dev qt5-qmake libqt4-dev libasound2-dev libpulse-dev libtool autoconf automake liboctave-dev python-dev python-matplotlib opencpn bridge-utils crudini
if [ $? -ne 0 ]; then
	echo
	read -p "#### ERROR. ABORTING, PRESS ENTER TO EXIT ####"
	exit 1
fi
echo
echo "INSTALLING PYTHON PACKAGES..."
echo
sudo easy_install pip
sudo pip install --upgrade --quiet paho-mqtt pyudev pyrtlsdr pynmea2 twython websocket-client spidev requests requests_oauthlib
if [ $? -ne 0 ]; then
	echo
	read -p "#### ERROR. ABORTING, PRESS ENTER TO EXIT ####"
	exit 1
fi
echo
echo "UPDATING NODEJS..."
echo
pkill -f signalk-server
curl -sL https://deb.nodesource.com/setup_6.x | sudo -E bash -
sudo apt-get -qq install nodejs
if [ $? -ne 0 ]; then
	echo
	read -p "#### ERROR. ABORTING, PRESS ENTER TO EXIT ####"
	exit 1
fi
echo
echo "DOWNLOADING SIGNAL K..."
echo
rm -rf signalk-server-node_tmp
git clone https://github.com/sailoog/signalk-server-node.git signalk-server-node_tmp
if [ $? -ne 0 ]; then
	echo
	read -p "#### ERROR. ABORTING, PRESS ENTER TO EXIT ####"
	exit 1
fi
echo
echo "CREATING SIGNAL K BACKUP..."
echo
SKDIRDATE=`date +signalk_bak_%Y_%m_%d:%H:%M:%S`
cp -a signalk-server-node/ $SKDIRDATE/
echo
echo "COMPRESSING SIGNAL K BACKUP INTO HOME..."
echo
tar cjf ~/$SKDIRDATE.tar.bz2 $SKDIRDATE
echo
echo "DELETING OLD SIGNAL K FILES..."
echo
rm -rf $SKDIRDATE
rm -rf signalk-server-node
echo
echo "INSTALLING NEW SIGNAL K FILES..."
echo
mv signalk-server-node_tmp signalk-server-node
cd signalk-server-node
npm install --quiet
cd ~/.config
echo
echo "UPDATING NODE-RED, NODE-RED-DASHBOARD AND NODE-RED-FREEBOARD..."
echo
#### TODO ####
echo
echo "COMPILING PACKAGES..."
echo
#### TODO ####
echo
echo "INSTALLING/UPDATING GQRX..."
echo
wget https://github.com/csete/gqrx/releases/download/v2.6/gqrx-2.6-rpi3-2.tar.xz
tar xf gqrx-2.6-rpi3-2.tar.xz
rm gqrx-2.6-rpi3-2.tar.xz
rm -rf gqrx
mv gqrx-2.6-rpi3-2 gqrx
cd gqrx
./setup_gqrx.sh

cd ~/.config
