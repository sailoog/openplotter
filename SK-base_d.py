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

import datetime
import json
import logging
import operator
import signal
import socket
import sys
import threading
import time
import websocket

from classes.N2K_send import N2K_send
from classes.actions import Actions
from classes.conf import Conf
from classes.language import Language
from classes.paths import Paths


class MySK:
	def __init__(self):
		logging.basicConfig()
		self.list_SK = []
		self.static_list = [[]]
		self.sortCol = 0

		paths = Paths()
		self.home = paths.home
		self.currentpath = Paths().currentpath
		self.conf = Conf(paths)

		Language(self.conf.get('GENERAL', 'lang'))

		self.data = []

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
		src = ''
		js_up = json.loads(message)
		if 'updates' in js_up:
			js_up = json.loads(message)['updates'][0]
		else:
			return
		js_source = js_up['source']
		label = js_source['label']
		if 'src' in js_source:
			src = js_source['src']
		elif 'talker' in js_source:
			src = js_source['talker']
		else:
			src = 'xx'

		if 'timestamp' in js_up:
			timestamp = js_up['timestamp']
		else:
			timestamp = '2000-01-01T00:00:00.000Z'

		values_ = js_up['values']
		srclabel2 = ''

		for values in values_:
			path = values['path']
			value = values['value']

			if type(value) is dict:
				if 'timestamp' in value:
					timestamp = value['timestamp']
				if 'source' in value:
					try:
						src2 = value['source']['talker']
					except:
						src2 = 'xx'
					srclabel2 = label + '.' + src2

				for lvalue in value:
					if lvalue in ['timestamp', 'source']:
						pass
					else:
						path2 = path + '.' + lvalue
						value2 = value[lvalue]
						self.update_add(value2, path2, srclabel2, timestamp)
			else:
				srclabel = label + '.' + src
				path2 = path + '.' + 'value'
				self.update_add(value, path2, srclabel, timestamp)

	def update_add(self, value, path, src, timestamp):
		# SRC SignalK Value Unit Interval Status Description timestamp	private_Unit private_Value priv_Faktor priv_Offset		
		#  0    1      2     3      4        5        6          7           8             9           10          11			

		if type(value) is list: value = value[0]

		if type(value) is float:
			pass
		elif type(value) is int:
			value = float(value)
		#else:
			#value = 0.0

		index = 0
		exists = False
		for i in self.list_SK:
			if path == i[1]:
				if src == i[0]:
					exists = True
					i[2] = value
					i[7] = timestamp
					#break
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
		ws.close()

	def on_open(self, ws):
		pass

	def run(self):
		self.ws = websocket.WebSocketApp("ws://localhost:3000/signalk/v1/stream?subscribe=self",
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
		# self.PGN_list = ['126992','127245','127250','127257','127488','127488_1','127489','127489_1','127505','127505_1','127505_2','127505_3','127508','128259','128267','128275','129025','129026','130306','130310','130311','130316','130316_1']

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
						['DC Electrical Properties.dcSource.voltage', [0, 0, 0, 0]])
					self.DC_Electrical_Properties_dcSource_current = self.setlist(
						['DC Electrical Properties.dcSource.current', [0, 0, 0, 0]])
					self.DC_Electrical_Properties_dcSource_temperature = self.setlist(
						['DC Electrical Properties.dcSource.temperature', [0, 0, 0, 0]])
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
				elif i == '130306':
					self.environment_wind_directionTrue = self.setlist(['environment.wind.directionTrue', [0, 0, 0, 0]])
					self.environment_wind_speedTrue = self.setlist(['environment.wind.speedTrue', [0, 0, 0, 0]])
				elif i == '130310':
					self.environment_outside_pressure = self.setlist(['environment.outside.pressure', [0, 0, 0, 0]])
					self.environment_outside_temperature = self.setlist(
						['environment.outside.temperature', [0, 0, 0, 0]])
					self.environment_water_temperature = self.setlist(['environment.water.temperature', [0, 0, 0, 0]])
				elif i == '130311':
					self.environment_outside_pressure = self.setlist(['environment.outside.pressure', [0, 0, 0, 0]])
					self.environment_humidity = self.setlist(['environment.humidity', [0, 0, 0, 0]])
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
		self.akt130306 = '130306' in self.PGN_list
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
			if self.akt127488: self.N2K.Send_Engine_Rapid(0, self.propulsion_port_revolutions[1][2], self.N2K.empty16,
														  self.N2K.empty8)
			if self.akt127245: self.N2K.Send_Rudder(self.steering_rudderAngle[1][2])
			if self.akt127250: self.N2K.Send_Heading(self.navigation_headingMagnetic[1][2])
			if self.akt128267: self.N2K.Send_Depth(self.environment_depth_belowTransducer[1][2],
												   self.environment_depth_surfaceToTransducer[1][2])

		if tick2a > self.cycle250_2:
			self.cycle250_2 += 0.250
			if self.akt127488_1: self.N2K.Send_Engine_Rapid(1, int(self.propulsion_starboard_revolutions[1][2]),
															self.N2K.empty16, self.N2K.empty8)

			if self.akt129025: self.N2K.Send_Position_Rapid(self.navigation_position_latitude[1][2],
															self.navigation_position_longitude[1][2])
			if self.akt129026: self.N2K.Send_COG_SOG(self.navigation_courseOverGroundTrue[1][2],
													 self.navigation_speedOverGround[1][2])
			if self.akt130306: self.N2K.Send_Wind_Data(self.environment_wind_speedTrue[1][2],
													   self.environment_wind_directionTrue[1][2])
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
																	   self.environment_humidity[1][2],
																	   self.environment_outside_pressure[1][2])
			if self.akt128275: self.N2K.Send_Distance_Log(self.navigation_log[1][2], self.navigation_logTrip[1][2])


class MySK_to_NMEA:
	def __init__(self, SK_):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

		self.SK = SK_
		self.nmea_list = []

		data = self.SK.conf.get('NMEA0183', 'sentences')
		try:
			temp_list = eval(data)
		except:
			temp_list = []
		for ii in temp_list:
			self.nmea_list.append(ii)

		self.SK.static_list.append([])
		self.SKb = self.SK.static_list[-1]

		for i in self.nmea_list:
			# print 'self.nmea_list',i
			for ii in i:
				if type(ii) is list:
					for iii in ii:
						if type(iii) is list:
							# print 'iii ',iii[0]
							self.SKb.append([iii[0], [0, 0, 0, 0]])
							iii.append(self.SKb[-1])

		self.cycle_list = []
		index = 0
		for i in self.nmea_list:
			cycle = i[2]
			self.cycle_list.append([cycle, time.time() + cycle, index])
			index += 1

	def nmea_make(self, index):
		NMEA_string = str(self.nmea_list[index][0])

		# print self.nmea_list[index][1]
		for i in self.nmea_list[index][1]:
			# print 'i ',i
			if type(i) is str:
				NMEA_string += ',' + i
			elif type(i) is list:
				value = i[4][1][2]
				if i[2] == '+':
					value = value + i[3]
				elif i[2] == '-':
					value = value - i[3]
				elif i[2] == '*':
					value = value * i[3]
				elif i[2] == '/':
					value = value / i[3]
				value_str = ''
				if i[1] == 'x.x':
					value_str = str(round(value, 1))
				elif i[1] == 'x.xx':
					value_str = str(round(value, 2))
				elif i[1] == 'hhmmss.ss':
					value_str = datetime.datetime.utcnow().strftime('%H%M%S.00')
				elif i[1] == 'ddmmyy':
					value_str = datetime.datetime.utcnow().strftime('%d%m%y')
				elif i[1] == 'ddmm.mm':
					value = abs(value)
					h = int(value)
					l = round((value - h) * 60, 5)
					value_str = ('00' + str(int(value)))[-2:] + str(l)
					str(round(value, 2))
				elif i[1] == 'dddmm.mm':
					value = abs(value)
					h = int(value)
					l = round((value - h) * 60, 5)
					value_str = ('000' + str(int(value)))[-3:] + str(l)
					str(round(value, 2))
				elif i[1] == 'N/S':
					if value > 0:
						value_str = 'N'
					else:
						value_str = 'S'
				elif i[1] == 'E/W':
					if value > 0:
						value_str = 'E'
					else:
						value_str = 'W'
				NMEA_string += ',' + value_str
		NMEA_string = '$OC' + NMEA_string + '*' + hex(reduce(operator.xor, map(ord, 'OC' + NMEA_string), 0)).upper()[
												  2:] + '\r\n'
		# print NMEA_string
		self.sock.sendto(NMEA_string, ('127.0.0.1', 55565))

	def NMEA_cycle(self, tick2a):
		for k in self.cycle_list:
			if tick2a > k[1]:
				k[1] += k[0]
				self.nmea_make(k[2])


class MySK_to_Action:
	def __init__(self, SK_):
		self.operators_list = [_('was not updated in the last (sec.)'), _('was updated in the last (sec.)'), '=',
							   '<', '<=', '>', '>=', _('is on'), _('is off'), _('contains')]

		self.tdif = time.time() - time.mktime(datetime.datetime.utcnow().timetuple())
		self.tdif = round(self.tdif, 0)
		self.triggers = []
		self.actions = Actions(SK)

		self.SK = SK_
		self.SKc = []

		self.cycle10 = time.time() + 0.01
		self.read_Action()

	def read_Action(self):
		self.SK.static_list.append([])
		self.SKc = self.SK.static_list[-1]

		data = self.SK.conf.get('ACTIONS', 'triggers')
		try:
			temp_list = eval(data)
		except:
			temp_list = []
		for ii in temp_list:
			if ii[0] == 1:
				ii.append(False)  # 5 state
				for iii in ii[4]:
					if iii[3] == 2: iii[2] *= 60
					if iii[3] == 3: iii[2] = (iii[2] * 60) * 60
					if iii[3] == 4: iii[2] = ((iii[2] * 24) * 60) * 60
					iii.append('')  # 4 last run
				self.triggers.append(ii)
				if ii[1] == -1: pass
				else:
					SKkey2 = ii[1]
					self.SKc.append([SKkey2, [0, 0, 0, 0, 0, 0, 0, 0]])
					ii[1] = self.SKc[-1]

	def Action_set(self, item, start):
		if start:
			now = time.time()
			for i in item[4]:
				if item[5] == False:
					item[5] = True
					try:
						self.actions.run_action(i[0], i[1])
						i[4] = now
					except Exception, e: print str(e)
				else:
					if i[3] == 0: pass
					else:
						if now - i[4] > i[2]:
							try:
								self.actions.run_action(i[0], i[1])
								i[4] = now
							except Exception, e: print str(e)				
		else:
			item[5] = False

	def Action_cycle(self, tick2a):
		if tick2a > self.cycle10:
			self.cycle10 += 0.1
			for index, item in enumerate(self.triggers):
				if item[1] == -1:
					self.Action_set(item, True)
				else:
					# trigger = item[1][0]
					trigger_value = item[1][1][2]
					now = time.time() - self.tdif
					operator_ = item[2]
					data = item[3]
					if type(item[1][1][7]) is int:
						trigger_value_timestamp = 0
					else:
						trigger_value_timestamp = datetime.datetime.strptime(item[1][1][7][:-5], '%Y-%m-%dT%H:%M:%S')
						trigger_value_timestamp = time.mktime(trigger_value_timestamp.timetuple())
					try:
						data_value = float(data)
					except:
						data_value = str(data)
					try:
						if trigger_value_timestamp:
							if type(data_value) is float:
								# not present for
								if operator_ == 0:
									self.Action_set(item, now - trigger_value_timestamp > data_value)
								# present in the last
								elif operator_ == 1:
									self.Action_set(item, now - trigger_value_timestamp < data_value)
								# equal (number)
								elif operator_ == 2:
									self.Action_set(item, float(trigger_value) == data_value)
								# less than
								elif operator_ == 3:
									self.Action_set(item, float(trigger_value) < data_value)
								# less than or equal to
								elif operator_ == 4:
									self.Action_set(item, float(trigger_value) <= data_value)
								# greater than
								elif operator_ == 5:
									self.Action_set(item, float(trigger_value) > data_value)
								# greater than or equal to
								elif operator_ == 6:
									self.Action_set(item, float(trigger_value) >= data_value)
								# switch on
								elif operator_ == 7:
									self.Action_set(item, float(trigger_value) == 1.0)
								# switch off
								elif operator_ == 8:
									self.Action_set(item, float(trigger_value) == 0.0)
								# contain (number)
								if operator_ == 9:
									self.Action_set(item, data_value in float(trigger_value))
							else:
								# equal (string)
								if operator_ == 2:
									self.Action_set(item, trigger_value == data_value)
								# contain (string)
								elif operator_ == 9:
									self.Action_set(item, data_value in trigger_value)
					except Exception, e:
						print str(e)
					# except: pass


def signal_handler(signal_, frame):
	print 'You pressed Ctrl+C!'
	SK.stop()
	sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)
SK = MySK()
SKN2K = MySK_to_N2K(SK)
SKNMEA = MySK_to_NMEA(SK)
SKAction = MySK_to_Action(SK)
SK.daemon = True
SK.start()

aktiv_N2K = True
aktiv_NMEA = True
aktiv_Action = True
if not SKN2K.PGN_list: aktiv_N2K = False
if not SKNMEA.nmea_list: aktiv_NMEA = False
if not SKAction.triggers: aktiv_Action = False

stop = 0
run_ = True
while run_:

	time.sleep(0.02)
	tick2 = time.time()
	if aktiv_N2K: SKN2K.N2K_cycle(tick2)
	if aktiv_NMEA: SKNMEA.NMEA_cycle(tick2)
	if aktiv_Action: SKAction.Action_cycle(tick2)
	#if stop > 5000:
	#	SK.stop()
	# run_=False
	#stop += 1
