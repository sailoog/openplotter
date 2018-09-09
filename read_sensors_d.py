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

import socket, time, platform, threading, os, pynmea2
from classes.conf import Conf
from signalk.client import SignalKClient


if platform.machine()[0:3]!='arm':
	print 'This is not a Raspberry Pi -> no GPIO, I2C and SPI'
else:
	import RPi.GPIO as GPIO
	import spidev,RTIMU
	from classes.bme280 import Bme280
	from classes.MS5607 import ms5607

def interpolread(idx,erg):
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
		
def read_adc(channel):
	adc = spi.xfer2([1,(8+channel)<<4,0])
	data = ((adc[1]&3) << 8) + adc[2]
	return data

# read heading, heel, pitch and GENERATE SK

#translate pypilot signalk -> node signalk
def oldTranslate(result):
	translation_table = {'imu.roll' : ['navigation.attitude.roll', 0.017453293], 'imu.pitch' : ['navigation.attitude.pitch', 0.017453293]}
	Erg = ''
	for translation in translation_table:
		if translation in result:
			value = result[translation]['value']
			tr = translation_table[translation]
			Erg += '{"path": "' + tr[0] + '","value":'+str(value*tr[1])+'},'
	return Erg

#translate pypilot signalk -> node signalk
def Translate(result):
	translation_table = {'imu.roll' : ['navigation.attitude.roll', 0.017453293], 'imu.pitch' : ['navigation.attitude.pitch', 0.017453293]}
	Erg = '{"path": "navigation.attitude","value":{'
	for translation in translation_table:
		if translation in result:
			value = result[translation]['value']
			tr = translation_table[translation]
			Erg += '"'+tr[0][20:]+'":'+str(value*tr[1])+','
	Erg += '"yaw": 0.0},'
	return Erg

def work_pypilot():
	#init compass
	mode = conf.get('PYPILOT', 'mode')
	if mode == 'disabled':
		print 'pypilot disabled  '
		return
        
	headingSK = conf.get('PYPILOT', 'translation_magnetic_h')
	attitudeSK = conf.get('PYPILOT', 'translation_attitude')
        
	SETTINGS_FILE = "RTIMULib"
	s = RTIMU.Settings(SETTINGS_FILE)
	imu = RTIMU.RTIMU(s)
	imuName = imu.IMUName()
	del imu
	del s
	if mode == 'imu':
		cmd = ['pypilot_boatimu', '-q']
	elif mode == 'basic autopilot':
		# ensure no serial getty running
		os.system('sudo systemctl stop serial-getty@ttyAMA0.service')
		os.system('sudo systemctl stop serial-getty@ttyS0.service')
		cmd = ['pypilot']

	try:
		translation_rate = float(conf.get('PYPILOT', 'translation_rate'))
	except:
		translation_rate = 1
		conf.set('PYPILOT', 'translation_rate', '1')

	pid = os.fork()
	try:
		if pid == 0:
			os.execvp(cmd[0], cmd)
			print 'failed to launch', cmd
			exit(1)
	except:
		print 'exception launching pypilot'
		exit(1)
	print 'launched pypilot pid', pid
	time.sleep(3) # wait 3 seconds to launch client

	def on_con(client):
		print 'connected'
		if headingSK == '1':
			client.watch('imu.heading')
		if attitudeSK == '1':
			client.watch('imu.pitch')
			client.watch('imu.roll')

	client = False
	tick1 = time.time()
	while read_sensors:
		ret = os.waitpid(pid, os.WNOHANG)
		if ret[0] == pid:
			# should we respawn pypilot if it crashes?
			print 'pypilot exited'
			break

		# connect to pypilot if not connected
		try:
			if not client:
				client = SignalKClient(on_con, 'localhost')
		except:
			time.sleep(1)
			continue # not much to do without connection
                
		try:
			result = client.receive()
		except:
			print 'disconnected from pypilot'
			client = False
			continue
                
		Erg = Translate(result)
		SignalK='{"updates":[{"$source":"OPsensors.I2C.'+imuName+'","values":['
		SignalK+=Erg[0:-1]+'}]}]}\n'
		sock.sendto(SignalK, ('127.0.0.1', 55557))

		if mode == 'imu':
			if 'imu.heading' in result:
				value = result['imu.heading']['value'] 
				hdm = str(pynmea2.HDM('AP', 'HDM', (str(value),'M')))+'\r\n'
				sock.sendto(hdm, ('127.0.0.1', 10110))
			if 'imu.roll' in result:
				value = result['imu.roll']['value'] 
				xdr_r = str(pynmea2.XDR('AP', 'XDR', ('A',str(value),'D','ROLL')))+'\r\n'
				sock.sendto(xdr_r, ('127.0.0.1', 10110))
			if 'imu.pitch' in result:
				value = result['imu.pitch']['value'] 
				xdr_p = str(pynmea2.XDR('AP', 'XDR', ('A',str(value),'D','PTCH')))+'\r\n'
				sock.sendto(xdr_p, ('127.0.0.1', 10110))

		while True:
			dt = translation_rate - time.time() + tick1
			if dt <= 0:
				break
			time.sleep(dt)
		tick1 = time.time()
                

        # cleanup
        print 'stopping pypilot pid:', pid
        try:
                os.kill(pid, 15)
                time.sleep(1) # wait one second to shut down pypilot
        except Exception, e:
                print 'exception stopping pypilot', e

        try:
                if os.waitpid(pid, os.WNOHANG)[0] == pid:
                        print 'pypilot stopped: ok'
                else:
                        print 'killing pypilot pid:', pid
                        os.kill(pid, 9) # try to kill with signal 9
        except:
                pass # pypilot already exited, or other exception
                
        print 'pypilot thread exiting'                


# read pressure, humidity, temperature and GENERATE SK
def work_imu_press_hum():
	timesleep = 0.1
	SETTINGS_FILE = "RTIMULib2"
	s = RTIMU.Settings(SETTINGS_FILE)
	if imu_press:
		pressure = RTIMU.RTPressure(s)
		pressure.pressureInit()
		pressName = imu_press[0]
		pressName = pressName.replace(' ', '')
		pressSK = imu_press[2][0][0]
		pressRate = imu_press[2][0][1]
		pressOffset = imu_press[2][0][2]
		temp_pressSK = imu_press[2][1][0]
		temp_pressRate = imu_press[2][1][1]
		temp_pressOffset = imu_press[2][1][2]
	if imu_hum:
		humidity = RTIMU.RTHumidity(s)
		humidity.humidityInit()
		humName = imu_hum[0]
		humName = humName.replace(' ', '')
		humSK = imu_hum[2][0][0]
		humRate = imu_hum[2][0][1]
		humOffset = imu_hum[2][0][2]
		temp_humSK = imu_hum[2][1][0]
		temp_humRate = imu_hum[2][1][1]
		temp_humOffset = imu_hum[2][1][2]

	tick1 = time.time()
	tick4 = tick1
	tick5 = tick1
	tick6 = tick1
	tick7 = tick1
	try:
		while read_sensors:
			time.sleep(timesleep)
			tick0 = time.time()
			if imu_press:
				Erg=''
				read=pressure.pressureRead()
				if read:
					if pressSK:
						if (read[0]): 
							pressureValue = read[1]
							if tick0 - tick4 > pressRate:
								Erg += '{"path": "'+pressSK+'","value":'+str((pressureValue*100)+pressOffset)+'},'
								tick4 = tick0
					if temp_pressSK:
						if (read[2]): 
							temp_pressValue = read[3]
							if tick0 - tick5 > temp_pressRate:
								Erg += '{"path": "'+temp_pressSK+'","value":'+str((temp_pressValue+273.15)+temp_pressOffset)+'},'
								tick5 = tick0
				if Erg:		
					SignalK='{"updates":[{"$source":"OPsensors.I2C.'+pressName+'","values":['
					SignalK+=Erg[0:-1]+']}]}\n'		
					sock.sendto(SignalK, ('127.0.0.1', 55557))
			if imu_hum:
				Erg=''
				read=humidity.humidityRead()
				if read:
					if humSK:
						if (read[0]): 
							humidityValue = read[1]
							if tick0 - tick6 > humRate:
								Erg += '{"path": "'+humSK+'","value":'+str(humidityValue/100+humOffset)+'},'
								tick6 = tick0
					if temp_humSK:
						if (read[2]): 
							temp_humValue = read[3]
							if tick0 - tick7 > temp_humRate:
								Erg += '{"path": "'+temp_humSK+'","value":'+str((temp_humValue+273.15)+temp_humOffset)+'},'
								tick7 = tick0
				if Erg:		
					SignalK='{"updates":[{"$source":"OPsensors.I2C.'+humName+'","values":['
					SignalK+=Erg[0:-1]+']}]}\n'		
					sock.sendto(SignalK, ('127.0.0.1', 55557))
	except Exception, e: print "RTIMULib2 (pressure, humidity) reading failed: "+str(e)	

# read bme280 and send SK
def work_bme280():
	name = bme280[0]
	address = bme280[1]
	pressureSK = bme280[2][0][0]
	pressureRate = bme280[2][0][1]
	pressureOffset = bme280[2][0][2]
	temperatureSK = bme280[2][1][0]
	temperatureRate = bme280[2][1][1]
	temperatureOffset = bme280[2][1][2]
	humiditySK = bme280[2][2][0]
	humidityRate = bme280[2][2][1]
	humidityOffset = bme280[2][2][2]
	try:
		bme = Bme280(address)
		tick1 = time.time()
		tick2 = tick1
		tick3 = tick1
		while read_sensors:
			time.sleep(0.1)
			temperature,pressure,humidity = bme.readBME280All()
			tick0 = time.time()
			Erg=''
			if pressureSK:
				if tick0 - tick1 > pressureRate:
					Erg += '{"path": "'+pressureSK+'","value":'+str(pressureOffset+(pressure*100))+'},'
					tick1 = tick0
			if temperatureSK:
				if tick0 - tick2 > temperatureRate:
					Erg += '{"path": "'+temperatureSK+'","value":'+str(temperatureOffset+(temperature+273.15))+'},'
					tick2 = tick0
			if humiditySK:
				if tick0 - tick3 > humidityRate:
					Erg += '{"path": "'+humiditySK+'","value":'+str(humidityOffset+(humidity))+'},'
					tick3 = tick0
			if Erg:		
				SignalK='{"updates":[{"$source":"OPsensors.I2C.'+name+'","values":['
				SignalK+=Erg[0:-1]+']}]}\n'		
				sock.sendto(SignalK, ('127.0.0.1', 55557))
	except Exception, e: print "BME280 reading failed: "+str(e)

# read MS5607 and send SK
def work_MS5607():
	name = MS5607[0]
	address = MS5607[1]
	pressureSK = MS5607[2][0][0]
	pressureRate = MS5607[2][0][1]
	pressureOffset = MS5607[2][0][2]
	temperatureSK = MS5607[2][1][0]
	temperatureRate = MS5607[2][1][1]
	temperatureOffset = MS5607[2][1][2]
	try:
		MS = ms5607(address)
		tick1 = time.time()
		tick2 = tick1
		while read_sensors:
			time.sleep(0.1)
			dig_temperature = MS.getDigitalTemperature()
			dig_pressure = MS.getDigitalPressure()
			pressure = MS.convertPressureTemperature(dig_pressure, dig_temperature)
			temperature = MS.getTemperature()
			tick0 = time.time()
			Erg=''
			if pressureSK:
				if tick0 - tick1 > pressureRate:
					Erg += '{"path": "'+pressureSK+'","value":'+str(pressureOffset+(pressure))+'},'
					tick1 = tick0
			if temperatureSK:
				if tick0 - tick2 > temperatureRate:
					Erg += '{"path": "'+temperatureSK+'","value":'+str(temperatureOffset+(temperature+273.15))+'},'
					tick2 = tick0
			if Erg:		
				SignalK='{"updates":[{"$source":"OPsensors.I2C.'+name+'","values":['
				SignalK+=Erg[0:-1]+']}]}\n'		
				sock.sendto(SignalK, ('127.0.0.1', 55557))
	except Exception, e: print "MS5607-02BA03 reading failed: "+str(e)

# read SPI adc and GENERATE SK
def work_analog():
        if read_sensors:
                threading.Timer(rate_ana, work_analog).start()
	SignalK='{"updates":[{"$source":"OPsensors.SPI.MCP3008","values":[ '
	Erg=''
	send=False
	for i in MCP:
		if i[0]==1:
			send=True
			XValue=read_adc(i[1])
			if i[4]==1:
				XValue = interpolread(i[1],XValue)
			Erg +='{"path": "'+i[2]+'","value":'+str(XValue)+'},'

	if send:
		SignalK +=Erg[0:-1]+']}]}\n'
		sock.sendto(SignalK, ('127.0.0.1', 55557))	
	
# read gpio and GENERATE SK
def work_gpio():
        if read_sensors:
                threading.Timer(rate_gpio, work_gpio).start()
	c=0
	for i in gpio_list:
		channel=int(i[2])
		name = i[0]
		current_state = GPIO.input(channel)
		last_state=gpio_list[c][4]
		if current_state!=last_state:
			gpio_list[c][4]=current_state
			publish_sk(i[1],channel,current_state, name)
		c+=1

def publish_sk(io,channel,current_state,name):
	if io=='in':io='input'
	else: io='output'
	if current_state: current_state='1'
	else: current_state='0'
	SignalK='{"updates":[{"$source":"OPnotifications.GPIO.'+io+'.'+str(channel)+'","values":[{"path":"sensors.'+name+'","value":'+current_state+'}]}]}\n'
	sock.sendto(SignalK, ('127.0.0.1', 55558))

conf = Conf()
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
read_sensors = True

#init SPI MCP
rate_ana=0.25
MCP=[]
adjust_point=[]
SignalK=''
data=conf.get('SPI', 'mcp')
try:
	temp_list=eval(data)
except:temp_list=[]
analog_=False
for ii in temp_list:
	if '.*.' in ii[2]: ii[2]=ii[2].replace('*', ii[3])
	MCP.append(ii)	
	if ii[0]==1:analog_=True	
	if ii[0]==1 and ii[4]==1:
		if not conf.has_option('SPI', 'value_'+str(ii[1])):
			temp_list=[[0,0],[1023,1023]]
			conf.set('SPI', 'value_'+str(ii[1]), str(temp_list))
			conf.read()
		
		data=conf.get('SPI', 'value_'+str(ii[1]))
		try:
			temp_list=eval(data)
		except:temp_list = []
			
		adjust_point.append(temp_list)
	else:
		adjust_point.append([])
if analog_:
	try:
		spi = spidev.SpiDev()
		spi.open(0,1)
		spi.max_speed_hz = 200000
	except:
		analog_=False
		print 'spi is disabled in raspberry-pi-configuration device tab'
		
#init GPIO
rate_gpio=0.1
gpio_=False
try:
	gpio_list=eval(conf.get('GPIO', 'sensors'))
except: gpio_list=[]
if gpio_list:
	gpio_=True
	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)
	c=0
	for i in gpio_list:
		channel=int(i[2])
		if i[1]=='out':
			GPIO.setup(channel, GPIO.OUT)
			GPIO.output(channel, 0)
		if i[1]=='in':
			pull_up_down=GPIO.PUD_DOWN
			if i[3]=='up': pull_up_down=GPIO.PUD_UP
			GPIO.setup(channel, GPIO.IN, pull_up_down)
		gpio_list[c].append('')
		c=c+1

#init I2C
bme280 = False
MS5607 = False
imu_press = False
imu_hum = False
try:
	i2c_sensors=eval(conf.get('I2C', 'sensors'))
except: i2c_sensors=[]

if i2c_sensors:
	for i in i2c_sensors:
		if i[0] == 'BME280': bme280 = i
		elif i[0] == 'MS5607-02BA03': MS5607 = i
		elif 'rtimulib' in i[1]:
			temp_list = i[1].split('.')
			if temp_list[1] == 'press': imu_press = i
			elif temp_list[1] == 'hum': imu_hum = i



def cleanup(signal_number, frame):
        global read_sensors
        print 'read sensors got signal', signal_number, 'cleaning up'
        read_sensors = False

import signal

threads = []
def add_thread(func):
        thread = threading.Thread(target=func)
        thread.start()
        threads.append(thread)


# launch threads
if analog_: work_analog()
if gpio_: work_gpio()
if bme280:
	add_thread(work_bme280)
if MS5607:
	add_thread(work_MS5607)
if imu_press or imu_hum:
	add_thread(work_imu_press_hum)

add_thread(work_pypilot)

# catch signals to cleanly exit
for s in range(1, 16):
        if s == 2: # disable this for debugging to allow keyboard interrupts
                continue
        if s != 9 and s != 13:
                signal.signal(s, cleanup)
#signal.signal(signal.SIGCHLD, cleanup)
        
print 'read_sensors_d waiting for signal to exit '

# sleep on conditional
while read_sensors:
        time.sleep(1)

print 'waiting for threads'
for thread in threads:
        thread.join()
print 'read_sensors_d finished'
