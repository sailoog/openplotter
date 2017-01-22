#!/bin/bash

cd /home/pi/.config

if [ -d /home/pi/.config/signalk-server-node ]
then
    echo "exist"
	if [ -d /home/pi/.config/xsignalk-server-node ]
	then
		rm -rf xsignalk-server-node
	fi
	mv signalk-server-node xsignalk-server-node
fi

sudo apt-get install -y curl git build-essential
#sudo apt-get install -y libavahi-compat-libdnssd-dev

echo "signalk-server-node doesn't exist"
git clone https://github.com/SignalK/signalk-server-node.git
cd signalk-server-node
#npm install mdns
npm install

cd ~/.config/signalk-server-node/bower_components
rm -rf sailgauge
rm -rf simplegauges
cd ..
sudo npm install -g bower
bower install https://github.com/SignalK/sailgauge.git
bower install https://github.com/SignalK/simplegauges.git
