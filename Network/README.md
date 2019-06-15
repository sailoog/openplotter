OpenPlotter does use standard raspbian network!

The additional packets needed for AP are:
sudo apt-get install hostapd dnsmasq
The additional packets to use eth0 in the same net as the AP are:
sudo apt-get install bridge-utils

When activating a network profile with "Apply 1" OpenPlotter: copies the selected setting from here to the directory /home/pi/.openplotter/Network
OpenPlotter edit the individual settings as ssid password ... here.
Manual settings should be done here also.

The "Apply 2" button copies the .conf files into the system.

(wlan9 is used for the AP. In the past it was wlan1 or uap0. Now you can use more wifi adapter. But remember the internet connection could only work with the first gateway (use: "route -n" to see it)) 

Some settings are done by a cronjob which is called once when booting.
It starts the bash script /home/pi/.openplotter/start-ap-managed-wifi.sh

Headless mode with android device as display (android will be on usb0)
Use android device to connect to the rpi with usb cable.
Activate tethering usb in android.
Now you have a network connection between rpi and android.
Install realvnc.
Start realvnc with ip address 192.168.42.10 or openplotter.

Headless mode with iphone/ipad device as display (iphone will be on eth1)
Use iphone/ipad device to connect to the rpi with usb cable.
Install realvnc.
Start realvnc with ip address openplotter.local

The raspbian standard wifi settings (in the upper right corner) often don't want to change from one marina to the next one.
If you don't get the connection symbol you can "Turn Off Wifi" and "Turn On Wifi". To get it to work. (Wait an instant until the wlan list AP.)
If you are connected over the AP use the
bash file /home/pi/.openplotter/Network/restart_wlan0.sh

Internet sharing
To share the internet connection you have to switch to the network where internet is connected.
If you have more than one internet connection, only the connection with the lowest standard gateway matrix (first line of "route -n") can be shared.

Add ethernet port to the AP is only needed when you want to connect a ethernet mfd (plotter) or a ethernet radar.

Some usb wifi have 5 GHz but the driver don't support AP mode with 5 GHz.
There is no support for 5 GHz AP ac mode at the moment. 

For rpi 3b (not 3b+) you can use the internal wifi to act as AP and Station. This is good to save energy. But it isn't so realiable and it reduces speed.
(see https://github.com/peebles/rpi3-wifi-station-ap-stretch)

To have a good internet connection we recommend to use a usb wifi stick with antenna connected by a long usb cable (with active usb hub at the end to have good 5V supply)
to get best connection to the marina wifi.
