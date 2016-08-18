#!/usr/bin/env python

# This file is part of Openplotter.
# Copyright (C) 2015 by sailoog <https://github.com/sailoog/openplotter>
# 					  e-sailing <https://github.com/e-sailing/openplotter>
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

import subprocess, os, shutil, sys, pyudev, time
from classes.paths import Paths
from classes.conf import Conf

conf=Conf()
change=False

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
ipfix='192.168.7.7'
ipfix3='192.168.7'

ssid = conf.get('WIFI', 'ssid')
hw_mode = conf.get('WIFI', 'hw_mode')
channel = conf.get('WIFI', 'channel')
wpa = conf.get('WIFI', 'wpa')
share = conf.get('WIFI', 'share')
bridge = conf.get('WIFI', 'bridge')

paths=Paths()
currentpath=paths.currentpath

driver='nl80211'
error=0

if wifi_server=='1':
	file = open('/etc/default/hostapd', 'r',2000)
	bak=file.read()
	file.close()
	data= 'DAEMON_CONF="/etc/hostapd/hostapd.conf"'
	if bak!=data:
		change=True
		file = open('/etc/default/hostapd', 'w')
		file.write(data)
		file.close()

data='interface='+wlan+'\n'
if bridge=='1' and wifi_server=='1':	data+= 'bridge=br0\n'	
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
	change=True
	file = open('/etc/hostapd/hostapd.conf', 'w')
	file.write(data)
	file.close()

lan=wlan
if bridge=='1': lan='br0'
	
data=''	
if wifi_server=='1':	
	if bridge=='0':
		data+='auto lo\n'
		data+='iface lo inet loopback\n'
		data+='pre-down iwconfig '+wlan+' essid '+ssid+'\n'
		data+='allow-hotplug eth0\n'
		data+='iface eth0 inet dhcp\n'

		data+='auto eth0:0\n'
		data+='iface eth0:0 inet static\n'
		data+='address '+ipfix+'\n'
		data+='broadcast '+ipfix3+'.255\n'
		data+='netmask 255.255.255.0\n'
		
		data+='auto '+wlan+'\n'
		data+='iface '+wlan+' inet static\n'
		data+='address '+ip+'\n'
		data+='netmask 255.255.255.0\n'
		data+='post-up ifconfig '+wlan+' up\n'
		if share != '0':
			data+='post-up iptables -t nat -A POSTROUTING -o '+share+' -j MASQUERADE\n'
			data+='post-up iptables -A FORWARD -i '+ share + ' -o ' +lan+ ' -m state --state RELATED,ESTABLISHED -j ACCEPT\n'
			data+='post-up iptables -A FORWARD -i '+ lan+ ' -o '+ share+ ' -j ACCEPT\n'
		data+='post-up systemctl restart NetworkManager\n'
		data+='post-up service dnsmasq restart\n'
		data+='post-up service hostapd restart\n'
		data+='post-up ifconfig '+wlan+' '+ip3+'.1 netmask 255.255.255.0\n'
		
	else:
		data='auto lo\n'
		data+='iface lo inet loopback\n'
		
		data+='pre-down iwconfig '+wlan+' essid '+ssid+'\n'
		data+='auto '+wlan+'\n'
		data+='iface '+wlan+' inet manual\n'
		data+='allow-hotplug eth0\n'
		data+='iface eth0 inet manual\n'
		
		data+='auto br0\n'
		data+='iface br0 inet static\n'
		data+='bridge_ports eth0\n'
		data+='bridge_ports eth0 '+wlan+'\n'
		data+='address '+ip+'\n'
		data+='broadcast '+ip3+'.255\n'
		data+='netmask 255.255.255.0\n'
		data+='bridge_maxwait 1\n'
		
		data+='auto br0:0\n'
		data+='iface br0:0 inet static\n'
		data+='address '+ipfix+'\n'
		data+='broadcast '+ipfix3+'.255\n'
		data+='netmask 255.255.255.0\n'
		
		if share != '0':
			data+='post-up iptables -t nat -A POSTROUTING -o '+share+' -j MASQUERADE\n'
			data+='post-up iptables -A FORWARD -i '+ share + ' -o ' +lan+ ' -m state --state RELATED,ESTABLISHED -j ACCEPT\n'
			data+='post-up iptables -A FORWARD -i '+ lan+ ' -o '+ share+ ' -j ACCEPT\n'
		data+='post-up systemctl restart NetworkManager\n'
		data+='post-up service dnsmasq restart\n'
		data+='post-up service hostapd restart\n'
		data+='post-up ifconfig br0 '+ip3+'.1 netmask 255.255.255.0\n'
			
	file = open('/etc/network/interfaces', 'r',2000)
	bak=file.read()
	file.close()
	if bak!=data:
		change=True
		file = open('/etc/network/interfaces', 'w')
		file.write(data)
		file.close()

	if bridge=='0':
		wlanx='wlan0'
		if wlan[-1:]=='0':wlanx='wlan1'
		data='no-dhcp-interface=lo,eth0,'+wlanx+',ppp0\n'
		data+='interface='+wlan+'\n'
		data+='dhcp-range='+ip3+'.20,'+ip3+'.254,255.255.255.0,12h\n'
	else:
		data='no-dhcp-interface=lo,eth0,wlan0,wlan1,ppp0\n'
		data+='interface=br0\n'
		data+='dhcp-range='+ip3+'.100,'+ip3+'.200,255.255.255.0,12h\n'
	
	file = open('/etc/dnsmasq.conf', 'r',2000)
	bak=file.read()
	file.close()
	if bak!=data:
		change=True
		file = open('/etc/dnsmasq.conf', 'w')
		file.write(data)
		file.close()
	
	data='ddns-update-style none;\n'
	data+='default-lease-time 600;\n'
	data+='max-lease-time 7200;\n'
	data+='authoritative;\n'
	data+='log-facility local7;\n'
	data+='subnet '+ip3+'.0 netmask 255.255.255.0 {\n'
	data+='range '+ip3+'.100 '+ip3+'.200;\n'
	data+='option broadcast-address '+ip3+'.255;\n'
	data+='option routers '+ip3+'.1;\n'
	data+='option domain-name "local";\n'
	data+='option domain-name-servers 8.8.8.8, 8.8.4.4;\n'
	
	if bridge=='0':
		data+='interface '+wlan+';\n'
		data+='}\n'
	else:
		data+='interface br0;\n'
		data+='}\n'
	
	file = open('/etc/dhcp/dhcpd.conf', 'r',2000)
	bak=file.read()
	file.close()
	if bak!=data:
		change=True
		file = open('/etc/dhcp/dhcpd.conf', 'w')
		file.write(data)
		file.close()

	if change:
		if bridge=='1' and 'eth0:0' in subprocess.check_output('ifconfig'):
			subprocess.call(['ifconfig', 'eth0:0','down'])
		output=subprocess.call(['service', 'hostapd', 'stop'])
		output=subprocess.call(['service', 'dnsmasq', 'stop'])
		output=subprocess.call(['service', 'networking', 'stop'])
		output=subprocess.call(['systemctl', 'daemon-reload'])
		output=subprocess.call(['service', 'networking', 'start'])
		
	msg1=''
	network_info=''
	try: network_info=subprocess.check_output('service dnsmasq status'.split()) 
	except: pass
	for i in network_info.split('\n'):
		if 'running' in i: msg1+='running'
	if msg1 == '': error==1
	
	msg1=''
	network_info=''
	try: network_info=subprocess.check_output('service hostapd status'.split()) 
	except: pass
	for i in network_info.split('\n'):
		if 'running' in i: msg1+='running'
	if msg1 == '': error==1
	
	msg1=''
	network_info=''
	try: network_info=subprocess.check_output('service networking status'.split()) 
	except: pass
	for i in network_info.split('\n'):
		if 'SUCCESS' in i: msg1+='started'
	if msg1 == '': error==1	
	
	if error==1: print "WiFi access point failed."
	else:
		print "WiFi access point started.\n"
		print "SSID: "+ssid
		print 'Address: '+ip3+'.1'

else:
	file = open('/etc/network/interfaces', 'r',2000)
	bak=file.read()
	file.close()

	data='# interfaces(5) file used by ifup(8) and ifdown(8)\n'
	data+='auto lo\n'
	data+='iface lo inet loopback\n'

	data+='allow-hotplug eth0\n'
	data+='iface eth0 inet dhcp\n'
	data+='auto eth0:0\n'
	data+='iface eth0:0 inet static\n'
	data+='address '+ipfix+'\n'
	data+='broadcast '+ipfix3+'.255\n'
	data+='netmask 255.255.255.0\n'
	data+='post-up /sbin/ifconfig eth0:0 '+ipfix+' netmask 255.255.255.0\n'


	if bak!=data:
		file = open('/etc/network/interfaces', 'w')
		file.write(data)
		file.close()

		if 'br0:0' in subprocess.check_output('ifconfig'):
			subprocess.call(['brctl', 'delif','br0','eth0'])
			subprocess.call(['ifconfig', 'br0','down'])
			subprocess.call(['brctl', 'delbr','br0'])

		output=subprocess.call(['iptables', '-F'])
		if output != 0: error=1
		output=subprocess.call(['service', 'dnsmasq', 'stop'])
		if output != 0: error=1
		output=subprocess.call(['service', 'hostapd', 'stop'])
		if output != 0: error=1
		#output=subprocess.call(['service', 'networking', 'restart'])
		#if output != 0: error=1
		output=subprocess.call(['systemctl', 'daemon-reload'])
		if output != 0: error=1
		output=subprocess.call(['systemctl', 'restart', 'NetworkManager'])
		if output != 0: error=1

		if 'eth0:0' in subprocess.check_output('ifconfig'):pass
		else:
			subprocess.call(['ifconfig', 'eth0:0', ipfix,'netmask','255.255.255.0'])
		
		print "\nWiFi access point stopped."
			
data=''


file = open('/boot/config.txt', 'r')
file.seek(0)
for line in file:
	data0=''
	if '#' in line: data0=line
	else:
		if 'device' in line: data0='device='+wlan+'\n'
		elif 'ssid' in line: data0='ssid='+ssid+'\n'
		elif 'pass' in line: data0='pass='+passw+'\n'
		elif 'hw_mode' in line: data0='hw_mode='+hw_mode+'\n'
		elif 'channel' in line: data0='channel='+channel+'\n'
		elif 'wpa' in line: data0='wpa='+wpa+'\n'
		elif 'share' in line: data0='share='+share+'\n'
		elif 'bridge' in line: data0='bridge='+bridge+'\n'
		elif 'ip' in line: data0='ip='+ip+'\n'

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
