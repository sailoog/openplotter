#!/usr/bin/env python

# This file is part of Openplotter.
# Copyright (C) 2018 by sailoog <https://github.com/sailoog/openplotter>
# 					  e-sailing <https://github.com/e-sailing/openplotter>
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
import ConfigParser, os, yaml, json, subprocess
from conf import Conf


class SK_settings:
	def __init__(self):

		self.conf = Conf()
		self.home = self.conf.home
		
		self.setting_file = self.home+'/.signalk/settings.json'
		self.load()
		
	def load(self):
		
		if os.path.isfile(self.setting_file):
			with open(self.setting_file) as data_file:
				self.data = yaml.load(data_file)
		else: self.data = {}

		self.sslport = -1
		if 'sslport' in self.data: self.sslport = self.data['sslport']
		self.port = -1
		if 'port' in self.data: self.port = self.data['port']
		self.ssl = -1
		if 'ssl' in self.data: self.ssl = self.data['ssl']
		
		self.http = 'http://'
		self.ws = 'ws://'
		self.aktport = self.port
		if self.ssl:
			self.http = 'https://'
			self.ws = 'wss://'
			self.aktport = self.sslport
			
		self.ip = '10.10.10.1'
		
		if self.conf.has_section('WIFI'):
			if self.conf.has_option('WIFI', 'ip'):
				self.ip = self.conf.get('WIFI', 'ip')
				
		self.http_address = self.http+self.ip+':'+str(self.aktport)
		
		#check defaults
		write = False
		OPcan = False
		OPpypilot = False
		OPkplex = False
		OPwifi = False
		OPserial = False
		OPnotifications = False
		OPsensors = False
		if 'pipedProviders' in self.data:
			try:
				for i in self.data['pipedProviders']:
					if i['id'] == 'OPcan': OPcan = True
					elif i['id'] == 'OPpypilot': 
						OPpypilot = True
						if not i['enabled']: 
							i['enabled'] = True
							write = True
					elif i['id'] == 'OPkplex': 
						OPkplex = True
						if not i['enabled']: 
							i['enabled'] = True
							write = True
					elif i['id'] == 'OPwifi': 
						OPwifi = True
						if not i['enabled']: 
							i['enabled'] = True
							write = True
					elif i['id'] == 'OPserial': 
						OPserial = True
						if not i['enabled']: 
							i['enabled'] = True
							write = True
					elif i['id'] == 'OPnotifications': 
						OPnotifications = True
						if not i['enabled']: 
							i['enabled'] = True
							write = True
					elif i['id'] == 'OPsensors': 
						OPsensors = True
						if not i['enabled']: 
							i['enabled'] = True
							write = True
			except:
				print 'Error parsing setting.json'

		if not OPcan: self.data['pipedProviders'].append({'pipeElements': [{'type': 'providers/simple', 'options': {'logging': False, 'type': 'NMEA2000', 'subOptions': {'device': '/dev/ttyOP_', 'type': 'ngt-1'}}}], 'enabled': False, 'id': 'OPcan'})
		if not OPpypilot: self.data['pipedProviders'].append({'pipeElements': [{'type': 'providers/simple', 'options': {'logging': False, 'type': 'NMEA0183', 'subOptions': {'host': 'localhost', 'type': 'tcp', 'port': '20220'}}}], 'enabled': True, 'id': 'OPpypilot'})
		if not OPkplex: self.data['pipedProviders'].append({'pipeElements': [{'type': 'providers/simple', 'options': {'logging': False, 'type': 'NMEA0183', 'subOptions': {'host': 'localhost', 'type': 'tcp', 'port': '30330'}}}], 'enabled': True, 'id': 'OPkplex'})
		if not OPwifi: self.data['pipedProviders'].append({'pipeElements': [{'type': 'providers/simple', 'options': {'logging': False, 'type': 'SignalK', 'subOptions': {'type': 'udp', 'port': '55561'}}}], 'enabled': True, 'id': 'OPwifi'})
		if not OPserial: self.data['pipedProviders'].append({'pipeElements': [{'type': 'providers/simple', 'options': {'logging': False, 'type': 'SignalK', 'subOptions': {'type': 'udp', 'port': '55559'}}}], 'enabled': True, 'id': 'OPserial'})
		if not OPnotifications: self.data['pipedProviders'].append({'pipeElements': [{'type': 'providers/simple', 'options': {'logging': False, 'type': 'SignalK', 'subOptions': {'type': 'udp', 'port': '55558'}}}], 'enabled': True, 'id': 'OPnotifications'})
		if not OPsensors: self.data['pipedProviders'].append({'pipeElements': [{'type': 'providers/simple', 'options': {'logging': False, 'type': 'SignalK', 'subOptions': {'type': 'udp', 'port': '55557'}}}], 'enabled': True, 'id': 'OPsensors'})

		#check can devices
		self.ngt1=''
		self.ngt1_enabled=-1
		self.ngt1_device=''
		self.canbus=''
		self.canbus_enabled=-1
		self.canbus_interface=''
		count = 0
		if 'pipedProviders' in self.data:
			try:
				for i in self.data['pipedProviders']:
					if i['pipeElements'][0]['options']['subOptions']['type'] == 'ngt-1':
						self.ngt1_enabled=i['enabled']
						self.ngt1=count
						self.ngt1_device=i['pipeElements'][0]['options']['subOptions']['device']
					elif i['pipeElements'][0]['options']['subOptions']['type'] == 'canbus':
						self.canbus_enabled=i['enabled']
						self.canbus=count
						self.canbus_interface=i['pipeElements'][0]['options']['subOptions']['interface']
					count+=1
			except:
				print 'Error parsing setting.json'

		if write or not OPcan or not OPpypilot or not OPkplex or not OPwifi or not OPserial or not OPnotifications or not OPsensors: self.write_settings()
				
	def set_ngt1_device(self,device):
		if self.ngt1_enabled != -1:
			self.data['pipedProviders'][self.ngt1]['pipeElements'][0]['options']['subOptions']['device'] = device
			self.write_settings()

	def set_ngt1_enable(self,enable):
		if self.ngt1_enabled != -1:
			if enable == 1:
				self.data['pipedProviders'][self.ngt1]['enabled']=True
			elif enable == 0:
				self.data['pipedProviders'][self.ngt1]['enabled']=False
			self.write_settings()

	def set_canbus_enable(self,enable):
		if self.canbus_enabled != -1:
			if enable == 1:
				self.data['pipedProviders'][self.canbus]['enabled']=True
			elif enable == 0:
				self.data['pipedProviders'][self.canbus]['enabled']=False
			self.write_settings()
			
	def write_settings(self):
		data = json.dumps(self.data, indent=4, sort_keys=True)
		try:
			wififile = open(self.setting_file, 'w')
			wififile.write(data)
			wififile.close()
			# stopping sk server
			subprocess.call(['sudo', 'systemctl', 'stop', 'signalk.service'])
			subprocess.call(['sudo', 'systemctl', 'stop', 'signalk.socket'])
			# restarting sk server
			subprocess.call(['sudo', 'systemctl', 'start', 'signalk.socket'])
			subprocess.call(['sudo', 'systemctl', 'start', 'signalk.service'])
			self.load()
		except:
			print 'Error saving setting.json'

					
					
		
