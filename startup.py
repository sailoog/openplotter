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

import subprocess, time, ConfigParser
from classes.paths import Paths
from classes.conf import Conf

paths=Paths()
home=paths.home
currentpath=paths.currentpath

device=''
ssid=''
passw=''

try:
	boot_conf = ConfigParser.SafeConfigParser()
	boot_conf.read('/boot/config.txt')
	device=boot_conf.get('OPENPLOTTER', 'device')
	ssid=boot_conf.get('OPENPLOTTER', 'ssid')
	passw=boot_conf.get('OPENPLOTTER', 'pass')
except Exception,e: print str(e)

conf=Conf()

if device and ssid and passw:
	conf.set('WIFI', 'enable', '1')
	conf.set('WIFI', 'device', device)
	conf.set('WIFI', 'ssid', ssid)
	conf.set('WIFI', 'password', passw)

delay=int(conf.get('STARTUP', 'delay'))

kplex=conf.get('STARTUP', 'kplex')
opencpn=conf.get('STARTUP', 'opencpn')
opencpn_no=conf.get('STARTUP', 'opencpn_no_opengl')
opencpn_fullscreen=conf.get('STARTUP', 'opencpn_fullscreen')
x11vnc=conf.get('STARTUP', 'x11vnc')
gps_time=conf.get('STARTUP', 'gps_time')
signalk=conf.get('STARTUP', 'signalk')

enable=conf.get('AIS-SDR', 'enable')
gain=conf.get('AIS-SDR', 'gain')
ppm=conf.get('AIS-SDR', 'ppm')
channel=conf.get('AIS-SDR', 'channel')

wifi_server=conf.get('WIFI', 'enable')
wlan=conf.get('WIFI', 'device')
passw2=conf.get('WIFI', 'password')
ssid2=conf.get('WIFI', 'ssid')
share=conf.get('WIFI', 'share')
if not share: share='0'

nmea_hdg=conf.get('STARTUP', 'nmea_hdg')
nmea_heel=conf.get('STARTUP', 'nmea_heel')
nmea_press=conf.get('STARTUP', 'nmea_press')
nmea_temp_p=conf.get('STARTUP', 'nmea_temp_p')
nmea_hum=conf.get('STARTUP', 'nmea_hum')
nmea_temp_h=conf.get('STARTUP', 'nmea_temp_h')

#1W
DS18B20='0'
sensors_list=eval(conf.get('1W', 'DS18B20'))
for i in sensors_list:
	if i[5]=='1': DS18B20='1'

nmea_mag_var=conf.get('STARTUP', 'nmea_mag_var')
nmea_hdt=conf.get('STARTUP', 'nmea_hdt')
nmea_rot=conf.get('STARTUP', 'nmea_rot')
TW_STW=conf.get('STARTUP', 'tw_stw')
TW_SOG=conf.get('STARTUP', 'tw_sog')

#######################################################
time.sleep(delay)

subprocess.call(['pkill', '-9', 'x11vnc'])
if x11vnc=='1':
	subprocess.Popen(['x11vnc', '-forever'])         

opencpn_commands=[]
opencpn_commands.append('opencpn')
if opencpn_no=='1': opencpn_commands.append('-no_opengl')
if opencpn_fullscreen=='1': opencpn_commands.append('-fullscreen')

if opencpn=='1' and len(opencpn_commands)>1: subprocess.Popen(opencpn_commands)
if opencpn=='1' and len(opencpn_commands)==1: subprocess.Popen('opencpn')

if wifi_server=='1':
	subprocess.Popen(['sudo', 'python', currentpath+'/wifi_server.py', '1', wlan, passw2, ssid2, share])
else:
	subprocess.Popen(['sudo', 'python', currentpath+'/wifi_server.py', '0', wlan, passw2, ssid2, share])
	
time.sleep(16)

subprocess.call(['pkill', '-9', 'kplex'])
if kplex=='1':
	subprocess.Popen('kplex')        

subprocess.call(["pkill", '-9', "node"])
if signalk=='1':
	subprocess.Popen(home+'/.config/signalk-server-node/bin/nmea-from-10110', cwd=home+'/.config/signalk-server-node')       

if gps_time=='1':
	subprocess.call(['sudo', 'python', currentpath+'/time_gps.py'])

subprocess.call(['pkill', '-f', 'i2c.py'])
if nmea_hdg=='1' or nmea_heel=='1' or nmea_press=='1' or nmea_temp_p=='1' or nmea_hum=='1' or nmea_temp_h=='1': 
	subprocess.Popen(['python', currentpath+'/i2c.py'], cwd=currentpath+'/imu')

subprocess.call(['pkill', '-f', '1w.py'])
if DS18B20=='1': 
	subprocess.Popen(['python', currentpath+'/1w.py'])

subprocess.call(['pkill', '-f', 'calculate.py'])
if nmea_mag_var=='1' or nmea_hdt=='1' or nmea_rot=='1' or TW_STW=='1' or TW_SOG=='1': 
	subprocess.Popen(['python', currentpath+'/calculate.py'])

subprocess.call(['pkill', '-f', 'monitoring.py'])
subprocess.Popen(['python',currentpath+'/monitoring.py'])

subprocess.call(['pkill', '-9', 'aisdecoder'])
subprocess.call(['pkill', '-9', 'rtl_fm'])
if enable=='1':
	frecuency='161975000'
	if channel=='b': frecuency='162025000'
	rtl_fm=subprocess.Popen(['rtl_fm', '-f', frecuency, '-g', gain, '-p', ppm, '-s', '48k'], stdout = subprocess.PIPE)
	aisdecoder=subprocess.Popen(['aisdecoder', '-h', '127.0.0.1', '-p', '10110', '-a', 'file', '-c', 'mono', '-d', '-f', '/dev/stdin'], stdin = rtl_fm.stdout)
