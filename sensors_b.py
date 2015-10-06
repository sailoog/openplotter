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

import sys, ConfigParser, os, socket, time, pynmea2
from w1thermsensor import W1ThermSensor

pathname = os.path.dirname(sys.argv[0])
currentpath = os.path.abspath(pathname)

data_conf = ConfigParser.SafeConfigParser()
data_conf.read(currentpath+'/openplotter.conf')

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

eng_temp=''

tick=time.time()

while True:
	tick2=time.time()

	#GENERATE
	if tick2-tick > float(data_conf.get('STARTUP', 'nmea_rate_sen')):
		tick=time.time()

		# read DS18B20
		if data_conf.get('STARTUP', 'nmea_eng_temp')=='1':
			sensor = W1ThermSensor()
			eng_temp = sensor.get_temperature()

		# XDR
		list_tmp=[]			
		if data_conf.get('STARTUP', 'nmea_eng_temp')=='1' and eng_temp:
			eng_temp=round(eng_temp,1)
			list_tmp.append('C')
			list_tmp.append(str(eng_temp))
			list_tmp.append('C')
			list_tmp.append('ENGT')
		if list_tmp:
			xdr = pynmea2.XDR('OP', 'XDR', (list_tmp))
			xdr1=str(xdr)
			xdr2=xdr1+"\r\n"
			sock.sendto(xdr2, ('localhost', 10110))
			eng_temp=''

