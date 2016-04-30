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

import subprocess, os, shutil, sys, pyudev
from classes.paths import Paths
from classes.conf import Conf

conf=Conf()

wifi_server=sys.argv[1]
wlan = conf.get('WIFI', 'device')
passw = conf.get('WIFI', 'password')
ssid = conf.get('WIFI', 'ssid')
hw_mode = conf.get('WIFI', 'hw_mode')
channel = conf.get('WIFI', 'channel')
wpa = conf.get('WIFI', 'wpa')
share = conf.get('WIFI', 'share')

paths=Paths()
currentpath=paths.currentpath

subprocess.call(['service', 'hostapd', 'stop'])
subprocess.call(['service', 'dnsmasq', 'stop'])
subprocess.call(['ifdown', wlan])

if wifi_server=='1':

	error=0

	original=os.path.isfile('/usr/sbin/hostapd.org')
	if not original: shutil.copyfile('/usr/sbin/hostapd', '/usr/sbin/hostapd.org')

	driver='nl80211'
	chipset= 'default'

	context = pyudev.Context()
	for device in context.list_devices(subsystem='net'):
		if device['INTERFACE']==wlan:
			if device['ID_NET_DRIVER']=='brcmfmac':
				shutil.copyfile('/usr/sbin/hostapd.org', '/usr/sbin/hostapd')
				chipset= 'Built-in WiFi'
			if device['ID_NET_DRIVER']=='rtl8192cu':
				driver='rtl871xdrv'
				chipset= 'RTL8192CU'
				shutil.copyfile(currentpath+'/wifi_drivers/RTL8192CU/hostapd', '/usr/sbin/hostapd')
			if device['ID_NET_DRIVER']=='rtl8192eu':
				driver='rtl871xdrv'
				chipset= 'RTL8192EU'
				shutil.copyfile(currentpath+'/wifi_drivers/RTL8192EU/hostapd', '/usr/sbin/hostapd')
			if device['ID_NET_DRIVER']=='rtl8188cus':
				driver='rtl871xdrv'
				chipset= 'RTL8188CUS'
				shutil.copyfile(currentpath+'/wifi_drivers/RTL8188CUS/hostapd', '/usr/sbin/hostapd')
			if device['ID_NET_DRIVER']=='rtl8188eu':
				driver=''
				chipset= 'RTL8188EU'
				shutil.copyfile(currentpath+'/wifi_drivers/RTL8188EU/hostapd', '/usr/sbin/hostapd')
			if chipset == 'default':
				shutil.copyfile('/usr/sbin/hostapd.org', '/usr/sbin/hostapd')
		
	subprocess.call(['chmod', '755', '/usr/sbin/hostapd'])

	subprocess.call(['rfkill', 'unblock', 'wifi'])

	data= 'DAEMON_CONF="/etc/hostapd/hostapd.conf"'
	file = open('/etc/default/hostapd', 'w')
	file.write(data)
	file.close()

	data='interface='+wlan+'\n'
	if driver!='': data+= 'driver='+driver+'\n'
	data+= 'hw_mode='+hw_mode+'\n'
	data+= 'channel='+channel+'\n'
	data+= 'ieee80211n=1\n'
	data+= 'wmm_enabled=1\n'
	data+= 'ssid='+ssid+'\n'
	data+= 'auth_algs=1\n'
	data+= 'wpa='+wpa+'\n'
	data+= 'wpa_key_mgmt=WPA-PSK\n'
	data+= 'rsn_pairwise=CCMP\n'
	data+= 'wpa_passphrase='+passw+'\n'

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
	
	if share!='0':
		output=subprocess.call(['iptables', '-t', 'nat', '-A', 'POSTROUTING', '-o', share, '-j', 'MASQUERADE'])
		if output != 0: error=1
		output=subprocess.call(['iptables', '-A', 'FORWARD', '-i', share, '-o', wlan, '-m', 'state', '--state', 'RELATED,ESTABLISHED', '-j', 'ACCEPT'])
		if output != 0: error=1
		output=subprocess.call(['iptables', '-A', 'FORWARD', '-i', wlan, '-o', share, '-j', 'ACCEPT'])
		if output != 0: error=1
	
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
		print "SSID: "+ssid
		print "Adress: 10.10.10.1"

else:
	data='# interfaces(5) file used by ifup(8) and ifdown(8)\nauto lo\niface lo inet loopback'
	file = open('/etc/network/interfaces', 'w')
	file.write(data)
	file.close()
	subprocess.call(['/etc/init.d/network-manager', 'restart'])
	print "\nWiFi access point stopped."

data=''
file = open('/boot/config.txt', 'r')
file.seek(0)
for line in file:
	data0=''
	if '#' in line: data0=line
	else:
		if 'device' in line: data0='device='+wlan+'\n'
		if 'ssid' in line: data0='ssid='+ssid+'\n'
		if 'pass' in line: data0='pass='+passw+'\n'
		if 'hw_mode' in line: data0='hw_mode='+hw_mode+'\n'
		if 'channel' in line: data0='channel='+channel+'\n'
		if 'wpa' in line: data0='wpa='+wpa+'\n'
		if 'share' in line: data0='share='+share+'\n'
	if not data0: data0=line
	data+=data0
file.close()
file = open('/boot/config.txt', 'w')
file.write(data)
file.close()