#!/usr/bin/env python

import socket, pynmea2, subprocess

fecha=''
hora=''

try:
	sock_in = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock_in.settimeout(10)
	sock_in.connect(('127.0.0.1', 10110))
except socket.error, error_msg:
	print 'Failed to connect with localhost:10110.'
	print 'Error: '+ str(error_msg[0])
else:
	cont = 0
	while True:
		frase_nmea =''
		try:
			frase_nmea = sock_in.recv(512)
		except socket.error, error_msg:
			try:
				print 'Failed to connect with localhost:10110.'
				print 'Error: '+ str(error_msg[0])
				sys.stdout.flush()
			except: pass
			break
		else:
			if frase_nmea:
				try:
					msg = pynmea2.parse(frase_nmea)
					if msg.sentence_type == 'RMC':
						fecha = msg.datestamp
						hora =  msg.timestamp
						break
					else: 
						cont=cont+1
				except: pass
				if cont >= 30: break

	if fecha and hora:
		subprocess.call([ 'date', '--set', fecha.strftime('%Y-%m-%d'), '--utc'])
		subprocess.call([ 'date', '--set', hora.strftime('%H:%M:%S'), '--utc'])
		print 'Date and time retrieved from NMEA data successfully.'
	else:
		print 'Unable to retrieve date or time from NMEA data.'