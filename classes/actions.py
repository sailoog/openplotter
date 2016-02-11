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
import subprocess, time
from paths import Paths
from classes.twitterbot import TwitterBot
from classes.gmailbot import GmailBot
import RPi.GPIO as GPIO

class Actions():

	def __init__(self):

		self.options=[None]*28
		#ATENTION. If order changes, edit "run_action()" and ctrl_actions.py
		# 0 name, 1 message, 2 field data
		self.options[0]= _('wait'),_('Enter seconds to wait in the field below.'),1
		self.options[1]= _('command'),_('Enter a Linux command and arguments in the field below.'),1
		self.options[2]= _('reset'),0,0
		self.options[3]= _('shutdown'),0,0
		self.options[4]= _('stop NMEA multiplexer'),0,0
		self.options[5]= _('reset NMEA multiplexer'),0,0
		self.options[6]= _('stop Signal K server'),0,0
		self.options[7]= _('reset Signal K server'),0,0
		self.options[8]= _('stop WiFi access point'),_('Be careful, if you are connected by remote you may not be able to reconnect again.'),0
		self.options[9]= _('start WiFi access point'),_('Be sure you have filled in all fields in "WiFi AP" tab and enabled WiFi access point.'),0
		self.options[10]= _('stop SDR-AIS'),0,0
		self.options[11]= _('reset SDR-AIS'),_('Be sure you have filled in Gain and Correction fields in "SDR-AIS" tab and enabled AIS NMEA generation.'),0
		self.options[12]= _('publish Twitter'),_('Be sure you have filled in all fields in "Accounts" tab, selected data to publish and enabled Twitter checkbox.\n\nEnter text to publish in the field below (optional).'),1
		self.options[13]= _('send e-mail'),_('Be sure you have filled in all fields in "Accounts" tab, and enabled Gmail checkbox.\n\nEnter the subject in the field below.'),1
		self.options[14]= _('play sound'),'OpenFileDialog',1
		self.options[15]= _('stop all sounds'),0,0
		self.options[16]= _('show message'),_('Enter the message in the field below.'),1
		self.options[17]= _('close all messages'),0,0
		self.options[18]= _('start all actions'),0,0
		self.options[19]= _('stop all actions'),_('This action will stop all the triggers except the trigger which has an action "start all actions" defined.'),0
		self.options[20]= _('Set Output 1 to High'),_('ATTENTION! if you set this output to "High" and there is not a resistor or a circuit connected to the selected GPIO pin, YOU CAN DAMAGE YOUR BOARD.'),0
		self.options[21]= _('Set Output 1 to Low'),0,0
		self.options[22]= _('Set Output 2 to High'),_('ATTENTION! if you set this output to "High" and there is not a resistor or a circuit connected to the selected GPIO pin, YOU CAN DAMAGE YOUR BOARD.'),0
		self.options[23]= _('Set Output 2 to Low'),0,0
		self.options[24]= _('Set Output 3 to High'),_('ATTENTION! if you set this output to "High" and there is not a resistor or a circuit connected to the selected GPIO pin, YOU CAN DAMAGE YOUR BOARD.'),0
		self.options[25]= _('Set Output 3 to Low'),0,0
		self.options[26]= _('Set Output 4 to High'),_('ATTENTION! if you set this output to "High" and there is not a resistor or a circuit connected to the selected GPIO pin, YOU CAN DAMAGE YOUR BOARD.'),0
		self.options[27]= _('Set Output 4 to Low'),0,0

		self.time_units=[_('no repeat'),_('seconds'), _('minutes'), _('hours'), _('days')]

		paths=Paths()
		self.home=paths.home
		self.currentpath=paths.currentpath

	
	def run_action(self,option,text,conf,a):
		conf.read()
		if option=='0': time.sleep(float(text))
		if option=='1':
			if text:
				text=text.split(' ')
				subprocess.Popen(text)		
		if option=='2': 
			subprocess.Popen(['sudo', 'reboot'])
		if option=='3': 
			subprocess.Popen(['sudo', 'shutdown', '-h', 'now'])
		if option=='4': 
			subprocess.Popen(['pkill', '-9', 'kplex'])
		if option=='5':
			subprocess.call(['pkill', '-9', 'kplex'])
			subprocess.Popen('kplex')
		if option=='6': 
			subprocess.Popen(["pkill", '-9', "node"])
		if option=='7':
			subprocess.call(["pkill", '-9', "node"]) 
			subprocess.Popen(self.home+'/.config/signalk-server-node/bin/nmea-from-10110', cwd=self.home+'/.config/signalk-server-node') 
		if option=='8':
			wlan=conf.get('WIFI', 'device')
			passw2=conf.get('WIFI', 'password')
			ssid2=conf.get('WIFI', 'ssid')
			subprocess.Popen(['sudo', 'python', self.currentpath+'/wifi_server.py', '0', wlan, passw2, ssid2])
			conf.set('WIFI', 'enable', '0')
		if option=='9':
			wlan=conf.get('WIFI', 'device')
			passw2=conf.get('WIFI', 'password')
			ssid2=conf.get('WIFI', 'ssid')
			subprocess.Popen(['sudo', 'python', self.currentpath+'/wifi_server.py', '1', wlan, passw2, ssid2])
			conf.set('WIFI', 'enable', '1')
		if option=='10':
			subprocess.Popen(['pkill', '-9', 'aisdecoder'])
			subprocess.Popen(['pkill', '-9', 'rtl_fm'])
			conf.set('AIS-SDR', 'enable', '0')
		if option=='11':
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
		if option=='12':
			now = time.strftime("%H:%M:%S")
			tweetStr = now+' '+text
			send_data=eval(conf.get('TWITTER', 'send_data'))
			for ii in send_data:
				for index,item in enumerate(a.DataList):
					if ii==item[9]:
						timestamp=item[4]
						if timestamp:
							now=time.time()
							age=now-timestamp
							if age < 20:
								data=''
								value=''
								unit=''
								data=item[1]
								value=item[2]
								unit=item[3]
								if unit: tweetStr+= ' '+data+':'+str(value)+str(unit)
								else: tweetStr+= ' '+data+':'+str(value)+' '
						timestamp=''
			apiKey = conf.get('TWITTER', 'apiKey')
			apiSecret = conf.get('TWITTER', 'apiSecret')
			accessToken = conf.get('TWITTER', 'accessToken')
			accessTokenSecret = conf.get('TWITTER', 'accessTokenSecret')
			if len(tweetStr)>140: tweetStr=tweetStr[0:140]
			try:
				msg=TwitterBot(apiKey,apiSecret,accessToken,accessTokenSecret)
				msg.send(tweetStr)
			except Exception,e: print str(e)
		if option=='13':
			subject = text
			body = ''
			for ii in a.DataList:
				timestamp=ii[4]
				if timestamp:
					now=time.time()
					age=now-timestamp
					if age < 20:
						data=''
						value=''
						unit=''
						data=ii[0]
						value=ii[2]
						unit=ii[3]
						if unit: body += data+': '+str(value)+' '+str(unit)+'\n'
						else: body+= data+': '+str(value)+'\n'
			GMAIL_USERNAME = conf.get('GMAIL', 'gmail')
			GMAIL_PASSWORD = conf.get('GMAIL', 'password')
			recipient = conf.get('GMAIL', 'recipient')
			if not body: body = time.strftime("%H:%M:%S")+' '+subject
			try:
				msg=GmailBot(GMAIL_USERNAME,GMAIL_PASSWORD,recipient)
				msg.send(subject,body)
			except Exception,e: print str(e)
		if option=='14':
			subprocess.Popen(['mpg123',text])
		if option=='15':
			subprocess.Popen(['pkill', '-9', 'mpg123'])
		if option=='16':
			subprocess.Popen(['python', self.currentpath+'/message.py', text, conf.get('GENERAL','lang')])
		if option=='17':
			subprocess.Popen(['pkill', '-f', 'message.py'])
		if option=='18':
			tmp=''
			data=conf.get('ACTIONS', 'triggers')
			triggers=data.split('||')
			triggers.pop()
			for index,item in enumerate(triggers):
				ii=item.split(',')
				triggers[index]=ii
			for index,item in enumerate(triggers):
				tmp +='1,'
				tmp +=triggers[index][1]+','+triggers[index][2]+','+triggers[index][3]+'||'
			conf.set('ACTIONS', 'triggers', tmp)
			return 'read'
		if option=='19':
			subprocess.Popen(['python', self.currentpath+'/ctrl_actions.py', '0'])
		if option=='20':
			if conf.get('OUTPUT1', 'enable')=='1':
				channel=int(conf.get('OUTPUT1', 'gpio'))
				GPIO.output(channel, 1)
		if option=='21':
			if conf.get('OUTPUT1', 'enable')=='1':
				channel=int(conf.get('OUTPUT1', 'gpio'))
				GPIO.output(channel, 0)
		if option=='22':
			if conf.get('OUTPUT2', 'enable')=='1':
				channel=int(conf.get('OUTPUT2', 'gpio'))
				GPIO.output(channel, 1)
		if option=='23':
			if conf.get('OUTPUT2', 'enable')=='1':
				channel=int(conf.get('OUTPUT2', 'gpio'))
				GPIO.output(channel, 0)
		if option=='24':
			if conf.get('OUTPUT3', 'enable')=='1':
				channel=int(conf.get('OUTPUT3', 'gpio'))
				GPIO.output(channel, 1)
		if option=='25':
			if conf.get('OUTPUT3', 'enable')=='1':
				channel=int(conf.get('OUTPUT3', 'gpio'))
				GPIO.output(channel, 0)
		if option=='26':
			if conf.get('OUTPUT4', 'enable')=='1':
				channel=int(conf.get('OUTPUT4', 'gpio'))
				GPIO.output(channel, 1)
		if option=='27':
			if conf.get('OUTPUT4', 'enable')=='1':
				channel=int(conf.get('OUTPUT4', 'gpio'))
				GPIO.output(channel, 0)