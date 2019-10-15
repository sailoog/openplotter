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

import serial
import socket
import sys

from classes.conf import Conf

conf = Conf()

activ = False
activ = conf.get('N2K', 'output') == '1'
if not activ:
	sys.exit(0)

try:
	ser = serial.Serial(conf.get('N2K', 'can_usb'), 115200, timeout=0.5)
except:
	print 'failed to start N2K output server on ' + conf.get('N2K', 'can_usb')
	sys.exit(0)

	
Quelle = '127.0.0.1'  # Adresse des eigenen Rechners
Port = 55560

e_udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # s.o.
e_udp_sock.bind((Quelle, Port))


def SendCommandtoSerial(data):
	crc = 0
	# start = codecs.decode('1002', 'hex_codec')
	start = (0x10, 0x02)
	ende = (0x10, 0x03)
	i = 0
	while i < data[1] + 2:
		crc += data[i]
		i += 1
	crc = (256 - crc) & 255
	data[data[1] + 2] = crc
	i = 0
	ser.write(chr(start[0]))
	ser.write(chr(start[1]))
	while i < data[1] + 3:
		ser.write(chr(data[i]))
		# print format(data[i], '02x')
		if data[i] == 0x10:
			ser.write(chr(data[i]))
		i += 1
	ser.write(chr(ende[0]))
	ser.write(chr(ende[1]))

def put_recive_to_serial():
	while 1:
		data1, addr = e_udp_sock.recvfrom(512)
		# Data buffer had to be potenz of 2
		data = bytearray(data1)
		if data[7] + 9 == len(data):
			SendCommandtoSerial(data)
			datap = ''
			dat = 0
			for i in range(8, data[7] + 9):
				dat = dat + data[i]
				datap += ' ' + ('0' + hex(data[i])[2:])[-2:]

put_recive_to_serial()
