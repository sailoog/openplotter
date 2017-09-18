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
from classes.language import Language

action=sys.argv[1]

#see actions.py
start_all_actions='ACT19'

conf = Conf()
currentpath = conf.home+conf.get('GENERAL', 'op_folder')+'/openplotter'

Language(conf)

triggers=[]
data=conf.get('ACTIONS', 'triggers')
try:
	triggers=eval(data)
except:triggers=[]

#stop all
if action=='0':
	i=0
	for ii in triggers:
		templist=ii[4]
		start=0
		for iii in templist:
			if iii[0]==start_all_actions: 
				start=1
		triggers[i][0]=start
		i=i+1
	conf.set('ACTIONS', 'triggers', str(triggers))
	subprocess.call(['pkill', '-f', 'SK-base_d.py'])
	subprocess.Popen(['pkill', '-9', 'mpg123'])
	subprocess.Popen(['python', currentpath + '/SK-base_d.py'])

#start all
if action=='1':
	i=0
	for ii in triggers:
		triggers[i][0]=1
		i=i+1
	conf.set('ACTIONS', 'triggers', str(triggers))
	subprocess.call(['pkill', '-f', 'SK-base_d.py'])
	subprocess.Popen(['python', currentpath + '/SK-base_d.py'])

app = wx.App()

if action=='0':
	wx.MessageBox(_('All actions have been stopped.'), 'Info', wx.OK | wx.ICON_INFORMATION)
if action=='1':
	wx.MessageBox(_('All actions have been started.'), 'Info', wx.OK | wx.ICON_INFORMATION)

sys.exit()