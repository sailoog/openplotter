openplotter-sailpi
==================
Project page: http://campus.sailoog.com/course/view.php?id=9

Instructions
------------

##### Create an SD card with the last version of Raspian:
http://www.raspberrypi.org/downloads/

##### Install dependencies:
```sh
sudo apt-get install python-pip python-wxgtk2.8 isc-dhcp-server hostapd
```

##### Install kplex:
http://www.stripydog.com/kplex/kplex.html

##### Install pynme2:
```sh
git clone git://github.com/Knio/pynmea2.git
cd pynmea2
sudo pip install pynmea2
```
##### Follow this tutorial:
https://learn.adafruit.com/setting-up-a-raspberry-pi-as-a-wifi-access-point?view=all

##### Copy this repository to /home/pi/.config/openplotter

##### Set permissions:
```sh
cd /home/pi/.config/openplotter
sudo chmod 755 reset_kplex_cron.sh
sudo chmod 755 gps_time_cron.sh
sudo chmod 755 openplotter.py
sudo chmod 755 gps_time_daemon.py

cd /home/pi/.config/openplotter/nmea_wifi_server
sudo chown root:root switch_access_point.sh
sudo chmod 755 switch_access_point.sh
```
##### Run:
```sh
python /home/pi/.config/openplotter/openplotter.py
```



