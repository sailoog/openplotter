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

import socket, pynmea2, time, datetime, json, serial, codecs
from w1thermsensor import W1ThermSensor
from classes.paths import Paths
from classes.conf import Conf

conf=Conf()

paths=Paths()
home=paths.home

N2Kdev= conf.get('N2K', 'can_usb')
n2k_exist=False
if conf.get('N2K', 'enable')=='1':
	try:
		ser = serial.Serial(N2Kdev, 115200, timeout=0.5)
		n2k_exist=True
	except: pass

def Send_Engine(Instance, OilTemperature, Temperature,):
	data_ = (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0)
	data = bytearray(data_)
	length = 26
	lPGN = 127489
	OilPressure_16 = 0xffff
	CoollantPressure_16 = 0xffff
	FuelPressure_16 = 0xffff
	OilTemperature_16 = int(OilTemperature * 10)
	if OilTemperature==0:OilTemperature_16 = 0xffff
	Temperature_16 = int(Temperature * 100)
	if Temperature==0:Temperature_16 = 0xffff
	AlternatorPotential_16 = 0xffff
	FuelRate_16 = 0xffff
	TotalEngineHours_32 = 0xffffffff
	Status_32 = 0
	EngineLoad_8 = 0xff
	EngineTorque_8 = 0xff
	i=8
	data[i+0] = Instance & 255
	data[i+1] = OilPressure_16 & 255
	data[i+2] = (OilPressure_16 >> 8) & 255
	data[i+3] = OilTemperature_16 & 255
	data[i+4] = (OilTemperature_16 >> 8) & 255
	data[i+5] = Temperature_16 & 255
	data[i+6] = (Temperature_16 >> 8) & 255
	data[i+7] = AlternatorPotential_16 & 255
	data[i+8] = (AlternatorPotential_16 >> 8) & 255
	data[i+9] = FuelRate_16 & 255
	data[i+10] = (FuelRate_16 >> 8) & 255
	data[i+11] = TotalEngineHours_32 & 255
	data[i+12] = (TotalEngineHours_32 >> 8) & 255
	data[i+13] = (TotalEngineHours_32 >> 16) & 255
	data[i+14] = (TotalEngineHours_32 >> 24) & 255
	data[i+15] = CoollantPressure_16 & 255
	data[i+16] = (CoollantPressure_16 >> 8) & 255
	data[i+17] = FuelPressure_16 & 255
	data[i+18] = (FuelPressure_16 >> 8) & 255
	data[i+19] = 0xff
	data[i+20] = Status_32 & 255
	data[i+21] = (Status_32 >> 8) & 255
	data[i+22] = (Status_32 >> 16) & 255
	data[i+23] = (Status_32 >> 24) & 255
	data[i+24] = EngineLoad_8 & 255
	data[i+25] = EngineTorque_8 & 255

	data[0] = 0x94 #command
	data[1] = (length + 6) #Actisense length
	data[2] = 6 #priority
	data[3] = lPGN &255#PGN
	data[4] = (lPGN >> 8)&255 #PGN
	data[5] = (lPGN >> 16)&255 #PGN
	data[6] = 255 #receiver
	data[7] = length #NMEA len
	SendCommandtoSerial(data)

def SendCommandtoSerial(data):
	if n2k_exist:
		crc = 0
		#start = codecs.decode('1002', 'hex_codec')
		start = (0x10, 0x02)
		ende = codecs.decode('1003', 'hex_codec')
		ende = (0x10, 0x03)
		i = 0
		while i < data[1] + 2:
			crc += data[i]
			i += 1
		crc = (256 - crc) & 255
		data[data[1] + 2] = crc
		i = 0
		ser.write(chr(start[0]))
		ser.write(chr(start[1]))
		while i < data[1] + 3:
			ser.write(chr(data[i]))
			#print format(data[i], '02x')
			if data[i] == 0x10:
				ser.write(chr(data[i]))
			i += 1
		ser.write(chr(ende[0]))
		ser.write(chr(ende[1]))
	


with open(home+'/.config/signalk-server-node/settings/openplotter-settings.json') as data_file:
	data = json.load(data_file)

mmsi=data['vessel']['uuid']

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

try:
	sensors_list=eval(conf.get('1W', 'DS18B20'))
except: sensors_list=[]

sensors=[]

for index,item in enumerate(sensors_list):
	try:
		type=W1ThermSensor.THERM_SENSOR_DS18B20
		for sensor in W1ThermSensor.get_available_sensors():
			if item[3] == sensor.id:
				type = sensor.type
		
		sensors.append(W1ThermSensor(type, item[3]))
	except Exception,e: 
		sensors_list[index][4]='0'
		sensors_list[index][5]='0'
		print str(e)
	
	for i in sensors_list:
		if i[4]=='0' and i[5]=='0':
			sensors_list.remove(i)
	
	dataf_ = (0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0)
	dataf = [float(i) for i in dataf_]

	datab_ = (0,0,0,0,0,0,0,0)
	datab = bytearray(datab_)
	engine0=0
	engine1=0
	index=1
	for i in sensors_list:
		if i[5]=='1':
			if i[0]=='propulsion.port.oilTemperature':
				datab[0]=index
				engine0=1
			if i[0]=='propulsion.port.coolantTemperature':
				datab[1]=index
				engine0=1
			if i[0]=='propulsion.starboard.oilTemperature':
				datab[2]=index
				engine1=1
			if i[0]=='propulsion.starboard.coolantTemperature':
				datab[3]=index
				engine1=1
		try:
			float(i[6])
		except:
			print 'Offset: '+i[6]+' is not a correct decimal number'
			i[6]='0.0'
			
		index+=1
		
while True:
	time.sleep(0.1)
	temp=''
	list_tmp=[]
	list_signalk=[]
	list_signalk_path=[]
	ib=0
	c=0
	#try:
	for i in sensors_list:
		temp=sensors[ib].get_temperature(W1ThermSensor.KELVIN)
		ib=ib+1
		#dataf[ib]=temp
		dataf[ib]=temp+float(i[6])
		if i[4]=='1':
			list_signalk.append(str(temp))
			list_signalk_path.append(i[0])
		
		if (ib & 1)>0:
			if engine0:
				Send_Engine(0,dataf[datab[0]],dataf[datab[1]])
		else:		
			if engine1:
				Send_Engine(1,dataf[datab[2]],dataf[datab[3]])
			
	if list_signalk!=[]:				
		SignalK = '{"updates": [{"source": {"type": "Sensors","src" : "1W"},"timestamp": "'+str( datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f') )[0:23]+'Z","values":[ '
		Erg=''
		i=0
		for j in list_signalk:
			Erg += '{"path": "'+list_signalk_path[i]+'","value":'+list_signalk[i]+'},'
			i+=1
		SignalK+=Erg[0:-1]+']}],"context": "vessels.'+mmsi+'"}\n'			
		sock.sendto(SignalK, ('127.0.0.1', 7777))	
	#except Exception,e: print str(e)

															
