#!/bin/bash
##sudo apt-get update
##sudo apt-get -y dist-upgrade
if [ $? -ne 0 ]; then
	echo
	read -p "#### ERROR. ABORTING, PRESS ENTER TO EXIT ####"
	exit 1
fi
echo
echo "INSTALLING DEPENDENCIES..."
echo
##sudo apt-get -y install gettext python-w1thermsensor python-wxgtk3.0 hostapd dnsmasq mpg123 python-gammu gammu mosquitto crudini whois libusb-1.0-0-dev libfftw3-dev qt5-qmake libasound2-dev libpulse-dev autoconf automake python-dev python-matplotlib bridge-utils libqt4-dev libvolk1-bin libusb-1.0-0 gr-iqbal qt5-default libqt5svg5 libportaudio2 make gcc xsltproc curl git build-essential libtool i2c-tools cmake libnss-mdns avahi-utils libavahi-compat-libdnssd-dev swig python-numpy python-scipy python-serial python-pil python-opengl python-flask
#sudo apt-get -y install gettext gpsd gpsd-clients python-w1thermsensor python-wxgtk3.0 hostapd dnsmasq isc-dhcp-server network-manager network-manager-gnome mpg123 python-gammu gammu mosquitto crudini whois libusb-1.0-0-dev libfftw3-dev qt5-qmake libasound2-dev libpulse-dev  autoconf automake python-dev python-matplotlib bridge-utils libqt4-dev gnuradio libvolk1-bin libusb-1.0-0 gr-iqbal qt5-default libqt5svg5 libportaudio2 make gcc xsltproc curl git build-essential libtool librtlsdr-dev rtl-sdr i2c-tools cmake zygrib libnss-mdns avahi-utils libavahi-compat-libdnssd-dev swig python-numpy python-scipy python-serial python-gps python-pil python-opengl python-flask
if [ $? -ne 0 ]; then
	echo
	read -p "#### ERROR. ABORTING, PRESS ENTER TO EXIT ####"
	exit 1
fi
echo
echo "INSTALLING PYTHON PACKAGES..."
echo
##sudo easy_install pip
##sudo pip install --upgrade paho-mqtt pyudev pynmea2 twython websocket-client spidev PyMata requests_oauthlib requests pyglet pywavefront ujson Flask flask-socketio pyyaml
#sudo pip install --upgrade paho-mqtt pyudev pyrtlsdr pynmea2 twython websocket-client spidev PyMata requests_oauthlib requests pyglet pywavefront ujson Flask flask-socketio
if [ $? -ne 0 ]; then
	echo
	read -p "#### ERROR. ABORTING, PRESS ENTER TO EXIT ####"
	exit 1
fi
echo
echo "COMPILING PACKAGES..."
echo
op_folder=/home/pi/.config/openplotter
repository=sailoog
echo $op_folder
cd $op_folder/..
mkdir compiling


cd $op_folder/../compiling
git clone -b 1.4 https://github.com/stripydog/kplex.git
cd kplex
make
sudo make install

cd $op_folder/../compiling
git clone https://github.com/$repository/geomag.git
cd geomag/geomag
python setup.py build
sudo python setup.py install

cd $op_folder/../compiling
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

cd $op_folder/../compiling
git clone https://github.com/$repository/pypilot
cd pypilot
python setup.py build
sudo python setup.py install

cd $op_folder/../compiling
git clone https://github.com/$repository/pypilot_data.git
if [ ! -d ~/.pypilot ]; then
	mkdir ~/.pypilot
fi
cd pypilot_data
cp -f ui/Vagabond.mtl ~/.pypilot/
cp -f ui/Vagabond.obj ~/.pypilot/
cp -f ui/compass.png ~/.pypilot/

cd $op_folder/..
sudo rm -rf $HOME$op_folder/compiling/

echo '{"host": "localhost"}' > ~/.pypilot/signalk.conf

if grep -Fq "self.shininess = min(128, self.shininess)" /usr/local/lib/python2.7/dist-packages/pywavefront/material.py
then
	true
else
	sudo sed -i '103 i \\tself.shininess = min(128, self.shininess)' /usr/local/lib/python2.7/dist-packages/pywavefront/material.py
fi

cd $op_folder/..
