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

import datetime,json,operator,signal,socket,sys,threading,time,websocket,math,re,geomag
from dateutil import tz
from classes.N2K_send import N2K_send
from classes.actions import Actions
from classes.conf import Conf
from classes.language import Language

class MySK:
	def __init__(self):
		self.list_SK = []
		self.static_list = [[]]
		self.sortCol = 0

		self.conf = Conf()
		self.home = self.conf.home
		self.currentpath = self.home+self.conf.get('GENERAL', 'op_folder')+'/openplotter'
		
		Language(self.conf)

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
		js_up = json.loads(message)
		 
		try:
			js_up = json.loads(message)['updates'][0]
		except:
			return
		
		label = ''
		src = ''
		if '$source' in js_up:
			src = js_up['$source']
		elif 'source' in js_up:
			label = js_up['source']['label']
			src = label
			if 'type' in js_up['source']: 
				if js_up['source']['type'] == 'NMEA0183':
					if 'talker' in js_up['source']: src +='.'+js_up['source']['talker']
					if 'sentence' in js_up['source']: src +='.'+js_up['source']['sentence']
				elif js_up['source']['type'] == 'NMEA2000':
					if 'src' in js_up['source']: src +='.'+js_up['source']['src']
					if 'pgn' in js_up['source']: src +='.'+str(js_up['source']['pgn'])

		try:
			timestamp = js_up['timestamp']
		except:
			timestamp = '2000-01-01T00:00:00.000Z'

		values_ = js_up['values']
		for values in values_:
			path = values['path']
			value = values['value']
			src2 = src
			timestamp2 = timestamp
			if type(value) is dict:
				if 'timestamp' in value: timestamp2 = value['timestamp']

				if '$source' in value:
					src2 = value['$source']
				elif 'source' in value:
					src2 = label
					if 'type' in value['source']: 
						if value['source']['type'] == 'NMEA0183':
							if 'talker' in value['source']: src2 +='.'+value['source']['talker']
							if 'sentence' in value['source']: src2 +='.'+value['source']['sentence']
						elif value['source']['type'] == 'NMEA2000':
							if 'src' in value['source']: src2 +='.'+value['source']['src']
							if 'pgn' in value['source']: src2 +='.'+str(value['source']['pgn'])

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

		if type(value) is float: pass
		elif type(value) is unicode: value = str(value)
		elif type(value) is int: value = float(value)		
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
			for ii in i:
				if type(ii) is list:
					for iii in ii:
						if type(iii) is list:
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

		for i in self.nmea_list[index][1]:
			if type(i) is str:
				NMEA_string += ',' + i
			elif type(i) is list:
				value = i[4][1][2]
				if type(value) is float:
					pass
				else:
					value = 0.0
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
				elif i[1] == 'x.x|deg':
					value_str = str(round(value*57.2957795, 1))
				elif i[1] == 'x.x|kn':
					value_str = str(round(value*1.94384, 1))
				elif i[1] == 'x.x|C':
					value_str = str(round(value-273.15, 1))
				elif i[1] == 'x.x|F':
					value_str = str(round(value*1.8 -459.67, 1))
				elif i[1] == 'x.xx':
					value_str = str(round(value, 2))
				elif i[1] == 'x.xxx':
					value_str = str(round(value, 3))
				elif i[1] == 'x.xxxx':
					value_str = str(round(value, 4))
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
		CRC = hex(reduce(operator.xor, map(ord, 'OC' + NMEA_string), 0)).upper()[2:]
		NMEA_string = '$OC' + NMEA_string + '*' + ('0' + CRC)[-2:] + '\r\n'
		# print NMEA_string
		self.sock.sendto(NMEA_string, ('localhost', 10110))

	def NMEA_cycle(self, tick2a):
		for k in self.cycle_list:
			if tick2a > k[1]:
				k[1] += k[0]
				self.nmea_make(k[2])


class MySK_to_Action_Calc:
	def __init__(self, SK_):
		self.operators_list = [_('was not updated in the last (sec.)'), _('was updated in the last (sec.)'), '=',
							   '<', '<=', '>', '>=', _('contains')]

		self.triggers = []
		self.actions = Actions(SK)

		self.SK = SK_
		self.SKc = []

		self.cycle10 = time.time() + 0.01
		self.read_Action()
		self.read_Calc()

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
					if iii[3] != 0: iii.append(time.time())  # 4 last run
					else: iii.append('')
					var_list=re.findall(r'\<(.*?)\>',iii[1])
					for iiii in var_list:
						exist = False
						for iiiii in self.SKc:
							if iiiii[0] == iiii:
								exist = True
								break
						if not exist: self.SKc.append([iiii, ['', '', '', '', '', '', '', '']])
				self.triggers.append(ii)
				if ii[1] == -1: pass
				else:
					splitlist = ii[1].split('.')
					magnitude = splitlist.pop()
					ii.append(magnitude)  # 6 magnitude
					SKkey2 = '.'.join(splitlist)
					self.SKc.append([SKkey2, ['', '', '', '', '', '', '', '']])
					ii[1] = self.SKc[-1]

	def setlist(self, listx):
		self.SKc.append(listx)
		return listx					
					
	def read_Calc(self):
		tick = time.time()
		self.calcMagneticVariation = self.SK.conf.get('CALCULATE', 'mag_var')=='1'
		self.calcTrueHeading = self.SK.conf.get('CALCULATE', 'hdt')=='1'
		self.calcTrueHeading_dev = self.SK.conf.get('CALCULATE', 'hdt_dev')=='1'
		self.calcRateTurn = self.SK.conf.get('CALCULATE', 'rot')=='1'
		self.calcWindTrueWater = self.SK.conf.get('CALCULATE', 'tw_stw')=='1'
		self.calcWindTrueGround = self.SK.conf.get('CALCULATE', 'tw_sog')=='1'

		if self.calcWindTrueWater or self.calcTrueHeading or self.calcTrueHeading_dev or self.calcRateTurn or self.calcWindTrueGround or self.calcMagneticVariation:
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

		if self.calcMagneticVariation:
			self.navigation_position_latitude = self.setlist(['navigation.position.latitude', [0, 0, 0, 0, 0, 0, 0, 0]])
			self.navigation_position_longitude = self.setlist(['navigation.position.longitude', [0, 0, 0, 0, 0, 0, 0, 0]])
			self.mag_var_rate = float(self.SK.conf.get('CALCULATE', 'mag_var_rate'))
			self.mag_var_rate_tick = tick
			self.mag_var_accuracy = float(self.SK.conf.get('CALCULATE', 'mag_var_accuracy'))

		if self.calcTrueHeading or self.calcTrueHeading_dev:
			self.navigation_headingMagnetic = self.setlist(['navigation.headingMagnetic', [0, 0, 0, 0, 0, 0, 0, 0]])
			self.navigation_magneticVariation = self.setlist(['navigation.magneticVariation', [0, 0, 0, 0, 0, 0, 0, 0]])
			self.hdt_rate = float(self.SK.conf.get('CALCULATE', 'hdt_rate'))
			self.hdt_rate_tick = tick
			self.hdt_accuracy = float(self.SK.conf.get('CALCULATE', 'hdt_accuracy'))
			if self.calcTrueHeading_dev:
				self.deviation_table = []
				data = self.SK.conf.get('COMPASS', 'deviation')
				if not data:
					temp_list = []
					for i in range(37):
						temp_list.append([i*10,i*10])
					self.SK.conf.set('COMPASS', 'deviation', str(temp_list))
					data = self.SK.conf.get('COMPASS', 'deviation')
				try: self.deviation_table=eval(data)
				except: self.deviation_table = []

		if self.calcRateTurn:
			self.navigation_headingMagnetic = self.setlist(['navigation.headingMagnetic', [0, 0, 0, 0, 0, 0, 0, 0]])
			self.rot_rate = float(self.SK.conf.get('CALCULATE', 'rot_rate'))
			self.rot_rate_tick = tick
			self.rot_accuracy = float(self.SK.conf.get('CALCULATE', 'rot_accuracy'))
			self.last_heading = ''
			self.heading_time = ''

		#self.environment_wind_angleApparent = self.setlist(['environment.wind.angleApparent', [0, 0, 0, 0]])
		#self.environment_wind_speedApparent = self.setlist(['environment.wind.speedApparent', [0, 0, 0, 0]])		
		#if self.calcWindTrueWater:
		#	self.navigation_speedThroughWater = self.setlist(['navigation.speedThroughWater', [0, 0, 0, 0]])
		#if self.calcWindTrueGround:
		#	self.navigation_courseOverGroundTrue = self.setlist(['navigation.courseOverGroundTrue', [0, 0, 0, 0]])
		#	self.navigation_speedOverGround = self.setlist(['navigation.speedOverGround', [0, 0, 0, 0]])
		#	self.navigation_headingMagnetic = self.setlist(['navigation.headingMagnetic', [0, 0, 0, 0]])
							
	def Action_set(self, item, cond):
		if cond:
			now = time.time()
			for i in item[4]:
				if item[5] == False:
					try:
						self.actions.run_action(i[0], self.getSKValues(i[1]))
						i[4] = now
					except Exception, e: print str(e)
				else:
					if i[3] == 0: pass
					else:
						if now - i[4] > i[2]:
							try:
								self.actions.run_action(i[0], self.getSKValues(i[1]))
								i[4] = now
							except Exception, e: print str(e)			
			item[5] = True
		else: item[5] = False

	def getSKValues(self, data):
		var_list=re.findall(r'\<(.*?)\>',data)
		for i in var_list:
			for ii in self.SKc:
				if i==ii[0]: 
					data=data.replace('<'+i+'>', str(ii[1][2]))
					break
		return data

	def Action_Calc_cycle(self, tick2a):
		now = tick2a
		for index, item in enumerate(self.triggers):
			error = False
			operator_ = item[2]
			if item[1] == -1:
				try:
					data_value = datetime.datetime.strptime(item[3], '%Y-%m-%dT%H:%M:%S')
					data_value = time.mktime(data_value.timetuple())
					data_value = float(data_value)
				except Exception, e: 
					print str(e)
					error = True
				if not error:
					# less than or equal to
					if operator_ == 4:
						self.Action_set(item, now <= data_value)
					# greater than or equal to
					elif operator_ == 6:
						self.Action_set(item, now >= data_value)
			else:
				if item[6] == 'value':
					try:
						trigger_value = item[1][1][2]
						try:
							data_value = float(item[3])
						except:
							data_value = str(item[3])
					except Exception, e: 
						print str(e)
						error = True
				elif item[6] == 'source':
					try:
						trigger_value = item[1][1][0]
						try:
							data_value = float(item[3])
						except:
							data_value = str(item[3])
					except Exception, e: 
						print str(e)
						error = True
				elif item[6] == 'timestamp':
					try:
						if type(item[1][1][7]) is int:
							trigger_value = 0
						else:
							trigger_value = datetime.datetime.strptime(item[1][1][7][:-5], '%Y-%m-%dT%H:%M:%S')
							trigger_value = time.mktime(trigger_value.timetuple())
						data_value = datetime.datetime.strptime(item[3], '%Y-%m-%dT%H:%M:%S')
						data_value = time.mktime(data_value.timetuple())
					except Exception, e: 
						print str(e)
						error = True
				if not error:
					try:
						if type(data_value) is float:
							try:
								trigger_value_float = float(trigger_value)
							except Exception, e: pass
							else:
								# equal (number)
								if operator_ == 2:
									self.Action_set(item, trigger_value_float == data_value)
								# less than
								elif operator_ == 3:
									self.Action_set(item, trigger_value_float < data_value)
								# less than or equal to
								elif operator_ == 4:
									self.Action_set(item, trigger_value_float <= data_value)
								# greater than
								elif operator_ == 5:
									self.Action_set(item, trigger_value_float > data_value)
								# greater than or equal to
								elif operator_ == 6:
									self.Action_set(item, trigger_value_float >= data_value)
							# contain (number)
							if operator_ == 7:
								self.Action_set(item, str(data_value) in str(trigger_value))
							# not present for
							elif operator_ == 0:
								if trigger_value == 0: self.Action_set(item, True)
								else: self.Action_set(item, now - trigger_value > data_value)
							# present in the last
							elif operator_ == 1:
								self.Action_set(item, now - trigger_value < data_value)
						else:
							# equal (string)
							if operator_ == 2:
								self.Action_set(item, str(trigger_value) == data_value)
							# contain (string)
							elif operator_ == 7:
								self.Action_set(item, data_value in str(trigger_value))
					except Exception, e: print str(e)
					#except: pass
		
		Erg = ''

		if self.calcMagneticVariation:
			lat = self.navigation_position_latitude[1][2]
			lon = self.navigation_position_longitude[1][2]
			timestamp = self.navigation_position_latitude[1][7]
			if lat and lon and timestamp:
				timestamp = datetime.datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%fZ')
				timestamp = timestamp.replace(tzinfo=tz.tzutc())
				timestamp = timestamp.astimezone(tz.tzlocal())
				timestamp_local = time.mktime(timestamp.timetuple())
				if now - self.mag_var_rate_tick > self.mag_var_rate:
					date = datetime.date.today()
					var=float(geomag.declination(lat, lon, 0, date))
					self.mag_var_rate_tick = now
					if now - timestamp_local < self.mag_var_accuracy:
						Erg += '{"path": "navigation.magneticVariation","value":'+str((var*0.017453293))+'},'
					else:
						Erg += '{"path": "navigation.magneticVariation","value": null},'

		if self.calcTrueHeading:
			heading_m = self.navigation_headingMagnetic[1][2]
			var = self.navigation_magneticVariation[1][2]
			timestamp = self.navigation_headingMagnetic[1][7]
			if heading_m and var and timestamp:
				timestamp = datetime.datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%fZ')
				timestamp = timestamp.replace(tzinfo=tz.tzutc())
				timestamp = timestamp.astimezone(tz.tzlocal())
				timestamp_local = time.mktime(timestamp.timetuple())
				if now - self.hdt_rate_tick > self.hdt_rate:
					heading_t = float(heading_m)+float(var)
					self.hdt_rate_tick = now
					if now - timestamp_local < self.hdt_accuracy:
						Erg += '{"path": "navigation.headingTrue","value":'+str(heading_t)+'},'
					else:
						Erg += '{"path": "navigation.headingTrue","value": null},'

		if self.calcTrueHeading_dev:
			heading_m = float(self.navigation_headingMagnetic[1][2])*57.2957795
			var = float(self.navigation_magneticVariation[1][2])*57.2957795
			timestamp = self.navigation_headingMagnetic[1][7]
			if heading_m and var and timestamp:
				timestamp = datetime.datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%fZ')
				timestamp = timestamp.replace(tzinfo=tz.tzutc())
				timestamp = timestamp.astimezone(tz.tzlocal())
				timestamp_local = time.mktime(timestamp.timetuple())
				if now - self.hdt_rate_tick > self.hdt_rate:
					if self.deviation_table:
						ix = int(heading_m / 10)
						heading_m = self.deviation_table[ix][1]+(self.deviation_table[ix+1][1]-self.deviation_table[ix][1])*0.1*(heading_m-self.deviation_table[ix][0])
					if heading_m<0: heading_m=360+heading_m
					elif heading_m>360: heading_m=-360+heading_m
					heading_t = heading_m+var
					self.hdt_rate_tick = now
					if now - timestamp_local < self.hdt_accuracy:
						Erg += '{"path": "navigation.headingTrue","value":'+str(heading_t*0.017453293)+'},'
					else:
						Erg += '{"path": "navigation.headingTrue","value": null},'

		if self.calcRateTurn:
			heading_m = self.navigation_headingMagnetic[1][2]
			timestamp = self.navigation_headingMagnetic[1][7]
			if heading_m and timestamp:
				timestamp = datetime.datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%fZ')
				timestamp = timestamp.replace(tzinfo=tz.tzutc())
				timestamp = timestamp.astimezone(tz.tzlocal())
				timestamp_local = time.mktime(timestamp.timetuple())
				if now - self.rot_rate_tick > self.rot_rate:
					if not self.last_heading:
						self.last_heading = float(heading_m)
						self.heading_time = time.time()					
					else:
						heading_change = float(heading_m)-self.last_heading
						last_heading_time = self.heading_time
						self.heading_time = time.time()
						self.last_heading = float(heading_m)
						rot = heading_change/((self.heading_time - last_heading_time)/60)	
						self.rot_rate_tick = now
						if now - timestamp_local < self.rot_accuracy:
							Erg += '{"path": "navigation.rateOfTurn","value":'+str(rot)+'},'
						else:
							Erg += '{"path": "navigation.rateOfTurn","value": null},'

		if Erg:
			SignalK='{"updates":[{"$source":"OPcalculations","values":['
			SignalK+=Erg[0:-1]+']}]}\n'		
			self.sock.sendto(SignalK, ('127.0.0.1', 55557))	
		'''
		if self.calcWindTrueWater | self.calcWindTrueGround:
			Erg = ''
			if self.calcWindTrueWater:
				x = self.environment_wind_speedApparent[1][2] * math.sin(self.environment_wind_angleApparent[1][2])
				y1 = self.environment_wind_speedApparent[1][2] * math.cos(self.environment_wind_angleApparent[1][2])
				y2 = y1 - self.navigation_speedThroughWater[1][2]

				speed = math.sqrt(x**2+y2**2)
				if y2 != 0:
					beta2 = math.degrees(math.atan(x/y2))
					if y2 < 0:
						if self.environment_wind_angleApparent[1][2]>=0:
							beta2 += 180
						else:
							beta2 -= 180
				else:
					if self.environment_wind_angleApparent[1][2]>0:
						beta2 = 90
					else:
						beta2 = -90
				Erg += '{"path": "environment.wind.angleTrueWater","value":'+str(0.017453293*beta2)+'},'
				Erg += '{"path": "environment.wind.speedTrue","value":'+str(speed)+'},'

			if self.calcWindTrueGround:
				beta1 = self.environment_wind_angleApparent[1][2] + self.navigation_headingMagnetic[1][2]
				x1 = self.environment_wind_speedApparent[1][2] * math.sin(beta1)
				y1 = self.environment_wind_speedApparent[1][2] * math.cos(beta1)
				x2 = self.navigation_speedOverGround[1][2] * math.sin(self.navigation_courseOverGroundTrue[1][2])
				y2 = self.navigation_speedOverGround[1][2] * math.cos(self.navigation_courseOverGroundTrue[1][2])
				x3 = x1 - x2
				y3 = y1 - y2
				
				speed = math.sqrt(x3**2+y3**2)
				if y3 != 0:
					beta3 = math.degrees(math.atan(x3/y3))
					if y3 > 0:
						if x3 < 0:
							beta3 += 360
					else:
						beta3 += 180
				else:
					if x3 > 0:
						beta3 = 90
					else:
						beta3 = 270

				Erg += '{"path": "environment.wind.angleTrueGround","value":'+str(0.017453293*beta3)+'},'
				Erg += '{"path": "environment.wind.speedOverGround","value":'+str(speed)+'},'

			SignalK='{"updates":[{"$source":"OPcalculations","values":['
			SignalK+=Erg[0:-1]+']}]}\n'		
			self.sock.sendto(SignalK, ('127.0.0.1', 55557))	
		'''

def signal_handler(signal_, frame):
	print 'You pressed Ctrl+C!'
	SK.stop()
	sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)
SK = MySK()
SKN2K = MySK_to_N2K(SK)
SKNMEA = MySK_to_NMEA(SK)
SKAction = MySK_to_Action_Calc(SK)
SK.daemon = True
SK.start()

aktiv_N2K = True
aktiv_NMEA = True
aktiv_Action = False
if not SKN2K.PGN_list: aktiv_N2K = False
if not SKNMEA.nmea_list: aktiv_NMEA = False
if SKAction.triggers: aktiv_Action = True
if SKAction.calcMagneticVariation: aktiv_Action = True
if SKAction.calcTrueHeading: aktiv_Action = True
if SKAction.calcTrueHeading_dev: aktiv_Action = True
if SKAction.calcRateTurn: aktiv_Action = True
#if SKAction.calcWindTrueWater: aktiv_Action = True
#if SKAction.calcWindTrueGround: aktiv_Action = True

stop = 0
if aktiv_N2K or aktiv_NMEA or aktiv_Action:
	while 1:
		time.sleep(0.02)
		tick2 = time.time()
		if aktiv_N2K: SKN2K.N2K_cycle(tick2)
		if aktiv_NMEA: SKNMEA.NMEA_cycle(tick2)
		if aktiv_Action: SKAction.Action_Calc_cycle(tick2)
