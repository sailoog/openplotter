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

import platform

if platform.machine()[0:3]!='arm': print 'Error: This is not a Raspberry Pi -> no GPIO, I2C and SPI'
else: import RTIMU

try:

	SETTINGS_FILE = "RTIMULib"
	s = RTIMU.Settings(SETTINGS_FILE)
	imu = RTIMU.RTIMU(s)

	result = [['',''], ['',''], ['','']]

	with open(SETTINGS_FILE+'.ini', "r") as infile:
		for line in infile:
			if 'IMUType=' in line:
				tmp = line.split("=")
				IMUType = tmp[1].strip()
			if 'I2CSlaveAddress=' in line:
				tmp = line.split("=")
				I2CSlaveAddress = tmp[1].strip()
		if IMUType == '0': pass
		elif IMUType == '1': pass
		elif IMUType == '2': result[0][0] = 'InvenSense MPU-9150'
		elif IMUType == '3': result[0][0] = 'STM L3GD20H + LSM303D'
		elif IMUType == '4': result[0][0] = 'STM L3GD20 + LSM303DLHC'
		elif IMUType == '5': result[0][0] = 'STM LSM9DS0'
		elif IMUType == '6': result[0][0] = 'STM LSM9DS1'
		elif IMUType == '7': result[0][0] = 'InvenSense MPU-9250'
		elif IMUType == '8': result[0][0] = 'STM L3GD20H + LSM303DLHC'
		elif IMUType == '9': result[0][0] = 'Bosch BMX055'
		elif IMUType == '10': result[0][0] = 'Bosch BNX055'
		elif IMUType == '11': result[0][0] = 'InvenSense MPU-9255'
		if I2CSlaveAddress == '0': pass
		else: result[0][1] = hex(int(I2CSlaveAddress))
	
	SETTINGS_FILE2 = "RTIMULib2"
	s2 = RTIMU.Settings(SETTINGS_FILE2)
	pressure = RTIMU.RTPressure(s2)
	humidity = RTIMU.RTHumidity(s2)

	with open(SETTINGS_FILE2+'.ini', "r") as infile:
		for line in infile:
			if 'PressureType=' in line:
				tmp = line.split("=")
				PressureType = tmp[1].strip()
			if 'I2CPressureAddress=' in line:
				tmp = line.split("=")
				I2CPressureAddress = tmp[1].strip()
			if 'HumidityType=' in line:
				tmp = line.split("=")
				HumidityType = tmp[1].strip()
			if 'I2CHumidityAddress=' in line:
				tmp = line.split("=")
				I2CHumidityAddress = tmp[1].strip()
		if PressureType == '0': pass
		elif PressureType == '1': pass
		elif PressureType == '2': result[1][0] = 'BMP180'
		elif PressureType == '3': result[1][0] = 'LPS25H'
		elif PressureType == '4': result[1][0] = 'MS5611'
		elif PressureType == '5': result[1][0] = 'MS5637'
		if I2CPressureAddress == '0': pass
		else: result[1][1] = hex(int(I2CPressureAddress))
		if HumidityType == '0': pass
		elif HumidityType == '1': pass
		elif HumidityType == '2': result[2][0] = 'HTS221'
		elif HumidityType == '3': result[2][0] = 'HTU21D'
		if I2CHumidityAddress == '0': pass
		else: result[2][1] = hex(int(I2CHumidityAddress))

	print 'result:'+str(result)

except Exception, e: print "Error: "+str(e)
