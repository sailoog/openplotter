#!/usr/bin/env python

import ConfigParser, subprocess, time
from os.path import expanduser

home = expanduser("~")

data_conf = ConfigParser.SafeConfigParser()
data_conf.read(home+'/.config/openplotter/openplotter.conf')

kplex=data_conf.get('STARTUP', 'kplex')
opencpn=data_conf.get('STARTUP', 'opencpn')
opencpn_no=data_conf.get('STARTUP', 'opencpn_no_opengl')
x11vnc=data_conf.get('STARTUP', 'x11vnc')
gps_time=data_conf.get('STARTUP', 'gps_time')
sow=data_conf.get('STARTUP', 'iivbw')

enable=data_conf.get('AIS-SDR', 'enable')
gain=data_conf.get('AIS-SDR', 'gain')
ppm=data_conf.get('AIS-SDR', 'ppm')

wifi_server=data_conf.get('WIFI', 'enable')
wlan=data_conf.get('WIFI', 'device')
passw=data_conf.get('WIFI', 'password')

if kplex=='1':
	subprocess.Popen(["pkill", "kplex"])
	time.sleep(1)
	subprocess.Popen('kplex')        
else: 
	stop_kplex=subprocess.Popen(['pkill', '-9', 'kplex'])

if opencpn=='1':
	start_opencpn=subprocess.Popen('opencpn')

if opencpn_no=='1':
	start_opencpn_no=subprocess.Popen(['opencpn', '-no_opengl'])

if enable=='1':
	rtl_fm=subprocess.Popen(['rtl_fm', '-f', '161975000', '-g', gain, '-p', ppm, '-s', '48k'], stdout = subprocess.PIPE)
	aisdecoder=subprocess.Popen(['aisdecoder', '-h', '127.0.0.1', '-p', '10110', '-a', 'file', '-c', 'mono', '-d', '-f', '/dev/stdin'], stdin = rtl_fm.stdout)         
else: 
	aisdecoder=subprocess.Popen(['pkill', '-9', 'aisdecoder'], stdout = subprocess.PIPE)
	rtl_fm=subprocess.Popen(['pkill', '-9', 'rtl_fm'], stdin = aisdecoder.stdout)

if x11vnc=='1':
	start_x11vnc=subprocess.Popen(['x11vnc', '-forever'])         
else: 
	stop_x11vnc=subprocess.Popen(['pkill', '-9', 'x11vnc'])

if gps_time=='1':
	subprocess.call(['sudo', 'python', home+'/.config/openplotter/time_gps.py'])

if sow=='1':
	subprocess.Popen(['python', home+'/.config/openplotter/sog2sow.py'])
else:
	subprocess.Popen(['pkill', '-f', 'sog2sow.py'])

if wifi_server=='1':
	subprocess.call(['sudo', 'python', home+'/.config/openplotter/wifi_server.py', '1', wlan, passw])
