#!/usr/bin/env python

import subprocess
from os.path import expanduser

home = expanduser("~")

file=open(home+'/.config/openplotter/ais-sdr.conf', 'r')
data=file.readlines()
file.close()

for index,item in enumerate(data):
	item2=item.strip('\n')
	opcion, valor =item2.split('=')
	if opcion=='gain':
		gain=valor
	if opcion=='ppm':
		ppm=valor
	if opcion=='enable' and valor=='1':
		subprocess.Popen(['rtl_fm', '-f', '161975000', '-g', gain, '-p', ppm, '-s', '48k'])
		subprocess.Popen(['aisdecoder', '-h', '127.0.0.1', '-p', '10110', '-a', 'file', '-c', 'mono', '-d', '-f', '/dev/stdin'])
	if opcion=='enable' and valor=='0':
		subprocess.Popen(['pkill', '-9', 'aisdecoder'])
		subprocess.Popen(['pkill', '-9', 'rtl_fm'])
           

