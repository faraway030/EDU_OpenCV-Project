#!/usr/bin/bash

DIR='/opt/OpenCV-Project'
if (( $EUID != 0 )); then
	sudo su
fi
mkdir $DIR
if [ -d $DIR ]; then
	cd $DIR
	curl -sSL https://raw.githubusercontent.com/faraway030/EDU_OpenCV-Project/master/client.py > client.py
	chmod a+x client.py
fi
