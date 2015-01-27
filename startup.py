#!/usr/bin/env python

import ConfigParser, subprocess, os, sys, time

pathname = os.path.dirname(sys.argv[0])
currentpath = os.path.abspath(pathname)

data_conf = ConfigParser.SafeConfigParser()
data_conf.read(currentpath+'/openplotter.conf')

kplex=data_conf.get('STARTUP', 'kplex')
opencpn=data_conf.get('STARTUP', 'opencpn')
opencpn_no=data_conf.get('STARTUP', 'opencpn_no_opengl')
opencpn_fullscreen=data_conf.get('STARTUP', 'opencpn_fullscreen')
x11vnc=data_conf.get('STARTUP', 'x11vnc')
gps_time=data_conf.get('STARTUP', 'gps_time')
sow=data_conf.get('STARTUP', 'iivbw')

enable=data_conf.get('AIS-SDR', 'enable')
gain=data_conf.get('AIS-SDR', 'gain')
ppm=data_conf.get('AIS-SDR', 'ppm')

wifi_server=data_conf.get('WIFI', 'enable')
wlan=data_conf.get('WIFI', 'device')
passw=data_conf.get('WIFI', 'password')

if x11vnc=='1':
	subprocess.Popen(['x11vnc', '-forever'])         
else: 
	subprocess.call(['pkill', '-9', 'x11vnc'])

opencpn_commands=[]
opencpn_commands.append('opencpn')
if opencpn_no=='1': opencpn_commands.append('-no_opengl')
if opencpn_fullscreen=='1': opencpn_commands.append('-fullscreen')

if opencpn=='1' and len(opencpn_commands)>1: subprocess.Popen(opencpn_commands)
if opencpn=='1' and len(opencpn_commands)==1: subprocess.Popen('opencpn')

if enable=='1':
	rtl_fm=subprocess.Popen(['rtl_fm', '-f', '161975000', '-g', gain, '-p', ppm, '-s', '48k'], stdout = subprocess.PIPE)
	aisdecoder=subprocess.Popen(['aisdecoder', '-h', '127.0.0.1', '-p', '10110', '-a', 'file', '-c', 'mono', '-d', '-f', '/dev/stdin'], stdin = rtl_fm.stdout)         
else: 
	subprocess.call(['pkill', '-9', 'aisdecoder'])
	subprocess.call(['pkill', '-9', 'rtl_fm'])
	
if wifi_server=='1':
	subprocess.Popen(['sudo', 'python', currentpath+'/wifi_server.py', '1', wlan, passw])
else:
	subprocess.Popen(['sudo', 'python', currentpath+'/wifi_server.py', '0', wlan, passw])
	
time.sleep(11)

if kplex=='1':
	subprocess.call(["pkill", '-9', "kplex"])
	subprocess.Popen('kplex')        
else: 
	subprocess.call(['pkill', '-9', 'kplex'])

if gps_time=='1':
	subprocess.call(['sudo', 'python', currentpath+'/time_gps.py'])

if sow=='1':
	subprocess.Popen(['python', currentpath+'/sog2sow.py'])
else:
	subprocess.call(['pkill', '-f', 'sog2sow.py'])

