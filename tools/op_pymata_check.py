#!/usr/bin/python

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
import signal, sys, time
from PyMata.pymata import PyMata

def signal_handler(sig, frame):
	print('You pressed Ctrl+C!!!!')
	board.close()
	if board is not None:
		board.reset()
	sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
board = PyMata("/dev/ttyOP_FIRM")
time.sleep(1)
board.reset
board.close
