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
import json
from conf import Conf

class GetKeys:
	def __init__(self):
		conf = Conf()
		home = conf.home
		keys = []
		with open(home +'/.config/signalk-server-node/node_modules/signalk-schema/keyswithmetadata.json') as data_file:
			data = json.load(data_file)
		for i in data:
			if '/vessels/*/' in i:
				key = i.replace('/vessels/*/','')
				key = key.replace('RegExp','*')
				key = key.replace('/','.')
				if data[i].has_key('description'): description = data[i]['description']
				else: description = '[missing]'
				if data[i].has_key('units'): units = data[i]['units']
				else: units = ''
				keys.append([key,description,units])
		list_tmp = []
		groups = [_('ungrouped')]
		ungrouped = []
		for i in keys:
			items=i[0].split('.')
			if not items[0] in list_tmp: 
				list_tmp.append(items[0])
			else:
				if not items[0] in groups: 
					groups.append(items[0])
		for i in list_tmp:
			if not i in groups: ungrouped.append(i)
		
		self.keys = sorted(keys)
		self.groups = sorted(groups)
		self.ungrouped = sorted(ungrouped)