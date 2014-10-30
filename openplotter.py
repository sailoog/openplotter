#!/usr/bin/env python

import wx, subprocess, socket, pynmea2, time, sys, os, ConfigParser
from wx.lib.mixins.listctrl import CheckListCtrlMixin

home = os.path.expanduser("~")

class CheckListCtrl(wx.ListCtrl, CheckListCtrlMixin):
	def __init__(self, parent):
		wx.ListCtrl.__init__(self)
		CheckListCtrlMixin.__init__(self)

class MyFrame(wx.Frame):
		
		def __init__(self, parent, title):

			wx.Frame.__init__(self, parent, title=title, size=(700,420))

			self.read_conf()

			menubar = wx.MenuBar()
			self.startup = wx.Menu()
			self.startup_item1 = self.startup.Append(wx.ID_ANY, 'OpenCPN', 'If selected OpenCPN will run at startup', kind=wx.ITEM_CHECK)
			self.Bind(wx.EVT_MENU, self.check_startup, self.startup_item1)
			self.startup_item2 = self.startup.Append(wx.ID_ANY, 'NMEA multiplexor (Kplex)', 'If selected Kplex will run at startup', kind=wx.ITEM_CHECK)
			self.Bind(wx.EVT_MENU, self.check_startup, self.startup_item2)
			self.startup_item3 = self.startup.Append(wx.ID_ANY, 'Remote desktop (x11vnc)', 'If selected x11vnc will run at startup', kind=wx.ITEM_CHECK)
			self.Bind(wx.EVT_MENU, self.check_startup, self.startup_item3)
			menubar.Append(self.startup, 'Startup')
			time_ = wx.Menu()
			time_item1 = time_.Append(wx.ID_ANY, 'Set time zone', 'Set time zone in the new window')
			self.Bind(wx.EVT_MENU, self.time_zone, time_item1)
			time_item2 = time_.Append(wx.ID_ANY, 'Set time from GPS', 'Set system time from GPS')
			self.Bind(wx.EVT_MENU, self.time_gps, time_item2)
			menubar.Append(time_, 'Time')
			wifi_server = wx.Menu()
			wifi_server_item1 = wifi_server.Append(wx.ID_ANY, 'Set Server/Client', 'Switch WiFi between "access point" and "DHCP client"')
			self.Bind(wx.EVT_MENU, self.OnClick_nmea_server, wifi_server_item1)
			wifi_server_item2 = wifi_server.Append(wx.ID_ANY, 'Network manager', 'Manage your networks')
			self.Bind(wx.EVT_MENU, self.OnClick_network_man, wifi_server_item2)
			menubar.Append(wifi_server, 'WiFi')
			self.SetMenuBar(menubar)

########################################################

			nmea=wx.StaticBox(self, label=' Add NMEA input / output ', size=(690, 105), pos=(5, 5))
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

			wx.StaticText(self, label='<--', pos=(320, 35))

			self.add_serial_in =wx.Button(self, label="Add serial input", pos=(360, 30))
			self.Bind(wx.EVT_BUTTON, self.add_serial_input, self.add_serial_in)

			self.add_serial_out =wx.Button(self, label="Add serial output", pos=(520, 30))
			self.Bind(wx.EVT_BUTTON, self.add_serial_output, self.add_serial_out)

			self.type = ['TCP', 'UDP']
			self.typeComboBox = wx.ComboBox(self, choices=self.type, style=wx.CB_READONLY, size=(65, 30), pos=(10, 70))
			self.typeComboBox.SetValue('TCP')

			self.address = wx.TextCtrl(self, -1, size=(130, 30), pos=(80, 70))

			self.port = wx.TextCtrl(self, -1, size=(90, 30), pos=(215, 70))

			wx.StaticText(self, label='<--', pos=(320, 75))

			self.add_network_in =wx.Button(self, label="Add network input", pos=(360, 70))
			self.Bind(wx.EVT_BUTTON, self.add_network_input, self.add_network_in)

			self.add_network_out =wx.Button(self, label="Add network output", pos=(520, 70))
			self.Bind(wx.EVT_BUTTON, self.add_network_output, self.add_network_out)

########################################################

			in_out=wx.StaticBox(self, label=' NMEA inputs / outputs ', size=(475, 260), pos=(5, 115))
			estilo = in_out.GetFont()
			estilo.SetWeight(wx.BOLD)
			in_out.SetFont(estilo)

			self.list_input = wx.ListCtrl(self, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER, size=(295, 90), pos=(10, 140))
			self.list_input.InsertColumn(0, 'Type', width=60)
			self.list_input.InsertColumn(1, 'Port/Address', width=140)
			self.list_input.InsertColumn(2, 'Bauds/Port', width=95)

			inputs = wx.StaticText(self, label='Inputs', pos=(320, 145))
			estilo = inputs.GetFont()
			estilo.SetWeight(wx.BOLD)
			inputs.SetFont(estilo)

			self.button_delete_input =wx.Button(self, label="Delete selected", pos=(315, 165))
			self.Bind(wx.EVT_BUTTON, self.delete_input, self.button_delete_input)

			self.list_output = wx.ListCtrl(self, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER, size=(295, 90), pos=(10, 240))
			self.list_output.InsertColumn(0, 'Type', width=60)
			self.list_output.InsertColumn(1, 'Port/Address', width=140)
			self.list_output.InsertColumn(2, 'Bauds/Port', width=95)

			outputs = wx.StaticText(self, label='Outputs', pos=(320, 245))
			estilo = outputs.GetFont()
			estilo.SetWeight(wx.BOLD)
			outputs.SetFont(estilo)

			self.button_delete_output =wx.Button(self, label="Delete selected", pos=(315, 265))
			self.Bind(wx.EVT_BUTTON, self.delete_output, self.button_delete_output)

			self.show_output =wx.Button(self, label="Show output", pos=(315, 300))
			self.Bind(wx.EVT_BUTTON, self.show_output_window, self.show_output)

			self.restart =wx.Button(self, label="Restart", pos=(10, 337))
			self.Bind(wx.EVT_BUTTON, self.restart_multiplex, self.restart)

			self.button_apply =wx.Button(self, label="Apply changes", pos=(120, 337))
			self.Bind(wx.EVT_BUTTON, self.apply_changes, self.button_apply)

########################################################

			ais_sdr=wx.StaticBox(self, label=' AIS-SDR ', size=(210, 130), pos=(485, 115))
			estilo = ais_sdr.GetFont()
			estilo.SetWeight(wx.BOLD)
			ais_sdr.SetFont(estilo)

			self.ais_sdr_enable = wx.CheckBox(self, label='Enable', pos=(490, 135))
			self.ais_sdr_enable.Bind(wx.EVT_CHECKBOX, self.OnOffAIS)

			self.gain = wx.TextCtrl(self, -1, size=(50, 30), pos=(490, 165))
			gain_text = wx.StaticText(self, label='Gain', pos=(550, 170))

			self.ppm = wx.TextCtrl(self, -1, size=(50, 30), pos=(490, 205))
			ppm_text = wx.StaticText(self, label='Error correction', pos=(550, 210))

########################################################

			self.png = wx.StaticBitmap(self, -1, wx.Bitmap(home+'/.config/openplotter/openplotter500.png', wx.BITMAP_TYPE_ANY), pos=(540, 250))

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
							output_tmp.append('all address')
							item2=self.extract_value(data[index+2])
							output_tmp.append(item2)
							self.outputs.append(output_tmp)
					if '[broadcast]' in item:
						if 'direction=in' in data[index+1]:
							input_tmp=[]
							input_tmp.append('UDP')
							input_tmp.append('all address')
							item2=self.extract_value(data[index+2])
							input_tmp.append(item2)
							self.inputs.append(input_tmp)
				self.write_inputs()
				self.write_outputs()

			except IOError:
				self.SetStatusText('Configuration file does not exist. Add inputs and apply changes')

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
				self.SetStatusText('It is impossible to set "'+port+'" as input because this port is already in use.')

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
				self.SetStatusText('It is impossible to set "'+port+'" as output because this port is already in use.')
		
		def add_network_input(self,event):
			input_tmp=[]
			found=False
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
				self.SetStatusText('You have to enter at least a port number.')
		
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
					self.SetStatusText('Sorry. It is not possible to create UDP outputs.')
			else:
				self.SetStatusText('You have to enter at least a port number.')

		def OnClick_nmea_server(self,event):
			subprocess.Popen(['lxterminal', '-e', 'sudo '+home+'/.config/openplotter/nmea_wifi_server/switch_access_point.sh'])
			self.SetStatusText('Set NMEA server in the new window')

		def OnClick_network_man(self,event):
			subprocess.Popen('/usr/sbin/wpa_gui')
			self.SetStatusText('Manage networks in the new window')

		def OnOffAIS(self, e):
			sender = e.GetEventObject()
			isChecked = sender.GetValue()
			if isChecked:
				self.gain.SetEditable(False)
				self.gain.SetForegroundColour((180,180,180))
				self.ppm.SetEditable(False)
				self.ppm.SetForegroundColour((180,180,180)) 
				gain=self.gain.GetValue()
				ppm=self.ppm.GetValue()
				rtl_fm=subprocess.Popen(['rtl_fm', '-f', '161975000', '-g', gain, '-p', ppm, '-s', '48k'], stdout = subprocess.PIPE)
				aisdecoder=subprocess.Popen(['aisdecoder', '-h', '127.0.0.1', '-p', '10110', '-a', 'file', '-c', 'mono', '-d', '-f', '/dev/stdin'], stdin = rtl_fm.stdout)         
			else: 
				self.gain.SetEditable(True)
				self.gain.SetForegroundColour((wx.NullColor))
				self.ppm.SetEditable(True)
				self.ppm.SetForegroundColour((wx.NullColor))
				aisdecoder=subprocess.Popen(['pkill', '-9', 'aisdecoder'], stdout = subprocess.PIPE)
				rtl_fm=subprocess.Popen(['pkill', '-9', 'rtl_fm'], stdin = aisdecoder.stdout)
			self.write_ais_conf()

		def set_conf(self):
			self.gain.SetValue(self.data_conf.get('AIS-SDR', 'gain'))
			self.ppm.SetValue(self.data_conf.get('AIS-SDR', 'ppm'))
			enable=self.data_conf.get('AIS-SDR', 'enable')
			if enable=='1':
					self.ais_sdr_enable.SetValue(True)
					self.gain.SetEditable(False)
					self.gain.SetForegroundColour((180,180,180))
					self.ppm.SetEditable(False)
					self.ppm.SetForegroundColour((180,180,180))
			opencpn=self.data_conf.get('STARTUP', 'opencpn')
			kplex=self.data_conf.get('STARTUP', 'kplex')
			x11vnc=self.data_conf.get('STARTUP', 'x11vnc')
			if opencpn=='1': self.startup.Check(self.startup_item1.GetId(), True)
			if kplex=='1': self.startup.Check(self.startup_item2.GetId(), True)
			if x11vnc=='1': self.startup.Check(self.startup_item3.GetId(), True)

		def write_ais_conf(self):
			enable_estado=self.ais_sdr_enable.GetValue()
			gain=self.gain.GetValue()
			ppm=self.ppm.GetValue()
			self.data_conf.set('AIS-SDR', 'gain', gain)
			self.data_conf.set('AIS-SDR', 'ppm', ppm)
			enable='0'
			if enable_estado==True: enable='1'
			self.data_conf.set('AIS-SDR', 'enable', enable)
			with open(home+'/.config/openplotter/openplotter.conf', 'wb') as configfile:
				self.data_conf.write(configfile)

		def time_gps(self,event):
			fecha=""
			hora=""
			self.SetStatusText('Waiting for GPS data in localhost:10110 ...')
			try:
				s = socket.socket()
				s.connect(("localhost", 10110))
				cont = 0
				while True:
					cont = cont + 1
					frase_nmea = s.recv(512)
					if frase_nmea[1:3]=='GP':
						msg = pynmea2.parse(frase_nmea)
						if msg.sentence_type == 'RMC':
						   fecha = msg.datestamp
						   hora =  msg.timestamp
						   break
					if cont > 15:
						break
				s.close()
			except socket.error, error_msg:
				self.SetStatusText('Failed to connect with localhost:10110. '+'Error code: ' + str(error_msg[0]))
			if (fecha) and (hora):
				subprocess.call([ 'sudo', 'date', '--set', fecha.strftime('%Y-%m-%d'), '--utc'])
				subprocess.call([ 'sudo', 'date', '--set', hora.strftime('%H:%M:%S'), '--utc'])
				self.SetStatusText("Date and time retrieved from GPS successfully")
			else:
				self.SetStatusText("Unable to retrieve date or time from GPS")

		def time_zone(self,event):
			subprocess.Popen(['lxterminal', '-e', 'sudo dpkg-reconfigure tzdata'])
			self.SetStatusText('Set time zone in the new window')
		
		def restart_multiplex(self,event):
			self.restart_kplex()

		def restart_kplex(self):
			self.SetStatusText('Closing Kplex')
			subprocess.Popen(["pkill", "kplex"])
			time.sleep(1)
			subprocess.Popen('kplex')
			self.SetStatusText('Kplex restarted')
				
		def show_output_window(self,event):
			show_output=subprocess.Popen(['python', home+'/.config/openplotter/output.py'])

		def check_startup(self, e):
			opencpn="0"
			kplex="0"
			x11vnc="0"
			if self.startup_item1.IsChecked(): opencpn="1"
			if self.startup_item2.IsChecked(): kplex="1"
			if self.startup_item3.IsChecked(): x11vnc="1"
			self.data_conf.set('STARTUP', 'opencpn', opencpn)
			self.data_conf.set('STARTUP', 'kplex', kplex)
			self.data_conf.set('STARTUP', 'x11vnc', x11vnc)
			with open(home+'/.config/openplotter/openplotter.conf', 'wb') as configfile:
				self.data_conf.write(configfile)



app = wx.App(False)
frame = MyFrame(None, 'OpenPlotter Settings')
app.MainLoop()
