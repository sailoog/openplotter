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
from twitterbot import TwitterBot
from gmailbot import GmailBot
from paths import Paths
from conf import Conf
from language import Language

class Actions():

	def __init__(self):

		paths=Paths()
		self.home=paths.home
		self.currentpath=paths.currentpath

		self.conf=Conf()

		Language(self.conf.get('GENERAL','lang'))

		self.options=[None]*18

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


	def execute(self,on_off,switch,option):
		if option=='0': return
		if option=='1':
			command=self.conf.get('SWITCH'+switch, on_off+'_command')
			if command:
				command=command.split(' ')
				subprocess.Popen(command)		
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
			subprocess.Popen(home+'/.config/signalk-server-node/bin/nmea-from-10110', cwd=self.home+'/.config/signalk-server-node') 
		if option=='8':
			wlan=self.conf.get('WIFI', 'device')
			passw2=self.conf.get('WIFI', 'password')
			ssid2=self.conf.get('WIFI', 'ssid')
			subprocess.Popen(['sudo', 'python', self.currentpath+'/wifi_server.py', '0', wlan, passw2, ssid2])
			self.conf.set('WIFI', 'enable', '0')
		if option=='9':
			wlan=self.conf.get('WIFI', 'device')
			passw2=self.conf.get('WIFI', 'password')
			ssid2=self.conf.get('WIFI', 'ssid')
			subprocess.Popen(['sudo', 'python', self.currentpath+'/wifi_server.py', '1', wlan, passw2, ssid2])
			self.conf.set('WIFI', 'enable', '1')
		if option=='10':
			subprocess.Popen(['pkill', '-9', 'aisdecoder'])
			subprocess.Popen(['pkill', '-9', 'rtl_fm'])
			self.conf.set('AIS-SDR', 'enable', '0')
		if option=='11':
			gain=self.conf.get('AIS-SDR', 'gain')
			ppm=self.conf.get('AIS-SDR', 'ppm')
			channel=self.conf.get('AIS-SDR', 'channel')
			subprocess.call(['pkill', '-9', 'aisdecoder'])
			subprocess.call(['pkill', '-9', 'rtl_fm'])
			frecuency='161975000'
			if channel=='b': frecuency='162025000'
			rtl_fm=subprocess.Popen(['rtl_fm', '-f', frecuency, '-g', gain, '-p', ppm, '-s', '48k'], stdout = subprocess.PIPE)
			aisdecoder=subprocess.Popen(['aisdecoder', '-h', '127.0.0.1', '-p', '10110', '-a', 'file', '-c', 'mono', '-d', '-f', '/dev/stdin'], stdin = rtl_fm.stdout)
			self.conf.set('AIS-SDR', 'enable', '1')
		if option=='12':
			subprocess.call(['sudo','pkill', '-f', 'monitoring.py'])
			self.conf.set('TWITTER', 'enable', '1')
			subprocess.Popen(['sudo','python', self.currentpath+'/monitoring.py'])
		if option=='13':
			subprocess.call(['sudo','pkill', '-f', 'monitoring.py'])
			self.conf.set('TWITTER', 'enable', '0')
			if self.conf.get('GMAIL', 'enable')=='1':
				subprocess.Popen(['sudo','python', self.currentpath+'/monitoring.py'])
		if option=='14':
			apiKey = self.conf.get('TWITTER', 'apiKey')
			apiSecret = self.conf.get('TWITTER', 'apiSecret')
			accessToken = self.conf.get('TWITTER', 'accessToken')
			accessTokenSecret = self.conf.get('TWITTER', 'accessTokenSecret')
			now = time.strftime("%H:%M:%S")
			tweetStr=self.conf.get('SWITCH'+switch, on_off+'_command')
			if tweetStr:
				tweetStr = now+' '+tweetStr
				if len(tweetStr)>140: tweetStr=tweetStr[0:140]
				try:
					msg=TwitterBot(apiKey,apiSecret,accessToken,accessTokenSecret)
					msg.send(tweetStr)
				except: pass
		if option=='15':
			subprocess.call(['sudo','pkill', '-f', 'monitoring.py'])
			self.conf.set('GMAIL', 'enable', '1')
			subprocess.Popen(['sudo','python', self.currentpath+'/monitoring.py'])
		if option=='16':
			subprocess.call(['sudo','pkill', '-f', 'monitoring.py'])
			self.conf.set('GMAIL', 'enable', '0')
			if self.conf.get('TWITTER', 'enable')=='1':
				subprocess.Popen(['sudo','python', self.currentpath+'/monitoring.py'])
		if option=='17':
			GMAIL_USERNAME = self.conf.get('GMAIL', 'gmail')
			GMAIL_PASSWORD = self.conf.get('GMAIL', 'password')
			recipient = self.conf.get('GMAIL', 'recipient')
			subject=self.conf.get('SWITCH'+switch, on_off+'_command')
			body = time.strftime("%H:%M:%S")+' '+subject
			if subject:
				try:
					msg=GmailBot(GMAIL_USERNAME,GMAIL_PASSWORD,recipient)
					msg.send(subject,body)
				except: pass

