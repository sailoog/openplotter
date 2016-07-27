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
import time, socket, datetime, json
from classes.conf import Conf
from classes.check_vessel_self import checkVesselSelf

def on_message(client, userdata, msg):
	path=msg.topic
	path=path.replace('/','.')
	path='notifications.mqtt.'+path
	value='{"message": "'+msg.payload+'"}'
	timestamp=str( datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f') )[0:23]+'Z'
	SignalK='{"context": "vessels.'+uuid+'","updates":[{"source":{"type": "notifications","src":"mqtt"},"timestamp":"'+timestamp+'","values":[{"path":"'+path+'","value":'+value+'}]}]}\n'
	sock.sendto(SignalK, ('127.0.0.1', 55558))

def on_connect(client, userdata, flags, rc):
	for i in topics_list:
		try:
			client.subscribe(i, qos=0)
		except Exception,e: print str(e)

def stop():
	if client: client.loop_stop()
	if client_local: client_local.loop_stop()

def send_null():
	list_path=[]
	for ii in topics_list:
		if '/' in ii:
			list_tmp=ii.split('/')
			path_tmp='notifications.mqtt'
			for iii in list_tmp:
				path_tmp=path_tmp+'.'+iii
				if not path_tmp in list_path: list_path.append(path_tmp)
		else:
			path_tmp='notifications.mqtt.'+ii
			if not path_tmp in list_path: list_path.append(path_tmp)
	values=''
	timestamp=str( datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f') )[0:23]+'Z'
	SignalK='{"context": "vessels.'+uuid+'","updates":[{"source":{"type": "notifications","src":"mqtt"},"timestamp":"'+timestamp+'","values":['
	for i in list_path:
		values+= '{"path": "'+i+'","value": {"message": null}},'
	SignalK+=values[0:-1]+']}]}\n'
	sock.sendto(SignalK, ('127.0.0.1', 55558))


conf=Conf()

vessel_self=checkVesselSelf()
uuid=vessel_self.uuid

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

x=conf.get('MQTT', 'topics')
if x: topics_list=eval(x)
else: topics_list=[]

local_broker='127.0.0.1'
local_port='1883'
user=conf.get('MQTT', 'username')
passw=conf.get('MQTT', 'password')
broker=conf.get('MQTT', 'broker')
port=conf.get('MQTT', 'port')
client=''
client_local=''

if user and passw and topics_list:
	if broker and port:
		client = paho.Client()
		client.on_message = on_message
		client.on_connect = on_connect
		client.username_pw_set(user, passw)
		try:
			client.connect(broker, port)
			client.loop_start()
		except Exception,e: print str(e)
	client_local = paho.Client()
	client_local.on_message = on_message
	client_local.on_connect = on_connect
	client_local.username_pw_set(user, passw)
	client_local.connect(local_broker, local_port)
	send_null()
	client_local.loop_forever()
