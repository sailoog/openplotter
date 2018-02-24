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

import socket
import time


class N2K_send:
	def __init__(self):
		self.empty8 = 0xFF
		self.empty16 = 0xFFFF
		self.empty32 = 0xFFFFFFFF

		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.data = 0

	def Send_System_Time(self):
		length = 8
		lPGN = 126992
		self.set_header(length, lPGN)

		time_ = time.time()
		date_16 = int(int(time_) / 86400)
		time_32 = long((time_ - date_16 * 86400) * 10000)

		i = 8
		self.data[i + 0] = 0x01
		self.data[i + 1] = 0x01

		self.set_data16(2, int(date_16), date_16)
		self.set_data32(4, long(time_32), time_32)
		self.send_UDP()

	def Send_Rudder(self, angle):
		length = 8
		lPGN = 127245
		self.set_header(length, lPGN)

		i = 8
		self.data[i + 0] = 0x01
		self.data[i + 6] = 0xFF
		self.data[i + 7] = 0xFF

		self.set_data16(2, int(angle * 10000), angle)
		self.set_data16(4, int(angle * 10000), angle)
		self.send_UDP()

	def Send_Heading(self, angle):
		length = 8
		lPGN = 127250
		self.set_header(length, lPGN)

		i = 8
		self.data[i + 0] = 0x01
		self.data[i + 7] = 0x01

		self.set_data16(1, int(angle * 10000), angle)
		self.send_UDP()

	def Send_Attitude(self, Yaw, Pitch, Roll):
		length = 8
		lPGN = 127257
		self.set_header(length, lPGN)

		self.set_data16(1, int(Yaw * 10000), Yaw)
		self.set_data16(3, int(Pitch * 10000), Pitch)
		self.set_data16(5, int(Roll * 10000), Roll)
		self.send_UDP()

	def Send_Engine_Rapid(self, Instance, Rpm, BoostPressure, TiltTrim):
		length = 8
		lPGN = 127488
		self.set_header(length, lPGN)

		self.set_data8(0, Instance, Instance)
		self.set_data16(1, int(Rpm * 4.0), Rpm)
		self.set_data16(3, int(BoostPressure * 10.0), BoostPressure)
		self.set_data8(5, int(TiltTrim), TiltTrim)
		self.send_UDP()

	def Send_Engine(self, Instance, OilPressure, OilTemperature, Temperature, AlternatorPotential, FuelRate,
					TotalEngineHours, CoollantPressure, FuelPressure, Status, EngineLoad, EngineTorque):
		length = 26
		lPGN = 127489
		self.set_header(length, lPGN)

		self.set_data8(0, Instance, Instance)
		self.set_data16(1, int(OilPressure * 10.0), OilPressure)
		self.set_data16(3, int(OilTemperature * 10.0), OilTemperature)
		self.set_data16(5, int(Temperature * 100), Temperature)
		self.set_data16(7, int(AlternatorPotential * 100), AlternatorPotential)
		self.set_data16(9, int(FuelRate * 10.0), FuelRate)
		self.set_data32(11, long(TotalEngineHours), TotalEngineHours)
		self.set_data16(15, int(CoollantPressure * 10.0), CoollantPressure)
		self.set_data16(17, int(FuelPressure * 10.0), FuelPressure)
		self.set_data8(19, self.empty8, self.empty8)
		self.set_data32(20, long(Status), Status)
		self.set_data8(24, int(EngineLoad), EngineLoad)
		self.set_data8(25, int(EngineTorque), EngineTorque)
		self.send_UDP()

	def Send_FluidLevel(self, Instance, SK_name, Level, Capacity):
		length = 8
		lPGN = 127505
		self.set_header(length, lPGN)

		# 0:Fuel
		# 1:Water
		# 2:Gray water
		# 3:Live well
		# 4:Oil
		# 5:Black water
		ftype = 0
		if "petrol" in SK_name:
			ftype = 0
		elif "diesel" in SK_name:
			ftype = 0
		elif "lpg" in SK_name:
			ftype = 0
		elif "fresh water" in SK_name:
			ftype = 1
		elif "greywater" in SK_name:
			ftype = 2
		elif "rum" in SK_name:
			ftype = 3
		elif "holding" in SK_name:
			ftype = 5

		i = 8
		self.data[i + 0] = (Instance & 15) + (ftype & 15) * 16

		self.set_data16(1, int(Level * 250), Level)
		self.set_data32(3, long(Capacity * 10.0), Capacity)
		self.set_data8(7, self.empty8, self.empty8)
		self.send_UDP()

	def Send_Battery_Status(self, Voltage, Current, Temp):
		length = 8
		lPGN = 127508
		self.set_header(length, lPGN)

		self.set_data16(1, int(Voltage * 100), Voltage)
		self.set_data16(3, int(Current * 10), Current)
		self.set_data16(5, int(Temp * 100), Temp)
		self.send_UDP()

	def Send_Speed(self, SpeedWater, SpeedGround):
		length = 8
		lPGN = 128259
		self.set_header(length, lPGN)

		self.set_data16(1, int(SpeedWater * 100.0), SpeedWater)
		self.set_data16(3, int(SpeedGround * 100.0), SpeedGround)
		self.set_data8(5, self.empty8, self.empty8)
		self.set_data8(6, self.empty8, self.empty8)
		self.set_data8(7, self.empty8, self.empty8)
		self.send_UDP()

	def Send_Depth(self, Depth, Offset):
		length = 8
		lPGN = 128267
		self.set_header(length, lPGN)

		self.set_data32(1, long(Depth * 100), Depth)
		self.set_data16(5, int(Offset * 1.0), Offset)
		self.set_data8(7, self.empty8, self.empty8)
		self.send_UDP()

	def Send_Distance_Log(self, Log, TripLog):
		length = 14
		lPGN = 128275
		self.set_header(length, lPGN)

		time_ = time.time()
		date_16 = int(int(time_) / 86400)
		time_32 = long((time_ - date_16 * 86400) * 10000)

		self.set_data16(0, date_16, date_16)
		self.set_data32(2, time_32, time_32)
		self.set_data32(6, long(Log), Log)
		self.set_data32(10, long(TripLog), TripLog)
		self.send_UDP()

	def Send_Position_Rapid(self, Latitude, Longitude):
		length = 8
		lPGN = 129025
		self.set_header(length, lPGN)

		self.set_data32(0, long(Latitude * 10000000), Latitude)
		self.set_data32(4, long(Longitude * 10000000), Longitude)
		self.send_UDP()

	def Send_COG_SOG(self, CourseGround, SpeedGround):
		length = 8
		lPGN = 129026
		self.set_header(length, lPGN)

		i = 8
		self.data[i + 5] = 0xFF
		self.data[i + 6] = 0xFF
		self.data[i + 7] = 0xFF

		self.set_data16(2, int(CourseGround * 10000.0), CourseGround)
		self.set_data16(4, int(SpeedGround * 100.0), SpeedGround)
		self.send_UDP()

	def Send_Wind_Data(self, Speed, Angle, type):
		# type 
		# 0=True (referenced to North)
		# 1=Magnetic
		# 2=Apparent
		# 3=True (boat referenced)
	
		length = 8
		lPGN = 130306
		self.set_header(length, lPGN)

		i = 8
		self.data[i + 0] = 0x01

		self.set_data16(1, int(Speed * 100.0), Speed)
		self.set_data16(3, int(Angle * 10000.0), Angle)
		self.set_data8(5, type, type)
		self.send_UDP()

	def Send_Environmental_Parameters(self, WaterTemp, OutsideAirTemp, Pressure):
		#	length = 8
		#	self.data = bytearray(length+9)
		#	lPGN = 130310
		#	WaterTemp_16 = int(WaterTemp * 100 + 27315)
		#	OutsideAirTemp_16 = int(OutsideAirTemp * 100 + 27315)
		#	Pressure_16 = int(Pressure)
		#	i=8
		#	data[i+1] = WaterTemp_16 & 255
		#	data[i+2] = (WaterTemp_16 >> 8) & 255
		#	data[i+3] = OutsideAirTemp_16 & 255
		#	data[i+4] = (OutsideAirTemp_16 >> 8) & 255
		#	data[i+5] = Pressure_16 & 255
		#	data[i+6] = (Pressure_16 >> 8) & 255
		#	if not b1:data[i+1] = data[i+2] = 255
		#	if not b2:data[i+3] = data[i+4] = 255
		#	if not b3:data[i+5] = data[i+6] = 255
		#
		#	data[0] = 0x94 #command
		#	data[1] = (length + 6) #Actisense length
		#	data[2] = 6 #priority
		#	data[3] = lPGN &255#PGN
		#	data[4] = (lPGN >> 8)&255 #PGN
		#	data[5] = (lPGN >> 16)&255 #PGN
		#	data[6] = 255 #receiver
		#	data[7] = length #NMEA len
		#	print " ".join("%s"% (('0'+hex(n)[2:])[-2:]) for n in data)
		#	sock.sendto(data, ('127.0.0.1', 7778))

		length = 8
		lPGN = 130310
		self.set_header(length, lPGN)

		self.set_data16(1, int(WaterTemp * 100), WaterTemp)
		self.set_data16(3, int(OutsideAirTemp * 100), OutsideAirTemp)
		self.set_data16(5, int(Pressure / 100), Pressure)
		#	print " ".join("%s"% (('0'+hex(n)[2:])[-2:]) for n in data)
		self.send_UDP()

	def Send_Environmental_Parameters2(self, WaterTemp, Humidity, Pressure):
		length = 8
		lPGN = 130311
		self.set_header(length, lPGN)

		self.set_data16(2, int(WaterTemp * 100), WaterTemp)
		self.set_data16(4, int(Humidity * 25000), Humidity)
		self.set_data16(6, int(Pressure / 100), Pressure)
		self.send_UDP()

	def Send_Temperature(self, Temp, SK_name):
		length = 8
		lPGN = 130316
		self.set_header(length, lPGN)

		Temp_24 = long(Temp * 1000)

		i = 8
		if 'water.temperature' in SK_name:
			source = 0
		elif 'outside.temperature' in SK_name:
			source = 1
		elif 'inside.temperature' in SK_name:
			source = 2
		elif 'engineRoom' in SK_name:
			source = 3
		elif 'heamainCabin' in SK_name:
			source = 4
		elif 'liveWell' in SK_name:
			source = 5
		elif 'baitWell' in SK_name:
			source = 6
		elif 'refrigerator' in SK_name:
			source = 7
		elif 'heating' in SK_name:
			source = 8
		elif 'dewPointTemperature' in SK_name:
			source = 9
		elif 'apparentWindChillTemperature' in SK_name:
			source = 10
		elif 'theoreticalWindChillTemperature' in SK_name:
			source = 11
		elif 'heatIndexTemperature' in SK_name:
			source = 12
		elif 'freezer' in SK_name:
			source = 13
		elif 'exhaustTemperature' in SK_name:
			source = 14
		else:
			source = 252

		self.data[i + 2] = source
		self.data[i + 3] = Temp_24 & 255
		self.data[i + 4] = (Temp_24 >> 8) & 255
		self.data[i + 5] = (Temp_24 >> 16) & 255
		self.set_data16(6, int(Temp * 10), Temp)
		self.send_UDP()

	# 00 = Sea Temperature
	# 01 = Outside Temperature
	# 02 = Inside Temperature
	# 03 = Engine Room Temperature
	# 04 = Main Cabin Temperature
	# 05 = Live Well Temperature
	# 06 = Bait Well Temperature
	# 07 = Refrigeration Temperature
	# 08 = Heating System Temperature
	# 09 = Dew Point Temperature
	# 10 = Wind Chill Temperature, Apparent
	# 11 = Wind Chill Temperature, Theoretical
	# 12 = Heat Index Temperature
	# 13 = Freezer Temperature
	# 14 = Exhaust Gas Temperature
	# 15 through 128 Reserved
	# 129 through 252 Generic Temperature Sources other than those defined

	def set_header(self, length, lPGN):
		self.data = bytearray(length + 9)
		self.data[0] = 0x94  # command
		self.data[1] = (length + 6)  # Actisense length
		self.data[2] = 6  # priority
		self.data[3] = lPGN & 255  # PGN
		self.data[4] = (lPGN >> 8) & 255  # PGN
		self.data[5] = (lPGN >> 16) & 255  # PGN
		self.data[6] = 255  # receiver
		self.data[7] = length  # NMEA len

	def set_data32(self, point, value, raw):
		if raw == self.empty32:
			value = raw
		self.data[8 + point] = value & 255
		self.data[9 + point] = (value >> 8) & 255
		self.data[10 + point] = (value >> 16) & 255
		self.data[11 + point] = (value >> 24) & 255

	def set_data16(self, point, value, raw):
		if raw == self.empty16:
			value = raw
		self.data[8 + point] = value & 255
		self.data[9 + point] = (value >> 8) & 255

	def set_data8(self, point, value, raw):
		if raw == self.empty8:
			value = raw
		self.data[8 + point] = value & 255

	def send_UDP(self):
		self.sock.sendto(self.data, ('127.0.0.1', 55560))
