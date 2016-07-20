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

import socket, time, pynmea2, RTIMU, math, csv, datetime, json, subprocess
from classes.paths import Paths
from classes.conf import Conf

paths=Paths()
currentpath=paths.currentpath
home=paths.home

conf=Conf()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

poll_interval = 1
	
heading_sk=conf.get('I2C', 'sk_hdg')=='1'
heel_sk=conf.get('I2C', 'sk_heel')=='1'
pitch_sk=conf.get('I2C', 'sk_pitch')=='1'
pressure_sk=conf.get('I2C', 'sk_press')=='1'
p_temp_sk=conf.get('I2C', 'sk_temp_p')=='1'
humidity_sk=conf.get('I2C', 'sk_hum')=='1'
h_temp_sk=conf.get('I2C', 'sk_temp_h')=='1'
try:
	heading_offset=float(conf.get('OFFSET', 'heading'))
	heel_offset=float(conf.get('OFFSET', 'heel'))
	pitch_offset=float(conf.get('OFFSET', 'pitch'))
	pressure_offset=float(conf.get('OFFSET', 'pressure'))
	p_temp_offset=float(conf.get('OFFSET', 'temperature_p'))
	humidity_offset=float(conf.get('OFFSET', 'humidity'))
	h_temp_offset=float(conf.get('OFFSET', 'temperature_h'))
except:
	heading_offset=heel_offset=pitch_offset=pressure_offset=p_temp_offset=humidity_offset=h_temp_offset=0.0
	print 'Bad format in offset value' 

p_temp_skt=conf.get('I2C', 'p_temp_skt')
h_temp_skt=conf.get('I2C', 'h_temp_skt')
humidity_skt=conf.get('I2C', 'hum_skt')

rate_imu=float(conf.get('I2C', 'rate_imu'))
rate_press=float(conf.get('I2C', 'rate_press'))
rate_hum=float(conf.get('I2C', 'rate_hum'))
	
#press_temp_log_b = conf.get('STARTUP', 'press_temp_log')=='1'


with open('/home/pi/.config/signalk-server-node/settings/openplotter-settings.json') as data_file:
	data = json.load(data_file)
uuid=data['vessel']['uuid']

if heading_sk or heel_sk or pitch_sk:
	SETTINGS_FILE = "RTIMULib"
	s = RTIMU.Settings(SETTINGS_FILE)
	imu = RTIMU.RTIMU(s)
	imu.IMUInit()
	imu.setSlerpPower(0.02)
	imu.setGyroEnable(True)
	imu.setAccelEnable(True)
	imu.setCompassEnable(True)
	poll_interval = imu.IMUGetPollInterval()

if pressure_sk:
	SETTINGS_FILE2 = "RTIMULib2"
	s2 = RTIMU.Settings(SETTINGS_FILE2)
	pressure_val = RTIMU.RTPressure(s2)
	pressure_val.pressureInit()

if humidity_sk:
	SETTINGS_FILE3 = "RTIMULib3"
	s3 = RTIMU.Settings(SETTINGS_FILE3)
	humidity_val = RTIMU.RTHumidity(s3)
	humidity_val.humidityInit()

'''
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
'''

heading_m=''
heel=''
pitch=''
pressure=''
temperature_p=''
humidity=''
temperature_h=''

tick_imu=time.time()
tick_press=time.time()
tick_hum=time.time()

while True:
	tick2=time.time()
	time.sleep(poll_interval*1.0/1000.0)
	# read IMU
	if heading_sk or heel_sk or pitch_sk:
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
	if pressure_sk:
		read=pressure_val.pressureRead()
		if read:
			if (read[0]):
				pressure=read[1]+pressure_offset
			if (read[2]):
				temperature_p=read[3]+p_temp_offset

	# read humidity
	if humidity_sk:
		read=humidity_val.humidityRead()
		if read:
			if (read[0]):
				humidity=read[1]+humidity_offset
			if (read[2]):
				temperature_h=read[3]+h_temp_offset

	#GENERATE
	# Avoid generation if SK paths are not selected
	if tick2-tick_imu > rate_imu:
		tick_imu=time.time()
	
		list_signalk_path2=[]
		list_signalk2=[]

		if heading_sk:
			list_signalk_path2.append('navigation.headingMagnetic')
			list_signalk2.append(str(0.017453293*heading_m))			
		if heel_sk:
			list_signalk_path2.append('navigation.attitude.roll')
			list_signalk2.append(str(0.017453293*heel))	
		if pitch_sk:
			list_signalk_path2.append('navigation.attitude.pitch')
			list_signalk2.append(str(0.017453293*pitch))

		if list_signalk2:
			SignalK = '{"updates": [{"source": {"type": "I2C","src" : "imu"},"timestamp": "'+str( datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f') )[0:23]+'Z","values":[ '
			Erg=''
			for i in range(0,len(list_signalk2)):
				Erg += '{"path": "'+list_signalk_path2[i]+'","value":'+list_signalk2[i]+'},'
			SignalK+=Erg[0:-1]+']}],"context": "vessels.'+uuid+'"}\n'			
			sock.sendto(SignalK, ('127.0.0.1', 7777))	

	if tick2-tick_press > rate_press:
		tick_press=time.time()

		list_signalk_path1=[]
		list_signalk1=[]

		if pressure_sk:	
			list_signalk_path1.append('environment.outside.pressure')
			list_signalk1.append(str(pressure*100))			
		if p_temp_sk:
			list_signalk_path1.append(p_temp_skt)
			list_signalk1.append(str(round(temperature_p,2)+273.15))

		if list_signalk1:
			SignalK = '{"updates": [{"source": {"type": "I2C","src" : "press"},"timestamp": "'+str( datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f') )[0:23]+'Z","values":[ '
			Erg=''
			for i in range(0,len(list_signalk1)):
				Erg += '{"path": "'+list_signalk_path1[i]+'","value":'+list_signalk1[i]+'},'
			SignalK+=Erg[0:-1]+']}],"context": "vessels.'+uuid+'"}\n'
			sock.sendto(SignalK, ('127.0.0.1', 7777))			
		
	if tick2-tick_hum > rate_hum:
		tick_hum=time.time()

		list_signalk_path3=[]
		list_signalk3=[]

		if humidity_sk:	
			list_signalk_path3.append(humidity_skt)
			list_signalk3.append(str(humidity))
		if h_temp_sk:
			list_signalk_path3.append(h_temp_skt)
			list_signalk3.append(str(round(temperature_h,2)+273.15))

		if list_signalk3:
			SignalK = '{"updates": [{"source": {"type": "I2C","src" : "hum"},"timestamp": "'+str( datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f') )[0:23]+'Z","values":[ '
			Erg=''
			for i in range(0,len(list_signalk3)):
				Erg += '{"path": "'+list_signalk_path3[i]+'","value":'+list_signalk3[i]+'},'
			SignalK+=Erg[0:-1]+']}],"context": "vessels.'+uuid+'"}\n'
			sock.sendto(SignalK, ('127.0.0.1', 7777))

		'''
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
'''