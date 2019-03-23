OpenPlotter does use standard raspbian network!

The additional packets needed for AP are:
sudo apt-get install hostapd dnsmasq
The additional packets to use eth0 in the same net as the AP are:
sudo apt-get install bridge-utils

When activating a network profile with "set" OpenPlotter copies the selected setting from here to directory to /home/pi/.openplotter/Network
OpenPlotter edit the individual settings as ssid password ... here.
Manual settings should be done here also.

The "Apply" button copies the .conf files into the system.

Some settings are done by a cronjob which is called once when booting.
It starts the bash script /home/pi/.openplotter/start-ap-managed-wifi.sh

Headless mode / use android device as display
Use android device to connect to the rpi with usb cable.
Activate tethering usb in android.
Now you have a network connection between rpi and android. 
Start realvnc on android with ip address 192.168.42.100.
(see settings in dhcpcd.conf)

The raspbian standard wifi settings (in the upper right corner) often don't want to change from one marina to the next one.
If you don't get the connection symbol you can "Turn Off Wifi" and "Turn On Wifi". To get it to work.
If you are connected over the AP use the
bash file /home/pi/.openplotter/Network/restart_wlan0.sh
