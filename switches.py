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
import ConfigParser, os, sys, subprocess
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

#[0]= _('nothing')
#[1]= _('command')
#[2]= _('reset')
#[3]= _('shutdown')
#[4]= _('stop NMEA multiplexer')
#[5]= _('start NMEA multiplexer')
#[6]= _('stop Signal K server')
#[7]= _('start Signal K server')
#[8]= _('stop WiFi access point')
#[9]= _('start WiFi access point')
#[10]= _('stop SDR-AIS')
#[11]= _('start SDR-AIS')

def switch_options(switch,option):
	if option=='0': return
	if option=='2': subprocess.Popen(['sudo', 'reboot'])
	if option=='3': subprocess.Popen(['sudo', 'halt'])

def switch1(channel):
	global state1
	if GPIO.input(channel):
		if not state1:
			switch_options('1', data_conf.get('SWITCH1', 'on_action'))
			state1=True
	else:
		if state1:
			switch_options('1', data_conf.get('SWITCH1', 'off_action'))
			state1=False

def switch2(channel):
	global state2
	if GPIO.input(channel):
		if not state2:
			switch_options('2', data_conf.get('SWITCH2', 'on_action'))
			state2=True
	else:
		if state2:
			switch_options('2', data_conf.get('SWITCH2', 'off_action'))
			state2=False

def switch3(channel):
	global state3
	if GPIO.input(channel):
		if not state3:
			switch_options('3', data_conf.get('SWITCH3', 'on_action'))
			state3=True
	else:
		if state3:
			switch_options('3', data_conf.get('SWITCH3', 'off_action'))
			state3=False

def switch4(channel):
	global state4
	if GPIO.input(channel):
		if not state4:
			switch_options('4', data_conf.get('SWITCH4', 'on_action'))
			state4=True
	else:
		if state4:
			switch_options('4', data_conf.get('SWITCH4', 'off_action'))
			state4=False

GPIO.setmode(GPIO.BCM)

if data_conf.get('SWITCH1', 'enable')=='1':
	channel1=int(data_conf.get('SWITCH1', 'gpio'))
	pull_up_down=GPIO.PUD_DOWN
	if data_conf.get('SWITCH1', 'pull_up_down')=='Pull Up': pull_up_down=GPIO.PUD_UP
	GPIO.setup(channel1, GPIO.IN, pull_up_down=pull_up_down)
	GPIO.add_event_detect(channel1, GPIO.BOTH, callback=switch1)

if data_conf.get('SWITCH2', 'enable')=='1':
	channel2=int(data_conf.get('SWITCH2', 'gpio'))
	pull_up_down=GPIO.PUD_DOWN
	if data_conf.get('SWITCH2', 'pull_up_down')=='Pull Up': pull_up_down=GPIO.PUD_UP
	GPIO.setup(channel2, GPIO.IN, pull_up_down=pull_up_down)
	GPIO.add_event_detect(channel2, GPIO.BOTH, callback=switch2)

if data_conf.get('SWITCH3', 'enable')=='1':
	channel3=int(data_conf.get('SWITCH3', 'gpio'))
	pull_up_down=GPIO.PUD_DOWN
	if data_conf.get('SWITCH3', 'pull_up_down')=='Pull Up': pull_up_down=GPIO.PUD_UP
	GPIO.setup(channel3, GPIO.IN, pull_up_down=pull_up_down)
	GPIO.add_event_detect(channel3, GPIO.BOTH, callback=switch3)

if data_conf.get('SWITCH4', 'enable')=='1':
	channel4=int(data_conf.get('SWITCH4', 'gpio'))
	pull_up_down=GPIO.PUD_DOWN
	if data_conf.get('SWITCH4', 'pull_up_down')=='Pull Up': pull_up_down=GPIO.PUD_UP
	GPIO.setup(channel4, GPIO.IN, pull_up_down=pull_up_down)
	GPIO.add_event_detect(channel4, GPIO.BOTH, callback=switch4)

try:  
	while True:
		sleep(1000)
finally:
    GPIO.cleanup()