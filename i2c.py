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

import socket, time, pynmea2, RTIMU, math, csv, datetime, json, subprocess, codecs, serial
from classes.paths import Paths
from classes.conf import Conf

paths=Paths()
currentpath=paths.currentpath
home=paths.home

conf=Conf()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
N2Kdev= conf.get('SIGNALK', 'can_usb')
n2k_exist=False
if (len(N2Kdev)>3):
	try:
		ser = serial.Serial(N2Kdev, 115200, timeout=0.5)
		n2k_exist=True
	except: pass

#nmea_hdg_b = conf.get('STARTUP', 'nmea_hdg')=='1'
#nmea_heel_b = conf.get('STARTUP', 'nmea_heel')=='1'
#nmea_pitch_b = conf.get('STARTUP', 'nmea_pitch')=='1'
poll_interval = 1

#e_imu = False
#e_pres = False
#e_hum = False
#log_list_b = False

def Send_Attitude(Yaw, Pitch, Roll):
	data_ = (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0)
	data = bytearray(data_)
	length = 8
	lPGN = 127257
	Yaw_16 = int(Yaw * 174.53293)
	Pitch_16 = int(Pitch * 174.53293)
	Roll_16 = int(Roll * 174.53293)
	i=8
	data[i+1] = Yaw_16 & 255
	data[i+2] = (Yaw_16 >> 8) & 255
	data[i+3] = Pitch_16 & 255
	data[i+4] = (Pitch_16 >> 8) & 255
	data[i+5] = Roll_16 & 255
	data[i+6] = (Roll_16 >> 8) & 255
			
	data[0] = 0x94 #command
	data[1] = (length + 6) #Actisense length
	data[2] = 6 #priority
	data[3] = lPGN &255#PGN
	data[4] = (lPGN >> 8)&255 #PGN
	data[5] = (lPGN >> 16)&255 #PGN
	data[6] = 255 #receiver
	data[7] = length #NMEA len
	SendCommandtoSerial(data)

def Send_Environmental_Parameters2(WaterTemp, Humidity, Pressure,b1,b2,b3):
	data_ = (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0)
	data = bytearray(data_)
	length = 8
	lPGN = 130311
	WaterTemp_16 = int(WaterTemp * 100 + 27315)
	Humidity_16 = int(Humidity*250)
	Pressure_16 = int(Pressure)
	i=8
	data[i+2] = WaterTemp_16 & 255
	data[i+3] = (WaterTemp_16 >> 8) & 255
	data[i+4] = Humidity_16 & 255
	data[i+5] = (Humidity_16 >> 8) & 255
	data[i+6] = Pressure_16 & 255
	data[i+7] = (Pressure_16 >> 8) & 255
	if not b1:data[i+2] = data[i+3] = 255
	if not b2:data[i+4] = data[i+5] = 255
	if not b3:data[i+6] = data[i+7] = 255
	
	data[0] = 0x94 #command
	data[1] = (length + 6) #Actisense length
	data[2] = 6 #priority
	data[3] = lPGN &255#PGN
	data[4] = (lPGN >> 8)&255 #PGN
	data[5] = (lPGN >> 16)&255 #PGN
	data[6] = 255 #receiver
	data[7] = length #NMEA len
	SendCommandtoSerial(data)

def Send_Environmental_Parameters(WaterTemp, OutsideAirTemp, Pressure,b1,b2,b3):
	data_ = (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0)
	data = bytearray(data_)
	length = 8
	lPGN = 130310
	WaterTemp_16 = int(WaterTemp * 100 + 27315)
	OutsideAirTemp_16 = int(OutsideAirTemp * 100 + 27315)
	Pressure_16 = int(Pressure)
	i=8
	data[i+1] = WaterTemp_16 & 255
	data[i+2] = (WaterTemp_16 >> 8) & 255
	data[i+3] = OutsideAirTemp_16 & 255
	data[i+4] = (OutsideAirTemp_16 >> 8) & 255
	data[i+5] = Pressure_16 & 255
	data[i+6] = (Pressure_16 >> 8) & 255
	if not b1:data[i+1] = data[i+2] = 255
	if not b2:data[i+3] = data[i+4] = 255
	if not b3:data[i+5] = data[i+6] = 255

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
	


heading_183=conf.get('I2C', 'nmea_hdg')=='1'
heading_2k=conf.get('I2C', 'n2k_hdg')=='1'
heading_sk=conf.get('I2C', 'sk_hdg')=='1'
heel_183=conf.get('I2C', 'nmea_heel')=='1'
heel_2k=conf.get('I2C', 'n2k_heel')=='1'
heel_sk=conf.get('I2C', 'sk_heel')=='1'
pitch_183=conf.get('I2C', 'nmea_pitch')=='1'
pitch_2k=conf.get('I2C', 'n2k_pitch')=='1'
pitch_sk=conf.get('I2C', 'sk_pitch')=='1'
pressure_183=conf.get('I2C', 'nmea_press')=='1'
pressure_2k=conf.get('I2C', 'n2k_press')=='1'
pressure_sk=conf.get('I2C', 'sk_press')=='1'
p_temp_183=conf.get('I2C', 'nmea_temp_p')=='1'
p_temp_2k=conf.get('I2C', 'n2k_temp_p')=='1'
p_temp_sk=conf.get('I2C', 'sk_temp_p')=='1'
humidity_183=conf.get('I2C', 'nmea_hum')=='1'
humidity_2k=conf.get('I2C', 'n2k_hum')=='1'
humidity_sk=conf.get('I2C', 'sk_hum')=='1'
h_temp_183=conf.get('I2C', 'nmea_temp_h')=='1'
h_temp_2k=conf.get('I2C', 'n2k_temp_h')=='1'
h_temp_sk=conf.get('I2C', 'sk_temp_h')=='1'

heading_offset=float(conf.get('OFFSET', 'heading'))
heel_offset=float(conf.get('OFFSET', 'heel'))
pitch_offset=float(conf.get('OFFSET', 'pitch'))
pressure_offset=float(conf.get('OFFSET', 'pressure'))
p_temp_offset=float(conf.get('OFFSET', 'temperature_p'))
humidity_offset=float(conf.get('OFFSET', 'humidity'))
h_temp_offset=float(conf.get('OFFSET', 'temperature_h'))

p_temp_skt=conf.get('I2C', 'p_temp_skt')
h_temp_skt=conf.get('I2C', 'h_temp_skt')

rate=float(conf.get('STARTUP', 'nmea_rate_sen'))

detected=subprocess.check_output(['python', currentpath+'/imu/check_sensors.py'], cwd=currentpath+'/imu')
l_detected=detected.split('\n')

e_imu=True
e_pres=True
e_hum=True
if 'none' in l_detected[0]:	e_imu=False
if 'none' in l_detected[2]:	e_pres=False
if 'none' in l_detected[3]:	e_hum=False
	
press_temp_log_b = conf.get('STARTUP', 'press_temp_log')=='1'


with open('/home/pi/.config/signalk-server-node/settings/openplotter-settings.json') as data_file:
	data = json.load(data_file)

mmsi=data['vessel']['uuid']
if e_imu:
	SETTINGS_FILE = "RTIMULib"
	s = RTIMU.Settings(SETTINGS_FILE)
	imu = RTIMU.RTIMU(s)
	imu.IMUInit()
	imu.setSlerpPower(0.02)
	imu.setGyroEnable(True)
	imu.setAccelEnable(True)
	imu.setCompassEnable(True)
	poll_interval = imu.IMUGetPollInterval()


if e_pres:
	SETTINGS_FILE2 = "RTIMULib2"
	s2 = RTIMU.Settings(SETTINGS_FILE2)
	pressure_val = RTIMU.RTPressure(s2)
	pressure_val.pressureInit()

if e_hum:
	SETTINGS_FILE3 = "RTIMULib3"
	s3 = RTIMU.Settings(SETTINGS_FILE3)
	humidity_val = RTIMU.RTHumidity(s3)
	humidity_val.humidityInit()

if press_temp_log_b:
	ifile  = open(currentpath+'/weather_log.csv', "r")
	reader = csv.reader(ifile)
	log_list = []
	for row in reader:
		log_list.append(row)
	ifile.close()
	if log_list: last_log=float(log_list[len(log_list)-1][0])
	else: last_log=0
	log_list_b = True

heading_m=''
heel=''
pitch=''
pressure=''
temperature_p=''
humidity=''
temperature_h=''

tick=time.time()

while True:
	tick2=time.time()
	time.sleep(poll_interval*1.0/1000.0)
	# read IMU
	if e_imu:
		if imu.IMURead():
			data = imu.getIMUData()
			fusionPose = data["fusionPose"]
			heading_m0=math.degrees(fusionPose[2])+heading_offset
			heel=math.degrees(fusionPose[0])+heel_offset
			pitch=math.degrees(fusionPose[1])+pitch_offset
			if heading_m0<0:
				heading_m0=360+heading_m0
			if heading_m0>360:
				heading_m0=-360+heading_m0
			heading_m=round(heading_m0,1)


	# read Pressure
	if e_pres:
		read=pressure_val.pressureRead()
		if read:
			if (read[0]):
				pressure=read[1]+pressure_offset
			if (read[2]):
				temperature_p=read[3]+p_temp_offset

	# read humidity
	if e_hum:
		read=humidity_val.humidityRead()
		if read:
			if (read[0]):
				humidity=read[1]+humidity_offset
			if (read[2]):
				temperature_h=read[3]+h_temp_offset

	#GENERATE
	if tick2-tick > rate:
		tick=time.time()
		# HDG
		if e_imu:
			if heading_183:
				hdg = pynmea2.HDG('OS', 'HDG', (str(heading_m),'','','',''))
				hdg1=str(hdg)
				hdg2=hdg1+"\r\n"
				sock.sendto(hdg2, ('127.0.0.1', 10110))
			if heading_sk:	
				SK_path = "navigation.headingMagnetic"
				SignalK = '{"updates": [{"source": {"type": "HDG","src" : "imu"},"timestamp": "'+str( datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f') )[0:23]+'Z","values":[ {"path": "'+SK_path+'","value":'+str(0.017453293*heading_m)+'}]}],"context": "vessels.'+mmsi+'"}\n'
				sock.sendto(SignalK, ('127.0.0.1', 7777))			

		list_tmp1=[]
		list_tmp2=[]		
		list_signalk_path1=[]
		list_signalk1=[]
		list_signalk_path2=[]
		list_signalk2=[]

		if e_imu:
			if heel_183:
				heel= round(heel,1)
				list_tmp2.append('A')
				list_tmp2.append(str(heel))
				list_tmp2.append('D')
				list_tmp2.append('I2CX')
			if heel_sk:
				list_signalk_path2.append('navigation.attitude.roll')
				list_signalk2.append(str(0.017453293*heel))
				
			if pitch_183:
				pitch= round(pitch,1)
				list_tmp2.append('A')
				list_tmp2.append(str(pitch))
				list_tmp2.append('D')
				list_tmp2.append('I2CY')
			if pitch_sk:
				list_signalk_path2.append('navigation.attitude.pitch')
				list_signalk2.append(str(0.017453293*pitch))
			
			if pitch_2k or heel_2k:
				Send_Attitude(0, pitch, heel)
		
		if e_pres:	
			if pressure_183:
				press=round(pressure,2)
				list_tmp1.append('P')
				list_tmp1.append(str(press))
				list_tmp1.append('B')
				list_tmp1.append('I2CP')
			if pressure_sk:
				list_signalk_path1.append('environment.air.outside.pressure')
				list_signalk1.append(str(pressure*100))			
			if p_temp_183:
				temp= round(temperature_p,1)
				list_tmp1.append('C')
				list_tmp1.append(str(temp))
				list_tmp1.append('C')
				list_tmp1.append('I2CT')
			if p_temp_sk:
				list_signalk_path1.append(p_temp_skt)
				list_signalk1.append(str(round(temperature_p,2)+273.15))
			if pressure_2k:
				Send_Environmental_Parameters(0.0,round(temperature_p,2),round(pressure,2),False,True,True)
				
		if e_hum:	
			if humidity_183:
				hum=round(humidity,1)
				list_tmp1.append('H')
				list_tmp1.append(str(hum))
				list_tmp1.append('R')
				list_tmp1.append('I2CH')
			if humidity_sk:
				list_signalk_path1.append('environment.air.outside.humidity')
				list_signalk1.append(str(hum))
			if humidity_2k:
				if e_pres and pressure_2k:
					Send_Environmental_Parameters2(0.0,round(humidity,3),round(pressure,2),False,True,False)				
				else:
					Send_Environmental_Parameters2(0.0,round(humidity,3),0.0,False,True,False)	
			if h_temp_183:
				temp= round(temperature_h,1)
				list_tmp1.append('C')
				list_tmp1.append(str(temp))
				list_tmp1.append('C')
				list_tmp1.append('I2CT')
			if h_temp_sk:
				list_signalk_path1.append(h_temp_skt)
				list_signalk1.append(str(temp+273.15))		
				
		if list_tmp1:
			xdr = pynmea2.XDR('OS', 'XDR', (list_tmp1))
			xdr1=str(xdr)
			xdr2=xdr1+"\r\n"
			sock.sendto(xdr2, ('127.0.0.1', 10110))
		
		if list_signalk1:
			SignalK = '{"updates": [{"source": {"type": "Sensors","src" : "bmp180"},"timestamp": "'+str( datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f') )[0:23]+'Z","values":[ '
			Erg=''
			
			for i in range(0,len(list_signalk1)):
				Erg += '{"path": "'+list_signalk_path1[i]+'","value":'+list_signalk1[i]+'},'
			SignalK+=Erg[0:-1]+']}],"context": "vessels.'+mmsi+'"}\n'
			sock.sendto(SignalK, ('127.0.0.1', 7777))			
			
		if list_tmp2:
			xdr = pynmea2.XDR('OS', 'XDR', (list_tmp2))
			xdr1=str(xdr)
			xdr2=xdr1+"\r\n"
			sock.sendto(xdr2, ('127.0.0.1', 10110))			
			heel=''
			pitch=''
		
		if list_signalk2:
			SignalK = '{"updates": [{"source": {"type": "Sensors","src" : "imu"},"timestamp": "'+str( datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f') )[0:23]+'Z","values":[ '
			Erg=''
			
			for i in range(0,len(list_signalk2)):
				Erg += '{"path": "'+list_signalk_path2[i]+'","value":'+list_signalk2[i]+'},'
			SignalK+=Erg[0:-1]+']}],"context": "vessels.'+mmsi+'"}\n'			
			sock.sendto(SignalK, ('127.0.0.1', 7777))			

			
		temperature=''
		if e_pres: temperature=temperature_p
		elif e_hum: temperature=temperature_h

		# log temperature pressure humidity
		try:
			if press_temp_log_b:
				if tick-last_log > 300:
					last_log=tick
					press2=0
					temp2=0
					hum2=0
					if pressure: press2=pressure
					if temperature: temp2=temperature
					if humidity: hum2=humidity
					new_row=[tick,press2,temp2,hum2]
					if len(log_list) < 288:
						log_list.append(new_row)
						ofile = open(currentpath+'/weather_log.csv', "a")
						writer = csv.writer(ofile)
						writer.writerow(new_row)
					if len(log_list) >= 288:
						del log_list[0]
						log_list.append(new_row)
						ofile = open(currentpath+'/weather_log.csv', "w")
						writer = csv.writer(ofile)
						for row in log_list:
							writer.writerow(row)
					ofile.close()
		except Exception,e: print str(e)
		
		temperature_p=''
		temperature_h=''
		pressure=''
		humidity=''