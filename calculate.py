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

import sys, ConfigParser, os, socket, time, pynmea2, geomag, datetime, math

pathname = os.path.dirname(sys.argv[0])
currentpath = os.path.abspath(pathname)

data_conf = ConfigParser.SafeConfigParser()
data_conf.read(currentpath+'/openplotter.conf')

def calculate_mag_var(position, date):
	if position[0] and position[2] and date:
		try:
			lat=lat_DM_to_DD(position[0])
			if position[1]=='S': lat = lat * -1
			lon=lon_DM_to_DD(position[2])
			if position[3]=='W': lon = lon * -1
			var=float(geomag.declination(lat, lon, 0, date))
			var=round(var,1)
			if var >= 0.0:
				mag_var=[var,'E']
			if var < 0.0:
				mag_var=[var*-1,'W']
		except: mag_var=['','']
	else: mag_var=['','']
	return mag_var

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

def check_nmea():
	position=['','','','']
	date=datetime.date.today()
	mag_var=['','']
	heading_m=''
	heading_t=''
	STW=''
	AWS=''
	AWA=['','']

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

					# refresh position
					if msg.sentence_type == 'RMC' or msg.sentence_type =='GGA' or msg.sentence_type =='GNS' or msg.sentence_type =='GLL':
						position1=[msg.lat, msg.lat_dir, msg.lon, msg.lon_dir]
						position=position1

					# refresh date
					if msg.sentence_type == 'RMC':
						date=msg.datestamp

					# refresh Speed Trought Water / heading true / heading magnetic
					if msg.sentence_type == 'VBW':
						STW=msg.lon_water_spd

					if msg.sentence_type == 'VHW':
						STW=msg.water_speed_knots
						heading_t=msg.heading_true
						heading_m=msg.heading_magnetic
					
					if msg.sentence_type == 'HDT':
						heading_t=msg.heading
					
					if msg.sentence_type == 'HDM' or msg.sentence_type == 'HDG':
						heading_m=msg.heading

					# refresh Apparent Wind Speed / Apparent Wind Angle
					if msg.sentence_type == 'VWR':
						AWS=msg.wind_speed_kn
						AWA1=[msg.deg_r, msg.l_r]
						AWA=AWA1

					if msg.sentence_type == 'MWV':
						if msg.wind_speed_units=='N':
							AWS=msg.wind_speed
						if msg.reference=='R':
							AWA1=float(msg.wind_angle)
							AWA2='R'
							if AWA1>180: 
								AWA1=360-AWA1
								AWA2='L'
							AWA=[AWA1, AWA2]


					#generate $OPRMC
					if  msg.sentence_type == 'RMC' and data_conf.get('STARTUP', 'nmea_rmc')=='1' and msg.talker != 'OP':
						msgstr=str(msg)
						items=msgstr.split(',')
						last_item=items[12].split('*')
						mag_var=calculate_mag_var(position,date)
						rmc = pynmea2.RMC('OP', 'RMC', (items[1],items[2],items[3],items[4],items[5],items[6],items[7],items[8],items[9],str(mag_var[0]),mag_var[1],last_item[0]))
						rmc1=str(rmc)
						rmc2=repr(rmc1)+"\r\n"
						rmc3=rmc2.replace("'", "")
						sock.sendto(rmc3, ('localhost', 10110))

					#calculate heading_t if not exists
					if not heading_t:
						if heading_m:
							mag_var=calculate_mag_var(position,date)
							var=mag_var[0]
							if mag_var[1]=='W':var=var*-1
							heading_t0=float(heading_m)+var
							if heading_t0>360: heading_t0=heading_t0-360
							if heading_t0<0: heading_t0=360+heading_t0
						else: heading_t0=''
					else: 
						heading_t0=float(heading_t)

					#generate True Wind
					if data_conf.get('STARTUP', 'tw_stw')=='1' and STW and AWS and AWA:
						STW0=float(STW)
						AWS0=float(AWS)
						AWA0=[float(AWA[0]),AWA[1]]
						TWS=math.sqrt((STW0**2+AWS**2)-(2*STW0*AWS0*math.cos(math.radians(AWA0[0]))))
						TWA=math.degrees(math.acos((AWS0**2-TWS**2-STW0**2)/(2*TWS*STW0)))
						TWA0=TWA
						if AWA0[1]=='L': TWA0=360-TWA0
						TWSr=round(TWS,1)
						TWA0r=round(TWA0,0)
						mwv = pynmea2.MWV('OP', 'MWV', (str(TWA0r),'T',str(TWSr),'N','A'))
						mwv1=str(mwv)
						mwv2=repr(mwv1)+"\r\n"
						mwv3=mwv2.replace("'", "")
						sock.sendto(mwv3, ('localhost', 10110))

						if heading_t0:
							if AWA0[1]=='R':
								TWD=heading_t0+TWA
							if AWA0[1]=='L':
								TWD=heading_t0-TWA
							if TWD>360: TWD=TWD-360
							if TWD<0: TWD=360+TWD
							TWDr=round(TWD,0)
							mwd = pynmea2.MWD('OP', 'MWD', (str(TWDr),'T','','M',str(TWSr),'N','',''))
							mwd1=str(mwd)
							mwd2=repr(mwd1)+"\r\n"
							mwd3=mwd2.replace("'", "")
							sock.sendto(mwd3, ('localhost', 10110))

				#except Exception,e: print str(e)
				except: pass
			else:
				break


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

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
