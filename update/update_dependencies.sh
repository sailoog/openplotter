#!/bin/bash
status=$3
op_folder=$(crudini --get ~/.openplotter/openplotter.conf GENERAL op_folder)

if [ -z $status ]; then
	status="stable"
fi

if [ -z $op_folder ]; then
	op_folder="/.config"
fi

if [ $status = "stable" ]; then
	repository="openplotter"
else
	repository="sailoog"
fi

cd $HOME$op_folder

echo
echo "REMOVING UNUSED PACKAGES..."
echo
sudo apt-get -y remove --purge librtimulib-dev librtimulib-utils librtimulib7 python-rtimulib python3-rtimulib realvnc* xrdp
sudo apt-get -y autoremove
echo
echo "UPDATING PACKAGE LISTS..."
echo
sudo apt-get update
if [ $? -ne 0 ]; then
	echo
	read -p "#### ERROR. ABORTING, PRESS ENTER TO EXIT ####"
	exit 1
fi
echo
echo "UPDATING PACKAGES..."
echo
sudo apt-get -y upgrade
if [ $? -ne 0 ]; then
	echo
	read -p "#### ERROR. ABORTING, PRESS ENTER TO EXIT ####"
	exit 1
fi
echo
echo "UPGRADING RASPBIAN..."
echo
sudo apt-get -y dist-upgrade
if [ $? -ne 0 ]; then
	echo
	read -p "#### ERROR. ABORTING, PRESS ENTER TO EXIT ####"
	exit 1
fi
echo
echo "INSTALLING DEPENDENCIES..."
echo
sudo apt-get -y install gettext gpsd python-w1thermsensor x11vnc xrdp python-wxgtk3.0 hostapd dnsmasq isc-dhcp-server network-manager network-manager-gnome mpg123 python-gammu gammu mosquitto libusb-1.0-0-dev libfftw3-dev qt5-qmake libasound2-dev libpulse-dev  autoconf automake python-dev python-matplotlib bridge-utils crudini libqt5gui5 libqt5core5a libqt5network5 libqt5widgets5 libqt5svg5 libportaudio2 make gcc xsltproc curl git build-essential libtool libusb-1.0.0-dev librtlsdr-dev rtl-sdr i2c-tools cmake libqt4-dev libproj-dev libnova-dev swig python-numpy python-scipy python-serial python-gps python-PIL python-opengl python-pillow python-flask libnss-mdns avahi-utils libavahi-compat-libdnssd-dev
if [ $? -ne 0 ]; then
	echo
	read -p "#### ERROR. ABORTING, PRESS ENTER TO EXIT ####"
	exit 1
fi
echo
echo "INSTALLING PYTHON PACKAGES..."
echo
sudo easy_install pip
sudo pip install --upgrade paho-mqtt pyudev pyrtlsdr pynmea2 twython websocket-client spidev PyMata requests_oauthlib requests pyglet pywavefront ujson
if [ $? -ne 0 ]; then
	echo
	read -p "#### ERROR. ABORTING, PRESS ENTER TO EXIT ####"
	exit 1
fi
echo
echo "UPDATING NODEJS AND NODE-RED..."
echo
rm -rf $HOME/.node-red/node_modules/node-red-contrib-freeboard
update-nodejs-and-nodered
sudo rm -rf /usr/share/applications/Node-RED.desktop
echo
echo "UPDATING SIGNAL K..."
echo
cd $HOME$op_folder
rm -rf signalk-server-node_tmp
git clone https://github.com/$repository/signalk-server-node.git signalk-server-node_tmp
cd ~/.config/signalk-server-node_tmp
npm install
npm install mdns
cd $HOME$op_folder
rm -rf signalk-server-node
mv signalk-server-node_tmp signalk-server-node
echo
echo "COMPILING PACKAGES..."
echo
cd $HOME$op_folder
mkdir compiling

cd $HOME$op_folder/compiling
git clone https://github.com/$repository/kalibrate-rtl.git
cd kalibrate-rtl
./bootstrap && CXXFLAGS='-W -Wall -O3'
./configure
make
sudo make install

cd $HOME$op_folder/compiling
git clone https://github.com/$repository/rtl_433.git
cd rtl_433/
mkdir build
cd build
cmake ../
make
sudo make install

cd $HOME$op_folder/compiling
pkill aisdecoder
git clone https://github.com/$repository/aisdecoder.git
cd aisdecoder
cmake -DCMAKE_BUILD_TYPE=release
make
sudo cp aisdecoder /usr/local/bin

cd $HOME$op_folder/compiling
git clone https://github.com/$repository/kplex.git
cd kplex
make
sudo make install

cd $HOME$op_folder/compiling
git clone git://github.com/$repository/canboat
cd canboat
make
sudo make install

cd $HOME$op_folder/compiling
git clone https://github.com/$repository/geomag.git
cd geomag/geomag
python setup.py build
sudo python setup.py install

cd $HOME$op_folder/compiling
git clone https://github.com/$repository/RTIMULib2.git
cd RTIMULib2/Linux
mkdir build
cd build
cmake ..
make -j4
sudo make install
sudo ldconfig
cd ..
cd RTIMULibDrive
make -j4
sudo make install
cd ..
cd RTIMULibDrive10
make -j4
sudo make install
cd ..
cd python
python setup.py build
sudo python setup.py install

cd $HOME$op_folder/compiling
git clone https://github.com/$repository/pypilot
cd pypilot
python setup.py build
sudo python setup.py install

cd $HOME$op_folder/compiling
git clone https://github.com/$repository/pypilot_data.git
if [ ! -d ~/.pypilot ]; then
	mkdir ~/.pypilot
fi
cd pypilot_data
cp -f ui/Vagabond.mtl ~/.pypilot/
cp -f ui/Vagabond.obj ~/.pypilot/
cp -f ui/compass.png ~/.pypilot/

cd $HOME$op_folder
sudo rm -rf $HOME$op_folder/compiling/

echo '{"host": "localhost"}' > ~/.pypilot/signalk.conf

if grep -Fq "self.shininess = min(128, self.shininess)" /usr/local/lib/python2.7/dist-packages/pywavefront/material.py
then
	true
else
	sudo sed -i '103 i \\tself.shininess = min(128, self.shininess)' /usr/local/lib/python2.7/dist-packages/pywavefront/material.py
fi

echo
echo "INSTALLING/UPDATING GQRX..."
echo
cd ~/.config
wget https://github.com/csete/gqrx/releases/download/v2.6/gqrx-2.6-rpi3-3.tar.xz
tar xf gqrx-2.6-rpi3-3.tar.xz
rm gqrx-2.6-rpi3-3.tar.xz
rm -rf gqrx
mv gqrx-2.6-rpi3-3 gqrx
cd gqrx
./setup_gqrx.sh

cd $HOME$op_folder
