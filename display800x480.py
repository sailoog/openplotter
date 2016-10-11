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

import subprocess

output = subprocess.check_output(['tvservice', '-d', '/dev/stdout'])
output = output[:128]
editfile = open('edid.dat', 'r', 5000)
bak = editfile.read()
editfile.close()
if output != bak:
	subprocess.check_output(['tvservice', '-d', 'edid.dat'])
output = subprocess.check_output(['edidparser', 'edid.dat'])
if '800x480' in output:
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
					data += 'hdmi_mode=1\n'
					data += 'hdmi_mode=87\n'
					data += 'hdmi_cvt 800 480 60 6 0 0 0\n'				
				data += l+'\n'
		else:
			data += '[EDID=' + output + ']\n'
			data += 'hdmi_group=2\n'
			data += 'hdmi_mode=1\n'
			data += 'hdmi_mode=87\n'
			data += 'hdmi_cvt 800 480 60 6 0 0 0\n'
			data += '[all]\n'
		configfile = open('/boot/config.txt', 'w')
		configfile.write(data)
		configfile.close()
		