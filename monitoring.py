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

import time, socket
from classes.twitterbot import TwitterBot
from classes.gmailbot import GmailBot
from classes.datastream import DataStream
from classes.conf import Conf
from classes.language import Language

conf=Conf()

Language(conf.get('GENERAL','lang'))

def send_twitter(error):
	apiKey = conf.get('TWITTER', 'apiKey')
	apiSecret = conf.get('TWITTER', 'apiSecret')
	accessToken = conf.get('TWITTER', 'accessToken')
	accessTokenSecret = conf.get('TWITTER', 'accessTokenSecret')
	tweetStr = ''
	send_data=eval(conf.get('TWITTER', 'send_data'))
	for ii in send_data:
		timestamp=eval('a.'+a.DataList[ii]+'[4]')
		if timestamp:
			now=time.time()
			age=now-timestamp
			if age < 20:
				data=''
				value=''
				unit=''
				data=eval('a.'+a.DataList[ii]+'[1]')
				value=eval('a.'+a.DataList[ii]+'[2]')
				unit=eval('a.'+a.DataList[ii]+'[3]')
				if a.DataList[ii]=='Lat': value='%02d %07.4f' % (int(value[:2]), float(value[2:]))
				if a.DataList[ii]=='Lon': value='%02d %07.4f' % (int(value[:3]), float(value[3:]))
				if unit: tweetStr+= data+':'+str(value)+str(unit)+' '
				else: tweetStr+= data+':'+str(value)+' '
	if error !=0 : tweetStr+= error
	if tweetStr:
		if len(tweetStr)>140: tweetStr=tweetStr[0:140]
		try:
			msg=TwitterBot(apiKey,apiSecret,accessToken,accessTokenSecret)
			msg.send(tweetStr)

		except: pass
		#except Exception,e: print str(e)

def send_gmail(error):
	GMAIL_USERNAME = conf.get('GMAIL', 'gmail')
	GMAIL_PASSWORD = conf.get('GMAIL', 'password')
	recipient = conf.get('GMAIL', 'recipient')
	subject = conf.get('GMAIL', 'subject')
	body = ''
	for ii in a.DataList:
		timestamp=eval('a.'+ii+'[4]')
		if timestamp:
			now=time.time()
			age=now-timestamp
			if age < 20:
				data=''
				value=''
				unit=''
				data=eval('a.'+ii+'[0]')
				value=eval('a.'+ii+'[2]')
				unit=eval('a.'+ii+'[3]')
				if ii=='Lat': value='%02d %07.4f' % (int(value[:2]), float(value[2:]))
				if ii=='Lon': value='%02d %07.4f' % (int(value[:3]), float(value[3:]))
				if unit: body += data+': '+str(value)+' '+str(unit)+'\n'
				else: body+= data+': '+str(value)+'\n'
	if error !=0 : body+= error
	if body:
		try:
			msg=GmailBot(GMAIL_USERNAME,GMAIL_PASSWORD,recipient)
			msg.send(subject,body)

		except: pass
		#except Exception,e: print str(e)

def connect():
	global sock_in
	global error
	try:
		sock_in = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock_in.settimeout(10)
		sock_in.connect(('localhost', 10110))
	except socket.error, error_msg:
		error= _('Failed to connect with localhost:10110. Error: ')+ str(error_msg[0])
		sock_in=''
		time.sleep(7)
	else: error=0



global sock_in
global error
global a
sock_in=''
a=DataStream()
error=0

while True:

	if not sock_in: connect()
	else:
		frase_nmea =''
		try:
			frase_nmea = sock_in.recv(1024)
		except socket.error, error_msg:
			error= _('Failed to connect with localhost:10110. Error: ')+ str(error_msg[0])
		else:
			if frase_nmea: 
				a.parse_nmea(frase_nmea)
				error=0
			else:
				error=_('No data, trying to reconnect...')
				sock_in=''
				time.sleep(7)
			
			

	if conf.get('GMAIL', 'enable')=='1':
		if conf.get('GMAIL', 'periodicity') and conf.get('GMAIL', 'periodicity')!='0':
			now= time.time()
			if not conf.get('GMAIL', 'last_send'):
				conf.set('GMAIL', 'last_send', str(now))
			last_send = float(conf.get('GMAIL', 'last_send')) 
			periodicity = float(conf.get('GMAIL', 'periodicity'))*60
			if (now-last_send) > periodicity:
				conf.set('GMAIL', 'last_send', str(now))
				send_gmail(error)

	if conf.get('TWITTER', 'enable')=='1':
		if conf.get('TWITTER', 'periodicity') and conf.get('TWITTER', 'periodicity')!='0':
			now= time.time()
			if not conf.get('TWITTER', 'last_send'):
				conf.set('TWITTER', 'last_send', str(now))
			last_send = float(conf.get('TWITTER', 'last_send')) 
			periodicity = float(conf.get('TWITTER', 'periodicity'))*60
			if (now-last_send) > periodicity:
				conf.set('TWITTER', 'last_send', str(now))
				send_twitter(error)

	if conf.get('SWITCH1', 'enable')=='1': a.switches_status(1, conf.get('SWITCH1', 'gpio'), conf.get('SWITCH1', 'pull_up_down'))
	if conf.get('SWITCH2', 'enable')=='1': a.switches_status(2, conf.get('SWITCH2', 'gpio'), conf.get('SWITCH2', 'pull_up_down'))
	if conf.get('SWITCH3', 'enable')=='1': a.switches_status(3, conf.get('SWITCH3', 'gpio'), conf.get('SWITCH3', 'pull_up_down'))
	if conf.get('SWITCH4', 'enable')=='1': a.switches_status(4, conf.get('SWITCH4', 'gpio'), conf.get('SWITCH4', 'pull_up_down'))



