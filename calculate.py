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

import time, socket, threading, datetime, geomag, pynmea2, math
from classes.datastream import DataStream
from classes.conf import Conf
from classes.language import Language

conf=Conf()

Language(conf.get('GENERAL','lang'))

global sock_in
global error
sock_in=''
error=0
a=DataStream()
last_heading=''
heading_time=''

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#thread1
def parse_nmea():
	global sock_in
	global error
	while True:
		if not sock_in: connect()
		else:
			frase_nmea =''
			try:
				frase_nmea = sock_in.recv(1024)
			except socket.error, error_msg:
				error= _('Failed to connect with localhost:10110. Error: ')+ str(error_msg[0])
				print error
			else:
				if frase_nmea: 
					a.parse_nmea(frase_nmea)
					error=0
				else:
					sock_in=''

def connect():
	global sock_in
	global error
	try:
		sock_in = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock_in.settimeout(5)
		sock_in.connect(('localhost', 10110))
	except socket.error, error_msg:
		error= _('Failed to connect with localhost:10110. Error: ')+ str(error_msg[0])
		print error
		sock_in=''
		time.sleep(7)
	else: error=0
#end thread1

# calculate
def calculate_mag_var(position, date):
	if position[0] and position[2] and date:
		try:
			var=float(geomag.declination(position[0], position[2], 0, date))
			var=round(var,1)
			if var >= 0.0:
				mag_var=[var,'E']
			if var < 0.0:
				mag_var=[var*-1,'W']
		except: mag_var=['','']
	else: mag_var=['','']
	return mag_var
# end calculate

thread1=threading.Thread(target=parse_nmea)	
if not thread1.isAlive(): thread1.start()

# loop
while True:
	#calculations
	if  conf.get('STARTUP', 'nmea_mag_var')=='1' or conf.get('STARTUP', 'nmea_hdt')=='1' or conf.get('STARTUP', 'nmea_rot')=='1' or conf.get('STARTUP', 'tw_stw')=='1'  or conf.get('STARTUP', 'tw_sog')=='1':
			
		time.sleep(float(conf.get('STARTUP', 'nmea_rate_cal')))

		accuracy=float(conf.get('STARTUP', 'cal_accuracy'))
		now=time.time()
		# refresh values
		position =[a.validate('Lat',now,accuracy), a.Lat[3], a.validate('Lon',now,accuracy), a.Lon[3]]
		date = a.validate('Date',now,accuracy)
		if not date: date = datetime.date.today()
		heading_m = a.validate('HDM',now,accuracy)
		mag_var = [a.validate('Var',now,accuracy), a.Var[3]]
		if not mag_var[0]: mag_var = calculate_mag_var(position,date)
		heading_t = a.validate('HDT',now,accuracy)
		if not heading_t:
			if heading_m and mag_var[0]:
				var=mag_var[0]
				if mag_var[1]=='W':var=var*-1
				heading_t=heading_m+var
				if heading_t>360: heading_t=heading_t-360
				if heading_t<0: heading_t=360+heading_t
		STW = a.validate('STW',now,accuracy)
		AWS = a.validate('AWS',now,accuracy) 
		AWA = [a.validate('AWA',now,accuracy), a.AWA[3]]
		if AWA[0]:
			if AWA[1]=='D':
				AWA[1]='R'
				if AWA[0]>180: 
					AWA[0]=360-AWA[0]
					AWA[1]='L'
		SOG = a.validate('SOG',now,accuracy)
		COG = a.validate('SOG',now,accuracy)
		# end refresh values
		#generate headint_t
		if  conf.get('STARTUP', 'nmea_hdt')=='1' and heading_t:
			hdt = pynmea2.HDT('OP', 'HDT', (str(round(heading_t,1)),'T'))
			hdt1=str(hdt)
			hdt2=hdt1+'\r\n'
			sock.sendto(hdt2, ('localhost', 10110))
		#generate magnetic variation
		if  conf.get('STARTUP', 'nmea_mag_var')=='1' and mag_var:
			hdg = pynmea2.HDG('OP', 'HDG', ('','','',str(mag_var[0]),mag_var[1]))
			hdg1=str(hdg)
			hdg2=hdg1+'\r\n'
			sock.sendto(hdg2, ('localhost', 10110))
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
		#generate True Wind STW
		if conf.get('STARTUP', 'tw_stw')=='1' and STW and AWS and AWA:
			print 'STW '
			print  STW
			print 'AWS '
			print  AWS 
			print 'AWA '
			print  AWA
			print 'heading_t '
			print  heading_t
			#TWA
			TWS=math.sqrt((STW**2+AWS**2)-(2*STW*AWS*math.cos(math.radians(AWA[0]))))
			TWA=math.degrees(math.acos((AWS**2-TWS**2-STW**2)/(2*TWS*STW)))
			TWA0=TWA
			if AWA[1]=='L': TWA0=360-TWA0
			TWSr=round(TWS,1)
			TWA0r=round(TWA0,0)
			mwv = pynmea2.MWV('OP', 'MWV', (str(TWA0r),'T',str(TWSr),'N','A'))
			mwv1=str(mwv)
			mwv2=mwv1+'\r\n'
			sock.sendto(mwv2, ('localhost', 10110))
			#TWD
			if heading_t:
				if AWA[1]=='R':
					TWD=heading_t+TWA
				if AWA[1]=='L':
					TWD=heading_t-TWA
				if TWD>360: TWD=TWD-360
				if TWD<0: TWD=360+TWD
				TWDr=round(TWD,0)
				mwd = pynmea2.MWD('OP', 'MWD', (str(TWDr),'T','','M',str(TWSr),'N','',''))
				mwd1=str(mwd)
				mwd2=mwd1+'\r\n'
				sock.sendto(mwd2, ('localhost', 10110))
				print ' '
				print 'TWA'
				print TWA0r
				print 'TWS'
				print TWSr
				print 'TWD'
				print TWDr
		#generate True Wind SOG
		if conf.get('STARTUP', 'tw_sog')=='1' and SOG and COG and heading_t and AWS and AWA:
			print 'SOG '
			print  SOG
			print 'COG '
			print  COG
			print 'AWS '
			print  AWS 
			print 'AWA '
			print  AWA
			print 'heading_t '
			print  heading_t
			#TWD
			D=heading_t-COG
			if AWA[1]=='R': AWD=AWA[0]+D
			if AWA[1]=='L': AWD=(AWA[0]*-1)+D
			if AWD > 0: AWD0=[AWD,'R']
			if AWD < 0: AWD0=[AWD*-1,'L']
			TWS=math.sqrt((SOG**2+AWS**2)-(2*SOG*AWS*math.cos(math.radians(AWD0[0]))))
			TWAc=math.degrees(math.acos((AWS**2-TWS**2-SOG**2)/(2*TWS*SOG)))
			if AWD0[1]=='R': TWD=COG+TWAc
			if AWD0[1]=='L': TWD=COG-TWAc
			if TWD>360: TWD=TWD-360
			if TWD<0: TWD=360+TWD
			TWDr=round(TWD,0)
			TWSr=round(TWS,1)
			mwd = pynmea2.MWD('OP', 'MWD', (str(TWDr),'T','','M',str(TWSr),'N','',''))
			mwd1=str(mwd)
			mwd2=mwd1+'\r\n'
			sock.sendto(mwd2, ('localhost', 10110))
			#TWA
			TWA=TWD-heading_t
			TWA0=TWA
			if TWA0 < 0: TWA0=360+TWA0
			TWA0r=round(TWA0,0)
			mwv = pynmea2.MWV('OP', 'MWV', (str(TWA0r),'T',str(TWSr),'N','A'))
			mwv1=str(mwv)
			mwv2=mwv1+'\r\n'
			sock.sendto(mwv2, ('localhost', 10110))
			print ' '
			print 'TWA'
			print TWA0r
			print 'TWS'
			print TWSr
			print 'TWD'
			print TWDr
	else: time.sleep(0.1)