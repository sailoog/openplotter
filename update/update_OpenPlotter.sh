#!/bin/bash
cd ~/.config

echo
echo "DOWNLOADING NEW OPENPLOTTER CODE..."
echo
rm -rf openplotter_tmp
if [ $3 = "stable" ]; then
	git clone https://github.com/sailoog/openplotter.git openplotter_tmp
else
	git clone -b beta https://github.com/sailoog/openplotter.git openplotter_tmp
fi
if [ $? -ne 0 ]; then
	echo
	read -p "#### ERROR. ABORTING, PRESS ENTER TO EXIT ####"
	exit 1
fi
echo
echo "CREATING OPENPLOTTER CODE BACKUP..."
echo
DIRDATE=`date +openplotter_bak_%Y_%m_%d:%H:%M:%S`
cp -a openplotter/ $DIRDATE/
cd $DIRDATE
find . -name "*.pyc" -type f -delete
cd ~/.config
source openplotter_tmp/update/update_settings.sh
if [ $1 = 1 ]; then
	source openplotter_tmp/update/update_dependencies.sh
fi
echo
echo "COMPRESSING OPENPLOTTER CODE BACKUP INTO HOME..."
echo
tar cjf ~/$DIRDATE.tar.bz2 $DIRDATE
echo
echo "DELETING OLD OPENPLOTTER CODE FILES..."
echo
rm -rf openplotter
rm -rf $DIRDATE
mv openplotter_tmp openplotter
echo
read -p "FINISHED, PRESS ENTER TO REBOOT SYSTEM."
shutdown -r now

