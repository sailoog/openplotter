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
from paths import Paths


class checkVesselSelf:
	def __init__(self):
		paths = Paths()
		home = paths.home
		file = paths.file
		currentpath = paths.currentpath
		if not self.util_process_exist('signalk-server'):
			print 'Signal K starting'
			if file != '1w_d.py': subprocess.call(['pkill', '-f', '1w_d.py'])
			if file != 'i2c_d.py': subprocess.call(['pkill', '-f', 'i2c_d.py'])
			if file != 'mqtt_d.py': subprocess.call(['pkill', '-f', 'mqtt_d.py'])
			if file != 'SK-base_d.py': subprocess.call(['pkill', '-f', 'SK-base_d.py'])
			if file != 'N2K-server_d.py': subprocess.call(['pkill', '-f', 'N2K-server_d.py'])
			time.sleep(2)
			subprocess.Popen(home + '/.config/signalk-server-node/bin/openplotter',
							 cwd=home + '/.config/signalk-server-node')
			starttime = time.time()
			error = True
			while starttime + 10 > time.time() and error:
				error = False
				time.sleep(0.2)
				try:
					response = requests.get('http://localhost:3000/signalk/v1/api/vessels/self')
				except:
					error = True

			if file != '1w_d.py': 
				time.sleep(1)
				subprocess.Popen(['python', currentpath + '/1w_d.py'])
				time.sleep(1)
			if file != 'mqtt_d.py': 
				subprocess.Popen(['python', currentpath + '/mqtt_d.py'])
				time.sleep(1)
			if file != 'SK-base_d.py': 
				subprocess.Popen(['python', currentpath + '/SK-base_d.py'])
				time.sleep(1)				
			if file != 'i2c_d.py': 
				subprocess.Popen(['python', currentpath + '/i2c_d.py'])
				time.sleep(1)				
			if file != 'N2K-server_d.py': 
				subprocess.Popen(['python', currentpath + '/N2K-server_d.py'])
				time.sleep(1)				

			subprocess.Popen(['keyword'])

		response = requests.get('http://localhost:3000/signalk/v1/api/vessels/self')
		data = response.json()
		self.uuid = data['uuid']
		if 'mmsi' in self.uuid:
			sp = self.uuid.split(':')
			self.mmsi = sp[len(sp) - 1]
		else:
			try:
				self.mmsi = data['mmsi']
			except:
				self.mmsi = '0000'
				print 'Error: No mmsi! mmsi has to be set'

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
