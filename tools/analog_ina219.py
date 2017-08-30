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

import socket, time, math, csv, datetime, subprocess, sys, os

op_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')
sys.path.append(op_folder+'/classes')
from ads1115 import Ads1115
from conf_analog import Conf_analog
from ina219 import INA219
from ina219 import DeviceRangeError

SHUNT_OHMS = 0.1

conf_analog=Conf_analog()
home = conf_analog.home

if len(sys.argv)>1:
	if sys.argv[1]=='settings':
		print home+'/.openplotter/openplotter_analog.conf'
		subprocess.Popen(['leafpad',home+'/.openplotter/openplotter_analog.conf'])
	exit
else:

	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	poll_interval = 1
	rate_analog = 1

	tick_analog=time.time()
	ina = INA219(SHUNT_OHMS,1.0,0x41)
	ina.configure()

	try:
		inaV = ina.voltage()
		inaA = ina.current()/1000
		inaW = inaV*inaA
	except DeviceRangeError as e:
		print e
	
	while True:
		tick2=time.time()
		time.sleep(poll_interval*1.0/1000.0)
		#GENERATE	

		if tick2-tick_analog > rate_analog:
			tick_analog=time.time()

			list_signalk_path1=[]
			list_signalk1=[]

			try:
				inaV = inaV*0.8 +ina.voltage()*0.2
				inaA = inaA*0.8 +ina.current()/1000*0.2
				inaW = inaV*inaA
			except DeviceRangeError as e:
				print e

			SignalK = '{"updates": [{"$source": "OPsensors.I2C.ina219","values":[ '
			Erg=''
			Erg += '{"path": "electrical.batteries.rpi.current","value":'+str(inaA)+'},'
			Erg += '{"path": "electrical.batteries.rpi.voltage","value":'+str(inaV)+'},'
			Erg += '{"path": "electrical.batteries.rpi.power","value":'+str(inaW)+'},'			
			SignalK +=Erg[0:-1]+']}]}\n'
			sock.sendto(SignalK, ('127.0.0.1', 55557))
