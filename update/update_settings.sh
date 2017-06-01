#!/bin/bash
cd ~/.config

echo
echo "APPLYING SETTINGS..."
echo
rm -rf openplotter_tmp/.git/
sudo chmod 755 openplotter_tmp/openplotter
sudo chmod 755 openplotter_tmp/keyword
sudo chmod 755 openplotter_tmp/startup
cp -f $DIRDATE/openplotter.conf openplotter_tmp/
crudini --set openplotter_tmp/openplotter.conf GENERAL version $2
crudini --set openplotter_tmp/openplotter.conf GENERAL state $3
python openplotter_tmp/update/update_signalk_settings.py $DIRDATE
cp -f $DIRDATE/imu/RTIMULib.ini openplotter_tmp/imu/settings/
cp -f $DIRDATE/imu/settings/RTIMULib.ini openplotter_tmp/imu/settings/

cd ~/.config