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
sudo apt-get -qq install gettext gpsd python-w1thermsensor x11vnc xrdp python-wxgtk3.0 hostapd dnsmasq isc-dhcp-server network-manager network-manager-gnome mpg123 python-gammu gammu mosquitto libusb-1.0-0-dev libfftw3-dev qt5-qmake libasound2-dev libpulse-dev  autoconf automake liboctave-dev python-dev python-matplotlib opencpn bridge-utils crudini libqt5gui5 libqt5core5a libqt5network5 libqt5widgets5 libqt5svg5 libportaudio2 make gcc xsltproc curl git build-essential libtool libusb-1.0.0-dev librtlsdr-dev rtl-sdr i2c-tools cmake libqt4-dev libproj-dev libnova-dev
if [ $? -ne 0 ]; then
	echo
	read -p "#### ERROR. ABORTING, PRESS ENTER TO EXIT ####"
	exit 1
fi
echo
echo "INSTALLING PYTHON PACKAGES..."
echo
sudo easy_install pip
sudo pip install --upgrade --quiet paho-mqtt pyudev pyrtlsdr pynmea2 twython websocket-client spidev PyMata requests_oauthlib requests  
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
npm install
cd ~/.config
echo
echo "UPDATING NODE-RED, NODE-RED-DASHBOARD AND NODE-RED-FREEBOARD..."
echo
#### TODO ####
echo
echo "COMPILING PACKAGES..."
echo
cd ~/.config
mkdir compiling
cd compiling

cd ~/.config/compiling
git clone https://github.com/sailoog/kalibrate-rtl.git
cd kalibrate-rtl
./bootstrap && CXXFLAGS='-W -Wall -O3'
./configure
make -s
sudo make -s install

cd ~/.config/compiling
git clone https://github.com/sailoog/rtl_433.git
cd rtl_433/
mkdir build
cd build
cmake ../
make -s
sudo make -s install

cd ~/.config/compiling
git clone https://github.com/sailoog/aisdecoder.git
cd aisdecoder
cmake -DCMAKE_BUILD_TYPE=release
make -s
sudo cp aisdecoder /usr/local/bin

cd ~/.config/compiling
git clone https://github.com/sailoog/kplex.git
cd kplex
make -s
sudo make -s install

cd ~/.config/compiling
git clone git://github.com/sailoog/canboat
cd canboat
make -s
sudo make -s install

cd ~/.config/compiling
git clone https://github.com/sailoog/geomag.git
cd geomag/geomag
python setup.py -q build
sudo python setup.py -q install

cd ~/.config/compiling
git clone https://github.com/sailoog/RTIMULib2.git
cd RTIMULib2/Linux
mkdir build
cd build
cmake ..
make -j4 -s
sudo make -s install
sudo ldconfig
cd ..
cd RTIMULibCal
make -j4 -s
sudo make -s install
cd ..
cd RTIMULibDrive
make -j4 -s
sudo make -s install
cd ..
cd RTIMULibDrive10
make -j4 -s
sudo make -s install
cd ..
cd RTIMULibDemo
qmake
make -j4 -s
sudo make -s install
cd ..
cd RTIMULibDemoGL
qmake
make -j4 -s
sudo make -s install
cd ..
cd python
python setup.py -q build
sudo python setup.py -q install

cd ~/.config
sudo rm -rf ~/.config/compiling/
echo
echo "INSTALLING/UPDATING GQRX..."
echo
wget https://github.com/csete/gqrx/releases/download/v2.6/gqrx-2.6-rpi3-3.tar.xz
tar xf gqrx-2.6-rpi3-3.tar.xz
rm gqrx-2.6-rpi3-3.tar.xz
rm -rf gqrx
mv gqrx-2.6-rpi3-3 gqrx
cd gqrx
./setup_gqrx.sh

cd ~/.config
