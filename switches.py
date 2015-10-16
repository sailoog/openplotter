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
import ConfigParser, os, sys
import RPi.GPIO as GPIO
from time import sleep

pathname = os.path.dirname(sys.argv[0])
currentpath = os.path.abspath(pathname)

data_conf = ConfigParser.SafeConfigParser()
data_conf.read(currentpath+'/openplotter.conf')

state1=False
state2=False
state3=False
state4=False

GPIO.setmode(GPIO.BCM)

def switch1(channel):
	global state1
	if GPIO.input(channel):
		if not state1:
			print "on"
			state1=True
	else:
		if state1:
			print "off"
			state1=False

if data_conf.get('SWITCH1', 'enable')=='1':
	channel=int(data_conf.get('SWITCH1', 'gpio'))
	pull_up_down=GPIO.PUD_DOWN
	if data_conf.get('SWITCH1', 'pull_up_down')=='Pull Up': pull_up_down=GPIO.PUD_UP
	GPIO.setup(channel, GPIO.IN, pull_up_down=pull_up_down)
	GPIO.add_event_detect(channel, GPIO.BOTH, callback=switch1)


try:  
	raw_input() 
finally:
    GPIO.cleanup()