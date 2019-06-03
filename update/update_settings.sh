#!/bin/bash

cd $op_folder/..

echo
echo "APPLYING SETTINGS..."
echo

grep -qF "dtoverlay=i2c-gpio,i2c_gpio_sda=2,i2c_gpio_scl=3,bus=3" "/boot/config.txt"  || echo "dtoverlay=i2c-gpio,i2c_gpio_sda=2,i2c_gpio_scl=3,bus=3" | sudo tee --append "/boot/config.txt"

chmod 755 openplotter_tmp/openplotter
chmod 755 openplotter_tmp/keyword
chmod 755 openplotter_tmp/startup

cp -f openplotter_tmp/tools/demo_tool/demo_tool.py ~/.openplotter/tools/demo_tool/
cp -f openplotter_tmp/tools/README.md ~/.openplotter/tools/

newversion=$(crudini --get openplotter_tmp/openplotter.conf GENERAL version)
newstate=$(crudini --get openplotter_tmp/openplotter.conf GENERAL state)
crudini --set ~/.openplotter/openplotter.conf GENERAL version $newversion
crudini --set ~/.openplotter/openplotter.conf GENERAL state $newstate
