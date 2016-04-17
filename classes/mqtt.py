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

import paho.mqtt.client as paho
import time

class Mqtt:
	def __init__(self,conf,a):
		self.a=a
		x=conf.get('MQTT', 'topics')
		if x: self.topics_list=eval(x)
		else: self.topics_list=[]

		local_broker='127.0.0.1'
		local_port='1883'
		user=conf.get('MQTT', 'username')
		passw=conf.get('MQTT', 'password')

		if self.topics_list:
			self.client_local = paho.Client()
			self.client_local.on_message = self.on_message
			self.client_local.on_connect = self.on_connect
			self.client_local.username_pw_set(user, passw)
			self.client_local.connect(local_broker, local_port)
			self.client_local.loop_start()

		broker=conf.get('MQTT', 'broker')
		port=conf.get('MQTT', 'port')

		if self.topics_list and broker and port :
			self.client = paho.Client()
			self.client.on_message = self.on_message
			self.client.on_connect = self.on_connect
			self.client.username_pw_set(user, passw)
			self.client.connect(broker, port)
			self.client.loop_start()


	def on_message(self, client, userdata, msg):
		for index, item in enumerate(self.a.DataList):
			if item[0]==msg.topic:
				self.a.DataList[index][2]=None
				time.sleep(0.05)
				self.a.DataList[index][2]=str(msg.payload)
				self.a.DataList[index][4]=time.time()
		#print(msg.topic+" "+str(msg.qos)+" "+str(msg.payload))

	def on_connect(self, client, userdata, flags, rc):
		for i in self.topics_list:
			try:
				client.subscribe(i[1], qos=0)
			except Exception,e: print str(e)

	def stop(self):
		self.client.loop_stop()
		self.client_local.loop_stop()