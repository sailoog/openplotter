#!/usr/bin/env python

# This file is part of Openplotter.
# Copyright (C) 2015 by sailoog <https://github.com/sailoog/openplotter>
#
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

import platform, sys, os

def resetfile(file):
	try:
		os.remove(self.currentpath + '/imu/'+file+'.ini')
	except: pass

def readfile(file):
	#result = [imu name, imu address, imu calibration],[press name, press address],[hum name, hum address]
	result = [['', '', 0], ['', ''], ['', '']]
	with open(file+'.ini', "r") as infile:
		for line in infile:
			if 'IMUType=' in line:
				tmp = line.split("=")
				IMUType = tmp[1].strip()
			if 'I2CSlaveAddress=' in line:
				tmp = line.split("=")
				I2CSlaveAddress = tmp[1].strip()
			if 'CompassCalValid=' in line:
				tmp = line.split("=")
				CompassCalValid = tmp[1].strip()
			if 'compassCalEllipsoidValid=' in line:
				tmp = line.split("=")
				compassCalEllipsoidValid = tmp[1].strip()
			if 'AccelCalValid=' in line:
				tmp = line.split("=")
				AccelCalValid = tmp[1].strip()
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
		if I2CSlaveAddress == '0': pass
		else: result[0][1] = hex(int(I2CSlaveAddress))
		if CompassCalValid == 'true' and compassCalEllipsoidValid == 'true' and AccelCalValid == 'true' : result[0][2] = 1
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
	print result

def autoDetect(file):
	SETTINGS_FILE = file
	s = RTIMU.Settings(SETTINGS_FILE)
	imu = RTIMU.RTIMU(s)
	pressure = RTIMU.RTPressure(s)
	humidity = RTIMU.RTHumidity(s)

if platform.machine()[0:3] == 'arm':
	import RTIMU

	reset = sys.argv[1]
	file = sys.argv[2]

	if reset == '1':
		try:
			resetfile(file)
			autoDetect(file)
			readfile(file)
		except Exception, e: print "RTIMU reset failed: "+str(e)
	else:
		try:
			autoDetect(file)
			readfile(file)
		except Exception, e: print "RTIMU detection failed"+str(e)
