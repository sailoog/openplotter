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
import os
import requests
import subprocess
import time
import json

class checkVesselSelf:
	def __init__(self, conf):

		home = conf.home
		currentpath = home+conf.get('GENERAL', 'op_folder')+'/openplotter'

		if not self.util_process_exist('signalk-server'):
			print 'Signal K starting'
			subprocess.call(['pkill', '-f', 'SK-base_d.py'])
			time.sleep(1)
			subprocess.Popen(['bin/signalk-server','-s','../../.openplotter/openplotter-settings.json'],cwd=home + '/.config/signalk-server-node')							 
			starttime = time.time()
			error = True
			while starttime + 10 > time.time() and error:
				error = False
				time.sleep(0.2)
				try:
					response = requests.get('http://localhost:3000/signalk/v1/api/vessels/self')
				except:
					error = True
			subprocess.Popen(['python', currentpath + '/SK-base_d.py'])
			time.sleep(1)									
		try:
			with open(home+'/.openplotter/openplotter-settings.json') as data_file:
				data = json.load(data_file)
		except:
			data = []
			print "Error: Can't open file "+home+"/.openplotter/openplotter-settings.json"

		raw_uuid = data['vessel']['uuid']
		self.mmsi = raw_uuid.split(':')[-1]
		self.uuid = 'urn:mrn:imo:mmsi:'+self.mmsi


	def util_process_exist(self, process_name):
		pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]
		exist = False
		for pid in pids:
			try:
				if process_name in open(os.path.join('/proc', pid, 'cmdline'), 'rb').read():
					exist = True
			except IOError:  # proc has already terminated
				continue
		return exist
