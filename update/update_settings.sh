#!/bin/bash
cd ~/.config

echo
echo "APPLYING SETTINGS..."
echo
rm -rf openplotter_tmp/.git/
chmod 755 openplotter_tmp/openplotter
chmod 755 openplotter_tmp/keyword
chmod 755 openplotter_tmp/startup
chmod 755 openplotter_tmp/update/update_OpenPlotter.sh
newversion=$(crudini --get openplotter_tmp/openplotter.conf GENERAL version)
newstate=$(crudini --get openplotter_tmp/openplotter.conf GENERAL state)
cp -f $DIRDATE/openplotter.conf openplotter_tmp/
crudini --set openplotter_tmp/openplotter.conf GENERAL version $newversion
crudini --set openplotter_tmp/openplotter.conf GENERAL state $newstate
python openplotter_tmp/update/update_signalk_settings.py $DIRDATE