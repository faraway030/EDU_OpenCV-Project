#!/usr/bin/bash

DIR='/opt/OpenCV-Project'
if (( $EUID != 0 )); then
	sudo su
fi

if [ ! -d $DIR ]; then
	mkdir $DIR
fi

if [ -d $DIR ]; then
	cd $DIR
	curl -sSL https://raw.githubusercontent.com/faraway030/EDU_OpenCV-Project/master/server.py > server.py
	curl -SSL https://raw.githubusercontent.com/faraway030/EDU_OpenCV-Project/master/esp_proxy.py > esp_proxy.py
	curl -SSL https://raw.githubusercontent.com/faraway030/EDU_OpenCV-Project/master/mqtt.py > mqtt.py
	chmod a+x server.py
	chmod a+x esp_proxy.py
	chmod a+x mqtt.py

	if [ ! -d $DIR/data ]; then
		mkdir $DIR/data
	fi
	curl -sSL https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_alt2.xml > data/haarcascade_frontalface_alt2.xml
fi
