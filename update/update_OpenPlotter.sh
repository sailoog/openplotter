#!/bin/bash

if [ $1 -eq 0 ] || [ $2 -eq 0 ]
	then
		echo "No arguments supplied: update_OpenPlotter.sh <type> <branch>"
		echo "<type>: major or minor"
		echo "<branch>: stable or beta"
		exit 1
fi

type=$1
branch=$2
op_folder=$(crudini --get ~/.openplotter/openplotter.conf GENERAL op_folder)
master_github_repositories=$(crudini --get ~/.openplotter/openplotter.conf UPDATE master_github_repositories)
beta_github_repositories=$(crudini --get ~/.openplotter/openplotter.conf UPDATE beta_github_repositories)
stable=$(crudini --get ~/.openplotter/openplotter.conf UPDATE stable_branch)
beta=$(crudini --get ~/.openplotter/openplotter.conf UPDATE beta_branch)

cd $op_folder/..

echo
echo "DOWNLOADING NEW OPENPLOTTER CODE..."
echo
rm -rf openplotter_tmp
if [ $branch = "stable" ]; then
	git clone -b $stable https://github.com/$master_github_repositories/openplotter.git openplotter_tmp
elif [ $branch = "beta" ]; then
	git clone -b $beta https://github.com/$master_github_repositories/openplotter.git openplotter_tmp
else
	echo
	read -p "#### WRONG BRANCH. ABORTING, PRESS ENTER TO EXIT ####"
	exit 1
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

cd $op_folder/..

source openplotter_tmp/update/update_settings.sh

if [ $type = "major" ]; then
	source openplotter_tmp/update/update_dependencies.sh
elif [ $type = "minor" ]; then
	:
else
	echo
	read -p "#### WRONG UPDATE TYPE. ABORTING, PRESS ENTER TO EXIT ####"
	exit 1
fi

cd $op_folder/..

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

