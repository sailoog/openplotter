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

import ujson
import threading
import websocket
import time
import datetime,operator,signal,socket,sys,re

from classes.N2K_send import N2K_send
from classes.conf import Conf
from classes.SK_settings import SK_settings

class MySK:
	def __init__(self):
		self.list_SK = []
		self.static_list = [[]]
		self.sortCol = 0

		self.conf = Conf()
		self.home = self.conf.home
		self.currentpath = self.conf.get('GENERAL', 'op_folder')

		SK_ = SK_settings(self.conf)
		self.ws_name = SK_.ws+SK_.ip+":"+str(SK_.aktport)+"/signalk/v1/stream?subscribe=self"

		self.data = []
		self.start()

	def json_interval(self, time_old, time_new):
		sek_n = float(time_new[17:22])
		sek_o = float(time_old[17:22])
		if sek_n >= sek_o:
			dif = sek_n - sek_o
		else:
			dif = sek_n + 60 - sek_o
		return float(dif)

	def OnClose(self, e):
		self.stop()
	
	def on_message(self, ws, message):
		js_up = ujson.loads(message)
		if 'updates' not in js_up:
			return
		js_up = js_up['updates'][0]
		label = ''
		src = ''
		type = ''
		value = ''
		
		if 'source' in js_up.keys():
			source=js_up['source']
			label = source['label']
			if 'type' in source:
				type = source['type']
				if type == 'NMEA0183':
					if 'talker' in source: 
						src =label+'.'+source['talker']
						if 'sentence' in source: src =label+'.'+source['sentence']
				elif type == 'NMEA2000':
					if 'src' in source: 
						src =label+'.'+source['src']
						if 'pgn' in source: src +='.'+str(source['pgn'])
		if '$source' in js_up and src=='':
			src = js_up['$source']

		if 'timestamp' in js_up.keys():
			timestamp = js_up['timestamp']
		else:
			timestamp = '2000-01-01T00:00:00.000Z'

		values_ = js_up['values']

		for values in values_:
			path = values['path']
			value = values['value']
			src2 = src
			timestamp2 = timestamp
			
			if isinstance(value, dict):
				if 'timestamp' in value: timestamp2 = value['timestamp']

				if '$source' in value and src=='':
					src = value['$source']
				elif 'source' in value:
					source=value['source']
					label = source['label']
					if 'type' in source:
						type = source['type']
						if type == 'NMEA0183':
							if 'talker' in source: 
								src =label+'.'+source['talker']
								if 'sentence' in source: src =label+'.'+source['sentence']
						elif type == 'NMEA2000':
							if 'src' in source: 
								src =label+'.'+source['src']
								if 'pgn' in source: src +='.'+str(source['pgn'])

				for lvalue in value:
					result = True
					if lvalue in ['source', '$source']:
						result = False
					elif lvalue == 'timestamp':
						if 'position' in path and 'RMC' in src2:
							self.update_add(timestamp2, 'navigation.datetime', src2, timestamp2)
						result = False
					if result:
						path2 = path + '.' + lvalue
						value2 = value[lvalue]
						self.update_add(value2, path2, src2, timestamp2)
			else:
				self.update_add(value, path, src, timestamp)
				
	def update_add(self, value, path, src, timestamp):
		# SRC SignalK Value Unit Interval Status Description timestamp	private_Unit private_Value priv_Faktor priv_Offset
		#  0    1      2     3      4        5        6          7           8             9           10          11
		if type(value) is list: value = value[0]
		
		if isinstance(value, float): pass
		elif isinstance(value, basestring): value = str(value)
		elif isinstance(value, int): value = float(value)
		elif value is None: value = 'None'
		else: value=0.0

		index = 0
		exists = False
		for i in self.list_SK:
			if path == i[1] and i[0] == src:
				exists = True
				i[2] = value
				i[7] = timestamp
				break
			index += 1
		if not exists:
						 
			self.list_SK.append([src, path, value, '', 0.0, 1, '', timestamp, '', 1, 0])

			for il in self.static_list:
				indexm = 0
				for im in il:
					if im[0] == path:
						im[1] = self.list_SK[-1]
						#break
					indexm += 1

	def on_error(self, ws, error):
		print error

	def on_close(self, ws):
		time.sleep(1)
		if self.ws is not None:
			self.ws.close()
		time.sleep(5)
		self.start()

	def on_open(self, ws):
		pass

	def run(self):
		self.ws = websocket.WebSocketApp(self.ws_name,
										 on_message=lambda ws, msg: self.on_message(ws, msg),
										 on_error=lambda ws, err: self.on_error(ws, err),
										 on_close=lambda ws: self.on_close(ws))
		self.ws.on_open = lambda ws: self.on_open(ws)
		self.ws.run_forever()
		self.ws = None

	def start(self):
		def run():
			self.run()

		self.thread = threading.Thread(target=run)
		self.thread.start()

	def stop(self):
		time.sleep(1)
		if self.ws is not None:
			self.ws.close()
		self.thread.join()

class MySK_to_N2K:
	def __init__(self, SK_):
		# self.PGN_list = ['126992','127245','127250','127257','127488','127488_1','127489','127489_1','127505','127505_1','127505_2','127505_3','127508','128259','128267','128275','129025','129026','130306_2','130306_3','130310','130311','130316','130316_1']

		def defvar():
			for i in self.PGN_list:
				if i == '126992':
					pass
				elif i == '127245':
					self.steering_rudderAngle = self.setlist(['steering.rudderAngle', [0, 0, 0, 0]])
				elif i == '127250':
					self.navigation_headingMagnetic = self.setlist(['navigation.headingMagnetic', [0, 0, 0, 0]])
				elif i == '127257':
					self.navigation_attitude_pitch = self.setlist(['navigation.attitude.pitch', [0, 0, 0, 0]])
					self.navigation_attitude_roll = self.setlist(['navigation.attitude.roll', [0, 0, 0, 0]])
					self.navigation_attitude_yaw = self.setlist(['navigation.attitude.yaw', [0, 0, 0, 0]])
				elif i == '127488':
					self.propulsion_port_revolutions = self.setlist(['propulsion.port.revolutions', [0, 0, 0, 0]])
				elif i == '127488_1':
					self.propulsion_starboard_revolutions = self.setlist(
						['propulsion.starboard.revolutions', [0, 0, 0, 0]])
				elif i == '127489':
					self.propulsion_port_oilTemperature = self.setlist(['propulsion.port.oilTemperature', [0, 0, 0, 0]])
					self.propulsion_port_temperature = self.setlist(['propulsion.port.temperature', [0, 0, 0, 0]])
				elif i == '127489_1':
					self.propulsion_starboard_oilTemperature = self.setlist(
						['propulsion.starboard.oilTemperature', [0, 0, 0, 0]])
					self.propulsion_starboard_temperature = self.setlist(
						['propulsion.starboard.temperature', [0, 0, 0, 0]])
				elif i == '127505':
					self.tank_diesel_capacity = self.setlist(['tanks.fuel.standard.capacity', [0, 0, 0, 0]])
					self.tank_diesel_level = self.setlist(['tanks.fuel.standard.currentLevel', [0, 0, 0, 0]])
				elif i == '127505_1':
					self.tank_freshwater_capacity = self.setlist(['tanks.liveWell.standard.capacity', [0, 0, 0, 0]])
					self.tank_freshwater_level = self.setlist(['tanks.liveWell.standard.currentLevel', [0, 0, 0, 0]])
				elif i == '127505_2':
					self.tank_greywater_capacity = self.setlist(['tanks.wasteWater.standard.capacity', [0, 0, 0, 0]])
					self.tank_greywater_level = self.setlist(['tanks.wasteWater.standard.currentLevel', [0, 0, 0, 0]])
				elif i == '127505_3':
					self.tank_holding_capacity = self.setlist(['tanks.blackWater.standard.capacity', [0, 0, 0, 0]])
					self.tank_holding_level = self.setlist(['tanks.blackWater.standard.currentLevel', [0, 0, 0, 0]])
				elif i == '127508':
					self.DC_Electrical_Properties_dcSource_voltage = self.setlist(
						['electrical.batteries.service.voltage', [0, 0, 0, 0]])
					self.DC_Electrical_Properties_dcSource_current = self.setlist(
						['electrical.batteries.service.current', [0, 0, 0, 0]])
					self.DC_Electrical_Properties_dcSource_temperature = self.setlist(
						['electrical.batteries.service.temperature', [0, 0, 0, 0]])
				elif i == '128259':
					self.navigation_speedOverGround = self.setlist(['navigation.speedOverGround', [0, 0, 0, 0]])
					self.navigation_speedThroughWater = self.setlist(['navigation.speedThroughWater', [0, 0, 0, 0]])
				elif i == '128267':
					self.environment_depth_belowTransducer = self.setlist(
						['environment.depth.belowTransducer', [0, 0, 0, 0]])
					self.environment_depth_surfaceToTransducer = self.setlist(
						['environment.depth.surfaceToTransducer', [0, 0, 0, 0]])
				elif i == '128275':
					self.navigation_log = self.setlist(['navigation.log', [0, 0, 0, 0]])
					self.navigation_logTrip = self.setlist(['navigation.logTrip', [0, 0, 0, 0]])
				elif i == '129025':
					self.navigation_position_latitude = self.setlist(['navigation.position.latitude', [0, 0, 0, 0]])
					self.navigation_position_longitude = self.setlist(['navigation.position.longitude', [0, 0, 0, 0]])
				elif i == '129026':
					self.navigation_courseOverGroundTrue = self.setlist(
						['navigation.courseOverGroundTrue', [0, 0, 0, 0]])
					self.navigation_speedOverGround = self.setlist(['navigation.speedOverGround', [0, 0, 0, 0]])
				elif i == '130306_2':
					self.environment_wind_angleApparent = self.setlist(['environment.wind.angleApparent', [0, 0, 0, 0]])
					self.environment_wind_speedApparent = self.setlist(['environment.wind.speedApparent', [0, 0, 0, 0]])
				elif i == '130306_3':
					self.environment_wind_angleTrueWater = self.setlist(['environment.wind.angleTrueWater', [0, 0, 0, 0]])
					self.environment_wind_speedTrue = self.setlist(['environment.wind.speedTrue', [0, 0, 0, 0]])
				elif i == '130310':
					self.environment_outside_pressure = self.setlist(['environment.outside.pressure', [0, 0, 0, 0]])
					self.environment_outside_temperature = self.setlist(
						['environment.outside.temperature', [0, 0, 0, 0]])
					self.environment_water_temperature = self.setlist(['environment.water.temperature', [0, 0, 0, 0]])
				elif i == '130311':
					self.environment_outside_pressure = self.setlist(['environment.outside.pressure', [0, 0, 0, 0]])
					self.environment_inside_humidity = self.setlist(['environment.inside.humidity', [0, 0, 0, 0]])
					self.environment_water_temperature = self.setlist(['environment.water.temperature', [0, 0, 0, 0]])
				elif i == '130316':
					self.environment_inside_refrigerator_temperature = self.setlist(
						['environment.inside.refrigerator.temperature', [0, 0, 0, 0]])
				elif i == '130316_1':
					self.propulsion_port_exhaustTemperature = self.setlist(
						['propulsion.port.exhaustTemperature', [0, 0, 0, 0]])

		self.SK = SK_
		data = self.SK.conf.get('N2K', 'pgn_generate')
		try:
			self.PGN_list = eval(data)
		except:
			self.PGN_list = []

		self.akt126992 = '126992' in self.PGN_list
		self.akt127245 = '127245' in self.PGN_list
		self.akt127250 = '127250' in self.PGN_list
		self.akt127257 = '127257' in self.PGN_list
		self.akt127488 = '127488' in self.PGN_list
		self.akt127488_1 = '127488_1' in self.PGN_list
		self.akt127489 = '127489' in self.PGN_list
		self.akt127489_1 = '127489_1' in self.PGN_list
		self.akt127505 = '127505' in self.PGN_list
		self.akt127505_1 = '127505_1' in self.PGN_list
		self.akt127505_2 = '127505_2' in self.PGN_list
		self.akt127505_3 = '127505_3' in self.PGN_list
		self.akt127508 = '127508' in self.PGN_list
		self.akt128259 = '128259' in self.PGN_list
		self.akt128267 = '128267' in self.PGN_list
		self.akt128275 = '128275' in self.PGN_list
		self.akt129025 = '129025' in self.PGN_list
		self.akt129026 = '129026' in self.PGN_list
		self.akt130306_2 = '130306_2' in self.PGN_list
		self.akt130306_3 = '130306_3' in self.PGN_list
		self.akt130310 = '130310' in self.PGN_list
		self.akt130311 = '130311' in self.PGN_list
		self.akt130316 = '130316' in self.PGN_list
		self.akt130316_1 = '130316_1' in self.PGN_list

		self.N2K = N2K_send()

		self.cycle250 = time.time()
		self.cycle250_2 = time.time() + 0.111
		self.cycle500 = time.time() + 0.123
		self.cycle500_2 = time.time() + 0.241
		self.cycle500_3 = time.time() + 0.363
		self.cycle500_4 = time.time() - 0.025
		self.cycle1000 = time.time() + 0.087
		self.cycle1000_2 = time.time() + 0.207

		self.SK.static_list.append([])
		self.SKa = self.SK.static_list[-1]

		defvar()

	def setlist(self, listx):
		self.SKa.append(listx)
		return listx


	def N2K_cycle(self, tick2a):

		if tick2a > self.cycle250:
			self.cycle250 += 0.250
			if self.akt127488: self.N2K.Send_Engine_Rapid(0, self.propulsion_port_revolutions[1][2]*60., self.N2K.empty16,
														  self.N2K.empty8)
			if self.akt127245: self.N2K.Send_Rudder(self.steering_rudderAngle[1][2])
			if self.akt127250: self.N2K.Send_Heading(self.navigation_headingMagnetic[1][2])
			if self.akt128267: self.N2K.Send_Depth(self.environment_depth_belowTransducer[1][2],
													self.environment_depth_surfaceToTransducer[1][2])
			if self.akt130306_3: self.N2K.Send_Wind_Data(self.environment_wind_speedTrue[1][2],
													self.environment_wind_angleTrueWater[1][2],3)

		if tick2a > self.cycle250_2:
			self.cycle250_2 += 0.250
			if self.akt127488_1: self.N2K.Send_Engine_Rapid(1, int(self.propulsion_starboard_revolutions[1][2])*60.,
													self.N2K.empty16, self.N2K.empty8)

			if self.akt129025: self.N2K.Send_Position_Rapid(self.navigation_position_latitude[1][2],
													self.navigation_position_longitude[1][2])
			if self.akt129026: self.N2K.Send_COG_SOG(self.navigation_courseOverGroundTrue[1][2],
													 self.navigation_speedOverGround[1][2])
			if self.akt130306_2: self.N2K.Send_Wind_Data(self.environment_wind_speedApparent[1][2],
													self.environment_wind_angleApparent[1][2],2)
		if tick2a > self.cycle500:
			self.cycle500 += 0.500
			if self.akt127257: self.N2K.Send_Attitude(self.navigation_attitude_roll[1][2],
													self.navigation_attitude_pitch[1][2],
													self.navigation_attitude_yaw[1][2])
			if self.akt127505: self.N2K.Send_FluidLevel(0, 'diesel', self.tank_diesel_level[1][2],
													self.tank_diesel_capacity[1][2])
			if self.akt130316: self.N2K.Send_Temperature(self.environment_inside_refrigerator_temperature[1][2],
													 'refrigerator')

		if tick2a > self.cycle500_2:
			self.cycle500_2 += 0.500
			if self.akt127505_1: self.N2K.Send_FluidLevel(0, 'fresh water', self.tank_freshwater_level[1][2],
													self.tank_freshwater_capacity[1][2])
			if self.akt127489:
				self.N2K.Send_Engine(
					0,
					self.N2K.empty16,
					self.propulsion_port_oilTemperature[1][2],
					self.propulsion_port_temperature[1][2],
					self.N2K.empty16,
					self.N2K.empty16,
					self.N2K.empty32,
					self.N2K.empty16,
					self.N2K.empty16,
					0,
					self.N2K.empty8,
					self.N2K.empty8)

		if tick2a > self.cycle500_3:
			self.cycle500_3 += 0.500
			if self.akt127505_2: self.N2K.Send_FluidLevel(0, 'greywater', self.tank_greywater_level[1][2],
													self.tank_greywater_capacity[1][2])
			if self.akt130316_1: self.N2K.Send_Temperature(self.propulsion_port_exhaustTemperature[1][2],
													'exhaustTemperature')
		if tick2a > self.cycle500_4:
			self.cycle500_4 += 0.500
			if self.akt127505_3: self.N2K.Send_FluidLevel(0, 'holding', self.tank_holding_level[1][2],
													self.tank_holding_capacity[1][2])
			if self.akt128259: self.N2K.Send_Speed(self.navigation_speedThroughWater[1][2],
													self.navigation_speedOverGround[1][2])

			if self.akt127489_1:
				self.N2K.Send_Engine(
					1,
					self.N2K.empty16,
					self.propulsion_starboard_oilTemperature[1][2],
					self.propulsion_starboard_temperature[1][2],
					self.N2K.empty16,
					self.N2K.empty16,
					self.N2K.empty32,
					self.N2K.empty16,
					self.N2K.empty16,
					0,
					self.N2K.empty8,
					self.N2K.empty8)

		if tick2a > self.cycle1000:
			self.cycle1000 += 1.000
			if self.akt126992: self.N2K.Send_System_Time()
			if self.akt127508: self.N2K.Send_Battery_Status(self.DC_Electrical_Properties_dcSource_voltage[1][2],
													self.DC_Electrical_Properties_dcSource_current[1][2],
													self.DC_Electrical_Properties_dcSource_temperature[1][2])
		if tick2a > self.cycle1000_2:
			self.cycle1000_2 += 1.000
			if self.akt130310: self.N2K.Send_Environmental_Parameters(self.environment_water_temperature[1][2],
													self.environment_outside_temperature[1][2],
													self.environment_outside_pressure[1][2])
			if self.akt130311: self.N2K.Send_Environmental_Parameters2(self.environment_water_temperature[1][2],
													self.environment_inside_humidity[1][2],
													self.environment_outside_pressure[1][2])
			if self.akt128275: self.N2K.Send_Distance_Log(self.navigation_log[1][2], self.navigation_logTrip[1][2])

def signal_handler(signal_, frame):
	print 'You pressed Ctrl+C!'
	SK.stop()
	sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
SK = MySK()
SKN2K = MySK_to_N2K(SK)

timedif = (datetime.datetime.utcnow() - datetime.datetime.now()).total_seconds()
aktiv_N2K = True
if not SKN2K.PGN_list: aktiv_N2K = False

stop = 0
if aktiv_N2K or aktiv_NMEA:
	for iii in range(100):
		time.sleep(0.05)
		tick2 = time.time()
		if aktiv_N2K: SKN2K.N2K_cycle(tick2)
	while 1:
		time.sleep(0.05)
		tick2 = time.time()
		if aktiv_N2K: SKN2K.N2K_cycle(tick2)
