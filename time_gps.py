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

import socket, pynmea2, subprocess
from classes.conf import Conf
from classes.language import Language

fecha=''
hora=''
foundtime = False

conf = Conf()
Language(conf)

try:
	sock_in = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock_in.settimeout(10)
	sock_in.connect(('127.0.0.1', 10109))
except socket.error, error_msg:
	print _('Failed to connect with localhost:10109.')
	print _('Error: ')+ str(error_msg[0])
else:
	cont = 0
	while foundtime == False:
		frase_nmea =''
		try:
			frase_nmea = sock_in.recv(1024)
		except socket.error, error_msg:
			try:
				print _('Failed to connect with localhost:10109.')
				print _('Error: ')+ str(error_msg[0])
				sys.stdout.flush()
			except: pass
			break
		else:
			if frase_nmea:
				try:
					nmea_list=frase_nmea.split()

					for i in nmea_list:
						msg = pynmea2.parse(i)
						nmea_type=msg.sentence_type
						if nmea_type == 'RMC':
							fecha = msg.datestamp
							hora =  msg.timestamp
							foundtime = True
							break
						else: 
							cont=cont+1
				except: pass
				if cont >= 30: break

	if fecha and hora:
		subprocess.call([ 'date', '--set', fecha.strftime('%Y-%m-%d'), '--utc'])
		subprocess.call([ 'date', '--set', hora.strftime('%H:%M:%S'), '--utc'])
		print _('Date and time retrieved from NMEA data successfully.')
	else:
		print _('Unable to retrieve date or time from NMEA data.')
