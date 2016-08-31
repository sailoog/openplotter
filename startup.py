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

import subprocess, time, ConfigParser, os
from classes.paths import Paths
from classes.conf import Conf
from classes.check_vessel_self import checkVesselSelf

pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]
exist=False

device = ''
ssid = ''
passw = ''
hw_mode = ''
channel = ''
wpa = ''
boot_ap = 0
bridge = ''
ip = ''
share = ''

for pid in pids:
	try:
		if 'signalk-server' in open(os.path.join('/proc', pid, 'cmdline'), 'rb').read():
			exist=True
	except IOError: # proc has already terminated
		continue
#exist=False

if not exist:
	paths=Paths()
	currentpath=paths.currentpath

	boot_ap=0
	boot_sh=0
	boot_conf = ConfigParser.SafeConfigParser()
	boot_conf.read('/boot/config.txt')
	enable='0'
	try:
		enable=boot_conf.get('OPENPLOTTER', 'wifi_enable')
	except: 
		boot_conf.set('OPENPLOTTER', 'wifi_enable','0')
	try:
		device=boot_conf.get('OPENPLOTTER', 'device')
		ssid=boot_conf.get('OPENPLOTTER', 'ssid')
		passw=boot_conf.get('OPENPLOTTER', 'pass')
		hw_mode = boot_conf.get('OPENPLOTTER', 'hw_mode')
		channel = boot_conf.get('OPENPLOTTER', 'channel')
		wpa = boot_conf.get('OPENPLOTTER', 'wpa')
		boot_ap=1
	except: boot_ap=0
	try:
		share=boot_conf.get('OPENPLOTTER', 'share')
		boot_sh=1
	except: boot_sh=0
	try:
		bridge = boot_conf.get('OPENPLOTTER', 'bridge')
		ip = boot_conf.get('OPENPLOTTER', 'ip')
	except: pass

	conf=Conf(paths)

	if enable=='1':
		if not device: device='wlan0'
		if not ssid: ssid='OpenPlotter'
		if not passw: passw='12345678'
		if not hw_mode: hw_mode='g'
		if not channel: channel='6'
		if not wpa: wpa='2'
		if not bridge: bridge='0'
		if not ip: ip='10.10.10.1'	
		if conf.get('WIFI', 'enable')!=enable:   conf.set('WIFI', 'enable', enable)
		if conf.get('WIFI', 'device')!=device:   conf.set('WIFI', 'device', device)
		if conf.get('WIFI', 'ssid')!=ssid:       conf.set('WIFI', 'ssid', ssid)
		if conf.get('WIFI', 'password')!=passw:  conf.set('WIFI', 'password', passw)
		if conf.get('WIFI', 'hw_mode')!=hw_mode: conf.set('WIFI', 'hw_mode', hw_mode)
		if conf.get('WIFI', 'channel')!=channel: conf.set('WIFI', 'channel', channel)
		if conf.get('WIFI', 'wpa')!=wpa:         conf.set('WIFI', 'wpa', wpa)
		if conf.get('WIFI', 'bridge')!=bridge:   conf.set('WIFI', 'bridge', bridge)
		if conf.get('WIFI', 'ip')!=ip:           conf.set('WIFI', 'ip', ip)
		
	if boot_sh==1:
		if not share: share='0'
		if conf.get('WIFI', 'share')!=share: conf.set('WIFI', 'share', share)

	wifi_server=conf.get('WIFI', 'enable')

	delay=int(conf.get('STARTUP', 'delay'))

	kplex=conf.get('STARTUP', 'kplex')
	opencpn=conf.get('STARTUP', 'opencpn')
	opencpn_no=conf.get('STARTUP', 'opencpn_no_opengl')
	opencpn_fullscreen=conf.get('STARTUP', 'opencpn_fullscreen')
	x11vnc=conf.get('STARTUP', 'x11vnc')
	vnc_pass=conf.get('STARTUP', 'vnc_pass')
	gps_time=conf.get('STARTUP', 'gps_time')
	play=conf.get('STARTUP', 'play')
	sound=conf.get('STARTUP', 'sound')
	
	enable=conf.get('AIS-SDR', 'enable')
	gain=conf.get('AIS-SDR', 'gain')
	ppm=conf.get('AIS-SDR', 'ppm')
	channel=conf.get('AIS-SDR', 'channel')
		
	nmea_mag_var=conf.get('CALCULATE', 'nmea_mag_var')
	nmea_hdt=conf.get('CALCULATE', 'nmea_hdt')
	nmea_rot=conf.get('CALCULATE', 'nmea_rot')
	TW_STW=conf.get('CALCULATE', 'tw_stw')
	TW_SOG=conf.get('CALCULATE', 'tw_sog')

	N2K_output=conf.get('N2K', 'output')

	tools_py=[]
	if conf.has_section('TOOLS'):
		if conf.has_option('TOOLS', 'py'):
			data=conf.get('TOOLS', 'py')
			try:
				temp_list=eval(data)
			except:temp_list=[]
			if type(temp_list) is list: pass
			else:	temp_list=[]
			for ii in temp_list:
				tools_py.append(ii)

	#######################################################
	time.sleep(delay)

	try:
		subprocess.call(['pkill', '-9', 'x11vnc'])
		if x11vnc=='1':
			if vnc_pass=='1': process = subprocess.Popen(['x11vnc', '-forever', '-shared', '-usepw'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			else: process = subprocess.Popen(['x11vnc', '-forever', '-shared' ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			time.sleep(5)
	except: print 'x11vnc not installed'

	opencpn_commands = ['opencpn']
	if opencpn_no=='1': opencpn_commands.append('-no_opengl')
	if opencpn_fullscreen=='1': opencpn_commands.append('-fullscreen')

	if opencpn=='1' and len(opencpn_commands)>1: subprocess.Popen(opencpn_commands)
	if opencpn=='1' and len(opencpn_commands)==1: subprocess.Popen('opencpn')

	if wifi_server=='1':
		process = subprocess.Popen(['sudo', 'python', currentpath+'/wifi_server.py', '1'])
	else:
		process = subprocess.Popen(['sudo', 'python', currentpath+'/wifi_server.py', '0'])

	process.wait()

	subprocess.call(['pkill', '-9', 'kplex'])
	if kplex=='1':
		subprocess.Popen('kplex')

	subprocess.call(["pkill", '-9', "node"])
	vessel_self=checkVesselSelf()
	
	if gps_time=='1':
		subprocess.call(['sudo', 'python', currentpath+'/time_gps.py'])

	subprocess.call(['pkill', '-f', 'calculate_d.py'])
	if nmea_mag_var=='1' or nmea_hdt=='1' or nmea_rot=='1' or TW_STW=='1' or TW_SOG=='1': 
		subprocess.Popen(['python', currentpath+'/tools/calculate_d.py'])

	subprocess.call(['pkill', '-9', 'aisdecoder'])
	subprocess.call(['pkill', '-9', 'rtl_fm'])
	if enable=='1':
		frecuency='161975000'
		if channel=='b': frecuency='162025000'
		rtl_fm=subprocess.Popen(['rtl_fm', '-f', frecuency, '-g', gain, '-p', ppm, '-s', '48k'], stdout = subprocess.PIPE)
		aisdecoder=subprocess.Popen(['aisdecoder', '-h', '127.0.0.1', '-p', '10110', '-a', 'file', '-c', 'mono', '-d', '-f', '/dev/stdin'], stdin = rtl_fm.stdout)

	subprocess.call(['pkill', '-9', 'mpg123'])
	if play=='1':
		if sound:
			try: subprocess.Popen(['mpg123', '-q', sound])
			except: pass

	index=0
	for i in tools_py:
		if i[3]=='1':
			subprocess.Popen(['python',currentpath+'/tools/'+tools_py[index][2]])	
		index+=1
			