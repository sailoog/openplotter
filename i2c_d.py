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

import socket, time, pynmea2, math, csv, datetime, subprocess, platform, threading

class MyVar:
	heading_m=0.0
	heading=0.0
	heel=0.0
	pitch=0.0
	pressure=0.0
	temperature_p=0.0
	humidity=0.0
	temperature_h=0.0


if platform.machine()[0:3]!='arm':
	print 'this is not a raspberry pi -> no i2c and spi'
else:
	from classes.paths import Paths
	from classes.conf import Conf
	from classes.check_vessel_self import checkVesselSelf
	import RPi.GPIO as GPIO
	import spidev,RTIMU

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

	def publish_sk(io,channel,current_state,timestamp):
		if io=='in':io='input'
		else: io='output'
		if current_state: current_state='1'
		else: current_state='0'
		SignalK='{"context": "vessels.'+uuid+'","updates":[{"source":{"type": "GPIO","src":"GPIO'+str(channel)+'"},"timestamp":"'+timestamp+'","values":[{"path":"notifications.gpio.'+io+'.gpio'+str(channel)+'","value":'+current_state+'}]}]}\n'
		sock.sendto(SignalK, ('127.0.0.1', 55558))
	  
	conf=Conf(Paths())
	
	#init SPI MCP
	MCP=[]
	adjust_point=[]
	SignalK=''

	spi = spidev.SpiDev()
	spi.open(0,0)

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

	#init GPIO
	try:
		gpio_list=eval(conf.get('GPIO', 'sensors'))
	except: gpio_list=[]

	gpio_=False
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

	heading_sk=conf.get('I2C', 'sk_hdg')=='1'
	heel_sk=conf.get('I2C', 'sk_heel')=='1'
	pitch_sk=conf.get('I2C', 'sk_pitch')=='1'
	pressure_sk=conf.get('I2C', 'sk_press')=='1'
	p_temp_sk=conf.get('I2C', 'sk_temp_p')=='1'
	humidity_sk=conf.get('I2C', 'sk_hum')=='1'
	h_temp_sk=conf.get('I2C', 'sk_temp_h')=='1'
	imu_=False
	bmp_=False
	hum_=False
	if heading_sk or heel_sk or pitch_sk: imu_=True
	if pressure_sk or p_temp_sk: bmp_=True
	if humidity_sk or h_temp_sk: hum_=True

	if imu_ or bmp_ or hum_ or analog_ or gpio_:
		
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

		poll_interval = 1

		try:
			heading_offset=float(conf.get('OFFSET', 'heading'))
			heel_offset=float(conf.get('OFFSET', 'heel'))
			pitch_offset=float(conf.get('OFFSET', 'pitch'))
			pressure_offset=float(conf.get('OFFSET', 'pressure'))
			p_temp_offset=float(conf.get('OFFSET', 'temperature_p'))
			humidity_offset=float(conf.get('OFFSET', 'humidity'))
			h_temp_offset=float(conf.get('OFFSET', 'temperature_h'))
		except:
			heading_offset=heel_offset=pitch_offset=pressure_offset=p_temp_offset=humidity_offset=h_temp_offset=0.0
			print 'Bad format in offset value' 

		p_temp_skt=conf.get('I2C', 'p_temp_skt')
		if not p_temp_skt: p_temp_skt='environment.outside.temperature'
		h_temp_skt=conf.get('I2C', 'h_temp_skt')
		if not h_temp_skt: h_temp_skt='environment.inside.temperature'
		humidity_skt=conf.get('I2C', 'hum_skt')
		if not humidity_skt: humidity_skt='environment.inside.humidity'

		rate_imu=float(conf.get('I2C', 'rate_imu'))
		rate_bmp=float(conf.get('I2C', 'rate_press'))
		rate_hum=float(conf.get('I2C', 'rate_hum'))
		rate_ana=rate_imu
		rate_gpio=0.1
		
		vessel_self=checkVesselSelf()
		uuid=vessel_self.uuid

		if heading_sk or heel_sk or pitch_sk:
			SETTINGS_FILE = "RTIMULib"
			s = RTIMU.Settings(SETTINGS_FILE)
			imu = RTIMU.RTIMU(s)
			imu.IMUInit()
			imu.setSlerpPower(0.02)
			imu.setGyroEnable(True)
			imu.setAccelEnable(True)
			imu.setCompassEnable(True)
			poll_interval = imu.IMUGetPollInterval()

		if pressure_sk:
			SETTINGS_FILE2 = "RTIMULib2"
			s2 = RTIMU.Settings(SETTINGS_FILE2)
			pressure_val = RTIMU.RTPressure(s2)
			pressure_val.pressureInit()
			print pressure_val.pressureRead()

		if humidity_sk:
			SETTINGS_FILE3 = "RTIMULib3"
			s3 = RTIMU.Settings(SETTINGS_FILE3)
			humidity_val = RTIMU.RTHumidity(s3)
			humidity_val.humidityInit()

		def work_imu():
					threading.Timer(rate_imu, work_imu).start()
					if imu.IMURead():
						data = imu.getIMUData()
						fusionPose = data["fusionPose"]
						MyVar.heading=math.degrees(fusionPose[2])+heading_offset
						MyVar.heel=math.degrees(fusionPose[0])+heel_offset
						MyVar.pitch=math.degrees(fusionPose[1])+pitch_offset
						if heading<0: heading=360+heading
						elif heading>360: heading=-360+heading
					
					Erg=''
					if heading_sk:
						Erg += '{"path": "navigation.headingMagnetic","value":'+str(0.017453293*MyVar.heading)+'},'
					if heel_sk:
						Erg += '{"path": "navigation.attitude.roll","value":'+str(0.017453293*MyVar.heel)+'},'
					if pitch_sk:
						Erg += '{"path": "navigation.attitude.pitch","value":'+str(0.017453293*MyVar.pitch)+'},'

					timestamp=str( datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f') )[0:23]+'Z'
					SignalK='{"context": "vessels.'+uuid+'","updates":[{"source":{"type": "I2C","src":"'+imu.IMUName()+'"},"timestamp":"'+timestamp+'","values":['
					SignalK+=Erg[0:-1]+']}]}\n'		
					sock.sendto(SignalK, ('127.0.0.1', 55557))	

			# read Pressure and GENERATE
		def work_bmp():
					threading.Timer(rate_bmp, work_bmp).start()
					read=pressure_val.pressureRead()
					if read:
						if (read[0]): MyVar.pressure=read[1]+pressure_offset
						if (read[2]): MyVar.temperature_p=read[3]+p_temp_offset

					Erg=''
					if pressure_sk:
						Erg += '{"path": "environment.outside.pressure","value":'+str(MyVar.pressure*100)+'},'
					if p_temp_sk:
						Erg += '{"path": "'+p_temp_skt+'","value":'+str(round(MyVar.temperature_p,2)+273.15)+'},'
					
					timestamp=str( datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f') )[0:23]+'Z'
					SignalK='{"context": "vessels.'+uuid+'","updates":[{"source":{"type": "I2C","src":"'+pressure_val.pressureName()+'"},"timestamp":"'+timestamp+'","values":['
					SignalK+=Erg[0:-1]+']}]}\n'	
					sock.sendto(SignalK, ('127.0.0.1', 55557))			
					
			# read Humidity and GENERATE
		def work_hum():
					threading.Timer(rate_hum, work_hum).start()
					read=humidity_val.humidityRead()
					if read:
						if (read[0]): MyVar.humidity=read[1]+humidity_offset
						if (read[2]): MyVar.temperature_h=read[3]+h_temp_offset

					Erg=''
					if humidity_sk:
						Erg += '{"path": "'+humidity_skt+'","value":'+str(MyVar.humidity)+'},'
					if h_temp_sk:
						Erg += '{"path": "'+h_temp_skt+'","value":'+str(round(MyVar.temperature_h,2)+273.15)+'},'
							
					timestamp=str( datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f') )[0:23]+'Z'
					SignalK='{"context": "vessels.'+uuid+'","updates":[{"source":{"type": "I2C","src":"'+humidity_val.humidityName()+'"},"timestamp":"'+timestamp+'","values":['
					SignalK+=Erg[0:-1]+']}]}\n'	
					sock.sendto(SignalK, ('127.0.0.1', 55557))

			# read SPI adc and GENERATE
		def work_analog():
					threading.Timer(rate_ana, work_analog).start()
					timestamp=str( datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f') )[0:23]+'Z'
					SignalK=''
					for i in MCP:
						if i[0]==1:
							XValue=read_adc(i[1])
							if i[4]==1:
								XValue = interpolread(i[1],XValue)
							Erg ='{"context": "vessels.'+uuid+'","updates":[{"source":{"type": "SPI","src":"MCP3008.'+str(i[1])+'"},'
							Erg +='"timestamp":"'+timestamp+'","values":[{"path": "'+i[2]+'","value":'+str(XValue)+'}]}]}\n'
							SignalK+=Erg
					sock.sendto(SignalK, ('127.0.0.1', 55557))

			# read gpio and GENERATE
		def work_gpio():
					threading.Timer(rate_gpio, work_gpio).start()
					timestamp=str( datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f') )[0:23]+'Z'
					c=0
					for i in gpio_list:
						channel=int(i[2])
						current_state = GPIO.input(channel)
						last_state=gpio_list[c][4]
						if current_state!=last_state:
							gpio_list[c][4]=current_state
							publish_sk(i[1],channel,current_state,timestamp)
						c+=1

		if imu_:    work_imu()
		if bmp_:	work_bmp()
		if hum_:	work_hum()
		if analog_: work_analog()
		if gpio_:   work_gpio()
			
		
