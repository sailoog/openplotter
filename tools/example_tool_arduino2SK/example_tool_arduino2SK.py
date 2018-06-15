#!/usr/bin/python
'''
//Arduino code
int i=0;
// the setup routine runs once when you press reset:
void setup() {
  Serial.begin(9600);
}

void loop() {
  if (i>100) i=0;
  i++;
  Serial.print("ArduinoValue:");
  Serial.println(i);
  delay(300);        // delay in between reads for stability
}
'''

import signal, sys, time, socket, datetime, subprocess, math, serial

# Control-C signal handler to suppress exceptions if user presses Control C
# This is totally optional.
def signal_handler(sig, frame):
	print('You pressed Ctrl+C!!!!')
	sys.exit(0)
	
# init
signal.signal(signal.SIGINT, signal_handler)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
ser = serial.Serial('/dev/ttyOP_LEONARDO', 9600, timeout=1)
ser.flush()

Value = 0			
# forever loop until user presses Control-C
while 1:	
	serLine = ser.readline()
	if 'ArduinoValue:' in serLine:
		Value = serLine[13:-1]
		#print Value
		
	SignalK = '{"updates": [{"$source":"OPserial.BAT.V1","values":[{"path": "electrical.batteries.main.voltage","value":'+str(Value)+'}]}]}\n'
	#print SignalK
	sock.sendto(SignalK, ('localhost', 55559))
	time.sleep(0.300)
		
