#!/bin/bash

cd ~/.config/openplotter
ANSWER=""
if [ -d ~/.config/openplotter/.git ]
then
	git fetch origin
	UPSTREAM=${1:-'@{u}'}
	LOCAL=$(git rev-parse @)
	REMOTE=$(git rev-parse "$UPSTREAM")
	BASE=$(git merge-base @ "$UPSTREAM")

	if [ $LOCAL = $REMOTE ]; then
		echo "Up-to-date"
		ANSWER="Up-to-date"
	elif [ $LOCAL = $BASE ]; then
		echo "Need to pull"
	elif [ $REMOTE = $BASE ]; then
		echo "Need to push"
	else
		echo "Diverged"
	fi
else
    echo "no .git found"
fi

if [ "$ANSWER" == "" ]
then
    cd ~
	startup stop
    DIRDATE=`date +op_backup_%Y_%m_%d:%H:%M:%S`
	echo "backup files to:" $DIRDATE
    mkdir $DIRDATE
    mkdir $DIRDATE/classes
    mkdir $DIRDATE/OP-signalk
    mkdir $DIRDATE/other
    mkdir $DIRDATE/tools
    mkdir $DIRDATE/tools/classes

    cp ~/.config/openplotter/classes/* ~/$DIRDATE/classes
    cp ~/.config/openplotter/tools/classes/* ~/$DIRDATE/tools/classes
	rm ~/$DIRDATE/classes/*.pyc
	rm ~/$DIRDATE/tools/classes/*.pyc
    cp ~/.config/openplotter/* ~/$DIRDATE
    cp ~/.config/openplotter/OP-signalk/* ~/$DIRDATE/OP-signalk
    cp ~/.config/openplotter/tools/* ~/$DIRDATE/tools
    cp ~/.kplex.conf ~/$DIRDATE/other
    cp /boot/config.txt ~/$DIRDATE/other
    cp /etc/udev/rules.d/10-openplotter.rules ~/$DIRDATE/other

	cd ~/.config
	rm -rf openplotter
	git clone -b v0.9.0 https://github.com/sailoog/openplotter.git
	cd ~/.config/openplotter

    sudo chmod 755 openplotter
    sudo chmod 755 keyword
    sudo chmod 755 startup
    cp ~/.config/openplotter/update/*.sh ~/	
fi