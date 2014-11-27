#!/usr/bin/env python

import ConfigParser, subprocess, time, socket, pynmea2
from os.path import expanduser

home = expanduser("~")

data_conf = ConfigParser.SafeConfigParser()
data_conf.read(home+'/.config/openplotter/openplotter.conf')

kplex=data_conf.get('STARTUP', 'kplex')
opencpn=data_conf.get('STARTUP', 'opencpn')
x11vnc=data_conf.get('STARTUP', 'x11vnc')
gps_time=data_conf.get('STARTUP', 'gps_time')
sow=data_conf.get('STARTUP', 'iivbw')

enable=data_conf.get('AIS-SDR', 'enable')
gain=data_conf.get('AIS-SDR', 'gain')
ppm=data_conf.get('AIS-SDR', 'ppm')

if kplex=='1':
	subprocess.Popen(["pkill", "kplex"])
	time.sleep(1)
	subprocess.Popen('kplex')        
else: 
	stop_kplex=subprocess.Popen(['pkill', '-9', 'kplex'])

if opencpn=='1':
	start_opencpn=subprocess.Popen(['opencpn', '-no_opengl'])         
else: 
	stop_opencpn=subprocess.Popen(['pkill', '-9', 'opencpn'])

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
	fecha=""
	hora=""
	s = socket.socket()
	s.connect(("localhost", 10110))
	s.settimeout(10)
	cont = 0
	while True:
		cont = cont + 1
		frase_nmea = s.recv(512)
		if frase_nmea[1:3]=='GP':
			msg = pynmea2.parse(frase_nmea)
			if msg.sentence_type == 'RMC':
				fecha = msg.datestamp
				hora =  msg.timestamp
				break
		if cont > 15:
			break
	s.close()
	if (fecha) and (hora):
		subprocess.call([ 'sudo', 'date', '--set', fecha.strftime('%Y-%m-%d'), '--utc'])
		subprocess.call([ 'sudo', 'date', '--set', hora.strftime('%H:%M:%S'), '--utc'])

if sow=='1':
	subprocess.Popen(['python', home+'/.config/openplotter/sog2sow.py'])
else:
	subprocess.Popen(['pkill', '-f', 'sog2sow.py'])