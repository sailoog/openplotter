#!/usr/bin/env python

import socket, pynmea2

sock_in = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock_in.connect(('127.0.0.1', 10110))
sock_in.settimeout(10)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
	frase_nmea = sock_in.recv(512)
	if frase_nmea[1]=='G':
		msg = pynmea2.parse(frase_nmea)
		if msg.sentence_type == 'RMC':
			sog = msg.spd_over_grnd
			if not sog: sog=0.00
			vbw = pynmea2.VBW('II', 'VBW', (str(sog), '', 'A', str(sog), '', 'A'))
			vbw1=str(vbw)
			vbw2=repr(vbw1)+"\r\n"
			sock.sendto(str(vbw2), ('127.0.0.1', 10110))
			sogk = sog*1.852
			vhw = pynmea2.VHW('II', 'VHW', ('', 'T', '', 'M', str(sog), 'N', str(sogk), 'K'))
			vhw1=str(vhw)
			vhw2=repr(vhw1)+"\r\n"
			sock.sendto(str(vhw2), ('127.0.0.1', 10110))