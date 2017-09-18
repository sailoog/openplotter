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
import sys, os, wx, subprocess, pyudev, serial, time

op_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')
sys.path.append(op_folder+'/classes')
from conf import Conf
from language import Language

class AutoDetect:
	def __init__(self):
		self.serial = 0
		self.mpx = 0

	def readNMEA0183(self, port, baudrate):
		try:
			self.serial = serial.Serial(port, baudrate, timeout=1)
		except:
			return False
		timewait = time.time() + 1.5
		index = 0
		countwrong = 0
		print 'search NMEA0183 on ' + port + ' with baudrate ' + baudrate
		text = ''
		while time.time() < timewait:
			wx.Yield()
			try:
				c = self.serial.read(1)
			except: c = ''
			if c != '':
				b = ord(c)
				# print c
				if b == 10 or b == 13 or (32 <= b < 128):
					index += 1
					if b == 13:
						print '	' + text[:-1]
						text = ''
					elif b == 10:
						pass
					else:
						text += c

				else:
					#print 'countwrong ', b
					countwrong += 1

		if index > 10 and countwrong < index/10:
			print 'found NMEA0183 on ' + port + ' with baudrate ' + str(baudrate)
			return True
		else:
			return False

	def readNMEA0183false(self, port, baudrate):
		try:
			self.serial = serial.Serial(port, baudrate, timeout=1)
		except:
			return False
		timewait = time.time() + 1.5
		index = 0
		countwrong = 0
		print 'search NMEA0183 on ' + port + ' with baudrate ' + baudrate
		text = ''
		nmea = self.serial.readline()
		while time.time() < timewait:
			nmea = self.serial.readline()
			if len(nmea)>0:
			  if nmea[0] in ['$', '!']:
				index += 4
			  else:
				countwrong += 1
			else:
				countwrong += 1

		if index > 10 and countwrong < 2:
			print 'found NMEA0183 on ' + port + ' with baudrate ' + str(baudrate)
			return True
		else:
			return False

	def readNMEA0183name(self, port, baudrate):
		self.serial = serial.Serial(port, baudrate, timeout=1)
		timewait = time.time() + 10.1
		name_list = []
		nmea = self.serial.readline()
		while time.time() < timewait:
			wx.Yield()
			nmea = self.serial.readline()
			print '	' + nmea[:-2]
			if len(nmea) > 7:
				if nmea[1:3] not in name_list:
					name_list.append(nmea[1:3])

		if len(name_list) > 1:
			self.mpx+=1
			return 'MPX'+str(self.mpx)
		elif len(name_list) == 1:
			return name_list[0]
		else:
			return 'UNDEF'

	def readNMEA2000(self, port, baudrate):
		try:
			self.serial = serial.Serial(port, baudrate, timeout=1)
		except:
			return False
		timewait = time.time() + 0.5
		print 'search NMEA2000 on ' + port + ' with baudrate ' + baudrate

		data = [0x10, 0x2, 0xa1, 0x01, 0x01, 0x5d, 0x10, 0x03]
		for i in data:
			self.serial.write(chr(i))
		while time.time() < timewait:
			try:
				c = self.serial.read(1)
			except: c = ''
			if c != '':
				b = ord(c)
				if b == 0x10:
					try:
						c = self.serial.read(1)
					except: c = ''
					if c != '':
						b = ord(c)
						if b == 0x02:
							print 'found NMEA2000 on ' + port + ' with baudrate ' + str(baudrate)
							wx.Yield()
							return True
		print 'not found NMEA2000 on ' + port + ' with baudrate ' + str(baudrate)
		wx.Yield()
		return False


class RedirectText(object):
	def __init__(self, a_wx_text_ctrl):
		self.out = a_wx_text_ctrl

	# def write(self,string):
	#	self.out.WriteText(string)

	def write(self, string):
		wx.CallAfter(self.out.WriteText, string)


def on_setup(event):
	time.sleep(0.1)
	context = pyudev.Context()
	tty_list = []
	index = 0

	conf = Conf()
	home = conf.home
	
	subprocess.call(["pkill", '-f', "signalk-server-node"])
	subprocess.call(["pkill", '-9', "kplex"])
	subprocess.call(['pkill', '-f', '1w_d.py'])
	subprocess.call(['pkill', '-f', 'read_sensors_d.py'])
	subprocess.call(['pkill', '-f', 'mqtt_d.py'])
	subprocess.call(['pkill', '-f', 'SK-base_d.py'])
	subprocess.call(['pkill', '-f', 'N2K-server_d.py'])


	conf_list = []
	data = conf.get('UDEV', 'usbinst')
	try:
		temp_list = eval(data)
	except:
		temp_list = []
	for ii in temp_list:
		conf_list.append(ii)

	print
	print 'search for tty devices'
	for device in context.list_devices(subsystem='tty'):
		# print(device)
		imfd = ''
		ivfd = ''
		id_bus = ''
		id_vendor_id = 'internal'
		id_modell_id = ''
		id_serial_short = ''
		devname = ''
		devpath = ''

		if 'ID_MODEL_FROM_DATABASE' in device:	imfd = device['ID_MODEL_FROM_DATABASE']
		if 'ID_VENDOR_FROM_DATABASE' in device:	ivfd = device['ID_VENDOR_FROM_DATABASE']
		if 'ID_MODEL_ID' in device: id_modell_id = device['ID_MODEL_ID']
		if 'ID_VENDOR_ID' in device: id_vendor_id = device['ID_VENDOR_ID']
		if 'ID_SERIAL_SHORT' in device: id_serial_short = device['ID_SERIAL_SHORT']
		if 'ID_BUS' in device: id_bus = device['ID_BUS']
		if 'DEVNAME' in device: devname = device['DEVNAME']
		if 'DEVPATH' in device: devpath = device['DEVPATH']
		if 'platform' in devpath or id_bus == 'usb':
			devpath = devpath[:-(len(devpath) - devpath.find('/tty'))]
			devpath = devpath[devpath.rfind('/') + 1:]
			if devname != '/dev/ttyAMA0':
				print 'found:', devname, id_vendor_id, id_modell_id, id_serial_short, devpath, imfd, ivfd
				tty_list.append(['', str(id_vendor_id), str(id_modell_id), str(id_serial_short), str(devpath), 'dev',
								 str(devname[5:11]), str(devname), str(imfd), str(ivfd), 0])
			# for item in device:
			# print(item,device[item])
			# print('	  '+str(item)+':'+str(device[item]))
			index += 1

	print
	print 'sort tty devices'

	list_new = []
	for i in sorted(tty_list, key=lambda item: (item[2])):
		list_new.append(i)
	tty_list = list_new

	list_new = []
	for i in sorted(tty_list, key=lambda item: (item[1])):
		list_new.append(i)
	tty_list = list_new

	list_new = []
	for i in sorted(tty_list, key=lambda item: (item[0])):
		list_new.append(i)
	tty_list = list_new

	print
	print 'check if we have to switch from dev to port'

	t0 = 'x'
	t1 = 'x'
	t2 = 'x'
	safe = 0
	index = 0
	for i in tty_list:
		print 'test ',i
		if t0 == i[0] and t1 == i[1] and t2 == i[2]:
			tty_list[safe][5] = 'port'
			i[5] = 'port'
		else:
			t0 = i[0]
			t1 = i[1]
			t2 = i[2]
			safe = index
		index += 1

	print
	print 'search for NMEA0183 in tty devices'
	print
	wx.Yield()
	# self.update()

	baudrate_list = ['4800', '38400', '115200', '9600', '19200', '57600']
	baudrate_listN2K = ['115200']
	auto = AutoDetect()

	for i in tty_list:
		for baud in baudrate_list:
			wx.Yield()
			if i[10] == 0:
				if auto.readNMEA0183(i[7], baud):
					i[10] = str(baud)
					baud = baudrate_list[-1]

	print
	print 'create an autoname for found NMEA0183 devices'

	for i in tty_list:
		if i[10] != 0:
			index = 0
			ttyname = 'ttyOP_' + auto.readNMEA0183name(i[7], i[10])
			for j in tty_list:
				if ttyname in j[6]:
					index += 1
			if index != 0:
				i[0] = str(ttyname + str(index))
			else:
				i[0] = str(ttyname)
			print 'created the name:', i[0]

	print
	print 'search for NMEA2000 in tty devices'
	wx.Yield()

	for i in tty_list:
		if i[7] != '/dev/ttyAMA0' and i[0]=='':
		 print i
		 for baud in baudrate_listN2K:
			print 'n2k',i,baud
			wx.Yield()
			if i[10] == 0:
				print 'start'
				wx.Yield()
				if auto.readNMEA2000(i[7], baud):
					i[10] = str(baud)
					i[0] = 'ttyOP_N2K'
					baud = baudrate_listN2K[-1]
					i = tty_list[-1]
					print 'ja'
					wx.Yield()
					# break
	print
	print '########################## result ################################'
	wx.Yield()
	print
	print 'add new devices to openplotter.conf'

	data = ''
	for i in tty_list:
		if i[10] != 0:
			exists = False
			print i
			for ii in conf_list:
				if (i[1] == ii[1] and i[2] == ii[2] and i[3] == ii[3]) and i[5] != 'port':
					exists = True
			if not exists:
				for ii in conf_list:
					if i[0] == ii[0]:
						exists = True
				if not exists:
					conf_list.append([i[0], i[1], i[2], i[3], i[4], i[5], i[6]])
					data += str([i[0], i[1], i[2], i[3], i[4], i[5], i[6]]) + ','
					i[6] = 1
				else:
					print 'The auto created name ' + i[0] + ' already exists'
					i[10] = 0
	if len(data) > 0:
		print '[UDEV]'
		print 'usbinst = ['
		print data[:-1] + ']'
	else:
		print '- none -'

	conf.set('UDEV', 'usbinst', str(conf_list))

	for i in tty_list:
		if 'ttyOP_N2K' == i[0]:
			if len(conf.get('N2K', 'can_usb')) < 3:
				conf.set('N2K', 'can_usb', '/dev/ttyOP_N2K')
				conf.set('N2K', 'enable', '1')
				print '[N2K]'
				print 'enable = 1'
				print 'can_usb = /dev/ttyOP_N2K'

	print
	print 'add new devices to kplex (not activated and no filter)'

	f1 = open(home + '/.kplex.conf', 'r')
	data = f1.readlines()
	f1.close()

	dataa = ''
	for i in tty_list:
		if i[6] == 1 and i[0] != 'ttyOP_N2K':
			auto_name = 'auto_' + i[0][6:].lower()
			exists = False
			for index, item in enumerate(data):
				if auto_name in item:  exists = True
			if not exists:
				dataa += '#[serial]\n'
				dataa += '#name=' + auto_name + '\n'
				dataa += '#direction=in\n'
				dataa += '#optional=yes\n'
				dataa += '#filename=/dev/' + i[0] + '\n'
				dataa += '#baud=' + str(i[10]) + '\n\n'

	if dataa == '':
		print '- none -'
	else:
		print dataa

	newdata = ''
	for index, item in enumerate(data):
		if '###end of OpenPlotter GUI settings' in item:
			newdata += dataa
		newdata += item

	f1 = open(home + '/.kplex.conf', 'w')
	f1.write(newdata)
	f1.close()


class MyForm(wx.Frame):
	def __init__(self):
		self.serial = 0

		self.conf = Conf()
		Language(self.conf)
		wx.Frame.__init__(self, None, wx.ID_ANY, _('tty auto setup'), size=(720, 350))

		# Add a panel so it looks the correct on all platforms
		panel = wx.Panel(self, wx.ID_ANY)
		log = wx.TextCtrl(panel, wx.ID_ANY, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL)

		self.autostart = wx.CheckBox(panel, label=_('setup autostart on every boot'))
		self.autostart.Bind(wx.EVT_CHECKBOX, self.on_autostart)

		setup = wx.Button(panel, wx.ID_ANY, 'setup')
		setup.Bind(wx.EVT_BUTTON, on_setup)
		close = wx.Button(panel, wx.ID_CLOSE)
		close.Bind(wx.EVT_BUTTON, self.on_close)

		# Add widgets to a sizer		
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.autostart, 0, wx.ALL | wx.EXPAND, 5)
		hbox.Add((0, 0), 1, wx.ALL | wx.EXPAND, 5)
		hbox.Add(setup, 0, wx.ALL | wx.EXPAND, 5)
		hbox.Add(close, 0, wx.ALL | wx.EXPAND, 5)

		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.Add(log, 1, wx.ALL | wx.EXPAND, 5)
		vbox.Add(hbox, 0, wx.ALL | wx.CENTER | wx.EXPAND, 5)
		panel.SetSizer(vbox)

		self.tool_list = []
		data = self.conf.get('TOOLS', 'py')
		try:
			temp_list = eval(data)
		except:
			temp_list = []
		for ii in temp_list:
			self.tool_list.append(ii)
		self.tool = []
		self.tool_exist = False
		for i in self.tool_list:
			if i[2] == 'autosetup_tty.py':
				self.autostart.SetValue(i[3] == '1')
				self.tool.append(i)
				self.tool_exist = True

		# redirect text here
		redir = RedirectText(log)
		sys.stdout = redir

		print _('Auto setup detects hardware. Please make sure that all devices are turned on.')
		print

	def on_autostart(self, event):
		if self.tool_exist:
			if self.autostart.GetValue():
				self.tool[0][3] = '1'
			else:
				self.tool[0][3] = '0'

			self.conf.set('TOOLS', 'py', str(self.tool_list))

	def on_close(self, event):
		self.Close()


# Run the program
if __name__ == "__main__":
	app = wx.App(False)
	frame = MyForm().Show()
	app.MainLoop()
