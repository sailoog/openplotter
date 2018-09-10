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

import socket
from classes.language import Language

class Actions:
	def __init__(self, SK):
		self.SK = SK
		self.conf = SK.conf
		Language(self.conf)
		self.home = SK.home
		self.currentpath = SK.currentpath
		self.time_units = [_('no repeat'), _('seconds'), _('minutes'), _('hours'), _('days')]
		self.operators_list = [_('was not updated in the last (sec.)'), _('was updated in the last (sec.)'), '=',
							   '<', '<=', '>', '>=', _('contains')]		
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
				#GPIO.setmode(GPIO.BCM)
				#GPIO.setwarnings(False)
				for i in self.out_list:
					if i[1] == 'out':
						#GPIO.setup(int(i[2]), GPIO.OUT)
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
						self.options.append([_('Publish on topic: ').decode('utf8') + i[0], 0, 1, 'MQTT'+i[0]])
		except Exception,e: print 'ERROR setting MQTT actions: '+str(e)

		self.options.append([_('Set Signal K key value'), 'Write pairs of lines: Signal K key (first line) and a value (second line). Leave a blank line between pairs.', 1, 'ACT22'])

	def getOptionsListIndex(self, data):
		for index, item in enumerate(self.options):
			if item[3] == data: return index
