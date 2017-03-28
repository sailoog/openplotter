#!/bin/bash
cd ~/.config

echo
echo "UPDATING PACKAGES LISTS..."
echo
sudo apt-get update
echo
echo "INSTALLING/UPDATING PACKAGES..."
echo
sudo apt-get install cmake gettext gpsd python-w1thermsensor x11vnc xrdp python-wxgtk3.0 hostapd dnsmasq isc-dhcp-server network-manager network-manager-gnome mpg123 python-gammu gammu mosquitto libusb-1.0-0-dev libfftw3-dev qt5-qmake libqt4-dev libasound2-dev libpulse-dev libtool autoconf automake liboctave-dev python-dev python-matplotlib opencpn bridge-utils crudini
if [ $? -ne 0 ]; then
	echo
	read -p "#### ERROR. ABORTING, PRESS ENTER TO EXIT ####"
	exit 1
fi
echo
echo "INSTALLING/UPDATING PYTHON PACKAGES..."
echo
sudo pip install --upgrade paho-mqtt pyudev pyrtlsdr pynmea2 twython websocket-client spidev requests requests_oauthlib
if [ $? -ne 0 ]; then
	echo
	read -p "#### ERROR. ABORTING, PRESS ENTER TO EXIT ####"
	exit 1
fi
echo
echo "DOWNLOADING SIGNAL K..."
echo
pkill -f signalk-server
curl -sL https://deb.nodesource.com/setup_6.x | sudo -E bash -
sudo apt-get install -y nodejs
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
tar cvjf ~/$SKDIRDATE.tar.bz2 $SKDIRDATE
echo
echo "DELETING OLD SIGNAL K FILES..."
echo
rm -rf $SKDIRDATE
echo
echo "INSTALLING NEW SIGNAL K FILES..."
echo
mv signalk-server-node_tmp signalk-server-node
cd signalk-server-node
npm install
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
tar xvf gqrx-2.6-rpi3-2.tar.xz
rm gqrx-2.6-rpi3-2.tar.xz
rm -rf gqrx
mv gqrx-2.6-rpi3-2 gqrx
cd gqrx
./setup_gqrx.sh

cd ~/.config
