import socket
import pynmea2
import subprocess

fecha=""
hora=""

s = socket.socket()
s.connect(("localhost", 10110))

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
	subprocess.call([ 'date', '--set', fecha.strftime('%Y-%m-%d'), '--utc'])
	subprocess.call([ 'date', '--set', hora.strftime('%H:%M:%S'), '--utc'])
