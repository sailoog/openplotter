#!/usr/bin/env python

import socket, pynmea2, sys, time

def send_data():
	cont=0
	while True:
		sog = None
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
						cont=0
						sog = msg.spd_over_grnd
						if sog==None:
							try:
								print 'Speed Over Ground data not found, waiting for NMEA data...'
								sys.stdout.flush()
							except: pass
					else:
						cont=cont+1
						if cont>30:
							cont=0
							try:
								print 'Speed Over Ground data not found, waiting for NMEA data...'
								sys.stdout.flush()
							except: pass
				except: pass
			else:
				break

			if sog:
				vbw = pynmea2.VBW('II', 'VBW', (str(sog), '', 'A', str(sog), '', 'A'))
				vbw1=str(vbw)
				vbw2=repr(vbw1)+"\r\n"
				sock.sendto(str(vbw2), ('127.0.0.1', 10110))
				sogk = sog*1.852
				vhw = pynmea2.VHW('II', 'VHW', ('', 'T', '', 'M', str(sog), 'N', str(sogk), 'K'))
				vhw1=str(vhw)
				vhw2=repr(vhw1)+"\r\n"
				sock.sendto(str(vhw2), ('127.0.0.1', 10110))
				try:
					print vbw1
					print vhw1
					sys.stdout.flush()
				except: pass
	
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
	try:
		sock_in = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock_in.settimeout(10)
		sock_in.connect(('127.0.0.1', 10110))
	except socket.error, error_msg:
		try:
			print 'Failed to connect with localhost:10110.'
			print 'Error: '+ str(error_msg[0])
			sys.stdout.flush()
		except: pass
	else: 
		send_data()
	try:
		print 'No data, trying to reconnect...'
		sys.stdout.flush()
	except: pass
	time.sleep(7)
