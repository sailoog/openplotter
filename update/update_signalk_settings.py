#!/usr/bin/python
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

import sys, json


back_path = sys.argv[1]

try:
	with open(back_path+'/OP-signalk/openplotter-settings.json') as infile:
		old_data = json.load(infile)

	with open('openplotter_tmp/OP-signalk/openplotter-settings.json') as infile:
		new_data = json.load(infile)
except:
	print ''
	print "ERROR UPDATING OLD SIGNAL K SETTINGS"
	print ''
else:
	if 	'vessel' in old_data:
		if 	'uuid' in old_data['vessel']:
			new_data['vessel']['uuid'] = old_data['vessel']['uuid']
		
		for i in old_data['pipedProviders']:
			if i['id'] == 'CAN-USB':
				new_data['pipedProviders'].append(i)
		try:
			with open('openplotter_tmp/OP-signalk/openplotter-settings.json', 'w') as outfile:
				json.dump(new_data, outfile)
		except:
			print ''
			print "ERROR UPDATING OLD SIGNAL K SETTINGS"
			print ''