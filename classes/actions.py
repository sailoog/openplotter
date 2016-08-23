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
import subprocess, time, gammu, platform
from paths import Paths
from classes.twitterbot import TwitterBot
from classes.gmailbot import GmailBot
import paho.mqtt.publish as publish
if platform.machine()[0:3]=='arm':
	import RPi.GPIO as GPIO
else:
	import emulator.GPIO as GPIO

class Actions():

	def __init__(self,conf):
		self.conf=conf
		self.options=[]
		#ATENTION. If order changes, edit "run_action()" and ctrl_actions.py
		# 0 name, 1 message, 2 field data, 3 unique ID
		self.options.append([_('wait'),_('Enter seconds to wait in the field below.'),1,'ACT1'])
		self.options.append([_('command'),_('Enter a Linux command and arguments in the field below.'),1,'ACT2'])
		self.options.append([_('reset'),0,0,'ACT3'])
		self.options.append([_('shutdown'),0,0,'ACT4'])
		self.options.append([_('stop NMEA multiplexer'),0,0,'ACT5'])
		self.options.append([_('reset NMEA multiplexer'),0,0,'ACT6'])
		self.options.append([_('stop Signal K server'),0,0,'ACT7'])
		self.options.append([_('reset Signal K server'),0,0,'ACT8'])
		self.options.append([_('stop WiFi access point'),_('Be careful, if you are connected by remote you may not be able to reconnect again.'),0,'ACT9'])
		self.options.append([_('start WiFi access point'),_('Be sure you have filled in all fields in "WiFi AP" tab and enabled WiFi access point.'),0,'ACT10'])
		self.options.append([_('stop SDR-AIS'),0,0,'ACT11'])
		self.options.append([_('reset SDR-AIS'),_('Be sure you have filled in Gain and Correction fields in "SDR-AIS" tab and enabled AIS NMEA generation.'),0,'ACT12'])
		self.options.append([_('publish Twitter'),_('Be sure you have filled in all fields in "Accounts" tab, and enabled Twitter checkbox.\n\nEnter text to publish in the field below.'),1,'ACT13'])
		self.options.append([_('send e-mail'),_('Be sure you have filled in all fields in "Accounts" tab, and enabled Gmail checkbox.\n\nEnter the subject in the field below.'),1,'ACT14'])
		self.options.append([_('send SMS'),_('Be sure you have enabled sending SMS in "SMS" tab.\n\nEnter the text in the field below.'),1,'ACT21'])		
		self.options.append([_('play sound'),'OpenFileDialog',1,'ACT15'])
		self.options.append([_('stop all sounds'),0,0,'ACT16'])
		self.options.append([_('show message'),_('Enter the message in the field below.'),1,'ACT17'])
		self.options.append([_('close all messages'),0,0,'ACT18'])
		self.options.append([_('start all actions'),0,0,'ACT19'])
		self.options.append([_('stop all actions'),_('This action will stop all the triggers except the trigger which has an action "start all actions" defined.'),0,'ACT20'])

		#Outputs
		#x=conf.get('OUTPUTS', 'outputs')
		#if x: self.out_list=eval(x)
		#else: self.out_list=[]
		#for i in self.out_list:
		#	try:
		#		if i[0]=='1':
		#			self.options.append([i[1]+_(': High'),_('ATTENTION! if you set this output to "High" and there is not a resistor or a circuit connected to the selected GPIO pin, YOU CAN DAMAGE YOUR BOARD.'),0,'H'+i[4]])
		#			self.options.append([i[1]+_(': Low'),0,0,'L'+i[4]])
		#	except Exception,e: print str(e)

		#mqtt
		x=conf.get('MQTT', 'topics')
		if x: self.mqtt_list=eval(x)
		else: self.mqtt_list=[]
		for i in self.mqtt_list:
			try:
				self.options.append([_('Publish on topic ')+i[1],0,1,i[2]])
			except Exception,e: print str(e)

		self.time_units=[_('no repeat'),_('seconds'), _('minutes'), _('hours'), _('days')]

		paths=Paths()
		self.home=paths.home
		self.currentpath=paths.currentpath

	def getOptionsListIndex(self, data):
		for index, item in enumerate(self.options):
			if item[3]==data: return index

	def getoutlistIndex(self, data):
		for index, item in enumerate(self.out_list):
			if item[4]==data: return index

	def getmqttlistIndex(self, data):
		for index, item in enumerate(self.mqtt_list):
			if item[2]==data: return index

	def run_action(self,option,text):
		conf=self.conf
		conf.read()
		if option=='ACT1': 
			try:
				wait=float(text)
			except: wait=1.0
			time.sleep(wait)
		if option=='ACT2':
			if text:
				try:
					text=text.split(' ')
					subprocess.Popen(text)
				except Exception,e: print str(e)	
		if option=='ACT3': 
			subprocess.Popen(['sudo', 'reboot'])
		if option=='ACT4': 
			subprocess.Popen(['sudo', 'shutdown', '-h', 'now'])
		if option=='ACT5': 
			subprocess.Popen(['pkill', '-9', 'kplex'])
		if option=='ACT6':
			subprocess.call(['pkill', '-9', 'kplex'])
			subprocess.Popen('kplex')
		if option=='ACT7': 
			subprocess.Popen(["pkill", '-9', "node"])
		if option=='ACT8':
			subprocess.call(["pkill", '-9', "node"]) 
			subprocess.Popen(self.home+'/.config/signalk-server-node/bin/openplotter', cwd=self.home+'/.config/signalk-server-node') 
		if option=='ACT9':
			wlan=conf.get('WIFI', 'device')
			passw2=conf.get('WIFI', 'password')
			ssid2=conf.get('WIFI', 'ssid')
			subprocess.Popen(['sudo', 'python', self.currentpath+'/wifi_server.py', '0', wlan, passw2, ssid2])
			conf.set('WIFI', 'enable', '0')
		if option=='ACT10':
			wlan=conf.get('WIFI', 'device')
			passw2=conf.get('WIFI', 'password')
			ssid2=conf.get('WIFI', 'ssid')
			subprocess.Popen(['sudo', 'python', self.currentpath+'/wifi_server.py', '1', wlan, passw2, ssid2])
			conf.set('WIFI', 'enable', '1')
		if option=='ACT11':
			subprocess.Popen(['pkill', '-9', 'aisdecoder'])
			subprocess.Popen(['pkill', '-9', 'rtl_fm'])
			conf.set('AIS-SDR', 'enable', '0')
		if option=='ACT12':
			gain=conf.get('AIS-SDR', 'gain')
			ppm=conf.get('AIS-SDR', 'ppm')
			channel=conf.get('AIS-SDR', 'channel')
			subprocess.call(['pkill', '-9', 'aisdecoder'])
			subprocess.call(['pkill', '-9', 'rtl_fm'])
			frecuency='161975000'
			if channel=='b': frecuency='162025000'
			rtl_fm=subprocess.Popen(['rtl_fm', '-f', frecuency, '-g', gain, '-p', ppm, '-s', '48k'], stdout = subprocess.PIPE)
			aisdecoder=subprocess.Popen(['aisdecoder', '-h', '127.0.0.1', '-p', '10110', '-a', 'file', '-c', 'mono', '-d', '-f', '/dev/stdin'], stdin = rtl_fm.stdout)
			conf.set('AIS-SDR', 'enable', '1')
		if option=='ACT13':
			now = time.strftime("%H:%M:%S")
			tweetStr = now+' '+text
			apiKey = conf.get('TWITTER', 'apiKey')
			apiSecret = conf.get('TWITTER', 'apiSecret')
			accessToken = conf.get('TWITTER', 'accessToken')
			accessTokenSecret = conf.get('TWITTER', 'accessTokenSecret')
			if len(tweetStr)>140: tweetStr=tweetStr[0:140]
			try:
				msg=TwitterBot(apiKey,apiSecret,accessToken,accessTokenSecret)
				msg.send(tweetStr)
			except Exception,e: print str(e)
		if option=='ACT14':
			subject = text
			body = ''
			GMAIL_USERNAME = conf.get('GMAIL', 'gmail')
			GMAIL_PASSWORD = conf.get('GMAIL', 'password')
			recipient = conf.get('GMAIL', 'recipient')
			if not body: body = time.strftime("%H:%M:%S")+' '+subject
			try:
				msg=GmailBot(GMAIL_USERNAME,GMAIL_PASSWORD,recipient)
				msg.send(subject,body)
			except Exception,e: print str(e)
		if option=='ACT15':
			subprocess.Popen(['mpg123',text])
		if option=='ACT16':
			subprocess.Popen(['pkill', '-9', 'mpg123'])
		if option=='ACT17':
			subprocess.Popen(['python', self.currentpath+'/message.py', text, conf.get('GENERAL','lang')])
		if option=='ACT18':
			subprocess.Popen(['pkill', '-f', 'message.py'])
		if option=='ACT19':
			return 'read'
		if option=='ACT20':
			subprocess.Popen(['python', self.currentpath+'/ctrl_actions.py', '0'])
		if option[:4]=='HOUT':
				channel=self.out_list[self.getoutlistIndex(option[1:])][3]
				GPIO.output(channel, 1)
		if option[:4]=='LOUT':
				channel=self.out_list[self.getoutlistIndex(option[1:])][3]
				GPIO.output(channel, 0)
		if option=='ACT21':
			try:
				sm = gammu.StateMachine()
				sm.ReadConfig()
				sm.Init()
				message = {
					'Text': text, 
					'SMSC': {'Location': 1},
					'Number': conf.get('SMS','phone'),
				}
				sm.SendSMS(message)
			except Exception,e: print str(e)
		if option[:4]=='MQTT':
			topic=self.mqtt_list[self.getmqttlistIndex(option)][1]
			payload= text
			auth = {'username':conf.get('MQTT','username'), 'password':conf.get('MQTT','password')}
			publish.single(topic, payload=payload, hostname='127.0.0.1', port='1883', auth=auth)
			publish.single(topic, payload=payload, hostname=conf.get('MQTT','broker'), port=conf.get('MQTT','port'), auth=auth)
			