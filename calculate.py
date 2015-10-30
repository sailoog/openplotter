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

import socket, time, pynmea2, geomag, datetime, math
from classes.conf import Conf

conf=Conf()

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
	last_heading=''
	heading_time=''
	STW=''
	AWS=''
	AWA=''
	SOG=''
	COG=''
	tick=time.time()

	while True:
		tick2=time.time()

		frase_nmea =''
		try:
			frase_nmea = sock_in.recv(1024)
		except socket.error, error_msg:
			print 'Failed to connect with localhost:10110.'
			print 'Error: '+ str(error_msg[0])
			break
		else:
			if frase_nmea:
				try:
					nmea_list=frase_nmea.split()

					for i in nmea_list:
						msg = pynmea2.parse(i)
						nmea_type=msg.sentence_type

						#REFRESH NMEA

						# refresh position
						if nmea_type == 'RMC' or nmea_type =='GGA' or nmea_type =='GNS' or nmea_type =='GLL':
							position1=[msg.lat, msg.lat_dir, msg.lon, msg.lon_dir]
							position=position1

						# refresh date / SOG / COG
						if nmea_type == 'RMC':
							date=msg.datestamp
							SOG=msg.spd_over_grnd
							COG=msg.true_course

						if nmea_type == 'VTG':
							SOG=msg.spd_over_grnd_kts
							COG=msg.true_track

						# refresh Speed Trought Water / heading true / heading magnetic
						if nmea_type == 'VBW':
							STW=msg.lon_water_spd

						if nmea_type == 'VHW':
							STW=msg.water_speed_knots
							heading_t=msg.heading_true
							heading_m=msg.heading_magnetic
						
						if nmea_type == 'HDT':
							heading_t=msg.heading
						
						if nmea_type == 'HDM' or nmea_type == 'HDG':
							heading_m0=msg.heading
							if heading_m0: heading_m=heading_m0
						
						# refresh Apparent Wind Speed / Apparent Wind Angle
						if nmea_type == 'VWR':
							AWS=msg.wind_speed_kn
							AWA1=[msg.deg_r, msg.l_r]
							AWA=AWA1

						if nmea_type == 'MWV':
							if msg.wind_speed_units=='N':
								AWS=msg.wind_speed
							if msg.reference=='R':
								AWA1=float(msg.wind_angle)
								AWA2='R'
								if AWA1>180: 
									AWA1=360-AWA1
									AWA2='L'
								AWA=[AWA1, AWA2]

						#generate heading_t if not exists
						if not heading_t:
							if heading_m and position[0] and position[2] and date:
								mag_var=calculate_mag_var(position,date)
								var=mag_var[0]
								if mag_var[1]=='W':var=var*-1
								heading_t=float(heading_m)+var
								if heading_t>360: heading_t=heading_t-360
								if heading_t<0: heading_t=360+heading_t
							else: heading_t=''
						else: 
							heading_t=float(heading_t)

						#GENERATE NMEA

						if tick2-tick > float(conf.get('STARTUP', 'nmea_rate_cal')):
							tick=time.time()
							#generate magnetic variation
							if  conf.get('STARTUP', 'nmea_mag_var')=='1' and position[0] and position[2] and date:
								mag_var=calculate_mag_var(position,date)
								hdg = pynmea2.HDG('OP', 'HDG', ('','','',str(mag_var[0]),mag_var[1]))
								hdg1=str(hdg)
								hdg2=hdg1+'\r\n'
								sock.sendto(hdg2, ('localhost', 10110))

							#generate headint_t
							if  conf.get('STARTUP', 'nmea_hdt')=='1' and position[0] and position[2] and date and heading_m:
								mag_var=calculate_mag_var(position,date)
								var=float(mag_var[0])
								if mag_var[1]=='W':var=var*-1
								heading_t=float(heading_m)+var
								if heading_t>360: heading_t=heading_t-360
								if heading_t<0: heading_t=360+heading_t
								hdt = pynmea2.HDT('OP', 'HDT', (str(round(heading_t,1)),'T'))
								hdt1=str(hdt)
								hdt2=hdt1+'\r\n'
								sock.sendto(hdt2, ('localhost', 10110))

							#generate True Wind STW
							if conf.get('STARTUP', 'tw_stw')=='1' and STW and AWS and AWA:
								STW0=float(STW)
								AWS0=float(AWS)
								AWA0=[float(AWA[0]),AWA[1]]
								TWS=math.sqrt((STW0**2+AWS0**2)-(2*STW0*AWS0*math.cos(math.radians(AWA0[0]))))
								TWA=math.degrees(math.acos((AWS0**2-TWS**2-STW0**2)/(2*TWS*STW0)))
								TWA0=TWA
								if AWA0[1]=='L': TWA0=360-TWA0
								TWSr=round(TWS,1)
								TWA0r=round(TWA0,0)
								mwv = pynmea2.MWV('OP', 'MWV', (str(TWA0r),'T',str(TWSr),'N','A'))
								mwv1=str(mwv)
								mwv2=mwv1+'\r\n'
								sock.sendto(mwv2, ('localhost', 10110))

								if heading_t:
									if AWA0[1]=='R':
										TWD=heading_t+TWA
									if AWA0[1]=='L':
										TWD=heading_t-TWA
									if TWD>360: TWD=TWD-360
									if TWD<0: TWD=360+TWD
									TWDr=round(TWD,0)
									mwd = pynmea2.MWD('OP', 'MWD', (str(TWDr),'T','','M',str(TWSr),'N','',''))
									mwd1=str(mwd)
									mwd2=mwd1+'\r\n'
									sock.sendto(mwd2, ('localhost', 10110))
								
								STW=''
								AWS=''
								AWA=''
							
							#generate Rate of Turn (ROT)
							if conf.get('STARTUP', 'nmea_rot')=='1' and heading_m:
 								if not last_heading: #initialize
									last_heading = heading_m
 									heading_time = time.time()
								
								else:	#normal run
									heading_change = heading_m-last_heading
									last_heading_time = heading_time
									heading_time = time.time()
									last_heading = heading_m

 									if heading_change > 180:	#If we are "passing" north
 										heading_change = heading_change - 360
									if heading_change < -180: 	#if we are "passing north"
										heading_change = 360 + heading_change
									rot = float(heading_change)/((heading_time - last_heading_time)/60)
									rot= round(rot,1)				
									#consider damping ROT values
									
								rot = pynmea2.ROT('OP', 'ROT', (str(rot),'A'))
								rot1=str(rot)
								rot2=rot1+'\r\n'
								sock.sendto(rot2, ('localhost', 10110))
							
							#generate True Wind SOG
							if conf.get('STARTUP', 'tw_sog')=='1' and SOG and COG and heading_t and AWS and AWA:
								SOG0=float(SOG)
								COG0=float(COG)
								AWS0=float(AWS)
								AWA0=[float(AWA[0]),AWA[1]]
								D=heading_t-COG0
								if AWA0[1]=='R': AWD=AWA0[0]+D
								if AWA0[1]=='L': AWD=(AWA0[0]*-1)+D
								if AWD > 0: AWD0=[AWD,'R']
								if AWD < 0: AWD0=[AWD*-1,'L']
								TWS=math.sqrt((SOG0**2+AWS0**2)-(2*SOG0*AWS0*math.cos(math.radians(AWD0[0]))))
								TWAc=math.degrees(math.acos((AWS0**2-TWS**2-SOG0**2)/(2*TWS*SOG0)))
								if AWD0[1]=='R': TWD=COG0+TWAc
								if AWD0[1]=='L': TWD=COG0-TWAc
								if TWD>360: TWD=TWD-360
								if TWD<0: TWD=360+TWD
								TWDr=round(TWD,0)
								TWSr=round(TWS,1)
								mwd = pynmea2.MWD('OP', 'MWD', (str(TWDr),'T','','M',str(TWSr),'N','',''))
								mwd1=str(mwd)
								mwd2=mwd1+'\r\n'
								sock.sendto(mwd2, ('localhost', 10110))


								TWA=TWD-heading_t
								TWA0=TWA
								if TWA0 < 0: TWA0=360+TWA0
								TWA0r=round(TWA0,0)
								mwv = pynmea2.MWV('OP', 'MWV', (str(TWA0r),'T',str(TWSr),'N','A'))
								mwv1=str(mwv)
								mwv2=mwv1+'\r\n'
								sock.sendto(mwv2, ('localhost', 10110))

								AWS=''
								AWA=''
								SOG=''
								COG=''


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
