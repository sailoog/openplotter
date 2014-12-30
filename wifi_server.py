#!/usr/bin/env python

import subprocess, ConfigParser, os, gettext, shutil, sys

home = os.path.expanduser('~')

gettext.install('openplotter', home+'/.config/openplotter/locale', unicode=False)

wifi_server=sys.argv[1]
wlan = sys.argv[2]
passw = sys.argv[3]

if wifi_server=='1':

	error=0

	arm=0
	check_arm=os.uname()
	if check_arm[4].startswith("arm"): arm=1

	original=os.path.isfile('/usr/sbin/hostapd.org')
	if not original: shutil.copyfile('/usr/sbin/hostapd', '/usr/sbin/hostapd.org')

	driver='nl80211'
	msg= ''

	output=subprocess.check_output('lsusb')

	if arm==1 and 'RTL8188CUS' in output:
		driver='rtl871xdrv'
		shutil.copyfile(home+'/.config/openplotter/wifi_drivers/arm/RTL8188CUS/hostapd', '/usr/sbin/hostapd')
		subprocess.call(['chmod', '755', '/usr/sbin/hostapd'])
		msg= _('Using RTL8188CUS chipset and rtl871xdrv driver')
	if arm==1 and 'RTL8192CU' in output:
		driver='rtl871xdrv'
		shutil.copyfile(home+'/.config/openplotter/wifi_drivers/arm/RTL8192CU/hostapd', '/usr/sbin/hostapd')
		subprocess.call(['chmod', '755', '/usr/sbin/hostapd'])
		msg=  _('Using RTL8192CU chipset and rtl871xdrv driver')
	if driver == 'nl80211':
		shutil.copyfile('/usr/sbin/hostapd.org', '/usr/sbin/hostapd')
		subprocess.call(['chmod', '755', '/usr/sbin/hostapd'])
		msg=  _('Using default chipset and nl80211 driver')

	subprocess.call(['rfkill', 'unblock', 'wifi'])

	data= 'DAEMON_CONF="/etc/hostapd/hostapd.conf"'
	file = open('/etc/default/hostapd', 'w')
	file.write(data)
	file.close()

	data='interface='+wlan+'\ndriver='+driver+'\nssid=OpenPlotter\nchannel=6\nwmm_enabled=1\nwpa=1\nwpa_passphrase='+passw+'\nwpa_key_mgmt=WPA-PSK\nwpa_pairwise=TKIP\nrsn_pairwise=CCMP\nauth_algs=1\nmacaddr_acl=0'
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


	output=subprocess.call(['restart', 'network-manager'])
	if output != 0: error=1

	output=subprocess.call(['ifup', wlan])
	if output != 0: error=1

	output=subprocess.call(['service', 'dnsmasq', 'start'])
	if output != 0: error=1
	
	output=subprocess.check_output(['service', 'hostapd', 'start'])
	print output
	if 'fail' in output : error=1

	if error==1: print _("NMEA WiFi Server failed.\n")+msg
	else: print _("NMEA WiFi Server started.\n")+msg+_("\n\nSSID: OpenPlotter\nPassword: ")+passw+_("\n\nAdress: 10.10.10.1\nPort: 10110")


else:
	subprocess.call(['service', 'hostapd', 'stop'])
	subprocess.call(['service', 'dnsmasq', 'stop'])

	data='# interfaces(5) file used by ifup(8) and ifdown(8)\nauto lo\niface lo inet loopback'
	file = open('/etc/network/interfaces', 'w')
	file.write(data)
	file.close()

	subprocess.call(['ifdown', wlan])

	subprocess.call(['restart', 'network-manager'])

	print _("\nNMEA WiFi Server stopped.")


