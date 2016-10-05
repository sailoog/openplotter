import signal, sys, time, socket, datetime,json,subprocess, serial

from PyMata.pymata import PyMata
from classes.conf_analog import Conf_analog
from classes.paths import Paths

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
