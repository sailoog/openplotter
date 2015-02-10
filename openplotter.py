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

import wx, subprocess, time, sys, os, ConfigParser, gettext
from wx.lib.mixins.listctrl import CheckListCtrlMixin

home = os.path.expanduser('~')
pathname = os.path.dirname(sys.argv[0])
currentpath = os.path.abspath(pathname)

class CheckListCtrl(wx.ListCtrl, CheckListCtrlMixin):
	def __init__(self, parent):
		wx.ListCtrl.__init__(self)
		CheckListCtrlMixin.__init__(self)

class MyFrame(wx.Frame):
		
		def __init__(self, parent, title):

			gettext.install('openplotter', currentpath+'/locale', unicode=False)
			self.presLan_en = gettext.translation('openplotter', currentpath+'/locale', languages=['en'])
			self.presLan_ca = gettext.translation('openplotter', currentpath+'/locale', languages=['ca'])
			self.presLan_es = gettext.translation('openplotter', currentpath+'/locale', languages=['es'])
			self.read_conf()
			self.language=self.data_conf.get('GENERAL', 'lang')
			if self.language=='en':self.presLan_en.install()
			if self.language=='ca':self.presLan_ca.install()
			if self.language=='es':self.presLan_es.install()

			wx.Frame.__init__(self, parent, title=title, size=(700,420))
			
			self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))

			self.icon = wx.Icon(currentpath+'/openplotter.ico', wx.BITMAP_TYPE_ICO)
			self.SetIcon(self.icon)

			menubar = wx.MenuBar()
			self.startup = wx.Menu()
			self.startup_item1 = self.startup.Append(wx.ID_ANY, _('OpenCPN'), _('If selected OpenCPN will run at startup'), kind=wx.ITEM_CHECK)
			self.Bind(wx.EVT_MENU, self.check_startup, self.startup_item1)
			self.startup_item1b = self.startup.Append(wx.ID_ANY, _('no OpenGL'), _('If OpenCPN + no OpenGL are selected, OpenCPN will run at startup without OpenGL acceleration'), kind=wx.ITEM_CHECK)
			self.Bind(wx.EVT_MENU, self.check_startup, self.startup_item1b)
			self.startup_item1c = self.startup.Append(wx.ID_ANY, _('fullscreen'), _('If OpenCPN + fullscreen are selected, OpenCPN will run at startup in fullscreen mode'), kind=wx.ITEM_CHECK)
			self.Bind(wx.EVT_MENU, self.check_startup, self.startup_item1c)
			self.startup.AppendSeparator()
			self.startup_item2 = self.startup.Append(wx.ID_ANY, _('NMEA multiplexor (Kplex)'), _('If selected Kplex will run at startup'), kind=wx.ITEM_CHECK)
			self.Bind(wx.EVT_MENU, self.check_startup, self.startup_item2)
			self.startup_item2_2 = self.startup.Append(wx.ID_ANY, _('Set time from NMEA'), _('You need to define a valid NMEA time data input and run kplex at startup'), kind=wx.ITEM_CHECK)
			self.Bind(wx.EVT_MENU, self.check_startup, self.startup_item2_2)
			self.startup_item3 = self.startup.Append(wx.ID_ANY, _('Remote desktop (x11vnc)'), _('If selected x11vnc will run at startup'), kind=wx.ITEM_CHECK)
			self.Bind(wx.EVT_MENU, self.check_startup, self.startup_item3)
			menubar.Append(self.startup, _('Startup'))
			settings = wx.Menu()
			time_item1 = settings.Append(wx.ID_ANY, _('Set time zone'), _('Set time zone in the new window'))
			self.Bind(wx.EVT_MENU, self.time_zone, time_item1)
			time_item2 = settings.Append(wx.ID_ANY, _('Set time from NMEA'), _('Set system time from NMEA data'))
			self.Bind(wx.EVT_MENU, self.time_gps, time_item2)
			settings.AppendSeparator()
			gpsd_item1 = settings.Append(wx.ID_ANY, _('Set GPSD'), _('Set GPSD in the new window'))
			self.Bind(wx.EVT_MENU, self.reconfigure_gpsd, gpsd_item1)
			menubar.Append(settings, _('Settings'))

			self.lang = wx.Menu()
			self.lang_item1 = self.lang.Append(wx.ID_ANY, _('English'), _('Set English language'), kind=wx.ITEM_CHECK)
			self.Bind(wx.EVT_MENU, self.lang_en, self.lang_item1)
			self.lang_item2 = self.lang.Append(wx.ID_ANY, _('Catalan'), _('Set Catalan language'), kind=wx.ITEM_CHECK)
			self.Bind(wx.EVT_MENU, self.lang_ca, self.lang_item2)
			self.lang_item3 = self.lang.Append(wx.ID_ANY, _('Spanish'), _('Set Spanish language'), kind=wx.ITEM_CHECK)
			self.Bind(wx.EVT_MENU, self.lang_es, self.lang_item3)
			menubar.Append(self.lang, _('Language'))

			self.helpm = wx.Menu()
			self.helpm_item1=self.helpm.Append(wx.ID_ANY, _('&About'), _('About OpenPlotter'))
			self.Bind(wx.EVT_MENU, self.OnAboutBox, self.helpm_item1)
			menubar.Append(self.helpm, _('&Help'))

			self.SetMenuBar(menubar)

########################################################

			nmea=wx.StaticBox(self, label=_(' Add NMEA input / output '), size=(690, 105), pos=(5, 5))
			estilo = nmea.GetFont()
			estilo.SetWeight(wx.BOLD)
			nmea.SetFont(estilo)

			self.SerDevLs = []
			self.SerialCheck('/dev/rfcomm')
			self.SerialCheck('/dev/ttyUSB')
			self.SerialCheck('/dev/ttyS')
			self.SerialCheck('/dev/ttyACM')
			self.deviceComboBox = wx.ComboBox(self, choices=self.SerDevLs, style=wx.CB_DROPDOWN, size=(130, 30), pos=(80, 30))
			if self.SerDevLs : self.deviceComboBox.SetValue(self.SerDevLs[0])

			self.bauds = ['2400', '4800', '9600', '19200', '38400', '57600', '115200']
			self.baudComboBox = wx.ComboBox(self, choices=self.bauds, style=wx.CB_READONLY, size=(90, 30), pos=(215, 30))
			self.baudComboBox.SetValue('4800')

			wx.StaticText(self, label='Serial', pos=(320, 36))

			self.add_serial_in =wx.Button(self, label=_('Input'), pos=(375, 30))
			self.Bind(wx.EVT_BUTTON, self.add_serial_input, self.add_serial_in)

			self.add_serial_out =wx.Button(self, label=_('Output'), pos=(475, 30))
			self.Bind(wx.EVT_BUTTON, self.add_serial_output, self.add_serial_out)

			self.type = ['TCP', 'UDP']
			self.typeComboBox = wx.ComboBox(self, choices=self.type, style=wx.CB_READONLY, size=(65, 30), pos=(10, 70))
			self.typeComboBox.SetValue('TCP')

			self.address = wx.TextCtrl(self, -1, size=(130, 30), pos=(80, 70))

			self.port = wx.TextCtrl(self, -1, size=(90, 30), pos=(215, 70))

			wx.StaticText(self, label='Network', pos=(313, 76))

			self.add_network_in =wx.Button(self, label=_('Input'), pos=(375, 70))
			self.Bind(wx.EVT_BUTTON, self.add_network_input, self.add_network_in)

			self.add_gpsd_in =wx.Button(self, label=_('GPSD'), pos=(475, 70))
			self.Bind(wx.EVT_BUTTON, self.add_gpsd_input, self.add_gpsd_in)

			self.add_network_out =wx.Button(self, label=_('Output'), pos=(575, 70))
			self.Bind(wx.EVT_BUTTON, self.add_network_output, self.add_network_out)

########################################################

			in_out=wx.StaticBox(self, label=_(' NMEA inputs / outputs '), size=(475, 255), pos=(5, 110))
			estilo = in_out.GetFont()
			estilo.SetWeight(wx.BOLD)
			in_out.SetFont(estilo)

			self.list_input = wx.ListCtrl(self, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER, size=(295, 90), pos=(10, 130))
			self.list_input.InsertColumn(0, _('Type'), width=50)
			self.list_input.InsertColumn(1, _('Port/Address'), width=130)
			self.list_input.InsertColumn(2, _('Bauds/Port'), width=115)

			inputs = wx.StaticText(self, label=_('Inputs'), pos=(320, 135))
			estilo = inputs.GetFont()
			estilo.SetWeight(wx.BOLD)
			inputs.SetFont(estilo)

			self.button_delete_input =wx.Button(self, label=_('Delete selected'), pos=(315, 155))
			self.Bind(wx.EVT_BUTTON, self.delete_input, self.button_delete_input)

			self.list_output = wx.ListCtrl(self, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER, size=(295, 90), pos=(10, 230))
			self.list_output.InsertColumn(0, _('Type'), width=50)
			self.list_output.InsertColumn(1, _('Port/Address'), width=130)
			self.list_output.InsertColumn(2, _('Bauds/Port'), width=115)

			outputs = wx.StaticText(self, label=_('Outputs'), pos=(320, 235))
			estilo = outputs.GetFont()
			estilo.SetWeight(wx.BOLD)
			outputs.SetFont(estilo)

			self.button_delete_output =wx.Button(self, label=_('Delete selected'), pos=(315, 255))
			self.Bind(wx.EVT_BUTTON, self.delete_output, self.button_delete_output)

			self.show_output =wx.Button(self, label=_('Show output'), pos=(315, 290))
			self.Bind(wx.EVT_BUTTON, self.show_output_window, self.show_output)

			self.restart =wx.Button(self, label=_('Restart'), pos=(10, 325))
			self.Bind(wx.EVT_BUTTON, self.restart_multiplex, self.restart)

			self.button_apply =wx.Button(self, label=_('Apply changes'), pos=(120, 325))
			self.Bind(wx.EVT_BUTTON, self.apply_changes, self.button_apply)

########################################################

			ais_sdr=wx.StaticBox(self, label=_('AIS-SDR reception'), size=(210, 110), pos=(485, 110))
			estilo = ais_sdr.GetFont()
			estilo.SetWeight(wx.BOLD)
			ais_sdr.SetFont(estilo)

			self.ais_sdr_enable = wx.CheckBox(self, label=_('Enable'), pos=(490, 125))
			self.ais_sdr_enable.Bind(wx.EVT_CHECKBOX, self.OnOffAIS)

			self.gain = wx.TextCtrl(self, -1, size=(45, 30), pos=(595, 145))
			self.button_test_gain =wx.Button(self, label=_('Gain'), pos=(490, 145))
			self.Bind(wx.EVT_BUTTON, self.test_gain, self.button_test_gain)

			self.ppm = wx.TextCtrl(self, -1, size=(45, 30), pos=(595, 180))
			self.button_test_ppm =wx.Button(self, label=_('Correction'), pos=(490, 180))
			self.Bind(wx.EVT_BUTTON, self.test_ppm, self.button_test_ppm)

########################################################

			water_speed=wx.StaticBox(self, label=_('STW simulation'), size=(210, 45), pos=(485, 220))
			estilo = water_speed.GetFont()
			estilo.SetWeight(wx.BOLD)
			water_speed.SetFont(estilo)

			self.water_speed_enable = wx.CheckBox(self, label=_('SOG  -->  STW'), pos=(490, 235))
			self.water_speed_enable.Bind(wx.EVT_CHECKBOX, self.onoffwaterspeed)

########################################################

			wifi=wx.StaticBox(self, label=_('NMEA WiFi server'), size=(210, 100), pos=(485, 265))
			estilo = wifi.GetFont()
			estilo.SetWeight(wx.BOLD)
			wifi.SetFont(estilo)

			self.wifi_enable = wx.CheckBox(self, label=_('Enable'), pos=(490, 280))
			self.wifi_enable.Bind(wx.EVT_CHECKBOX, self.onwifi_enable)
			
			self.wlan = wx.TextCtrl(self, -1, size=(55, 25), pos=(490, 305))
			wx.StaticText(self, label=_('WiFi device'), pos=(550, 310))
			self.passw = wx.TextCtrl(self, -1, size=(100, 25), pos=(490, 335))
			wx.StaticText(self, label=_('Password'), pos=(595, 340))
########################################################

			self.CreateStatusBar()

			self.Centre()

			self.Show(True)

			self.read_kplex_conf()

			self.set_conf()

		
		def read_conf(self):
			self.data_conf = ConfigParser.SafeConfigParser()
			self.data_conf.read(currentpath+'/openplotter.conf')

		def SerialCheck(self,dev):
			num = 0
			for _ in range(99):
				s = dev + str(num)
				d = os.path.exists(s)
				if d == True:
					self.SerDevLs.append(s)      
				num = num + 1

		def read_kplex_conf(self):
			self.inputs = []
			self.outputs = []
			try:
				file=open(home+'/.kplex.conf', 'r')
				data=file.readlines()
				file.close()
				for index,item in enumerate(data):
					if '[serial]' in item:
						if 'direction=in' in data[index+1]:
							input_tmp=[]
							input_tmp.append('Serial')
							item2=self.extract_value(data[index+2])
							input_tmp.append(item2)
							item3=self.extract_value(data[index+3])
							input_tmp.append(item3)
							self.inputs.append(input_tmp)
						if 'direction=out' in data[index+1]:
							output_tmp=[]
							output_tmp.append('Serial')
							item2=self.extract_value(data[index+2])
							output_tmp.append(item2)
							item3=self.extract_value(data[index+3])
							output_tmp.append(item3)
							self.outputs.append(output_tmp)
					if '[tcp]' in item:
						if 'direction=in' in data[index+1]:
							input_tmp=[]
							input_tmp.append('TCP')
							item2=self.extract_value(data[index+2])
							input_tmp.append(item2)
							item3=self.extract_value(data[index+3])
							input_tmp.append(item3)
							self.inputs.append(input_tmp)
						if 'direction=out' in data[index+1]:
							output_tmp=[]
							output_tmp.append('TCP')
							output_tmp.append(_('all address'))
							item2=self.extract_value(data[index+2])
							output_tmp.append(item2)
							self.outputs.append(output_tmp)
					if '[broadcast]' in item:
						if 'direction=in' in data[index+1]:
							input_tmp=[]
							input_tmp.append('UDP')
							input_tmp.append(_('all address'))
							item2=self.extract_value(data[index+2])
							input_tmp.append(item2)
							self.inputs.append(input_tmp)
				self.write_inputs()
				self.write_outputs()

			except IOError:
				self.ShowMessage(_('Configuration file does not exist. Add inputs and apply changes.'))

		def extract_value(self,data):
			option, value =data.split('=')
			value=value.strip()
			return value

		def write_inputs(self):
			self.list_input.DeleteAllItems()
			for i in self.inputs:
				index = self.list_input.InsertStringItem(sys.maxint, i[0])
				self.list_input.SetStringItem(index, 1, i[1])
				self.list_input.SetStringItem(index, 2, i[2])
		def write_outputs(self):
			self.list_output.DeleteAllItems()
			for i in self.outputs:
				index = self.list_output.InsertStringItem(sys.maxint, i[0])
				self.list_output.SetStringItem(index, 1, i[1])
				self.list_output.SetStringItem(index, 2, i[2])

		def apply_changes(self,event):
			data='# For advanced manual configuration, please visit: http://www.stripydog.com/kplex/configuration.html\n# Editing this file by openplotter GUI, can eliminate manual settings.\n# You should not modify defaults.\n\n'
			for index,item in enumerate(self.inputs):
				if 'Serial' in item[0]:
					data=data+'[serial]\ndirection=in\nfilename='+item[1]+'\nbaud='+item[2]+'\noptional=yes\n\n'
				if 'TCP' in item[0]:
					data=data+'[tcp]\ndirection=in\naddress='+item[1]+'\nport='+item[2]+'\nmode=client\npersist=yes\nkeepalive=yes\noptional=yes\n\n'
				if 'UDP' in item[0]:
					data=data+'[broadcast]\ndirection=in\nport='+item[2]+'\noptional=yes\n\n'
			if not '[broadcast]\ndirection=in\nport=10110' in data: data=data+'#default input\n[broadcast]\ndirection=in\nport=10110\noptional=yes\n\n'
			for index,item in enumerate(self.outputs):
				if 'Serial' in item[0]:
					data=data+'[serial]\ndirection=out\nfilename='+item[1]+'\nbaud='+item[2]+'\noptional=yes\n\n'
				if 'TCP' in item[0]:
					data=data+'[tcp]\ndirection=out\nport='+item[2]+'\nmode=server\n\n'
			if not '[tcp]\ndirection=out\nport=10110' in data: data=data+'#default output\n[tcp]\ndirection=out\nport=10110\nmode=server\n\n'
			file = open(home+'/.kplex.conf', 'w')
			file.write(data)
			file.close()
			self.restart_kplex()
			self.read_kplex_conf()

		def delete_input(self,event):
			num = len(self.inputs)
			for i in range(num):
				if self.list_input.IsSelected(i):
					del self.inputs[i]
			self.write_inputs()

		def delete_output(self,event):
			num = len(self.outputs)
			for i in range(num):
				if self.list_output.IsSelected(i):
					del self.outputs[i]
			self.write_outputs()

		def add_serial_input(self,event):
			input_tmp=[]
			found=False
			input_tmp.append('Serial')
			port=self.deviceComboBox.GetValue()
			input_tmp.append(port)
			bauds=self.baudComboBox.GetValue()
			input_tmp.append(bauds)
			for sublist in self.inputs:
				if sublist[1] == port:found=True
			for sublist in self.outputs:
				if sublist[1] == port:found=True
			if found==False:
				self.inputs.append(input_tmp)
				self.write_inputs()
			else:
				self.ShowMessage(_('It is impossible to set input because this port is already in use.'))

		def add_serial_output(self,event):
			output_tmp=[]
			found=False
			output_tmp.append('Serial')
			port=self.deviceComboBox.GetValue()
			output_tmp.append(port)
			bauds=self.baudComboBox.GetValue()
			output_tmp.append(bauds)
			for sublist in self.inputs:
				if sublist[1] == port:found=True
			for sublist in self.outputs:
				if sublist[1] == port:found=True
			if found==False:
				self.outputs.append(output_tmp)
				self.write_outputs()
			else:
				self.ShowMessage(_('It is impossible to set output because this port is already in use.'))
		
		def add_network_input(self,event):
			input_tmp=[]
			type_=self.typeComboBox.GetValue()
			address=self.address.GetValue()
			port=self.port.GetValue()
			input_tmp.append(type_)
			input_tmp.append(address)
			input_tmp.append(port)
			if port:
				self.inputs.append(input_tmp)
				self.write_inputs()
			else:
				self.ShowMessage(_('You have to enter at least a port number.'))

		def add_gpsd_input(self,event):
			input_tmp=[]
			type_='TCP'
			address='127.0.0.1'
			port='2947'
			input_tmp.append(type_)
			input_tmp.append(address)
			input_tmp.append(port)
			self.inputs.append(input_tmp)
			self.write_inputs()
		
		def add_network_output(self,event):
			output_tmp=[]
			found=False
			type_=self.typeComboBox.GetValue()
			address=self.address.GetValue()
			port=self.port.GetValue()
			output_tmp.append(type_)
			output_tmp.append(address)
			output_tmp.append(port)
			if port:
				if 'TCP' in type_:
					self.outputs.append(output_tmp)
					self.write_outputs()
				else:
					self.ShowMessage(_('Sorry. It is not possible to create UDP outputs.'))
			else:
				self.ShowMessage(_('You have to enter at least a port number.'))
		
		def enableAISconf(self):
			self.gain.SetEditable(True)
			self.gain.SetForegroundColour((wx.NullColor))
			self.ppm.SetEditable(True)
			self.ppm.SetForegroundColour((wx.NullColor))
			
		def disableAISconf(self):
			self.gain.SetEditable(False)
			self.gain.SetForegroundColour((180,180,180))
			self.ppm.SetEditable(False)
			self.ppm.SetForegroundColour((180,180,180))
					
		def OnOffAIS(self, e):
			w_close=subprocess.call(['pkill', '-f', 'waterfall.py'])
			rtl_close=subprocess.call(['pkill', '-9', 'rtl_test'])
			isChecked = self.ais_sdr_enable.GetValue()
			if isChecked:
				output=subprocess.check_output('lsusb')
				if 'DVB-T' in output:
					self.disableAISconf() 
					gain=self.gain.GetValue()
					ppm=self.ppm.GetValue()
					rtl_fm=subprocess.Popen(['rtl_fm', '-f', '161975000', '-g', gain, '-p', ppm, '-s', '48k'], stdout = subprocess.PIPE)
					aisdecoder=subprocess.Popen(['aisdecoder', '-h', '127.0.0.1', '-p', '10110', '-a', 'file', '-c', 'mono', '-d', '-f', '/dev/stdin'], stdin = rtl_fm.stdout)         
					msg=_('SDR-AIS reception enabled')
				else:
					self.ais_sdr_enable.SetValue(False)
					msg=_('SDR device not found.\nSDR-AIS reception disabled.')
			else: 
				self.enableAISconf()
				aisdecoder=subprocess.call(['pkill', '-9', 'aisdecoder'])
				rtl_fm=subprocess.call(['pkill', '-9', 'rtl_fm'])
				msg=_('SDR-AIS reception disabled')
			self.write_conf()
			self.SetStatusText('')
			self.ShowMessage(msg)

		def onoffwaterspeed(self, e):
			sender = e.GetEventObject()
			isChecked = sender.GetValue()
			if isChecked:
				self.SetStatusText(_('Searching NMEA Speed Over Ground data in localhost:10110 ...'))
				sog_result=subprocess.Popen(['python', currentpath+'/sog2sow.py'], stdout=subprocess.PIPE)
				msg=''
				while sog_result.poll() is None:
					l = sog_result.stdout.readline()
					if 'Failed to connect with localhost:10110.' in l:
						msg+=_('Failed to connect with localhost:10110.')
					if 'Error: ' in l: msg+='\n'+l
					if 'No data, trying to reconnect...' in l:
						msg+=_('No data, trying to reconnect...')
						break
					if 'Speed Over Ground data not found, waiting for NMEA data...' in l:
						msg+=_('Speed Over Ground data not found, waiting for NMEA data...')
						break
					if '$IIVBW' in l: msg+=l
					if '$IIVHW' in l:
						msg+=l
						msg+=_('\nSpeed Over Ground retrieved from NMEA data successfully.')
						break
				sog_result.stdout.close()
				self.SetStatusText('')
				self.ShowMessage(msg)
			else:
				subprocess.call(['pkill', '-f', 'sog2sow.py'])
				self.SetStatusText('')
				self.ShowMessage(_('Speed Through Water simulation stopped'))
			self.write_conf()

		def set_conf(self):
			self.gain.SetValue(self.data_conf.get('AIS-SDR', 'gain'))
			self.ppm.SetValue(self.data_conf.get('AIS-SDR', 'ppm'))
			enable_ais=self.data_conf.get('AIS-SDR', 'enable')
			self.wlan.SetValue(self.data_conf.get('WIFI', 'device'))
			self.passw.SetValue(self.data_conf.get('WIFI', 'password'))
			enable_wifi=self.data_conf.get('WIFI', 'enable')
			if enable_ais=='1':
					self.ais_sdr_enable.SetValue(True)
					self.gain.SetEditable(False)
					self.gain.SetForegroundColour((180,180,180))
					self.ppm.SetEditable(False)
					self.ppm.SetForegroundColour((180,180,180))
			if enable_wifi=='1':
					self.wifi_enable.SetValue(True)
					self.wlan.SetEditable(False)
					self.wlan.SetForegroundColour((180,180,180))
					self.passw.SetEditable(False)
					self.passw.SetForegroundColour((180,180,180))
			opencpn=self.data_conf.get('STARTUP', 'opencpn')
			opencpn_no=self.data_conf.get('STARTUP', 'opencpn_no_opengl')
			opencpn_fullscreen=self.data_conf.get('STARTUP', 'opencpn_fullscreen')
			kplex=self.data_conf.get('STARTUP', 'kplex')
			gps_time=self.data_conf.get('STARTUP', 'gps_time')
			x11vnc=self.data_conf.get('STARTUP', 'x11vnc')
			IIVBW=self.data_conf.get('STARTUP', 'IIVBW')
			if opencpn=='1': self.startup.Check(self.startup_item1.GetId(), True)
			if opencpn_no=='1': self.startup.Check(self.startup_item1b.GetId(), True)
			if opencpn_fullscreen=='1': self.startup.Check(self.startup_item1c.GetId(), True)
			if kplex=='1': self.startup.Check(self.startup_item2.GetId(), True)
			if gps_time=='1': self.startup.Check(self.startup_item2_2.GetId(), True)
			if x11vnc=='1': self.startup.Check(self.startup_item3.GetId(), True)
			if IIVBW=='1': self.water_speed_enable.SetValue(True)
			language=self.data_conf.get('GENERAL', 'lang')
			if language=='en': self.lang.Check(self.lang_item1.GetId(), True)
			if language=='ca': self.lang.Check(self.lang_item2.GetId(), True)
			if language=='es': self.lang.Check(self.lang_item3.GetId(), True)

		def write_conf(self):
			enable_stw=self.water_speed_enable.GetValue()
			enable_ais=self.ais_sdr_enable.GetValue()
			enable_wifi=self.wifi_enable.GetValue()
			enable='0'
			if enable_ais==True: enable='1'
			self.data_conf.set('AIS-SDR', 'enable', enable)
			enable='0'
			if enable_wifi==True: enable='1'
			self.data_conf.set('WIFI', 'enable', enable)
			enable='0'
			if enable_stw==True: enable='1'
			self.data_conf.set('STARTUP', 'iivbw', enable)

			gain=self.gain.GetValue()
			ppm=self.ppm.GetValue()
			wlan=self.wlan.GetValue()
			passw=self.passw.GetValue()
			self.data_conf.set('AIS-SDR', 'gain', gain)
			self.data_conf.set('AIS-SDR', 'ppm', ppm)
			self.data_conf.set('WIFI', 'device', wlan)
			self.data_conf.set('WIFI', 'password', passw)

			with open(currentpath+'/openplotter.conf', 'wb') as configfile:
				self.data_conf.write(configfile)

		def time_gps(self,event):
			self.SetStatusText(_('Waiting for NMEA time data in localhost:10110 ...'))
			time_gps_result=subprocess.check_output(['sudo', 'python', currentpath+'/time_gps.py'])
			msg=''
			re=time_gps_result.splitlines()
			for current in re:
				if 'Failed to connect with localhost:10110.' in current: msg+=_('Failed to connect with localhost:10110.\n')
				if 'Error: ' in current: msg+=current+'\n'
				if 'Unable to retrieve date or time from NMEA data.' in current: msg+=_('Unable to retrieve date or time from NMEA data.\n')
				if 'UTC' in current:
					if not '00:00:00' in current: msg+=current+'\n'
				if 'Date and time retrieved from NMEA data successfully.' in current: msg+=_('Date and time retrieved from NMEA data successfully.')

			self.SetStatusText('')
			self.ShowMessage(msg)

		def time_zone(self,event):
			subprocess.Popen(['lxterminal', '-e', 'sudo dpkg-reconfigure tzdata'])
			self.SetStatusText(_('Set time zone in the new window'))

		def reconfigure_gpsd(self,event):
			subprocess.Popen(['lxterminal', '-e', 'sudo dpkg-reconfigure gpsd'])
			self.SetStatusText(_('Set GPSD in the new window'))
		
		def restart_multiplex(self,event):
			self.restart_kplex()

		def restart_kplex(self):
			self.SetStatusText(_('Closing Kplex'))
			subprocess.call(["pkill", '-9', "kplex"])
			subprocess.Popen('kplex')
			self.SetStatusText(_('Kplex restarted'))
				
		def show_output_window(self,event):
			close=subprocess.call(['pkill', '-f', 'output.py'])
			show_output=subprocess.Popen(['python', currentpath+'/output.py', self.language])

		def check_startup(self, e):
			opencpn="0"
			opencpn_nopengl="0"
			opencpn_fullscreen="0"
			kplex="0"
			x11vnc="0"
			gps_time="0"
			if self.startup_item1.IsChecked(): opencpn="1"
			if self.startup_item1b.IsChecked(): opencpn_nopengl="1"
			if self.startup_item1c.IsChecked(): opencpn_fullscreen="1"
			if self.startup_item2.IsChecked(): kplex="1"
			if self.startup_item2_2.IsChecked(): gps_time="1"
			if self.startup_item3.IsChecked(): x11vnc="1"
			self.data_conf.set('STARTUP', 'opencpn', opencpn)
			self.data_conf.set('STARTUP', 'opencpn_no_opengl', opencpn_nopengl)
			self.data_conf.set('STARTUP', 'opencpn_fullscreen', opencpn_fullscreen)
			self.data_conf.set('STARTUP', 'kplex', kplex)
			self.data_conf.set('STARTUP', 'gps_time', gps_time)
			self.data_conf.set('STARTUP', 'x11vnc', x11vnc)
			with open(currentpath+'/openplotter.conf', 'wb') as configfile:
				self.data_conf.write(configfile)

		def lang_en(self, e):
			self.lang_selected='en'
			self.write_lang_selected()
			self.lang.Check(self.lang_item1.GetId(), True)
		def lang_ca(self, e):
			self.lang_selected='ca'
			self.write_lang_selected()
			self.lang.Check(self.lang_item2.GetId(), True)
		def lang_es(self, e):
			self.lang_selected='es'
			self.write_lang_selected()
			self.lang.Check(self.lang_item3.GetId(), True)
		def write_lang_selected (self):
			self.lang.Check(self.lang_item1.GetId(), False)
			self.lang.Check(self.lang_item2.GetId(), False)
			self.lang.Check(self.lang_item3.GetId(), False)
			self.data_conf.set('GENERAL', 'lang', self.lang_selected)
			with open(currentpath+'/openplotter.conf', 'wb') as configfile:
				self.data_conf.write(configfile)
			self.ShowMessage(_('The selected language will be enabled when you restart'))

		def test_ppm(self,event):
			self.enableAISconf()
			aisdecoder=subprocess.call(['pkill', '-9', 'aisdecoder'])
			rtl_fm=subprocess.call(['pkill', '-9', 'rtl_fm'])
			w_close=subprocess.call(['pkill', '-f', 'waterfall.py'])
			rtl_close=subprocess.call(['pkill', '-9', 'rtl_test'])
			self.ais_sdr_enable.SetValue(False)
			output=subprocess.check_output('lsusb')
			if 'DVB-T' in output:
				ppm=self.ppm.GetValue()
				w_open=subprocess.Popen(['python', currentpath+'/waterfall.py', ppm])
				msg=_('SDR-AIS reception disabled.\nCheck the new window, calculate the ppm value and enable SDR-AIS reception again.')
			else:
				msg=_('SDR device not found.\nSDR-AIS reception disabled.')
				
			self.ShowMessage(msg)
			self.write_conf()


		def test_gain(self,event):
			self.enableAISconf()
			aisdecoder=subprocess.call(['pkill', '-9', 'aisdecoder'])
			rtl_fm=subprocess.call(['pkill', '-9', 'rtl_fm'])
			w_close=subprocess.call(['pkill', '-f', 'waterfall.py'])
			rtl_close=subprocess.call(['pkill', '-9', 'rtl_test'])
			self.ais_sdr_enable.SetValue(False)
			output=subprocess.check_output('lsusb')
			if 'DVB-T' in output:
				subprocess.Popen(['lxterminal', '-e', 'rtl_test'])
				msg=_('SDR-AIS reception disabled.\nCheck the new window, copy the maximum supported gain value and enable SDR-AIS reception again.')
			else:
				msg=_('SDR device not found.\nSDR-AIS reception disabled.')

			self.ShowMessage(msg)
			self.write_conf()

		def onwifi_enable (self, e):
			self.SetStatusText(_('Configuring NMEA WiFi server, wait please...'))
			isChecked = self.wifi_enable.GetValue()
			wlan=self.wlan.GetValue()
			passw=self.passw.GetValue()
			if isChecked:
				self.enable_disable_wifi(1)
				if len(passw)>=8:
					wifi_result=subprocess.check_output(['sudo', 'python', currentpath+'/wifi_server.py', '1', wlan, passw])
				else:
					wifi_result=_('Password must be at least 8 characters long')
					self.enable_disable_wifi(0)
			else: 
				self.enable_disable_wifi(0)
				wifi_result=subprocess.check_output(['sudo', 'python', currentpath+'/wifi_server.py', '0', wlan, passw])
			
			msg=wifi_result
			if 'NMEA WiFi Server failed.' in msg:
				msg=msg.replace('NMEA WiFi Server failed.', _('NMEA WiFi Server failed.'))
				self.enable_disable_wifi(0)
			msg=msg.replace('NMEA WiFi Server started.', _('NMEA WiFi Server started.'))
			msg=msg.replace('NMEA WiFi Server stopped.', _('NMEA WiFi Server stopped.'))
			self.SetStatusText('')
			self.ShowMessage(msg)
			self.write_conf()
		
		def enable_disable_wifi(self, s):
			if s==1:
				self.wlan.SetEditable(False)
				self.wlan.SetForegroundColour((180,180,180))
				self.passw.SetEditable(False)
				self.passw.SetForegroundColour((180,180,180))
				self.wifi_enable.SetValue(True)
			else:
				self.wlan.SetEditable(True)
				self.wlan.SetForegroundColour((wx.NullColor))
				self.passw.SetEditable(True)
				self.passw.SetForegroundColour((wx.NullColor))
				self.wifi_enable.SetValue(False)
		
		def OnAboutBox(self, e):
			description = _("OpenPlotter is a DIY open-source low-cost low-consumption sailing platform to run on x86 laptops and ARM boards (Raspberry Pi, Banana Pi, BeagleBone, Cubieboard...)")			
			licence = """This program is free software: you can redistribute it 
and/or modify it under the terms of the GNU General Public License 
as published by the Free Software Foundation, either version 2 of 
the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but 
WITHOUT ANY WARRANTY; without even the implied warranty of 
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License 
along with this program.  If not, see http://www.gnu.org/licenses/"""

			info = wx.AboutDialogInfo()
			info.SetName('OpenPlotter')
			info.SetVersion(self.data_conf.get('GENERAL', 'version'))
			info.SetDescription(description)
			info.SetCopyright('2013 - 2015 Sailoog')
			info.SetWebSite('http://www.sailoog.com')
			info.SetLicence(licence)
			info.AddDeveloper('Sailoog\n\nhttps://github.com/sailoog')
			info.AddDocWriter('Sailoog\n\nhttps://www.gitbook.com/@sailoog')
			info.AddArtist('Sailoog')
			info.AddTranslator('Catalan, English and Spanish by Sailoog')
			wx.AboutBox(info)

		def ShowMessage(self, w_msg):
			wx.MessageBox(w_msg, 'Info', wx.OK | wx.ICON_INFORMATION)


app = wx.App(False)
frame = MyFrame(None, 'OpenPlotter')
app.MainLoop()
