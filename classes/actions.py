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
import gammu, platform, subprocess, time, json, requests, socket, re

import paho.mqtt.publish as publish

from classes.gmailbot import GmailBot
from classes.twitterbot import TwitterBot

if platform.machine()[0:3] == 'arm':
	import RPi.GPIO as GPIO
else:
	import emulator.GPIO as GPIO


class Actions:
	def __init__(self, SK):
		self.SK = SK
		self.conf = SK.conf
		self.home = SK.home
		self.currentpath = SK.currentpath
		self.time_units = [_('no repeat'), _('seconds'), _('minutes'), _('hours'), _('days')]
		self.options = []
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		# ATENTION. If order changes, edit "run_action()" and ctrl_actions.py
		# 0 name, 1 message, 2 field data, 3 unique ID
		self.options.append([_('wait'), _('Enter seconds to wait in field "data".'), 1, 'ACT1'])
		self.options.append([_('command'), _('Enter a Linux command and arguments in the field below.'), 1, 'ACT2'])
		self.options.append([_('reset system'), 0, 0, 'ACT3'])
		self.options.append([_('shutdown system'), 0, 0, 'ACT4'])
		self.options.append(['startup stop', 0, 0, 'ACT7'])
		self.options.append(['startup restart', 0, 0, 'ACT8'])
		self.options.append([_('stop NMEA multiplexer'), 0, 0, 'ACT5'])
		self.options.append([_('reset NMEA multiplexer'), 0, 0, 'ACT6'])
		self.options.append([_('stop WiFi access point'),_('Access point will be disabled.\n\nIf you are on a headless system, you will not be able to reconnect again.\n\nAre you sure?'),0,'ACT9'])
		self.options.append([_('start WiFi access point'),_('Be sure you have filled in all fields in "WiFi AP" tab.'),0, 'ACT10'])
		#self.options.append([_('stop SDR-AIS'), 0, 0, 'ACT11'])
		#self.options.append([_('reset SDR-AIS'), _('Be sure you have filled in Gain and Correction fields in "SDR-AIS" tab and enabled AIS NMEA generation.'),0, 'ACT12'])
		self.options.append([_('publish Twitter'), _('Be sure you have filled in all fields in "Accounts" tab, and enabled Twitter checkbox.\n\nEnter text to publish in the field "data".'),1, 'ACT13'])
		self.options.append([_('send e-mail'), _('Be sure you have filled in all fields in "Accounts" tab, and enabled Gmail checkbox.\n\nEnter the subject in the field "data".'),1, 'ACT14'])
		self.options.append([_('send SMS'), _('Be sure you have enabled sending SMS in "SMS" tab.\n\nEnter the text in field "data".'), 1, 'ACT21'])
		self.options.append([_('play sound'), 'OpenFileDialog', 1, 'ACT15'])
		self.options.append([_('stop all sounds'), 0, 0, 'ACT16'])
		self.options.append([_('show message'), _('Enter the message in field "data".'), 1, 'ACT17'])
		self.options.append([_('close all messages'), 0, 0, 'ACT18'])
		self.options.append([_('start all actions'), 0, 0, 'ACT19'])
		self.options.append([_('stop all actions'), _('This action will stop all the triggers except the trigger which has an action "start all actions" defined.'),0, 'ACT20'])

		#init GPIO
		try:
			x=self.conf.get('GPIO', 'sensors')
			if x: self.out_list=eval(x)
			else: self.out_list=[]
			if self.out_list:
				GPIO.setmode(GPIO.BCM)
				GPIO.setwarnings(False)
				for i in self.out_list:
					if i[1] == 'out':
						GPIO.setup(int(i[2]), GPIO.OUT)
						self.options.append(['GPIO '+i[0]+_(': High'),_('ATTENTION! if you set this GPIO output to "High" and there is not a resistor or a circuit connected to the selected GPIO pin, YOU CAN DAMAGE YOUR BOARD.'),0,'H'+i[2]])
						self.options.append(['GPIO '+i[0]+_(': Low'),0,0,'L'+i[2]])
		except Exception,e: print 'ERROR setting GPIO actions: '+str(e)

		#init MQTT
		try:
			x = self.conf.get('MQTT', 'topics')
			if x: self.mqtt_list = eval(x)
			else: self.mqtt_list = []
			if self.mqtt_list:
				for i in self.mqtt_list:
					if i[1] == 0:
						self.options.append([_('Publish on topic: ') + i[0], 0, 1, 'MQTT'+i[0]])
		except Exception,e: print 'ERROR setting MQTT actions: '+str(e)

		self.options.append([_('Set Signal K key value'), 'Write pairs of lines: Signal K key (first line) and a value (second line). Leave a blank line between pairs.', 1, 'ACT22'])

	def getOptionsListIndex(self, data):
		for index, item in enumerate(self.options):
			if item[3] == data: return index

	def run_action(self, option, text):
		conf = self.conf
		if option[0] == 'H':
			channel = int(option[1:])
			GPIO.output(channel, 1)
		elif option[0] == 'L':
			channel = int(option[1:])
			GPIO.output(channel, 0)
		elif option == 'ACT1':
			try:
				wait = float(text)
				time.sleep(wait)
			except Exception,e: print 'ERROR wait action: '+str(e)
		elif option == 'ACT2':
			if text:
				try:
					text = text.split(' ')
					subprocess.Popen(text)
				except Exception,e: print 'ERROR command action: '+str(e)
		elif option == 'ACT3':
			subprocess.Popen(['sudo', 'reboot'])
		elif option == 'ACT4':
			subprocess.Popen(['sudo', 'shutdown', '-h', 'now'])
		elif option == 'ACT5':
			subprocess.Popen(['pkill', '-9', 'kplex'])
		elif option == 'ACT6':
			subprocess.call(['pkill', '-9', 'kplex'])
			subprocess.Popen('kplex')
		elif option == 'ACT7':
			subprocess.Popen(['startup', 'stop'])
		elif option == 'ACT8':
			subprocess.Popen(['startup', 'restart'])
		elif option == 'ACT9':
			subprocess.Popen(['sudo', 'python', self.currentpath +'/wifi_server.py', '0'])
			conf.set('WIFI', 'enable', '0')
		elif option == 'ACT10':
			subprocess.Popen(['sudo', 'python', self.currentpath+'/wifi_server.py', '1'])
			conf.set('WIFI', 'enable', '1')
		#elif option == 'ACT11':
		#elif option == 'ACT12':
		elif option == 'ACT13':
			now = time.strftime("%H:%M:%S")
			tweetStr = now + ' ' + text
			apiKey = conf.get('TWITTER', 'apiKey')
			apiSecret = conf.get('TWITTER', 'apiSecret')
			accessToken = conf.get('TWITTER', 'accessToken')
			accessTokenSecret = conf.get('TWITTER', 'accessTokenSecret')
			if len(tweetStr) > 140: tweetStr = tweetStr[0:140]
			try:
				msg = TwitterBot(apiKey, apiSecret, accessToken, accessTokenSecret)
				msg.send(tweetStr)
			except Exception,e: print 'ERROR Twitter action: '+str(e)
		elif option == 'ACT14':
			subject = text
			body = ''
			for i in self.SK.list_SK:
				body += i[1]+': '+str(i[2])+_('\nsource: ')+i[0]+_('\ntimestamp: ')+i[7]+'\n\n'
			GMAIL_USERNAME = conf.get('GMAIL', 'gmail')
			GMAIL_PASSWORD = conf.get('GMAIL', 'password')
			recipient = conf.get('GMAIL', 'recipient')
			if not body: body = time.strftime("%H:%M:%S") + ' ' + subject
			try:
				msg = GmailBot(GMAIL_USERNAME, GMAIL_PASSWORD, recipient)
				msg.send(subject, body)
			except Exception,e: print 'ERROR gmail action: '+str(e)
		elif option == 'ACT15':
			subprocess.Popen(['mpg123', '-q', text])
		elif option == 'ACT16':
			subprocess.Popen(['pkill', '-9', 'mpg123'])
		elif option == 'ACT17':
			subprocess.Popen(['python', self.currentpath + '/message.py', text, conf.get('GENERAL', 'lang')])
		elif option == 'ACT18':
			subprocess.Popen(['pkill', '-f', 'message.py'])
		elif option == 'ACT19':
			subprocess.Popen(['python', self.currentpath+'/ctrl_actions.py', '1'])
		elif option == 'ACT20':
			subprocess.Popen(['python', self.currentpath + '/ctrl_actions.py', '0'])
		elif option == 'ACT21':
			try:
				sm = gammu.StateMachine()
				sm.ReadConfig()
				sm.Init()
				message = {
					'Text': text,
					'SMSC': {'Location': 1},
					'Number': conf.get('SMS', 'phone'),
				}
				sm.SendSMS(message)
			except Exception,e: print 'ERROR SMS action: '+str(e)
		elif option == 'ACT22':
			pairs_list = text.split('\n\n')
			Erg=''
			if pairs_list:
				for i in pairs_list:
					try:
						pairs = i.split('\n')
						skkey = pairs[0].strip('\n')
						value = pairs[1].strip('\n')
						if re.match('^[0-9a-zA-Z\.]+$', skkey) and value:
							Erg += '{"path": "'+skkey+'","value":"'+str(value)+'"},'
					except Exception,e: print 'ERROR parsing Signal K key action: '+str(e)
				if Erg:		
					SignalK='{"updates":[{"$source":"OPactions","values":['
					SignalK+=Erg[0:-1]+']}]}\n'		
					self.sock.sendto(SignalK, ('127.0.0.1', 55557))
		elif option[:4] == 'MQTT':
			topic = option[4:]
			payload = text
			auth = {'username': conf.get('MQTT', 'username'), 'password': conf.get('MQTT', 'password')}
			publish.single(topic, payload=payload, hostname='127.0.0.1', port='1883', auth=auth)
			publish.single(topic, payload=payload, hostname=conf.get('MQTT', 'broker'), port=conf.get('MQTT', 'port'), auth=auth)
