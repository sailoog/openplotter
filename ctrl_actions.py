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

import sys, subprocess, wx
from classes.conf import Conf
from classes.paths import Paths
from classes.language import Language

action=sys.argv[1]

#see actions.py
start_all_actions='18'

paths=Paths()
currentpath=paths.currentpath

conf=Conf()

Language(conf.get('GENERAL','lang'))

data=conf.get('ACTIONS', 'triggers')
triggers=data.split('||')
triggers.pop()
for index,item in enumerate(triggers):
	ii=item.split(',')
	triggers[index]=ii

data=conf.get('ACTIONS', 'actions')
trigger_actions=data.split('||')
trigger_actions.pop()
for index,item in enumerate(trigger_actions):
	ii=item.split(',')
	trigger_actions[index]=ii

tmp=''
#stop all
if action=='0':
	for index,item in enumerate(triggers):
		start_all=False
		for i in trigger_actions:
			if int(i[0])==index and i[1]==start_all_actions: start_all=True
		if start_all==False: tmp +='0,'
		if start_all==True: tmp +='1,'
		tmp +=triggers[index][1]+','+triggers[index][2]+','+triggers[index][3]+'||'
	conf.set('ACTIONS', 'triggers', tmp)
	subprocess.Popen(['pkill', '-f', 'message.py'])
	subprocess.Popen(['pkill', '-9', 'mpg123'])
	
#start all
if action=='1':
	for index,item in enumerate(triggers):
		tmp +='1,'
		tmp +=triggers[index][1]+','+triggers[index][2]+','+triggers[index][3]+'||'
	conf.set('ACTIONS', 'triggers', tmp)

subprocess.call(['pkill', '-f', 'monitoring.py'])
subprocess.Popen(['python',currentpath+'/monitoring.py'])

app = wx.App()

if action=='0':
	wx.MessageBox(_('All actions have been stopped.'), 'Info', wx.OK | wx.ICON_INFORMATION)
if action=='1':
	wx.MessageBox(_('All actions have been started.'), 'Info', wx.OK | wx.ICON_INFORMATION)

sys.exit()