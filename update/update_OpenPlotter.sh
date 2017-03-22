#!/bin/bash
echo
echo "CREATING OPENPLOTTER BACKUP..."
echo
cd ~/.config
DIRDATE=`date +openplotter_bak_%Y_%m_%d:%H:%M:%S`
cp -a openplotter/ $DIRDATE/
cd $DIRDATE
find . -name "*.pyc" -type f -delete
# zip?
echo
echo "DOWNLOADING OPENPLOTTER CODE..."
echo
cd ~/.config
rm -rf openplotter_tmp
#### CHANGE TO MASTER ########################################################
git clone -b v0.9.0 https://github.com/sailoog/openplotter.git openplotter_tmp
rm -rf openplotter_tmp/.git/
##############################################################################
echo
echo "APPLYING OLD SETTINGS..."
echo
cd ~/.config
sudo chmod 755 openplotter_tmp/openplotter
sudo chmod 755 openplotter_tmp/keyword
sudo chmod 755 openplotter_tmp/startup
cp -f $DIRDATE/openplotter.conf openplotter_tmp/
cp -f $DIRDATE/OP-signalk/openplotter-settings.json openplotter_tmp/OP-signalk/
cp -f $DIRDATE/imu/RTIMULib.ini openplotter_tmp/imu/
cp -f $DIRDATE/imu/RTIMULib2.ini openplotter_tmp/imu/
cp -f $DIRDATE/imu/RTIMULib3.ini openplotter_tmp/imu/
echo
echo "DELETING OLD FILES..."
echo
rm -rf openplotter
mv openplotter_tmp openplotter

if [ $1 = 1 ]; then
	source ~/.config/openplotter/update/update_dependencies.sh
fi

startup restart
echo
read -p "FINISHED, PRESS ENTER TO EXIT."

