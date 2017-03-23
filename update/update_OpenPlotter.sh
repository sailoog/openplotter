#!/bin/bash

echo
echo "CREATING OPENPLOTTER CODE BACKUP..."
echo
cd ~/.config
DIRDATE=`date +openplotter_bak_%Y_%m_%d:%H:%M:%S`
cp -a openplotter/ $DIRDATE/
cd $DIRDATE
find . -name "*.pyc" -type f -delete
# zip?
echo
echo "DOWNLOADING NEW OPENPLOTTER CODE..."
echo
cd ~/.config
rm -rf openplotter_tmp
#### TODO change to master ###################################################
git clone -b v0.9.0 https://github.com/sailoog/openplotter.git openplotter_tmp
##############################################################################
rm -rf openplotter_tmp/.git/

if [ $1 = 1 ]; then
	source openplotter_tmp/update/update_dependencies.sh
fi

source openplotter_tmp/update/update_settings.sh

echo
echo "DELETING OLD FILES..."
echo
rm -rf openplotter
mv openplotter_tmp openplotter


startup restart
echo
read -p "FINISHED, PRESS ENTER TO EXIT."

