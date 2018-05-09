#!/bin/bash

cd $HOME

if [ $branch = "stable" ]; then
	repository=$master_github_repositories
elif [ $branch = "beta" ]; then
	repository=$beta_github_repositories
else
	echo
	read -p "#### WRONG GITHUB REPOSITORIES. ABORTING, PRESS ENTER TO EXIT ####"
	exit 1
fi

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
sudo apt-get -y dist-upgrade
if [ $? -ne 0 ]; then
	echo
	read -p "#### ERROR. ABORTING, PRESS ENTER TO EXIT ####"
	exit 1
fi

#echo
#echo "INSTALLING DEPENDENCIES..."
#echo
#sudo apt-get -y install 
#if [ $? -ne 0 ]; then
#	echo
#	read -p "#### ERROR. ABORTING, PRESS ENTER TO EXIT ####"
#	exit 1
#fi

echo
echo "UPDATING PYTHON PACKAGES..."
echo
sudo easy_install pip
sudo pip install --upgrade paho-mqtt pyudev pyrtlsdr pynmea2 twython websocket-client spidev PyMata requests requests_oauthlib PyMata pyglet pywavefront ujson Flask flask-socketio
if [ $? -ne 0 ]; then
	echo
	read -p "#### ERROR. ABORTING, PRESS ENTER TO EXIT ####"
	exit 1
fi

echo
echo "UPDATING NODEJS, NPM AND NODE-RED..."
echo
update-nodejs-and-nodered
sudo rm -rf /usr/share/applications/Node-RED.desktop
cd $HOME/.node-red
npm update node-red-dashboard
npm update node-red-contrib-jsonpath
npm update mdns

echo
echo "UPDATING SIGNAL K..."
echo
sudo npm install --unsafe-perm -g signalk-server

echo
echo "COMPILING PACKAGES..."
echo
cd $HOME
mkdir delete

cd $HOME/delete
git clone https://github.com/$repository/kalibrate-rtl.git
cd kalibrate-rtl
./bootstrap && CXXFLAGS='-W -Wall -O3'
./configure
make
sudo make install

cd $HOME/delete
git clone https://github.com/$repository/rtl_433.git
cd rtl_433/
mkdir build
cd build
cmake ../
make
sudo make install

cd $HOME/delete
pkill aisdecoder
git clone https://github.com/$repository/aisdecoder.git
cd aisdecoder
cmake -DCMAKE_BUILD_TYPE=release
make
sudo cp aisdecoder /usr/local/bin

cd $HOME/delete
git clone https://github.com/$repository/kplex.git
cd kplex
make
sudo make install

cd $HOME/delete
git clone git://github.com/$repository/canboat
cd canboat
make
sudo make install

cd $HOME/delete
git clone https://github.com/$repository/geomag.git
cd geomag/geomag
python setup.py build
sudo python setup.py install

cd $HOME/delete
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

cd $HOME/delete
git clone https://github.com/$repository/pypilot
git clone https://github.com/$repository/pypilot_data
cp -rv pypilot_data/* pypilot
cd pypilot
python setup.py build
sudo python setup.py install


cd $HOME
sudo rm -rf delete

if grep -Fq "self.shininess = min(128, self.shininess)" /usr/local/lib/python2.7/dist-packages/pywavefront/material.py
then
	true
else
	sudo sed -i '103 i \\tself.shininess = min(128, self.shininess)' /usr/local/lib/python2.7/dist-packages/pywavefront/material.py
fi

echo
echo "UPDATING GQRX..."
echo
cd ~/.config
wget https://github.com/csete/gqrx/releases/download/v2.11.4/gqrx-sdr-2.11.4-linux-rpi3.tar.xz
tar xf gqrx-sdr-2.11.4-linux-rpi3.tar.xz
rm gqrx-sdr-2.11.4-linux-rpi3.tar.xz
rm -rf gqrx
mv gqrx-sdr-2.11.4-linux-rpi3 gqrx
cd gqrx
sudo cp udev/*.rules /etc/udev/rules.d/
