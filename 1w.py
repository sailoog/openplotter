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

import socket, pynmea2, time, datetime, json
from w1thermsensor import W1ThermSensor
from classes.paths import Paths
from classes.conf import Conf

conf=Conf()

paths=Paths()
home=paths.home

with open(home+'/.config/signalk-server-node/settings/openplotter-settings.json') as data_file:
	data = json.load(data_file)

mmsi=data['vessel']['uuid']

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sensors_list=eval(conf.get('1W', 'DS18B20'))

sensors=[]
for index,item in enumerate(sensors_list):
	try:
		type=W1ThermSensor.THERM_SENSOR_DS18B20
		for sensor in W1ThermSensor.get_available_sensors():
			if item[3] == sensor.id:
				type = sensor.type
		
		sensors.append(W1ThermSensor(type, item[3]))
	except Exception,e: 
		sensors_list[index][5]='0'
		print str(e)

while True:
	time.sleep(0.01)
	temp=''
	list_tmp=[]
	list_signalk=[]
	list_signalk_path=[]
	ib=0
	c=0
	try:
		for i in sensors_list:
			if i[5]=='1':
 				if i[2]=='C': unit=W1ThermSensor.DEGREES_C
				if i[2]=='F': unit=W1ThermSensor.DEGREES_F
				if i[2]=='K': unit=W1ThermSensor.KELVIN
				temp=sensors[ib].get_temperature(unit)
				list_signalk.append(str(sensors[ib].get_temperature(W1ThermSensor.KELVIN)))
				list_signalk_path.append(i[0])
				temp=round(temp,1)
				list_tmp.append('C')
				list_tmp.append(str(temp))
				list_tmp.append(i[2])
				list_tmp.append(i[4])
				ib=ib+1
				c=c+1
				if c==3:
					xdr = pynmea2.XDR('OS', 'XDR', (list_tmp))
					xdr1=str(xdr)
					xdr2=xdr1+"\r\n"
					sock.sendto(xdr2, ('127.0.0.1', 10110))
					list_tmp=[]
					c=0
					
					SignalK = '{"updates": [{"source": {"type": "Sensors","src" : "imu"},"timestamp": "'+str( datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f') )[0:23]+'Z","values":[ '
					Erg=''
					for i in range(0,2):
						Erg += '{"path": "'+list_signalk_path[i]+'","value":'+list_signalk[i]+'},'
					SignalK+=Erg[0:-1]+']}],"context": "vessels.'+mmsi+'"}\n'			
					sock.sendto(SignalK, ('127.0.0.1', 7777))			
					
					
		if c>0:
			xdr = pynmea2.XDR('OS', 'XDR', (list_tmp))
			xdr1=str(xdr)
			xdr2=xdr1+"\r\n"
			sock.sendto(xdr2, ('127.0.0.1', 10110))

			SignalK = '{"updates": [{"source": {"type": "Sensors","src" : "imu"},"timestamp": "'+str( datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f') )[0:23]+'Z","values":[ '
			Erg=''
			for i in range(0,len(list_signalk)):
				Erg += '{"path": "'+list_signalk_path[i]+'","value":'+list_signalk[i]+'},'
			SignalK+=Erg[0:-1]+']}],"context": "vessels.'+mmsi+'"}\n'			
			sock.sendto(SignalK, ('127.0.0.1', 7777))			
			
			
	except Exception,e: print str(e)
