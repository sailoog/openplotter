#!/usr/bin/env python

import wx, subprocess, socket, pynmea2, time, sys, os, ConfigParser, gettext
from wx.lib.mixins.listctrl import CheckListCtrlMixin

home = os.path.expanduser('~')

class CheckListCtrl(wx.ListCtrl, CheckListCtrlMixin):
	def __init__(self, parent):
		wx.ListCtrl.__init__(self)
		CheckListCtrlMixin.__init__(self)

class MyFrame(wx.Frame):
		
		def __init__(self, parent, title):

			gettext.install('openplotter', home+'/.config/openplotter/locale', unicode=False)
			self.presLan_en = gettext.translation('openplotter', home+'/.config/openplotter/locale', languages=['en'])
			self.presLan_ca = gettext.translation('openplotter', home+'/.config/openplotter/locale', languages=['ca'])
			self.presLan_es = gettext.translation('openplotter', home+'/.config/openplotter/locale', languages=['es'])
			self.read_conf()
			language=self.data_conf.get('GENERAL', 'lang')
			if language=='en':self.presLan_en.install()
			if language=='ca':self.presLan_ca.install()
			if language=='es':self.presLan_es.install()

			wx.Frame.__init__(self, parent, title=title, size=(700,420))

			self.icon = wx.Icon(home+'/.config/openplotter/openplotter.ico', wx.BITMAP_TYPE_ICO)
			self.SetIcon(self.icon)

			menubar = wx.MenuBar()
			self.startup = wx.Menu()
			self.startup_item1 = self.startup.Append(wx.ID_ANY, _('OpenCPN'), _('If selected OpenCPN will run at startup'), kind=wx.ITEM_CHECK)
			self.Bind(wx.EVT_MENU, self.opengl, self.startup_item1)
			self.startup_item1b = self.startup.Append(wx.ID_ANY, _('OpenCPN (No OpenGL)'), _('If selected OpenCPN (No OpenGL) will run at startup'), kind=wx.ITEM_CHECK)
			self.Bind(wx.EVT_MENU, self.no_opengl, self.startup_item1b)
			self.startup.AppendSeparator()
			self.startup_item2 = self.startup.Append(wx.ID_ANY, _('NMEA multiplexor (Kplex)'), _('If selected Kplex will run at startup'), kind=wx.ITEM_CHECK)
			self.Bind(wx.EVT_MENU, self.check_startup, self.startup_item2)
			self.startup_item2_2 = self.startup.Append(wx.ID_ANY, _('Set system time from GPS'), _('You need to define a valid GPS input and run kplex at startup'), kind=wx.ITEM_CHECK)
			self.Bind(wx.EVT_MENU, self.check_startup, self.startup_item2_2)
			self.startup_item3 = self.startup.Append(wx.ID_ANY, _('Remote desktop (x11vnc)'), _('If selected x11vnc will run at startup'), kind=wx.ITEM_CHECK)
			self.Bind(wx.EVT_MENU, self.check_startup, self.startup_item3)
			menubar.Append(self.startup, _('Startup'))
			settings = wx.Menu()
			time_item1 = settings.Append(wx.ID_ANY, _('Set time zone'), _('Set time zone in the new window'))
			self.Bind(wx.EVT_MENU, self.time_zone, time_item1)
			time_item2 = settings.Append(wx.ID_ANY, _('Set time from GPS'), _('Set system time from GPS'))
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
			self.deviceComboBox = wx.ComboBox(self, choices=self.SerDevLs, style=wx.CB_DROPDOWN, size=(130, 30), pos=(80, 30))
			if self.SerDevLs : self.deviceComboBox.SetValue(self.SerDevLs[0])

			self.bauds = ['2400', '4800', '9600', '19200', '38400', '57600', '115200']
			self.baudComboBox = wx.ComboBox(self, choices=self.bauds, style=wx.CB_READONLY, size=(90, 30), pos=(215, 30))
			self.baudComboBox.SetValue('4800')

			wx.StaticText(self, label='Serial', pos=(320, 36))

			self.add_serial_in =wx.Button(self, label=_('Input'), pos=(380, 30))
			self.Bind(wx.EVT_BUTTON, self.add_serial_input, self.add_serial_in)

			self.add_serial_out =wx.Button(self, label=_('Output'), pos=(475, 30))
			self.Bind(wx.EVT_BUTTON, self.add_serial_output, self.add_serial_out)

			self.type = ['TCP', 'UDP']
			self.typeComboBox = wx.ComboBox(self, choices=self.type, style=wx.CB_READONLY, size=(65, 30), pos=(10, 70))
			self.typeComboBox.SetValue('TCP')

			self.address = wx.TextCtrl(self, -1, size=(130, 30), pos=(80, 70))

			self.port = wx.TextCtrl(self, -1, size=(90, 30), pos=(215, 70))

			wx.StaticText(self, label='Network', pos=(313, 76))

			self.add_network_in =wx.Button(self, label=_('Input'), pos=(380, 70))
			self.Bind(wx.EVT_BUTTON, self.add_network_input, self.add_network_in)

			self.add_network_out =wx.Button(self, label=_('Output'), pos=(475, 70))
			self.Bind(wx.EVT_BUTTON, self.add_network_output, self.add_network_out)

			wx.StaticText(self, label='|', pos=(580, 75))

			self.add_gpsd_in =wx.Button(self, label=_('GPSD'), pos=(595, 70))
			self.Bind(wx.EVT_BUTTON, self.add_gpsd_input, self.add_gpsd_in)

########################################################

			in_out=wx.StaticBox(self, label=_(' NMEA inputs / outputs '), size=(475, 260), pos=(5, 110))
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

			self.restart =wx.Button(self, label=_('Restart'), pos=(10, 330))
			self.Bind(wx.EVT_BUTTON, self.restart_multiplex, self.restart)

			self.button_apply =wx.Button(self, label=_('Apply changes'), pos=(120, 330))
			self.Bind(wx.EVT_BUTTON, self.apply_changes, self.button_apply)

########################################################

			ais_sdr=wx.StaticBox(self, label=_('AIS-SDR reception'), size=(210, 110), pos=(485, 110))
			estilo = ais_sdr.GetFont()
			estilo.SetWeight(wx.BOLD)
			ais_sdr.SetFont(estilo)

			self.ais_sdr_enable = wx.CheckBox(self, label=_('Enable'), pos=(490, 125))
			self.ais_sdr_enable.Bind(wx.EVT_CHECKBOX, self.OnOffAIS)

			self.gain = wx.TextCtrl(self, -1, size=(45, 30), pos=(595, 150))
			self.button_test_gain =wx.Button(self, label=_('Gain'), pos=(490, 150))
			self.Bind(wx.EVT_BUTTON, self.test_gain, self.button_test_gain)

			self.ppm = wx.TextCtrl(self, -1, size=(45, 30), pos=(595, 185))
			self.button_test_ppm =wx.Button(self, label=_('Correction'), pos=(490, 185))
			self.Bind(wx.EVT_BUTTON, self.test_ppm, self.button_test_ppm)

########################################################

			water_speed=wx.StaticBox(self, label=_('STW simulation'), size=(210, 50), pos=(485, 220))
			estilo = water_speed.GetFont()
			estilo.SetWeight(wx.BOLD)
			water_speed.SetFont(estilo)

			self.water_speed_enable = wx.CheckBox(self, label=_('SOG  -->  STW'), pos=(490, 235))
			self.water_speed_enable.Bind(wx.EVT_CHECKBOX, self.onoffwaterspeed)

########################################################

			wifi=wx.StaticBox(self, label=_('NMEA WiFi server'), size=(210, 100), pos=(485, 270))
			estilo = wifi.GetFont()
			estilo.SetWeight(wx.BOLD)
			wifi.SetFont(estilo)

			self.wifi_enable = wx.CheckBox(self, label=_('Enable'), pos=(490, 285))
			self.wifi_enable.Bind(wx.EVT_CHECKBOX, self.onwifi_enable)
			
			self.wlan = wx.TextCtrl(self, -1, size=(55, 25), pos=(490, 310))
			wx.StaticText(self, label=_('WiFi device'), pos=(550, 315))
			self.passw = wx.TextCtrl(self, -1, size=(100, 25), pos=(490, 340))
			wx.StaticText(self, label=_('Password'), pos=(595, 345))
########################################################

			self.CreateStatusBar()

			self.Centre()

			self.Show(True)

			self.read_kplex_conf()

			self.set_conf()

		
		def read_conf(self):
			self.data_conf = ConfigParser.SafeConfigParser()
			self.data_conf.read(home+'/.config/openplotter/openplotter.conf')

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
				self.SetStatusText(_('Configuration file does not exist. Add inputs and apply changes'))

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
					data=data+'[serial]\ndirection=out\nfilename='+item[1]+'\nbaud='+item[2]+'\n\n'
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
				self.SetStatusText(_('It is impossible to set input because this port is already in use.'))

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
				self.SetStatusText(_('It is impossible to set output because this port is already in use.'))
		
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
				self.SetStatusText(_('You have to enter at least a port number.'))

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
					self.SetStatusText(_('Sorry. It is not possible to create UDP outputs.'))
			else:
				self.SetStatusText(_('You have to enter at least a port number.'))

		def OnOffAIS(self, e):
			isChecked = self.ais_sdr_enable.GetValue()
			if isChecked:
				w_close=subprocess.Popen(['pkill', '-f', 'waterfall.py'])
				rtl_close=subprocess.Popen(['pkill', '-9', 'rtl_test'])
				self.gain.SetEditable(False)
				self.gain.SetForegroundColour((180,180,180))
				self.ppm.SetEditable(False)
				self.ppm.SetForegroundColour((180,180,180)) 
				gain=self.gain.GetValue()
				ppm=self.ppm.GetValue()
				rtl_fm=subprocess.Popen(['rtl_fm', '-f', '161975000', '-g', gain, '-p', ppm, '-s', '48k'], stdout = subprocess.PIPE)
				aisdecoder=subprocess.Popen(['aisdecoder', '-h', '127.0.0.1', '-p', '10110', '-a', 'file', '-c', 'mono', '-d', '-f', '/dev/stdin'], stdin = rtl_fm.stdout)         
				self.SetStatusText(_('SDR-AIS reception enabled'))
			else: 
				self.gain.SetEditable(True)
				self.gain.SetForegroundColour((wx.NullColor))
				self.ppm.SetEditable(True)
				self.ppm.SetForegroundColour((wx.NullColor))
				aisdecoder=subprocess.Popen(['pkill', '-9', 'aisdecoder'], stdout = subprocess.PIPE)
				rtl_fm=subprocess.Popen(['pkill', '-9', 'rtl_fm'], stdin = aisdecoder.stdout)
				self.SetStatusText(_('SDR-AIS reception disabled'))
			self.write_conf()

		def onoffwaterspeed(self, e):
			sender = e.GetEventObject()
			isChecked = sender.GetValue()
			if isChecked:
				sog=""
				self.SetStatusText(_('Waiting for GPS data in localhost:10110 ...'))
				try:
					s = socket.socket()
					s.connect(("localhost", 10110))
					s.settimeout(10)
					cont = 0
					while True:
						cont = cont + 1
						frase_nmea = s.recv(512)
						if frase_nmea[1]=='G':
							msg = pynmea2.parse(frase_nmea)
							if msg.sentence_type == 'RMC':
								sog = msg.spd_over_grnd
								break
						if cont > 15:
							break
					s.close()
				except socket.error, error_msg:
					self.SetStatusText(_('Failed to connect with localhost:10110. ')+_('Error code: ') + str(error_msg[0]))
					self.water_speed_enable.SetValue(False)
				else:
					if (sog):
						self.SetStatusText(_('Speed Over Ground retrieved from GPS successfully'))
					else:
						self.SetStatusText(_('Unable to retrieve Speed Over Ground from GPS, waiting for fixed data.'))
					subprocess.Popen(['python', home+'/.config/openplotter/sog2sow.py'])
			else:
				subprocess.Popen(['pkill', '-f', 'sog2sow.py'])
				self.SetStatusText(_('Speed Through Water simulation stopped'))
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
			kplex=self.data_conf.get('STARTUP', 'kplex')
			gps_time=self.data_conf.get('STARTUP', 'gps_time')
			x11vnc=self.data_conf.get('STARTUP', 'x11vnc')
			IIVBW=self.data_conf.get('STARTUP', 'IIVBW')
			if opencpn=='1': self.startup.Check(self.startup_item1.GetId(), True)
			if opencpn_no=='1': self.startup.Check(self.startup_item1b.GetId(), True)
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

			with open(home+'/.config/openplotter/openplotter.conf', 'wb') as configfile:
				self.data_conf.write(configfile)

		def time_gps(self,event):
			self.SetStatusText(_('Waiting for GPS data in localhost:10110 ...'))
			time_gps_result=subprocess.check_output(['sudo', 'python', home+'/.config/openplotter/time_gps.py'])
			parsed_out = self.parse_msg(time_gps_result, 'time_gps.py')
			msg=''
			if 'Failed to connect with localhost:10110.' in parsed_out[1]: msg=_('Failed to connect with localhost:10110.')
			if 'Date and time retrieved from GPS successfully.' in parsed_out[1]: msg=_('Date and time retrieved from GPS successfully.')
			if 'Unable to retrieve date or time from GPS.' in parsed_out[1]: msg=_('Unable to retrieve date or time from GPS.')
			self.SetStatusText('')
			self.ShowMessage(parsed_out[0]+'\n'+msg)

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
			subprocess.Popen(["pkill", "kplex"])
			time.sleep(1)
			subprocess.Popen('kplex')
			self.SetStatusText(_('Kplex restarted'))
				
		def show_output_window(self,event):
			show_output=subprocess.Popen(['python', home+'/.config/openplotter/output.py'])

		def no_opengl(self, e):
			self.startup.Check(self.startup_item1.GetId(), False)
			self.check_startup(e)

		def opengl(self, e):
			self.startup.Check(self.startup_item1b.GetId(), False)
			self.check_startup(e)

		def check_startup(self, e):
			opencpn="0"
			opencpn_nopengl="0"
			kplex="0"
			x11vnc="0"
			gps_time="0"
			if self.startup_item1.IsChecked(): opencpn="1"
			if self.startup_item1b.IsChecked(): opencpn_nopengl="1"
			if self.startup_item2.IsChecked(): kplex="1"
			if self.startup_item2_2.IsChecked(): gps_time="1"
			if self.startup_item3.IsChecked(): x11vnc="1"
			self.data_conf.set('STARTUP', 'opencpn', opencpn)
			self.data_conf.set('STARTUP', 'opencpn_no_opengl', opencpn_nopengl)
			self.data_conf.set('STARTUP', 'kplex', kplex)
			self.data_conf.set('STARTUP', 'gps_time', gps_time)
			self.data_conf.set('STARTUP', 'x11vnc', x11vnc)
			with open(home+'/.config/openplotter/openplotter.conf', 'wb') as configfile:
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
			with open(home+'/.config/openplotter/openplotter.conf', 'wb') as configfile:
				self.data_conf.write(configfile)
			self.SetStatusText(_('The selected language will be enabled when you restart'))

		def test_ppm(self,event):
			self.ais_sdr_enable.SetValue(False)
			self.OnOffAIS(event)
			ppm=self.ppm.GetValue()
			w_close=subprocess.Popen(['pkill', '-f', 'waterfall.py'])
			rtl_close=subprocess.Popen(['pkill', '-9', 'rtl_test'])
			time.sleep(1)
			w_open=subprocess.Popen(['python', home+'/.config/openplotter/waterfall.py', ppm])
			self.SetStatusText(_('Check the new window and calculate the ppm value'))

		def test_gain(self,event):
			self.ais_sdr_enable.SetValue(False)
			self.OnOffAIS(event)
			w_close=subprocess.Popen(['pkill', '-f', 'waterfall.py'])
			rtl_close=subprocess.Popen(['pkill', '-9', 'rtl_test'])
			time.sleep(1)
			subprocess.Popen(['lxterminal', '-e', 'rtl_test'])
			self.SetStatusText(_('Check the new window and copy the maximum supported gain value'))

		def onwifi_enable (self, e):
			self.SetStatusText(_('Configuring NMEA WiFi server, wait please...'))
			isChecked = self.wifi_enable.GetValue()
			self.write_conf()
			wlan=self.wlan.GetValue()
			passw=self.passw.GetValue()
			if isChecked:
				self.wlan.SetEditable(False)
				self.wlan.SetForegroundColour((180,180,180))
				self.passw.SetEditable(False)
				self.passw.SetForegroundColour((180,180,180))
				wifi_result=subprocess.check_output(['sudo', 'python', home+'/.config/openplotter/wifi_server.py', '1', wlan, passw])
			else: 
				self.wlan.SetEditable(True)
				self.wlan.SetForegroundColour((wx.NullColor))
				self.passw.SetEditable(True)
				self.passw.SetForegroundColour((wx.NullColor))
				wifi_result=subprocess.check_output(['sudo', 'python', home+'/.config/openplotter/wifi_server.py', '0', wlan, passw])
			parsed_out = self.parse_msg(wifi_result, 'wifi_server.py')
			msg=''
			if 'NMEA WiFi Server failed.' in parsed_out[1]: msg=_('NMEA WiFi Server failed.')
			if 'NMEA WiFi Server started.' in parsed_out[1]: msg=_('NMEA WiFi Server started.')
			if 'NMEA WiFi Server stopped.' in parsed_out[1]: msg=_('NMEA WiFi Server stopped.')
			self.SetStatusText('')
			self.ShowMessage(parsed_out[0]+'\n'+msg)

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
			info.SetVersion('2.0')
			info.SetDescription(description)
			info.SetCopyright('(C) 2013 - 2014 Sailoog')
			info.SetWebSite('http://www.sailoog.com')
			info.SetLicence(licence)
			info.AddDeveloper('Sailoog\n\nhttps://github.com/sailoog')
			info.AddDocWriter('Sailoog\n\nhttps://www.gitbook.com/@sailoog')
			info.AddArtist('Sailoog')
			info.AddTranslator('Catalan, English, Spanish by Sailoog')
			wx.AboutBox(info)

		def ShowMessage(self, w_msg):
			wx.MessageBox(w_msg, 'Info', wx.OK | wx.ICON_INFORMATION)

		def parse_msg(self, output, f):
			txt=''
			msg=''
			re=output.splitlines()
			for current in re:
				if f in current:
					msg=current.replace(f+": ", "")
				else:
					txt+=current+"\n"
			return txt, msg


app = wx.App(False)
frame = MyFrame(None, 'OpenPlotter')
app.MainLoop()
