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
import signal, sys, os, time, socket, subprocess
import shlex

op_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')
sys.path.append(op_folder+'/classes')
from conf_analog import Conf_analog

sen_frequenz = '433967780'
sen_type = '03'
#for sensor type see: rtl_433 -h
sen_temp_SK = 'environment.inside.refrigerator.temperature'
sen_humi_SK = 'environment.inside.humidity'

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

	SK_name.append(sen_temp_SK);
	SK_name.append(sen_humi_SK);

if len(sys.argv)>1:
	if sys.argv[1]=='settings':
		print 'No config file or gui! Changes must be made in the python file'
	exit
else:
	index=0
	SignalK=''
	RawValue=[]
	SK_name=[]
	channel_rtl=''
	type_rtl=''
	output=''
	finish=False
	proc = subprocess.Popen(shlex.split('rtl_433 -f'+ sen_frequenz + ' -R' + sen_type +' -s280000'), bufsize = 1, stdout=subprocess.PIPE)
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	init()
	index=0
		
	for line in iter(proc.stdout.readline, b''):
		if 'Temperature:' in line:
			temperature_rtl = float(line[14:-3])
			if line[-2:-1] == 'F':
				temperature_rtl = (temperature_rtl-32.)/1.8 +273.15
			else:
				temperature_rtl += 273.15
			output += line[:-1] + '   float=' + str(temperature_rtl) + '\n'
		elif 'Humidity:' in line:
			humidity_rtl = float(line[11:-3])
			output += line[:-1] + '   float=' + str(humidity_rtl) + '\n'
			finish=True
		elif 'Channel:' in line:
			channel_rtl = line[-2:-1]
			output += line[:-1] + '   char=' + channel_rtl + '\n'
		elif 'Prologue sensor' in line:
			type_rtl = 'PRO'
			#output += '   shortcut='
			output += str(line[:-1]) + '   shortcut=' + str(type_rtl) + '\n'
		else:
			output += line
		if finish:
			finish=False
			print output
			output=''
			SignalK = '{"updates":[{"$source":"OPsensors.RTL433.'+type_rtl+channel_rtl+'","values":[ '
			Erg=''
			Erg += '{"path": "'+SK_name[1]+'","value":'+str(humidity_rtl)+'},'
			Erg += '{"path": "'+SK_name[0]+'","value":'+str(temperature_rtl)+'},'

			SignalK +=Erg[0:-1]+']}]}\n'
			sock.sendto(SignalK, ('127.0.0.1', 55557))
			print SignalK
			sys.stdout.flush()
			time.sleep(0.2)

	proc.wait()
