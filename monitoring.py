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

import ConfigParser, os, sys, gettext, time, socket
from classes.twitterbot import TwitterBot
from classes.gmailbot import GmailBot
from classes.datastream import DataStream

pathname = os.path.dirname(sys.argv[0])
currentpath = os.path.abspath(pathname)

data_conf = ConfigParser.SafeConfigParser()
data_conf.read(currentpath+'/openplotter.conf')

gettext.install('openplotter', currentpath+'/locale', unicode=False)
presLan_en = gettext.translation('openplotter', currentpath+'/locale', languages=['en'])
presLan_ca = gettext.translation('openplotter', currentpath+'/locale', languages=['ca'])
presLan_es = gettext.translation('openplotter', currentpath+'/locale', languages=['es'])
presLan_fr = gettext.translation('openplotter', currentpath+'/locale', languages=['fr'])
language=data_conf.get('GENERAL', 'lang')
if language=='en':presLan_en.install()
if language=='ca':presLan_ca.install()
if language=='es':presLan_es.install()
if language=='fr':presLan_fr.install()

def write_conf():
	with open(currentpath+'/openplotter.conf', 'wb') as configfile:
		data_conf.write(configfile)

def send_twitter(error):
	apiKey = data_conf.get('TWITTER', 'apiKey')
	apiSecret = data_conf.get('TWITTER', 'apiSecret')
	accessToken = data_conf.get('TWITTER', 'accessToken')
	accessTokenSecret = data_conf.get('TWITTER', 'accessTokenSecret')
	tweetStr = ''
	send_data=eval(data_conf.get('TWITTER', 'send_data'))
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
	GMAIL_USERNAME = data_conf.get('GMAIL', 'gmail')
	GMAIL_PASSWORD = data_conf.get('GMAIL', 'password')
	recipient = data_conf.get('GMAIL', 'recipient')
	subject = data_conf.get('GMAIL', 'subject')
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
			
			

	if data_conf.get('GMAIL', 'enable')=='1':
		if data_conf.get('GMAIL', 'periodicity') and data_conf.get('GMAIL', 'periodicity')!='0':
			now= time.time()
			if not data_conf.get('GMAIL', 'last_send'):
				data_conf.read(currentpath+'/openplotter.conf')
				data_conf.set('GMAIL', 'last_send', str(now))
				write_conf()
			last_send = float(data_conf.get('GMAIL', 'last_send')) 
			periodicity = float(data_conf.get('GMAIL', 'periodicity'))*60
			if (now-last_send) > periodicity:
				data_conf.read(currentpath+'/openplotter.conf')
				data_conf.set('GMAIL', 'last_send', str(now))
				write_conf()
				send_gmail(error)

	if data_conf.get('TWITTER', 'enable')=='1':
		if data_conf.get('TWITTER', 'periodicity') and data_conf.get('TWITTER', 'periodicity')!='0':
			now= time.time()
			if not data_conf.get('TWITTER', 'last_send'):
				data_conf.read(currentpath+'/openplotter.conf')
				data_conf.set('TWITTER', 'last_send', str(now))
				write_conf()
			last_send = float(data_conf.get('TWITTER', 'last_send')) 
			periodicity = float(data_conf.get('TWITTER', 'periodicity'))*60
			if (now-last_send) > periodicity:
				data_conf.read(currentpath+'/openplotter.conf')
				data_conf.set('TWITTER', 'last_send', str(now))
				write_conf()
				send_twitter(error)

	if data_conf.get('SWITCH1', 'enable')=='1': a.switches_status(1, data_conf.get('SWITCH1', 'gpio'), data_conf.get('SWITCH1', 'pull_up_down'))
	if data_conf.get('SWITCH2', 'enable')=='1': a.switches_status(2, data_conf.get('SWITCH2', 'gpio'), data_conf.get('SWITCH2', 'pull_up_down'))
	if data_conf.get('SWITCH3', 'enable')=='1': a.switches_status(3, data_conf.get('SWITCH3', 'gpio'), data_conf.get('SWITCH3', 'pull_up_down'))
	if data_conf.get('SWITCH4', 'enable')=='1': a.switches_status(4, data_conf.get('SWITCH4', 'gpio'), data_conf.get('SWITCH4', 'pull_up_down'))



