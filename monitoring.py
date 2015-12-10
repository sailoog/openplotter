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

import time, socket, threading
import RPi.GPIO as GPIO
from classes.datastream import DataStream
from classes.conf import Conf
from classes.language import Language
from classes.actions import Actions

conf=Conf()

Language(conf.get('GENERAL','lang'))

global trigger_actions
global triggers
trigger_actions=''
triggers=''
global sock_in
global error
sock_in=''
error=0
a=DataStream()
actions=Actions()
nodata=''
channel1=''
channel2=''
channel3=''
channel4=''

GPIO.setmode(GPIO.BCM)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def read_triggers():
	global triggers
	data=conf.get('ACTIONS', 'triggers')
	triggers=data.split('||')
	triggers.pop()
	for index,item in enumerate(triggers):
		ii=item.split(',')
		ii[0]=int(ii[0])
		ii[1]=int(ii[1])
		ii[2]=int(ii[2])
		ii[3]=float(ii[3])
		ii.append(False)# 4 state
		triggers[index]=ii

def read_actions():
	global trigger_actions
	data=conf.get('ACTIONS', 'actions')
	trigger_actions=data.split('||')
	trigger_actions.pop()
	for index,item in enumerate(trigger_actions):
		ii=item.split(',')
		ii[0]=int(ii[0])
		ii[1]=int(ii[1])
		ii[3]=float(ii[3])
		ii[4]=int(ii[4])
		if ii[4]==2: ii[3]=ii[3]*60
		if ii[4]==3: ii[3]=(ii[3]*60)*60
		if ii[4]==4: ii[3]=((ii[3]*24)*60)*60
		ii.append('')# 5 last run
		trigger_actions[index]=ii

def start_actions(trigger):
	global trigger_actions
	for index,i in enumerate(trigger_actions):
		if i[0]==trigger:
			now=time.time()
			if triggers[trigger][4]==False:
				trigger_actions[index][5]=now
				re=''
				try:
					re=actions.run_action(str(i[1]),i[2],conf,a)
				except Exception,e: print str(e)
				if re=='read':
					read_triggers()
					read_actions()
			else:
				if i[4]==0: pass
				else:
					if now-i[5] > i[3]:
						trigger_actions[index][5]=now
						re=''
						try:
							re=actions.run_action(str(i[1]),i[2],conf,a)
						except Exception,e: print str(e)
						if re=='read':
							read_triggers()
							read_actions()
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

# no loop
read_triggers()
read_actions()

thread1=threading.Thread(target=parse_nmea)	
if not thread1.isAlive(): thread1.start()

if conf.get('SWITCH1', 'enable')=='1':
	channel1=int(conf.get('SWITCH1', 'gpio'))
	pull_up_down=GPIO.PUD_DOWN
	if conf.get('SWITCH1', 'pull_up_down')=='Pull Up': pull_up_down=GPIO.PUD_UP
	GPIO.setup(channel1, GPIO.IN, pull_up_down=pull_up_down)
if conf.get('SWITCH2', 'enable')=='1':
	channel2=int(conf.get('SWITCH2', 'gpio'))
	pull_up_down=GPIO.PUD_DOWN
	if conf.get('SWITCH2', 'pull_up_down')=='Pull Up': pull_up_down=GPIO.PUD_UP
	GPIO.setup(channel2, GPIO.IN, pull_up_down=pull_up_down)
if conf.get('SWITCH3', 'enable')=='1':
	channel3=int(conf.get('SWITCH3', 'gpio'))
	pull_up_down=GPIO.PUD_DOWN
	if conf.get('SWITCH3', 'pull_up_down')=='Pull Up': pull_up_down=GPIO.PUD_UP
	GPIO.setup(channel3, GPIO.IN, pull_up_down=pull_up_down)
if conf.get('SWITCH4', 'enable')=='1':
	channel4=int(conf.get('SWITCH4', 'gpio'))
	pull_up_down=GPIO.PUD_DOWN
	if conf.get('SWITCH4', 'pull_up_down')=='Pull Up': pull_up_down=GPIO.PUD_UP
	GPIO.setup(channel4, GPIO.IN, pull_up_down=pull_up_down)
#end no loop

# loop
while True:
	time.sleep(0.01)
	#switches
	if channel1:
		if GPIO.input(channel1):
			a.SW1[2]=1
			a.SW1[4]=time.time()
		else:
			a.SW1[2]=0
			a.SW1[4]=time.time()
	if channel2:
		if GPIO.input(channel2):
			a.SW2[2]=1
			a.SW2[4]=time.time()
		else:
			a.SW2[2]=0
			a.SW2[4]=time.time()
	if channel3:
		if GPIO.input(channel3):
			a.SW3[2]=1
			a.SW3[4]=time.time()
		else:
			a.SW3[2]=0
			a.SW3[4]=time.time()
	if channel4:
		if GPIO.input(channel4):
			a.SW4[2]=1
			a.SW4[4]=time.time()
		else:
			a.SW4[2]=0
			a.SW4[4]=time.time()
	#end switches

	#actions
	for index,item in enumerate(triggers):
		if item[0]==1:
			if item[1]==-1:
				operator=''
				start_actions(index)
				triggers[index][4]=True
			else:
				trigger=a.DataList[item[1]]
				trigger_value=eval('a.'+trigger+'[2]')
				now = time.time()
				trigger_value_timestamp=eval('a.'+trigger+'[4]')
				operator=item[2]
				data_value=float(item[3])
			#not present for
			if operator==0:
				if trigger_value_timestamp:
					if now-trigger_value_timestamp > data_value: 
						start_actions(index)
						triggers[index][4]=True
					else: 
						triggers[index][4]=False
					nodata=''
				else: 
					if not nodata: nodata=now
					if now-nodata > data_value: 
						start_actions(index)
						triggers[index][4]=True
					else: 
						triggers[index][4]=False
			#present in the last
			if operator==1: 
				if trigger_value_timestamp:
					if now-trigger_value_timestamp < data_value:
						start_actions(index)
						triggers[index][4]=True
					else: 
						triggers[index][4]=False
			if operator==2 or operator==3 or operator==4 or operator==5 or operator==6:
				if trigger_value_timestamp:
					if now-trigger_value_timestamp < 20:
						#equal
						if operator==2:
							if float(trigger_value) == data_value: 
								start_actions(index)
								triggers[index][4]=True
							else: 
								triggers[index][4]=False
						#less than
						if operator==3:
							if float(trigger_value) < data_value: 
								start_actions(index)
								triggers[index][4]=True
							else: 
								triggers[index][4]=False
						#less than or equal to
						if operator==4:
							if float(trigger_value) <= data_value: 
								start_actions(index)
								triggers[index][4]=True
							else: 
								triggers[index][4]=False
						#greater than
						if operator==5:
							if float(trigger_value) > data_value:
								start_actions(index)
								triggers[index][4]=True
							else: 
								triggers[index][4]=False
						#greater than or equal to
						if operator==6:
							if float(trigger_value) >= data_value: 
								start_actions(index)
								triggers[index][4]=True
							else: 
								triggers[index][4]=False
			#switch on
			if operator==7:
				if trigger=='SW1' and channel1:
					if a.SW1[2]==1: 
						start_actions(index)
						triggers[index][4]=True
					else: 
						triggers[index][4]=False
				if trigger=='SW2' and channel2:
					if a.SW2[2]==1: 
						start_actions(index)
						triggers[index][4]=True
					else: 
						triggers[index][4]=False
				if trigger=='SW3' and channel3:
					if a.SW3[2]==1: 
						start_actions(index)
						triggers[index][4]=True
					else: 
						triggers[index][4]=False
				if trigger=='SW4' and channel4:
					if a.SW4[2]==1: 
						start_actions(index)
						triggers[index][4]=True
					else: 
						triggers[index][4]=False
			#switch off
			if operator==8:
				if trigger=='SW1' and channel1:
					if a.SW1[2]==0: 
						start_actions(index)
						triggers[index][4]=True
					else: 
						triggers[index][4]=False
				if trigger=='SW2' and channel2:
					if a.SW2[2]==0: 
						start_actions(index)
						triggers[index][4]=True
					else: 
						triggers[index][4]=False
				if trigger=='SW3' and channel3:
					if a.SW3[2]==0: 
						start_actions(index)
						triggers[index][4]=True
					else: 
						triggers[index][4]=False
				if trigger=='SW4' and channel4:
					if a.SW4[2]==0: 
						start_actions(index)
						triggers[index][4]=True
					else: 
						triggers[index][4]=False
	#end actions