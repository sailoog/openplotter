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

import socket, time, platform
if platform.machine()[0:3]!='arm':
	print 'this is not a raspberry pi -> no W1ThermSensor'
else:
	from w1thermsensor import W1ThermSensor
	from classes.conf import Conf	
	
	conf = Conf()

	try:
		sensors_list=eval(conf.get('1W', 'DS18B20'))
	except: sensors_list=[]

	if sensors_list:
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sensors=[]
		sensors_list2=[]
		for item in sensors_list:
			try:
				type=W1ThermSensor.THERM_SENSOR_DS18B20
				for sensor in W1ThermSensor.get_available_sensors():
					if item[2] == sensor.id:
						type = sensor.type
				sensors.append(W1ThermSensor(type, item[2]))
				sensors_list2.append(item)
			except Exception,e: print str(e)
				
		while True:
			time.sleep(0.1)
			list_signalk=[]
			ib=0
			for i in sensors_list2:
				try:
					temp=sensors[ib].get_temperature(W1ThermSensor.KELVIN)
					temp_offset=temp+float(i[3])
					value=str(temp_offset)
					path=i[1]
					name=i[0]
					SignalK='{"updates":[{"$source":"OPsensors.1W.'+name+'","values":[{"path":"'+path+'","value":'+value+'}]}]}\n'
					sock.sendto(SignalK, ('127.0.0.1', 55557))
				except Exception,e: print str(e)
				ib=ib+1	