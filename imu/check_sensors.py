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

import RTIMU, os

detected_imu=''
detected_pressure=''
calibrated=''


SETTINGS_FILE = "RTIMULib"
s = RTIMU.Settings(SETTINGS_FILE)
imu = RTIMU.RTIMU(s)
if (not imu.IMUInit()) or (imu.IMUName()=='Null IMU'): 
	os.remove('RTIMULib.ini')
else: 
	detected_imu=imu.IMUName()
	if imu.getCompassCalibrationValid() and imu.getCompassCalibrationEllipsoidValid() and imu.getAccelCalibrationValid(): 
		calibrated=1


SETTINGS_FILE2 = "RTIMULib2"
s2 = RTIMU.Settings(SETTINGS_FILE2)
pressure = RTIMU.RTPressure(s2)
if (not pressure.pressureInit()) or (pressure.pressureName()=='none'): 
	os.remove('RTIMULib2.ini')
else: 
	detected_pressure=pressure.pressureName()


if detected_imu: print detected_imu
else: print 'none'

if calibrated: print calibrated
else: print '0'

if detected_pressure: print detected_pressure
else: print 'none'
