#!/bin/bash
op_folder="/home/pi/.config"
cd $op_folder/..

echo
echo "APPLYING SETTINGS..."
echo

chmod 755 $op_folder/openplotter/openplotter
chmod 755 $op_folder/openplotter/keyword
chmod 755 $op_folder/openplotter/startup

if [ ! -d ~/.openplotter ]; then
	mkdir ~/.openplotter
fi

if [ ! -d ~/.openplotter/tools ]; then
	mkdir ~/.openplotter/tools
fi

cp -f $op_folder/openplotter/tools/demo_tool.py ~/.openplotter/tools/

if [ ! -f ~/.openplotter/openplotter.conf ]; then
	cp -f /home/pi/.config/openplotter.conf ~/.openplotter/
fi
newversion=$(crudini --get $op_folder/openplotter/openplotter.conf GENERAL version)
newstate=$(crudini --get $op_folder/openplotter/openplotter.conf GENERAL state)
crudini --set ~/.openplotter/openplotter.conf GENERAL version $newversion
crudini --set ~/.openplotter/openplotter.conf GENERAL state $newstate

if [ ! -f ~/.openplotter/private_unit.json ]; then
	cp -f $op_folder/openplotter/classes/private_unit.json ~/.openplotter/
fi
if [ ! -f ~/.openplotter/SK-simulator.conf ]; then
	cp -f $op_folder/openplotter/tools/SK-simulator.conf ~/.openplotter/
fi
if [ ! -f ~/.openplotter/openplotter_analog.conf ]; then
	cp -f $op_folder/openplotter/tools/openplotter_analog.conf ~/.openplotter/
fi
