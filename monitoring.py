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

import time, socket, threading, copy
from classes.datastream import DataStream
from classes.conf import Conf
from classes.language import Language
from classes.actions import Actions
from classes.mqtt import Mqtt

def read_triggers():
	global triggers
	data=conf.get('ACTIONS', 'triggers')
	try:
		temp_list=eval(data)
	except:temp_list=[]
	for ii in temp_list:
		if ii[1]==-1 or a.getDataListIndex(ii[1]):
			ii.append(False)# 5 state
			for iii in ii[4]:
				if iii[3]==2: iii[2]=iii[2]*60
				if iii[3]==3: iii[2]=(iii[2]*60)*60
				if iii[3]==4: iii[2]=((iii[2]*24)*60)*60
				iii.append('')# 4 last run
			triggers.append(ii)

def start_actions(trigger):
	global triggers
	for index,i in enumerate(triggers[trigger][4]):
		now=time.time()
		if triggers[trigger][5]==False:
			triggers[trigger][4][index][4]=now
			re=''
			try:
				re=actions.run_action(i[0],i[1],conf,a)
			except Exception,e: print str(e)
			if re=='read':
				startall()
		else:
			if i[3]==0: pass
			else:
				if now-i[4] > i[2]:
					triggers[trigger][4][index][4]=now
					re=''
					try:
						re=actions.run_action(i[0],i[1],conf,a)
					except Exception,e: print str(e)
					if re=='read':
						startall()

def startall():
	global triggers
	new_list = copy.deepcopy(triggers)
	i=0
	for ii in triggers:
		triggers[i][0]=1
		new_list[i][0]=1
		del new_list[i][5]
		ib=0
		for iii in ii[4]:
			del new_list[i][4][ib][4]
			ib=ib+1
		i=i+1
	conf.set('ACTIONS', 'triggers', str(new_list))
	del new_list

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
conf=Conf()

Language(conf.get('GENERAL','lang'))

global triggers
triggers=[]
global sock_in
global error
sock_in=''
error=0
a=DataStream(conf)
actions=Actions(conf)
nodata=''

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

read_triggers()

thread1=threading.Thread(target=parse_nmea)	
if not thread1.isAlive(): thread1.start()

mqtt=Mqtt(conf,a)

#end no loop

# loop
while True:
	time.sleep(0.01)
	a.checkinputs()
	a.checkoutputs()
	#actions
	for index,item in enumerate(triggers):
		if item[0]==1:
			if item[1]==-1:
				operator=''
				start_actions(index)
				triggers[index][5]=True
			else:
				trigger=a.getDataListIndex(item[1])
				trigger_value=a.DataList[trigger][2]
				now = time.time()
				trigger_value_timestamp=a.DataList[trigger][4]
				operator=item[2]
				data=a.getVariablesValue(item[3])
				try:
					data_value=float(data)
				except: data_value=''
				data_string=str(data)
			try:	
				#not present for
				if operator==0:
					if trigger_value_timestamp:
						if now-trigger_value_timestamp > data_value: 
							start_actions(index)
							triggers[index][5]=True
						else: 
							triggers[index][5]=False
						nodata=''
					else: 
						if not nodata: nodata=now
						if now-nodata > data_value: 
							start_actions(index)
							triggers[index][5]=True
						else: 
							triggers[index][5]=False
				#present in the last
				if operator==1: 
					if trigger_value_timestamp:
						if now-trigger_value_timestamp < data_value:
							start_actions(index)
							triggers[index][5]=True
						else: 
							triggers[index][5]=False
				if operator==2 or operator==3 or operator==4 or operator==5 or operator==6:
					if trigger_value_timestamp:
						#equal (number)
						if operator==2 and data_value:
							if float(trigger_value) == data_value: 
								start_actions(index)
								triggers[index][5]=True
							else: 
								triggers[index][5]=False
						#equal (string)
						if operator==2 and not data_value:
							if trigger_value == data_string:
								start_actions(index)
								triggers[index][5]=True
							else: 
								triggers[index][5]=False
						#less than
						if operator==3:
							if float(trigger_value) < data_value: 
								start_actions(index)
								triggers[index][5]=True
							else: 
								triggers[index][5]=False
						#less than or equal to
						if operator==4:
							if float(trigger_value) <= data_value: 
								start_actions(index)
								triggers[index][5]=True
							else: 
								triggers[index][5]=False
						#greater than
						if operator==5:
							if float(trigger_value) > data_value:
								start_actions(index)
								triggers[index][5]=True
							else: 
								triggers[index][5]=False
						#greater than or equal to
						if operator==6:
							if float(trigger_value) >= data_value: 
								start_actions(index)
								triggers[index][5]=True
							else: 
								triggers[index][5]=False
				#switch on
				if operator==7:
					if trigger_value==1: 
						start_actions(index)
						triggers[index][5]=True
					else: 
						triggers[index][5]=False

				#switch off
				if operator==8:
					if trigger_value==0: 
						start_actions(index)
						triggers[index][5]=True
					else: 
						triggers[index][5]=False

			#except Exception,e: print str(e)
			except: pass
