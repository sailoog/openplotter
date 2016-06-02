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
ip = conf.get('WIFI', 'ip')
ip_split=ip.split('.')
if len(ip_split)==4:
	ip3=ip_split[0]+'.'+ip_split[1]+'.'+ip_split[2]
else:
	print('wrong ip format in openplotter.conf switch to standard')
	ip='10.10.10.1'
	ip3='10.10.10'
ssid = conf.get('WIFI', 'ssid')
hw_mode = conf.get('WIFI', 'hw_mode')
channel = conf.get('WIFI', 'channel')
wpa = conf.get('WIFI', 'wpa')
share = conf.get('WIFI', 'share')
bridge = conf.get('WIFI', 'bridge')

paths=Paths()
currentpath=paths.currentpath

subprocess.call(['service', 'hostapd', 'stop'])
subprocess.call(['service', 'dnsmasq', 'stop'])
subprocess.call(['ifconfig', wlan, 'down'])

driver='nl80211'

if wifi_server=='1':

	error=0

	original=os.path.isfile('/usr/sbin/hostapd.org')
	if not original: shutil.copyfile('/usr/sbin/hostapd', '/usr/sbin/hostapd.org')

	chipset= 'default'

	context = pyudev.Context()
	for device in context.list_devices(subsystem='net'):
		if device['INTERFACE']==wlan:
			try:
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
			except Exception,e: print str(e)
	subprocess.call(['chmod', '755', '/usr/sbin/hostapd'])

	subprocess.call(['rfkill', 'unblock', 'wifi'])

	file = open('/etc/default/hostapd', 'r',2000)
	bak=file.read()
	file.close()
	data= 'DAEMON_CONF="/etc/hostapd/hostapd.conf"'
	if bak!=data:
		file = open('/etc/default/hostapd', 'w')
		file.write(data)
		file.close()

data='interface='+wlan+'\n'
if bridge=='1' and wifi_server=='1':	data+= 'bridge=br0\n'	
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

file = open('/etc/hostapd/hostapd.conf', 'r',2000)
bak=file.read()
file.close()
if bak!=data:
	file = open('/etc/hostapd/hostapd.conf', 'w')
	file.write(data)
	file.close()

if wifi_server=='1':	
	if bridge=='0':
		data='# interfaces(5) file used by ifup(8) and ifdown(8)\nauto lo\niface lo inet loopback\n\nauto '+wlan+'\niface '+wlan+' inet static\naddress '+ip+'\nnetmask 255.255.255.0'
		#data+='\nservice hostapd start\n'
		#data+='service dnsmasq start\n'
		#if share!='0':
		#	data+='pre-up iptables -t nat -A POSTROUTING -o '+share+' -j MASQUERADE\n'
		#	data+='pre-up iptables -A FORWARD -i '+share+' -o '+wlan+' -m state --state RELATED,ESTABLISHED -j ACCEPT\n'
		#	data+='pre-up iptables -A FORWARD -i '+wlan+' -o '+share+' -j ACCEPT\n'
	else:
		data='auto lo\n'
		data+='iface lo inet loopback\n'
		data+='auto '+wlan+'\n'
		data+='iface '+wlan+' inet manual\n'
		data+='auto br0\n'
		data+='iface br0 inet static\n'
		data+='bridge_ports eth0\n'
		data+='address '+ip+'\n'
		data+='broadcast '+ip3+'.255\n'
		data+='netmask 255.255.255.0\n'
		data+='bridge_maxwait 1\n'
		#data+='up /etc/init.d/network-manager restart\n'
		#data+='service hostapd start\n'
		#data+='service dnsmasq start\n'
		#data+='up /etc/init.d/isc-dhcp-server restart\n'
		#data+='pre-up iptables -t nat -A POSTROUTING -o '+share+' -j MASQUERADE\n'
		#data+='pre-up iptables -A FORWARD -i '+share+' -o br0 -m state --state RELATED,ESTABLISHED -j ACCEPT\n'
		#data+='pre-up iptables -A FORWARD -i br0 -o '+share+' -j ACCEPT\n'
	
	file = open('/etc/network/interfaces', 'r',2000)
	bak=file.read()
	file.close()
	if bak!=data:
		file = open('/etc/network/interfaces', 'w')
		file.write(data)
		file.close()

	if bridge=='0':
		data='interface=lo,'+wlan+'\nno-dhcp-interface=lo\ndhcp-range='+ip3+'.20,'+ip3+'.254,255.255.255.0,12h'
	else:
		data='no-dhcp-interface=lo,eth0,wlan0,wlan1,ppp0\n'
		data+='interface=br0\n'
		data+='dhcp-range='+ip3+'.100,'+ip3+'.200,255.255.255.0,12h\n'
	
	print data
	file = open('/etc/dnsmasq.conf', 'r',2000)
	bak=file.read()
	file.close()
	if bak!=data:
		file = open('/etc/dnsmasq.conf', 'w')
		file.write(data)
		file.close()

	
	data='ddns-update-style none;\ndefault-lease-time 600;\nmax-lease-time 7200;\nauthoritative;\nlog-facility local7;\nsubnet '+ip3+'.0 netmask 255.255.255.0 {\nrange '+ip3+'.100 '+ip3+'.200;\noption broadcast-address '+ip3+'.255;\noption routers '+ip3+'.1;\noption domain-name "local";\noption domain-name-servers 8.8.8.8, 8.8.4.4;\n'
	
	if bridge=='0':
		data+='interface '+wlan+';\n}\n'
	else:
		data+='interface br0;\n}\n'
	
	file = open('/etc/dhcp/dhcpd.conf', 'r',2000)
	bak=file.read()
	file.close()
	if bak!=data:
		file = open('/etc/dhcp/dhcpd.conf', 'w')
		file.write(data)
		file.close()

	lan=wlan
	if bridge=='1': lan='br0'
	
	if share!='0':
		output=subprocess.call(['iptables', '-t', 'nat', '-A', 'POSTROUTING', '-o', share, '-j', 'MASQUERADE'])
		if output != 0: error=1
		output=subprocess.call(['iptables', '-A', 'FORWARD', '-i', share, '-o', lan, '-m', 'state', '--state', 'RELATED,ESTABLISHED', '-j', 'ACCEPT'])
		if output != 0: error=1
		output=subprocess.call(['iptables', '-A', 'FORWARD', '-i', lan, '-o', share, '-j', 'ACCEPT'])
		if output != 0: error=1
		
	output=subprocess.call(['service', 'networking', 'reload'])
	if output != 0: error=1
	output=subprocess.call(['systemctl', 'restart', 'NetworkManager'])
	if output != 0: error=1
	output=subprocess.call(['/etc/init.d/networking', 'restart'])
	if output != 0: error=1
	#output=subprocess.call(['systemctl', 'daemon-reload'])
	#if output != 0: error=1

	if bridge=='1':
		output=subprocess.call(['/etc/init.d/isc-dhcp-server','restart'])
		if output != 0: error=1
	output=subprocess.call(['ifconfig', wlan,'up'])
	if output != 0: error=1

	
	if bridge=='0':
		output=subprocess.call(['service', 'dnsmasq', 'start'])
		if output != 0: error=1
	
	output=subprocess.check_output(['service', 'hostapd', 'start'])
	print output
	if 'fail' in output : error=1
	#if bridge=='1':
		#output=subprocess.call(['ifconfig','wlan0', '10.10.10.2'])
		#if output != 0: error=1
		#output=subprocess.call(['ifconfig','eth0', '10.10.10.3'])
		#if output != 0: error=1
	
	print 'Chipset: '+chipset+', driver: '+driver+'.\n'

	if error==1: print "WiFi access point failed."
	else: 
		print "WiFi access point started.\n"
		print "SSID: "+ssid
		print 'Address: '+ip3+'.1'


else:
	file = open('/etc/network/interfaces', 'r',2000)
	bak=file.read()
	file.close()

	data='# interfaces(5) file used by ifup(8) and ifdown(8)\nauto lo\niface lo inet loopback'
	if bak!=data:
		file = open('/etc/network/interfaces', 'w')
		file.write(data)
		file.close()

		if bridge=='1':
			try:
				subprocess.call(['/etc/init.d/isc-dhcp-server','stop'])
				subprocess.call(['brctl', 'delif','br0','eth0'])
				#subprocess.call(['brctl', 'delif','br0','wlan0'])
				subprocess.call(['ifconfig', 'br0','down'])
				subprocess.call(['brctl', 'delbr','br0'])
				#subprocess.call(['dhclient', 'eth0'])
				
			except: pass

		
		subprocess.call(['ifconfig',wlan,'down'])
		subprocess.call(['ifconfig',wlan,'up'])

		output=subprocess.call(['iptables', '-F'])
		if output != 0: error=1
		output=subprocess.call(['service', 'networking', 'restart'])
		if output != 0: error=1
		output=subprocess.call(['/etc/init.d/networking', 'restart'])
		if output != 0: error=1
		output=subprocess.call(['systemctl', 'daemon-reload'])
		if output != 0: error=1
		output=subprocess.call(['systemctl', 'restart', 'NetworkManager'])
		if output != 0: error=1

		
		print "\nWiFi access point stopped."
		
	subprocess.call(['ifconfig',wlan,'up'])

	
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

file = open('/boot/config.txt', 'r',2000)
bak=file.read()
file.close()

if bak!=data:
	file = open('/boot/config.txt', 'w')
	file.write(data)
	file.close()	

