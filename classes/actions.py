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

class Actions():

	def __init__(self):

		self.options=[None]*22
		#ATENTION. If order changes, edit "run_action()", "data_message()" and monitoring.py: "send_twitter(), send_gmail()"
		self.options[0]= _('nothing')
		self.options[1]= _('command')
		self.options[2]= _('reset')
		self.options[3]= _('shutdown')
		self.options[4]= _('stop NMEA multiplexer')
		self.options[5]= _('reset NMEA multiplexer')
		self.options[6]= _('stop Signal K server')
		self.options[7]= _('reset Signal K server')
		self.options[8]= _('stop WiFi access point')
		self.options[9]= _('start WiFi access point')
		self.options[10]= _('stop SDR-AIS')
		self.options[11]= _('reset SDR-AIS')
		self.options[12]= _('start Twitter monitoring')
		self.options[13]= _('stop Twitter monitoring')
		self.options[14]= _('publish Twitter')
		self.options[15]= _('start Gmail monitoring')
		self.options[16]= _('stop Gmail monitoring')
		self.options[17]= _('send e-mail')
		self.options[18]= _('play sound')
		self.options[19]= _('stop all sounds')
		self.options[20]= _('show message')
		self.options[21]= _('close all messages')

		self.time_units=[_('no repeat'),_('seconds'), _('minutes'), _('hours'), _('days')]

		paths=Paths()
		self.home=paths.home
		self.currentpath=paths.currentpath

	def data_message(self,action_selected):
		if action_selected==1: return _('Enter Linux command and arguments in the field below.')
		if action_selected==9: return _('Be sure you have filled in all fields in "WiFi AP" tab and enabled WiFi access point.')
		if action_selected==11: return _('Be sure you have filled in Gain and Correction fields in "SDR-AIS" tab and enabled AIS NMEA generation.')
		if action_selected==14 or action_selected==17: return _('Be sure you have filled in all fields in "Monitoring" tab and enabled Twitter or Gmail checkbox.\n\nEnter text to send in the field below.')
		if action_selected==12 or action_selected==15: return _('Be sure you have filled in all fields in "Monitoring" tab and enabled Twitter or Gmail checkbox.')
		if action_selected==18: return 'OpenFileDialog'
		if action_selected==20: return _('Enter the message in the field below.')
	
	def run_action(self,option,text,conf,extra):
		conf.read()
		if option=='0': return
		if option=='1':
			if text:
				text=text.split(' ')
				subprocess.Popen(text)		
		if option=='2': 
			subprocess.Popen(['sudo', 'reboot'])
		if option=='3': 
			subprocess.Popen(['sudo', 'halt'])
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
			conf.set('TWITTER', 'enable', '1')
		if option=='13':
			conf.set('TWITTER', 'enable', '0')
		if option=='14':
			apiKey = conf.get('TWITTER', 'apiKey')
			apiSecret = conf.get('TWITTER', 'apiSecret')
			accessToken = conf.get('TWITTER', 'accessToken')
			accessTokenSecret = conf.get('TWITTER', 'accessTokenSecret')
			now = time.strftime("%H:%M:%S")
			tweetStr=text
			if tweetStr:
				tweetStr = now+' '+tweetStr
				if len(tweetStr)>140: tweetStr=tweetStr[0:140]
				try:
					msg=TwitterBot(apiKey,apiSecret,accessToken,accessTokenSecret)
					msg.send(tweetStr)
				except Exception,e: print str(e)
		if option=='15':
			conf.set('GMAIL', 'enable', '1')
		if option=='16':
			conf.set('GMAIL', 'enable', '0')
		if option=='17':
			GMAIL_USERNAME = conf.get('GMAIL', 'gmail')
			GMAIL_PASSWORD = conf.get('GMAIL', 'password')
			recipient = conf.get('GMAIL', 'recipient')
			subject = text
			body = extra
			if not body: body = time.strftime("%H:%M:%S")+' '+subject
			if subject:
				try:
					msg=GmailBot(GMAIL_USERNAME,GMAIL_PASSWORD,recipient)
					msg.send(subject,body)
				except Exception,e: print str(e)
		if option=='18':
			subprocess.Popen(['mpg123',text])
		if option=='19':
			subprocess.Popen(['pkill', '-9', 'mpg123'])
		if option=='20':
			subprocess.Popen(['python', self.currentpath+'/message.py', text, conf.get('GENERAL','lang')])
		if option=='21':
			subprocess.call(['pkill', '-f', 'message.py'])