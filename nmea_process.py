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

import sys, ConfigParser, os, socket, time, pynmea2, geomag, datetime, RTIMU, math, threading, csv

pathname = os.path.dirname(sys.argv[0])
currentpath = os.path.abspath(pathname)

data_conf = ConfigParser.SafeConfigParser()
data_conf.read(currentpath+'/openplotter.conf')


#global variables
global position
position=['','','','']
global date
date=datetime.date.today()
global mag_var
mag_var=['','']
global heading
heading=''
global pressure
pressure=''
global temperature
temperature=''

def thread_frecuency():
	SETTINGS_FILE = "RTIMULib"
	s = RTIMU.Settings(SETTINGS_FILE)
	imu = RTIMU.RTIMU(s)
	pressure_val = RTIMU.RTPressure(s)
	imu.IMUInit()
	pressure_val.pressureInit()

	global heading
	global pressure
	global temperature

	tick=time.time()

	ifile  = open(currentpath+'/weather_log.csv', "r")
	reader = csv.reader(ifile)
	log_list = []
	for row in reader:
		log_list.append(row)
	ifile.close()
	if log_list: last_log=float(log_list[len(log_list)-1][0])
	else: last_log=0


	while True:

		tick2=time.time()

		if imu.IMURead():
			data = imu.getIMUData()
			(data["pressureValid"], data["pressure"], data["temperatureValid"], data["temperature"]) = pressure_val.pressureRead()
			fusionPose = data["fusionPose"]
			heading0=math.degrees(fusionPose[2])
			if heading0<0:
				heading0=360+heading0
			heading=round(heading0,1)
			if (data["pressureValid"]):
				pressure=data["pressure"]
			if (data["temperatureValid"]):
				temperature=data["temperature"]

		
		if tick2-tick > float(data_conf.get('STARTUP', 'nmea_rate')):

			tick=time.time()
# HDG
			if data_conf.get('STARTUP', 'nmea_hdg')=='1':
				calculate_mag_var()
				hdg = pynmea2.HDG('OP', 'HDG', (str(heading),'','',str(mag_var[0]),mag_var[1]))
				hdg1=str(hdg)
				hdg2=repr(hdg1)+"\r\n"
				hdg3=hdg2.replace("'", "")
				sock.sendto(hdg3, ('localhost', 10110))
# MDA			
			if data_conf.get('STARTUP', 'nmea_mda')=='1':
				press=round(pressure/1000,4)
				temp= round(temperature,1)
				mda = pynmea2.MDA('OP', 'MDA', ('','',str(press),'B',str(temp),'C','','','','','','','','','','','','','',''))
				mda1=str(mda)
				mda2=repr(mda1)+"\r\n"
				mda3=mda2.replace("'", "")
				sock.sendto(mda3, ('localhost', 10110))
# log temperature pressure
			if data_conf.get('STARTUP', 'press_temp_log')=='1':
				if tick-last_log > 300:
					last_log=tick
					new_row=[tick,pressure,temperature]
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


def calculate_mag_var():
	global mag_var
	if position[0] and position[2]:
		lat=lat_DM_to_DD(position[0])
		if position[1]=='S': lat = lat * -1
		lon=lon_DM_to_DD(position[2])
		if position[3]=='W': lon = lon * -1
		now = date
		var=float(geomag.declination(lat, lon, 0, now))
		var=round(var,1)
		if var >= 0.0:
			mag_var=[var,'E']
		if var < 0.0:
			mag_var=[var*-1,'W']
	else:
		mag_var=['','']

def lat_DM_to_DD(DM):
	degrees=float(DM[0:2])
	minutes=float(DM[2:len(DM)])
	minutes=minutes/60
	DD=degrees+minutes
	return DD

def lon_DM_to_DD(DM):
	degrees=float(DM[0:3])
	minutes=float(DM[3:len(DM)])
	minutes=minutes/60
	DD=degrees+minutes
	return DD

def create_rmc(msg):
	msgstr=str(msg)
	items=msgstr.split(',')
	last_item=items[12].split('*')
	if mag_var[0]: mag_var[0]=str(mag_var[0])
	rmc = pynmea2.RMC('OP', 'RMC', (items[1],items[2],items[3],items[4],items[5],items[6],items[7],items[8],items[9],mag_var[0],mag_var[1],last_item[0]))
	rmc1=str(rmc)
	rmc2=repr(rmc1)+"\r\n"
	rmc3=rmc2.replace("'", "")
	sock.sendto(rmc3, ('localhost', 10110))

def check_nmea():
	global position
	global date
	while True:
		frase_nmea =''
		try:
			frase_nmea = sock_in.recv(512)
		except socket.error, error_msg:
			print 'Failed to connect with localhost:10110.'
			print 'Error: '+ str(error_msg[0])
			break
		else:
			if frase_nmea:
				try:
					msg = pynmea2.parse(frase_nmea)

					#position
					if msg.sentence_type == 'RMC' or msg.sentence_type =='GGA' or msg.sentence_type =='GNS' or msg.sentence_type =='GLL':
						position=[msg.lat, msg.lat_dir, msg.lon, msg.lon_dir]

					#date
					if msg.sentence_type == 'RMC':
						date=msg.datestamp

					#$OPRMC
					if msg.talker != 'OP' and msg.sentence_type == 'RMC' and data_conf.get('STARTUP', 'nmea_rmc')=='1':
						create_rmc(msg)

				#except Exception,e: print str(e)
				except: pass
			else:
				break


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

hilo=threading.Thread(target=thread_frecuency)
hilo.setDaemon(1)
hilo.start()

while True:
	try:
		sock_in = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock_in.settimeout(10)
		sock_in.connect(('localhost', 10110))
	except socket.error, error_msg:
		print 'Failed to connect with localhost:10110.'
		print 'Error: '+ str(error_msg[0])
	else: 
		check_nmea()

	print 'No data, trying to reconnect...'
	time.sleep(7)