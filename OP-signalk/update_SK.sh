#!/bin/bash

cd /home/pi/.config

if [ -d /home/pi/.config/signalk-server-node ]
then
    echo "exist"
    rem cd /home/pi
    rem DIRDATE=`date +sk_backup_%Y_%m_%d:%H:%M:%S`
    rem mkdir $DIRDATE
    rem cp /home/pi/.config/signalk-server-node/settings/openplotter-settings.json /home/pi/$DIRDATE
	if [ -d /home/pi/.config/xsignalk-server-node ]
	then
		rm -rf xsignalk-server-node
	fi
	mv signalk-server-node xsignalk-server-node
fi

echo "signalk-server-node doesn't exist"
git clone https://github.com/SignalK/signalk-server-node.git
cd signalk-server-node
sudo apt-get install -y curl git build-essential
npm install mdns
npm install

cd /home/pi/config./openplotter/OP-signalk
sudo chmod 755 openplotter  

rem cd /home/pi/.config/openplotter
rem cp openplotter-settings.json /home/pi/.config/signalk-server-node/settings
rem sudo chmod 755 openplotter  
rem cp openplotter /home/pi/.config/signalk-server-node/bin
rem cp /home/pi/$DIRDATE/openplotter-settings.json /home/pi/.config/signalk-server-node/settings