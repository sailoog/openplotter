#!/usr/bin/env python

# This file is part of Openplotter.
# Copyright (C) 2015 by sailoog <https://github.com/sailoog/openplotter>
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

import subprocess, platform

if platform.machine()[0:3]!='arm':
	print 'this is not a raspberry pi -> no RPI display settings'
else:
	output = subprocess.check_output(['tvservice', '-d', '/dev/stdout'])
	output = output[:128]
	try:
		editfile = open('edid.dat', 'r', 5000)
		bak = editfile.read()
		editfile.close()
	except:
		bak = ''

	if output != bak:
		subprocess.check_output(['tvservice', '-d', 'edid.dat'])
	output = subprocess.check_output(['edidparser', 'edid.dat'])

	DisplayResolution = ''

	if '800x480' in output:
		DisplayResolution = '800 480'
		#DisplayResolution = '1024 600'
		#DisplayResolution = '1120 630'	
	elif '1024:600' in output:
		DisplayResolution = '1024 600'
	elif '1280:800' in output:
		DisplayResolution = '1280 800'

	if DisplayResolution != '':
		configfile = open('/boot/config.txt', 'r', 5000)
		data = configfile.read()
		configfile.close()
		output = subprocess.check_output(['tvservice', '-n'])
		output = output[12:-1]
		if ('[EDID=' + output) in data: pass
		else:
			if '[all]' in data: 
				line = data.split('\n')
				data = ''
				for l in line:
					if '[all]' in l:
						data += '[EDID=' + output + ']\n'
						data += 'hdmi_group=2\n'
						data += 'hdmi_mode=87\n'
						data += 'hdmi_cvt='+ DisplayResolution +' 60 6 0 0 0\n'
					data += l+'\n'
			else:
				data += '[EDID=' + output + ']\n'
				data += 'hdmi_group=2\n'
				data += 'hdmi_mode=87\n'
				data += 'hdmi_cvt='+ DisplayResolution +' 60 6 0 0 0\n'
				data += '[all]\n'
			configfile = open('/boot/config.txt', 'w')
			configfile.write(data)
			configfile.close()
