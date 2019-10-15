#!/usr/bin/python
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
import socket
from classes.conf import Conf

def on_message(client, userdata, msg):
	try:
		for i in topics_list:
			if msg.topic == i[0]:
				if i[1] == 0: #general
					path='notifications.'+msg.topic
					value = msg.payload
					value = value.replace('"', "'")
					SignalK='{"updates":[{"$source":"OPnotifications.MQTT.'+msg.topic+'","values":[{"path":"'+path+'","value":"'+value+'"}]}]}\n'
					sock.sendto(SignalK, ('127.0.0.1', 55558))
				if i[1] == 1: #signal k key input
					path = i[2]
					value = msg.payload
					value = value.replace('"', "'")
					SignalK='{"updates":[{"$source":"OPsensors.MQTT.'+msg.topic+'","values":[{"path":"'+path+'","value":"'+value+'"}]}]}\n'			
					sock.sendto(SignalK, ('127.0.0.1', 55557))
				if i[1] == 2: #signal k delta input
					SignalK = msg.payload		
					sock.sendto(SignalK, ('127.0.0.1', 55557))
	except Exception,e: print str(e)

def on_connect(client, userdata, flags, rc):
	try:
		for i in topics_list:
			client.subscribe(i[0], qos=0)
	except Exception,e: print str(e)

conf = Conf()

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
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
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
	client_local.loop_forever()
