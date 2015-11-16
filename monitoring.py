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
import RPi.GPIO as GPIO
from classes.datastream import DataStream
from classes.conf import Conf
from classes.language import Language
from classes.actions import Actions

conf=Conf()

Language(conf.get('GENERAL','lang'))

global sock_in
global error
sock_in=''
error=0
a=DataStream()
actions=Actions()

global state1
global state2
global state3
global state4
state1=False
state2=False
state3=False
state4=False

last_heading=''
heading_time=''

GPIO.setmode(GPIO.BCM)

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
		sock_in=''
		time.sleep(7)
	else: error=0
#end thread1

#switches
def switch1(channel):
	global state1
	if GPIO.input(channel):
		if not state1:
			a.SW1[2]=_('on')
			a.SW1[4]=time.time()
			actions.run_action(conf.get('SWITCH1', 'on_action'), conf.get('SWITCH1', 'on_command'), conf,'')
			state1=True
	else:
		if state1:
			a.SW1[2]=_('off')
			a.SW1[4]=time.time()
			actions.run_action(conf.get('SWITCH1', 'off_action'), conf.get('SWITCH1', 'off_command'), conf,'')
			state1=False

def switch2(channel):
	global state2
	if GPIO.input(channel):
		if not state2:
			a.SW2[2]=_('on')
			a.SW2[4]=time.time()
			actions.run_action(conf.get('SWITCH2', 'on_action'), conf.get('SWITCH2', 'on_command'), conf,'')
			state2=True
	else:
		if state2:
			a.SW2[2]=_('off')
			a.SW2[4]=time.time()
			actions.run_action(conf.get('SWITCH2', 'off_action'), conf.get('SWITCH2', 'off_command'), conf,'')
			state2=False

def switch3(channel):
	global state3
	if GPIO.input(channel):
		if not state3:
			a.SW3[2]=_('on')
			a.SW3[4]=time.time()
			actions.run_action(conf.get('SWITCH3', 'on_action'), conf.get('SWITCH3', 'on_command'), conf,'')
			state3=True
	else:
		if state3:
			a.SW3[2]=_('off')
			a.SW3[4]=time.time()
			actions.run_action(conf.get('SWITCH3', 'off_action'), conf.get('SWITCH3', 'off_command'), conf,'')
			state3=False

def switch4(channel):
	global state4
	if GPIO.input(channel):
		if not state4:
			a.SW4[2]=_('on')
			a.SW4[4]=time.time()
			actions.run_action(conf.get('SWITCH4', 'on_action'), conf.get('SWITCH4', 'on_command'), conf,'')
			state4=True
	else:
		if state4:
			a.SW4[2]=_('off')
			a.SW4[4]=time.time()
			actions.run_action(conf.get('SWITCH4', 'off_action'), conf.get('SWITCH4', 'off_command'), conf,'')
			state4=False
#end switches

#monitoring
def send_twitter(error):
	tweetStr = ''
	send_data=eval(conf.get('TWITTER', 'send_data'))
	for ii in send_data:
		timestamp=eval('a.'+a.DataList[ii]+'[4]')
		if timestamp:
			now=time.time()
			age=now-timestamp
			if age < 20:
				data=''
				value=''
				unit=''
				data=eval('a.'+a.DataList[ii]+'[1]')
				value=eval('a.'+a.DataList[ii]+'[2]')
				unit=eval('a.'+a.DataList[ii]+'[3]')
				if unit: tweetStr+= data+':'+str(value)+str(unit)+' '
				else: tweetStr+= data+':'+str(value)+' '
	if error !=0 : tweetStr+= error
	if tweetStr: actions.run_action('14',tweetStr,conf,'')

def send_gmail(error):
	subject = conf.get('GMAIL', 'subject')
	body = ''
	for ii in a.DataList:
		timestamp=eval('a.'+ii+'[4]')
		if timestamp:
			now=time.time()
			age=now-timestamp
			if age < 20:
				data=''
				value=''
				unit=''
				data=eval('a.'+ii+'[0]')
				value=eval('a.'+ii+'[2]')
				unit=eval('a.'+ii+'[3]')
				if unit: body += data+': '+str(value)+' '+str(unit)+'\n'
				else: body+= data+': '+str(value)+'\n'
	if error !=0 : body+= error
	if subject: actions.run_action('17',subject,conf,body)
#end monitoring

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

# no loop
thread1=threading.Thread(target=parse_nmea)	
if not thread1.isAlive(): thread1.start()

if conf.get('SWITCH1', 'enable')=='1':
	channel1=int(conf.get('SWITCH1', 'gpio'))
	pull_up_down=GPIO.PUD_DOWN
	if conf.get('SWITCH1', 'pull_up_down')=='Pull Up': pull_up_down=GPIO.PUD_UP
	GPIO.setup(channel1, GPIO.IN, pull_up_down=pull_up_down)
	GPIO.add_event_detect(channel1, GPIO.BOTH, callback=switch1)

if conf.get('SWITCH2', 'enable')=='1':
	channel2=int(conf.get('SWITCH2', 'gpio'))
	pull_up_down=GPIO.PUD_DOWN
	if conf.get('SWITCH2', 'pull_up_down')=='Pull Up': pull_up_down=GPIO.PUD_UP
	GPIO.setup(channel2, GPIO.IN, pull_up_down=pull_up_down)
	GPIO.add_event_detect(channel2, GPIO.BOTH, callback=switch2)

if conf.get('SWITCH3', 'enable')=='1':
	channel3=int(conf.get('SWITCH3', 'gpio'))
	pull_up_down=GPIO.PUD_DOWN
	if conf.get('SWITCH3', 'pull_up_down')=='Pull Up': pull_up_down=GPIO.PUD_UP
	GPIO.setup(channel3, GPIO.IN, pull_up_down=pull_up_down)
	GPIO.add_event_detect(channel3, GPIO.BOTH, callback=switch3)

if conf.get('SWITCH4', 'enable')=='1':
	channel4=int(conf.get('SWITCH4', 'gpio'))
	pull_up_down=GPIO.PUD_DOWN
	if conf.get('SWITCH4', 'pull_up_down')=='Pull Up': pull_up_down=GPIO.PUD_UP
	GPIO.setup(channel4, GPIO.IN, pull_up_down=pull_up_down)
	GPIO.add_event_detect(channel4, GPIO.BOTH, callback=switch4)

# loop
try:
	while True:		
		if conf.get('GMAIL', 'enable')=='1':
			if conf.get('GMAIL', 'periodicity') and conf.get('GMAIL', 'periodicity')!='0':
				now= time.time()
				if not conf.get('GMAIL', 'last_send'):
					conf.set('GMAIL', 'last_send', str(now))
				last_send = float(conf.get('GMAIL', 'last_send')) 
				periodicity = float(conf.get('GMAIL', 'periodicity'))*60
				if (now-last_send) > periodicity:
					conf.set('GMAIL', 'last_send', str(now))
					send_gmail(error)
		if conf.get('TWITTER', 'enable')=='1':
			if conf.get('TWITTER', 'periodicity') and conf.get('TWITTER', 'periodicity')!='0':
				now= time.time()
				if not conf.get('TWITTER', 'last_send'):
					conf.set('TWITTER', 'last_send', str(now))
				last_send = float(conf.get('TWITTER', 'last_send')) 
				periodicity = float(conf.get('TWITTER', 'periodicity'))*60
				if (now-last_send) > periodicity:
					conf.set('TWITTER', 'last_send', str(now))
					send_twitter(error)

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

		else: time.sleep(1)
finally:
    GPIO.cleanup()