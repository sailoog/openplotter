#!/bin/bash

echo
echo "APPLYING OLD SETTINGS..."
echo
sudo chmod 755 openplotter_tmp/openplotter
sudo chmod 755 openplotter_tmp/keyword
sudo chmod 755 openplotter_tmp/startup
cp -f $DIRDATE/openplotter.conf openplotter_tmp/
crudini --set openplotter_tmp/openplotter.conf GENERAL version $2
cp -f $DIRDATE/OP-signalk/openplotter-settings.json openplotter_tmp/OP-signalk/
cp -f $DIRDATE/imu/RTIMULib.ini openplotter_tmp/imu/
cp -f $DIRDATE/imu/RTIMULib2.ini openplotter_tmp/imu/
cp -f $DIRDATE/imu/RTIMULib3.ini openplotter_tmp/imu/