#!/usr/bin/env python
# This file is part of Openplotter.
# Copyright (C) 2019 by sailoog <https://github.com/sailoog/openplotter>
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

import fcntl
import sys
import os
import time
import tty
import termios, pyudev, serial

class raw(object):
    def __init__(self, stream):
        self.stream = stream
        self.fd = self.stream.fileno()
    def __enter__(self):
        self.original_stty = termios.tcgetattr(self.stream)
        tty.setcbreak(self.stream)
    def __exit__(self, type, value, traceback):
        termios.tcsetattr(self.stream, termios.TCSANOW, self.original_stty)

class nonblocking(object):
    def __init__(self, stream):
        self.stream = stream
        self.fd = self.stream.fileno()
    def __enter__(self):
        self.orig_fl = fcntl.fcntl(self.fd, fcntl.F_GETFL)
        fcntl.fcntl(self.fd, fcntl.F_SETFL, self.orig_fl | os.O_NONBLOCK)
    def __exit__(self, *args):
        fcntl.fcntl(self.fd, fcntl.F_SETFL, self.orig_fl)

		
context = pyudev.Context()
monitor = pyudev.Monitor.from_netlink(context)
monitor.filter_by(subsystem='tty')
print 'Please connect (or disconnect and reconnect) CANUSB adapter'


for device in iter(monitor.poll, None):
	if device.action == 'add':
		value = device['DEVPATH']
		port = value[len(value) - value.find('/tty'):]
		port = port[port.rfind('/') + 1:]
		print port
		try:
			ser = serial.Serial('/dev/'+port, 9600, timeout=0.5)
		except:
			print 'Can not open serial device (CAN-USB) connected on: '+port
			sys.exit(0)
		ser.write('0')
		time.sleep(0.2)
		sertext=ser.readline()
		if len(sertext)>=1:
			#time.sleep(0.2)
			#ser.write('0')
			c='0'
			while c<>'9':
				i=20
				while i>0:
					if ser.inWaiting():
						sertext=ser.readline()
						print sertext[:-1]
					else:
						i-=1
						time.sleep(0.05)
				i=180
				with raw(sys.stdin):
					with nonblocking(sys.stdin):				
						while i>0:
							try:
								c = sys.stdin.read(1)
								if c in ['1','2','3','4','5','6','7','8','9','0']:
									ser.write(c)
									i=-5
									#print 'ser.write('+c+')',i
									
							except IOError:
								#print 'not ready',i
								time.sleep(.1)						
							i-=1
						if i>-2:
							ser.write('0')
							#print 'ser.write(0)'
		sys.exit(0)
								