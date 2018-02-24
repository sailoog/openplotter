#!/usr/bin/python
import signal, sys, time, socket, datetime,subprocess,math

# Control-C signal handler to suppress exceptions if user presses Control C
# This is totally optional.
def signal_handler(sig, frame):
	print('You pressed Ctrl+C!!!!')
	if board is not None:
		board.reset()
	sys.exit(0)
	
# init
signal.signal(signal.SIGINT, signal_handler)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			
# forever loop until user presses Control-C
while 1:	
	tt = time.time()
	Value = tt - math.trunc(tt / 60) * 60

	SignalK = '{"updates": [{"$source":"OPserial.BAT.ABC","values":[{"path": "electrical.batteries.main.voltage","value":'+str(Value)+'}]}]}\n'
	#print SignalK
	sock.sendto(SignalK, ('localhost', 55559))
	time.sleep(1.000)
		
