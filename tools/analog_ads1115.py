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

import socket, time, RTIMU, math, csv, datetime, json, subprocess, sys
from classes.paths import Paths
from classes.ads1115 import Ads1115
from classes.conf_analog import Conf_analog

paths=Paths()
currentpath=paths.currentpath
home=paths.home

if len(sys.argv)>1:
	if sys.argv[1]=='settings':
		subprocess.Popen(['leafpad',currentpath+'/openplotter_analog.conf'])
	exit
else:

	conf_analog=Conf_analog()
	ads1115=Ads1115()

	a_index = [0,1,2,3]
	a_value =[0.0,0.0,0.0,0.0]
	index=0
	active=['0','0','0','0']
	SK_name=['0','0','0','0']

	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	poll_interval = 1
	rate_analog = 1
	ADS1115='ADS1115_'

	for i in a_index:
		active[i] = conf_analog.get(ADS1115+str(i), 'active')=='1'

		if active[i]:
			if 0==conf_analog.has_option(ADS1115+str(i), 'sk_name'):
				conf_analog.set(ADS1115+str(i), 'sk_name','0')

			SK_name[i] = conf_analog.get(ADS1115+str(i), 'sk_name')

	with open('/home/pi/.config/signalk-server-node/settings/openplotter-settings.json') as data_file:
		data = json.load(data_file)
	uuid=data['vessel']['uuid']

	tick_analog=time.time()

	while True:
		tick2=time.time()
		time.sleep(poll_interval*1.0/1000.0)
		#GENERATE	

		if tick2-tick_analog > rate_analog:
			tick_analog=time.time()

			list_signalk_path1=[]
			list_signalk1=[]

			for i in a_index:
				if active[i]:	
					list_signalk_path1.append(SK_name[i])
					list_signalk1.append(str(a_value[i]))			

			if list_signalk1:
				SignalK = '{"updates": [{"source": {"type": "I2C","src" : "ANA"},"timestamp": "'+str( datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f') )[0:23]+'Z","values":[ '
				Erg=''
				for i in range(0,len(list_signalk1)):
					Erg += '{"path": "'+list_signalk_path1[i]+'","value":'+list_signalk1[i]+'},'
				SignalK+=Erg[0:-1]+']}],"context": "vessels.'+uuid+'"}\n'
				sock.sendto(SignalK, ('127.0.0.1', 55557))			
		else:
			index+=1
			if index>3: index=0

			a_value[index]=ads1115.read(index)