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

import socket, time, pynmea2, RTIMU, math, csv
from classes.paths import Paths
from classes.conf import Conf

paths=Paths()
currentpath=paths.currentpath

conf=Conf()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

nmea_hdg_b = conf.get('STARTUP', 'nmea_hdg')=='1'
nmea_heel_b = conf.get('STARTUP', 'nmea_heel')=='1'
nmea_pitch_b = conf.get('STARTUP', 'nmea_pitch')=='1'
poll_interval = 1

imu_b = False
pressure_val_b = False
humidity_val_b = False
log_list_b = False

nmea_press_b = conf.get('STARTUP', 'nmea_press')=='1'
nmea_temp_p_b = conf.get('STARTUP', 'nmea_temp_p')=='1'
nmea_hum_b = conf.get('STARTUP', 'nmea_hum')=='1'
nmea_temp_h_b = conf.get('STARTUP', 'nmea_temp_h')=='1'
press_temp_log_b = conf.get('STARTUP', 'press_temp_log')=='1'

nmea_rate_sen = float(conf.get('STARTUP', 'nmea_rate_sen'))

if nmea_hdg_b or nmea_heel_b or nmea_pitch_b:
	SETTINGS_FILE = "RTIMULib"
	s = RTIMU.Settings(SETTINGS_FILE)
	imu = RTIMU.RTIMU(s)
	imu.IMUInit()
	imu.setSlerpPower(0.02)
	imu.setGyroEnable(True)
	imu.setAccelEnable(True)
	imu.setCompassEnable(True)
	poll_interval = imu.IMUGetPollInterval()
	imu_b = True
	


if nmea_press_b or nmea_temp_p_b:
	SETTINGS_FILE2 = "RTIMULib2"
	s2 = RTIMU.Settings(SETTINGS_FILE2)
	pressure_val = RTIMU.RTPressure(s2)
	pressure_val.pressureInit()
	pressure_val_b = True

if nmea_hum_b or nmea_temp_h_b:
	SETTINGS_FILE3 = "RTIMULib3"
	s3 = RTIMU.Settings(SETTINGS_FILE3)
	humidity_val = RTIMU.RTHumidity(s3)
	humidity_val.humidityInit()
	humidity_val_b = True

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
	if imu_b:
		if imu.IMURead():
			data = imu.getIMUData()
			fusionPose = data["fusionPose"]
			heading_m0=math.degrees(fusionPose[2])
			heel=math.degrees(fusionPose[0])
			pitch=math.degrees(fusionPose[1])
			if heading_m0<0:
				heading_m0=360+heading_m0
			heading_m=round(heading_m0,1)


	# read Pressure
	if pressure_val_b:
		read=pressure_val.pressureRead()
		if read:
			if (read[0]):
				pressure=read[1]
			if (read[2]):
				temperature_p=read[3]

	# read humidity
	if humidity_val_b:

		read=humidity_val.humidityRead()
		if read:
			if (read[0]):
				humidity=read[1]
			if (read[2]):
				temperature_h=read[3]

	#GENERATE
	if tick2-tick > nmea_rate_sen:
		tick=time.time()
		# HDG
		if nmea_hdg_b and heading_m:
			hdg = pynmea2.HDG('OS', 'HDG', (str(heading_m),'','','',''))
			hdg1=str(hdg)
			hdg2=hdg1+"\r\n"
			sock.sendto(hdg2, ('127.0.0.1', 10110))
			heading_m=''
		# XDR
		list_tmp1=[]
		list_tmp2=[]		
		if nmea_press_b and pressure:
			press=round(pressure/1000,4)
			list_tmp1.append('P')
			list_tmp1.append(str(press))
			list_tmp1.append('B')
			list_tmp1.append('I2CP')
		if nmea_temp_p_b and temperature_p:
			temp= round(temperature_p,1)
			list_tmp1.append('C')
			list_tmp1.append(str(temp))
			list_tmp1.append('C')
			list_tmp1.append('I2CT')
		if nmea_temp_h_b and temperature_h:
			temp= round(temperature_h,1)
			list_tmp1.append('C')
			list_tmp1.append(str(temp))
			list_tmp1.append('C')
			list_tmp1.append('I2CT')
		if nmea_hum_b and humidity:
			hum=round(humidity,1)
			list_tmp1.append('H')
			list_tmp1.append(str(hum))
			list_tmp1.append('R')
			list_tmp1.append('I2CH')
		if nmea_heel_b and heel:
			heel= round(heel,1)
			list_tmp2.append('A')
			list_tmp2.append(str(heel))
			list_tmp2.append('D')
			list_tmp2.append('I2CX')
		if nmea_pitch_b and pitch:
			pitch= round(pitch,1)
			list_tmp2.append('A')
			list_tmp2.append(str(pitch))
			list_tmp2.append('D')
			list_tmp2.append('I2CY')

		if list_tmp1:
			xdr = pynmea2.XDR('OS', 'XDR', (list_tmp1))
			xdr1=str(xdr)
			xdr2=xdr1+"\r\n"
			sock.sendto(xdr2, ('127.0.0.1', 10110))
		if list_tmp2:
			xdr = pynmea2.XDR('OS', 'XDR', (list_tmp2))
			xdr1=str(xdr)
			xdr2=xdr1+"\r\n"
			sock.sendto(xdr2, ('127.0.0.1', 10110))			
			heel=''
			pitch=''

		temperature=''
		if nmea_temp_p_b: temperature=temperature_p
		if nmea_temp_h_b: temperature=temperature_h

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