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
import socket, time, datetime
from classes.conf import Conf
from classes.check_vessel_self import checkVesselSelf
import RPi.GPIO as GPIO

def publish_sk(io,channel,current_state):
	if io=='in':io='input'
	if io=='out':io='output'
	channel=str(channel)
	path='notifications.gpio.'+io+'.gpio'+channel
	value='{"message": "'+current_state+'"}'
	timestamp=str( datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f') )[0:23]+'Z'
	SignalK='{"context": "vessels.'+uuid+'","updates":[{"source":{"type": "GPIO","src":"GPIO'+channel+'"},"timestamp":"'+timestamp+'","values":[{"path":"'+path+'","value":'+value+'}]}]}\n'
	sock.sendto(SignalK, ('127.0.0.1', 55558))

conf=Conf()

try:
	gpio_list=eval(conf.get('GPIO', 'sensors'))
except: gpio_list=[]

#name, io, gpio, pull, last_state
if gpio_list:
	vessel_self=checkVesselSelf()
	uuid=vessel_self.uuid
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)

	try:
		c=0
		for i in gpio_list:
			channel=int(i[2])
			if i[1]=='out':
				GPIO.setup(channel, GPIO.OUT)
				GPIO.output(channel, 0)
			if i[1]=='in':
				pull_up_down=GPIO.PUD_DOWN
				if i[3]=='up': pull_up_down=GPIO.PUD_UP
				GPIO.setup(channel, GPIO.IN, pull_up_down=pull_up_down)
			gpio_list[c].append('')
			c=c+1

		while True:
			time.sleep(0.1)
			c=0
			for i in gpio_list:
				channel=int(i[2])
				io=i[1]
				if GPIO.input(channel):
					current_state='H'
					last_state=gpio_list[c][4]
					if current_state!=last_state:
						gpio_list[c][4]=current_state
						#print i[1]+' GPIO'+str(channel)+': 1'
						publish_sk(io,channel,current_state)
				else:
					current_state='L'
					last_state=gpio_list[c][4]
					if current_state!=last_state:
						gpio_list[c][4]=current_state
						#print i[1]+' GPIO'+str(channel)+': 0'
						publish_sk(io,channel,current_state)
				c=c+1

	except Exception,e: print str(e)
	finally: GPIO.cleanup()