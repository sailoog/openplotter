#!/usr/bin/python

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
import signal, sys, time, socket, datetime, subprocess, os
from PyMata.pymata import PyMata

op_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')
sys.path.append(op_folder+'/classes')
from conf import Conf
from language import Language
from conf_analog import Conf_analog

# Control-C signal handler to suppress exceptions if user presses Control C
# This is totally optional.
def signal_handler(sig, frame):
	print('You pressed Ctrl+C!!!!')
	if board is not None:
		board.reset()
	sys.exit(0)

def interpolread(idx,erg):
	if adjust_point_active[idx]:
		lin = -999999
		for index,item in enumerate(adjust_point[idx]):
			if index==0:
				if erg <= item[0]:
					lin = item[1]
					#print 'under range'
					return lin
				save = item
			else:					
				if erg <= item[0]:
					a = (item[1]-save[1])/(item[0]-save[0])
					b = item[1]-a*item[0]
					lin = a*erg +b
					return lin
				save = item
				
		if lin == -999999:
			#print 'over range'
			lin = save[1]
		return lin
	else:
		return erg
		
def init():	
	signal.signal(signal.SIGINT, signal_handler)

	conf_analog = Conf_analog()

	FIRMATA='FIRMATA_'

	#example to set arduino A2 as analog input -> config file "openplotter_analog.conf"
	#[FIRMATA_2]
	#sk_name = tanks.fuel.left.currentLevel
	#adjust_points = [[403.0,0.0],[522.0,25.0],[708.0,50.0],[913.0,100],[1024.0,100.01]]	
	
	index=0
	for i in range(16):
		if conf_analog.has_section(FIRMATA+str(i)):
			channel.append(i)
			RawValue.append(0)
			adjust_point_active.append(0)
			adjust_point.append(0)
			channel_index.append(index)
			board.set_pin_mode(i, board.INPUT, board.ANALOG)
			if 0==conf_analog.has_option(FIRMATA+str(i), 'sk_name'):
				conf_analog.set(FIRMATA+str(i), 'sk_name','0')

			SK_name.append(conf_analog.get(FIRMATA+str(i), 'sk_name'))
			
			if 0==conf_analog.has_option(FIRMATA+str(i), 'adjust_points'):
				adjust_point_active[index] = 0
			else:
				line = conf_analog.get(FIRMATA+str(i), 'adjust_points')			
				if line: 
					adjust_point[index]=eval(line)
					adjust_point_active[index] = 1
				else: adjust_point[index]=[]
			index+=1

conf = Conf()
home = conf.home
currentpath = home+conf.get('GENERAL', 'op_folder')+'/openplotter'

if len(sys.argv)>1:
	index=1
	if sys.argv[1]=='settings':
		print home+'/.openplotter/openplotter_analog.conf'
		subprocess.Popen(['leafpad',home+'/.openplotter/openplotter_analog.conf'])
	exit
else:
	RawValue=[]
	adjust_point=[]
	adjust_point_active=[]
	channel=[]
	channel_index=[]
	SK_name=[]
	index=0
	SignalK=''

if os.path.exists('/dev/ttyOP_FIRM') and index == 0:
	output = subprocess.check_output(['python', currentpath+'/tools/op_pymata_check.py'])
	if 'Total Number' in output:
		pass
	else:
		print 'some errors so second try'
		output = subprocess.check_output(['python', currentpath+'/tools/op_pymata_check.py'])
		if 'Total Number' in output:
			pass
		else:
			print 'No Firmata on /dev/ttyOP_FIRM'
			sys.exit(0)
		
	board = PyMata("/dev/ttyOP_FIRM")		
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
				
	init()
	index=0
	length=len(channel_index)-1
		
	# A forever loop until user presses Control-C
	while 1:	
		RawValue[index]=board.analog_read(channel[index])
		time.sleep(0.100)

		index+=1
		if index > length:
			index=0

			SignalK = '{"updates": [{"$source":"OPserial.ARD.ANA","values":[ '
			Erg=''
			for i in channel_index:
				Erg += '{"path": "'+SK_name[i]+'","value":'+str(interpolread(i,RawValue[i]))+'},'
			
			SignalK +=Erg[0:-1]+']}]}\n'
			#print SignalK
			sock.sendto(SignalK, ('127.0.0.1', 55559))
			time.sleep(0.100)
else:
	print 'No serialport ttyOP_FIRM (Arduino with Firmata) found.'
	print 'Have you add the Arduino port in USB manager?'
