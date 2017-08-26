#!/bin/bash
op_folder=$(crudini --get ~/.openplotter/openplotter.conf GENERAL op_folder)
if [ -z $op_folder ]; then
	op_folder="/.config"
fi

cd $HOME$op_folder

echo
echo "APPLYING SETTINGS..."
echo

chmod 755 openplotter_tmp/openplotter
chmod 755 openplotter_tmp/keyword
chmod 755 openplotter_tmp/startup

if [ ! -d ~/.openplotter ]; then
	mkdir ~/.openplotter
fi

if [ ! -d ~/.openplotter/tools ]; then
	mkdir ~/.openplotter/tools
fi

cp -f openplotter_tmp/tools/demo_tool.py ~/.openplotter/tools/

if [ ! -f ~/.openplotter/openplotter.conf ]; then
	cp -f $DIRDATE/openplotter.conf ~/.openplotter/
fi
newversion=$(crudini --get openplotter_tmp/openplotter.conf GENERAL version)
newstate=$(crudini --get openplotter_tmp/openplotter.conf GENERAL state)
crudini --set ~/.openplotter/openplotter.conf GENERAL version $newversion
crudini --set ~/.openplotter/openplotter.conf GENERAL state $newstate

if [ ! -f ~/.openplotter/openplotter-settings.json ]; then
	cp -f $DIRDATE/OP-signalk/openplotter-settings.json ~/.openplotter/
fi
if [ ! -f ~/.openplotter/private_unit.json ]; then
	cp -f $DIRDATE/classes/private_unit.json ~/.openplotter/
fi
if [ ! -f ~/.openplotter/SK-simulator.conf ]; then
	cp -f $DIRDATE/tools/SK-simulator.conf ~/.openplotter/
fi
if [ ! -f ~/.openplotter/openplotter_analog.conf ]; then
	cp -f $DIRDATE/tools/openplotter_analog.conf ~/.openplotter/
fi
