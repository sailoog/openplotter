#!/usr/bin/env python

import socket, pynmea2, subprocess

fecha=""
hora=""

try:
	s = socket.socket()
	s.connect(("localhost", 10110))
	s.settimeout(10)
	cont = 0
	while True:
		cont = cont + 1
		frase_nmea = s.recv(512)
		if frase_nmea[1]=='G':
			msg = pynmea2.parse(frase_nmea)
			if msg.sentence_type == 'RMC':
				fecha = msg.datestamp
				hora =  msg.timestamp
				break
		if cont > 15:
			break
	s.close()
except socket.error, error_msg:
	print 'time_gps.py: Failed to connect with localhost:10110.'
	print 'Error: '+ str(error_msg[0])
else:
	if (fecha) and (hora):
		subprocess.call([ 'date', '--set', fecha.strftime('%Y-%m-%d'), '--utc'])
		subprocess.call([ 'date', '--set', hora.strftime('%H:%M:%S'), '--utc'])
		print 'time_gps.py: Date and time retrieved from GPS successfully.'
	else:
		print 'time_gps.py: Unable to retrieve date or time from GPS.'