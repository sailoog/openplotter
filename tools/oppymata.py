import signal, sys, time, socket, datetime,json,subprocess

from PyMata.pymata import PyMata
from classes.conf_analog import Conf_analog
from classes.paths import Paths


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

	conf_analog=Conf_analog()

	global uuid
	with open('/home/pi/.config/signalk-server-node/settings/openplotter-settings.json') as data_file:
		data = json.load(data_file)
	uuid=data['vessel']['uuid']


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


paths=Paths()
currentpath=paths.currentpath

if len(sys.argv)>1:
	if sys.argv[1]=='settings':
		subprocess.Popen(['leafpad',currentpath+'/openplotter_analog.conf'])
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

			SignalK = '{"updates": [{"source": {"type": "ARD","src" : "ANA"},"timestamp": "'+str( datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f') )[0:23]+'Z","values":[ '
			Erg=''
			for i in channel_index:
				Erg += '{"path": "'+SK_name[i]+'","value":'+str(interpolread(i,RawValue[i]))+'},'
			
			SignalK +=Erg[0:-1]+']}],"context": "vessels.'+uuid+'"}\n'
			#print SignalK
			sock.sendto(SignalK, ('127.0.0.1', 55559))
			time.sleep(0.100)
			
