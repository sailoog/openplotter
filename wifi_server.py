#!/usr/bin/env python

# This file is part of Openplotter.
# Copyright (C) 2015 by sailoog <https://github.com/sailoog/openplotter>
#
# Openplotter is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# any later version.
# Openplotter is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Openplotter. If not, see <http://www.gnu.org/licenses/>.

import subprocess, ConfigParser, os, gettext, shutil, sys

wifi_server=sys.argv[1]
wlan = sys.argv[2]
passw = sys.argv[3]

pathname = os.path.dirname(sys.argv[0])
currentpath = os.path.abspath(pathname)

subprocess.call(['service', 'hostapd', 'stop'])
subprocess.call(['service', 'dnsmasq', 'stop'])
subprocess.call(['ifdown', wlan])
	
if wifi_server=='1':

	error=0

	original=os.path.isfile('/usr/sbin/hostapd.org')
	if not original: shutil.copyfile('/usr/sbin/hostapd', '/usr/sbin/hostapd.org')

	driver='nl80211'
	chipset= 'default'

#Agregado -----------------------------
	wfap=''
	archivo = '/home/pi/.config/openplotter/WiFiAP.conf'
	if os.path.exists(archivo): # si ya fue configurado en openplotter
		wifiarc=open(archivo,'r')
		wfap=wifiarc.readline()
		wifiarc.close()
	else:
		# esto permite, para la primera vez, configurar varias microSD sin abrir OpenPlotter, directamente desde el lector, en la raiz
		archivo = '/boot/WiFiAP.conf'
		if os.path.exists(archivo): 
			wifiarc=open(archivo,'r')
			wfap=wifiarc.readline()
			wifiarc.close()
			# ahora grabo en localizacion principal
			wifiarc=open('/home/pi/.config/openplotter/WiFiAP.conf','w')
			wifiarc.write(wfap)
			wifiarc.close()
#======================================

	output=subprocess.check_output('lsusb')

	if 'RTL8188CUS' in output:
		driver='rtl871xdrv'
		chipset= 'RTL8188CUS'
		shutil.copyfile(currentpath+'/wifi_drivers/RTL8188CUS/hostapd', '/usr/sbin/hostapd')
		subprocess.call(['chmod', '755', '/usr/sbin/hostapd'])
	if 'RTL8192CU' in output:
		driver='rtl871xdrv'
		chipset= 'RTL8192CU'
		shutil.copyfile(currentpath+'/wifi_drivers/RTL8192CU/hostapd', '/usr/sbin/hostapd')
		subprocess.call(['chmod', '755', '/usr/sbin/hostapd'])
	if '0bda:818b' in output:
		driver='rtl871xdrv'
		chipset= 'RTL8192EU'
		shutil.copyfile(currentpath+'/wifi_drivers/RTL8192EU/hostapd', '/usr/sbin/hostapd')
		subprocess.call(['chmod', '755', '/usr/sbin/hostapd'])
	if chipset == 'default':
		shutil.copyfile('/usr/sbin/hostapd.org', '/usr/sbin/hostapd')
		subprocess.call(['chmod', '755', '/usr/sbin/hostapd'])

	subprocess.call(['rfkill', 'unblock', 'wifi'])

	data= 'DAEMON_CONF="/etc/hostapd/hostapd.conf"'
	file = open('/etc/default/hostapd', 'w')
	file.write(data)
	file.close()

#Modificado----------------------------
	data='interface='+wlan+'\ndriver='+driver+'\nssid=OpenPlotter'+wfap.strip()+'\nchannel=6\nwmm_enabled=1\nwpa=1\nwpa_passphrase='+passw+'\nwpa_key_mgmt=WPA-PSK\nwpa_pairwise=TKIP\nrsn_pairwise=CCMP\nauth_algs=1\nmacaddr_acl=0'
#======================================

	file = open('/etc/hostapd/hostapd.conf', 'w')
	file.write(data)
	file.close()

	data='# interfaces(5) file used by ifup(8) and ifdown(8)\nauto lo\niface lo inet loopback\n\nauto '+wlan+'\niface '+wlan+' inet static\naddress 10.10.10.1\nnetmask 255.255.255.0'
	file = open('/etc/network/interfaces', 'w')
	file.write(data)
	file.close()

	data='interface=lo,'+wlan+'\nno-dhcp-interface=lo\ndhcp-range=10.10.10.20,10.10.10.254,255.255.255.0,12h'
	file = open('/etc/dnsmasq.conf', 'w')
	file.write(data)
	file.close()

	nm_conf = ConfigParser.SafeConfigParser()
	nm_conf.read('/etc/NetworkManager/NetworkManager.conf')
	nm_conf.set('ifupdown', 'managed', 'false')
	with open('/etc/NetworkManager/NetworkManager.conf', 'wb') as configfile:
		nm_conf.write(configfile)

	output=subprocess.call(['/etc/init.d/network-manager', 'restart'])
	if output != 0: error=1

	output=subprocess.call(['ifup', wlan])
	if output != 0: error=1

	output=subprocess.call(['service', 'dnsmasq', 'start'])
	if output != 0: error=1
	
	output=subprocess.check_output(['service', 'hostapd', 'start'])
	print output
	if 'fail' in output : error=1

	print 'Chipset: '+chipset+', driver: '+driver+'.\n'

	if error==1: print "WiFi access point failed."
	else: 
		print "WiFi access point started.\n"
		print "SSID: OpenPlotter"
		print "Password: "+passw
		print "Adress: 10.10.10.1"


else:

	data='# interfaces(5) file used by ifup(8) and ifdown(8)\nauto lo\niface lo inet loopback'
	file = open('/etc/network/interfaces', 'w')
	file.write(data)
	file.close()

	subprocess.call(['/etc/init.d/network-manager', 'restart'])

	print "\nWiFi access point stopped."
