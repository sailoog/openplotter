#!/usr/bin/env python

import wx, subprocess, socket, pynmea2, threading, time, sys, os
from os.path import expanduser
from wx.lib.mixins.listctrl import CheckListCtrlMixin

home = expanduser("~")

class CheckListCtrl(wx.ListCtrl, CheckListCtrlMixin):
	def __init__(self, parent):
		wx.ListCtrl.__init__(self)
		CheckListCtrlMixin.__init__(self)

class MyFrame(wx.Frame):
		
		def __init__(self, parent, title):

			wx.Frame.__init__(self, parent, title=title, size=(700,400))

			hora=wx.StaticBox(self, label=' Time ', size=(210, 90), pos=(485, 5))
			estilo = hora.GetFont()
			estilo.SetWeight(wx.BOLD)
			hora.SetFont(estilo)

			self.button4 =wx.Button(self, label="Set time zone", pos=(490, 25))
			self.Bind(wx.EVT_BUTTON, self.OnClick4, self.button4)

			self.button3 =wx.Button(self, label="Set time from GPS", pos=(490, 60))
			self.Bind(wx.EVT_BUTTON, self.OnClick3, self.button3)

			server=wx.StaticBox(self, label=' NMEA WiFi Server ', size=(210, 130), pos=(485, 100))
			estilo = server.GetFont()
			estilo.SetWeight(wx.BOLD)
			server.SetFont(estilo)

			titulo3 = wx.StaticText(self, label='Supported chipsets:\nRT5370, RTL8192CU, RTL8188CUS', pos=(495, 120))
			estilo = titulo3.GetFont()
			estilo.SetPointSize(8)
			titulo3.SetFont(estilo)

			self.button_nmea_server =wx.Button(self, label="Set Server/Client", pos=(490, 160))
			self.Bind(wx.EVT_BUTTON, self.OnClick_nmea_server, self.button_nmea_server)

			self.button_network_man =wx.Button(self, label="Network manager", pos=(490, 195))
			self.Bind(wx.EVT_BUTTON, self.OnClick_network_man, self.button_network_man)

			nmea=wx.StaticBox(self, label=' NMEA Multiplexer ', size=(475, 197), pos=(5, 5))
			estilo = nmea.GetFont()
			estilo.SetWeight(wx.BOLD)
			nmea.SetFont(estilo)

			entradas = wx.StaticText(self, label='Inputs', pos=(10, 25))
			stilo = entradas.GetFont()
			estilo.SetWeight(wx.BOLD)
			estilo.SetPointSize(8)
			entradas.SetFont(estilo)

			self.device = wx.TextCtrl(self, -1, size=(105, 30), pos=(10, 45))

			self.SerDevLs = []
			self.SerialCheck('/dev/rfcomm')
			self.SerialCheck('/dev/ttyUSB')
			self.SerialCheck('/dev/ttyS')
			self.deviceComboBox = wx.ComboBox(self, choices=self.SerDevLs, style=wx.CB_DROPDOWN, size=(130, 30), pos=(117, 45))
			self.deviceComboBox.SetValue(self.SerDevLs[0])

			self.bauds = ['2400', '4800', '9600', '19200', '38400', '57600', '115200']
			self.baudComboBox = wx.ComboBox(self, choices=self.bauds, style=wx.CB_READONLY, size=(90, 30), pos=(250, 45))
			self.baudComboBox.SetValue('4800')

			self.button_add_new =wx.Button(self, label=" <- Add input", pos=(345, 45))
			self.Bind(wx.EVT_BUTTON, self.OnClick_add_new, self.button_add_new)

			self.list = wx.ListCtrl(self, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER, size=(330, 110), pos=(10, 85))
			self.list.InsertColumn(0, 'Device', width=125)
			self.list.InsertColumn(1, 'Port', width=125)
			self.list.InsertColumn(2, 'Baud rate', width=75)

			self.button_borrar_input =wx.Button(self, label=" <- Delete selec.", pos=(345, 85))
			self.Bind(wx.EVT_BUTTON, self.OnClick_borrar_input, self.button_borrar_input)

			self.button_apply =wx.Button(self, label="Apply changes", pos=(345, 165))
			self.Bind(wx.EVT_BUTTON, self.OnClick_apply, self.button_apply)

			salida = wx.StaticText(self, label='Output', pos=(10, 220))
			estilo = salida.GetFont()
			estilo.SetWeight(wx.BOLD)
			estilo.SetPointSize(8)
			salida.SetFont(estilo)

			salida2 = wx.StaticText(self, label='TCP -> localhost:10110', pos=(75, 220))
			estilo = salida2.GetFont()
			estilo.SetPointSize(8)
			salida2.SetFont(estilo)

			self.button2 =wx.Button(self, label="Restart multiplexer", pos=(240, 210))
			self.Bind(wx.EVT_BUTTON, self.OnClick2, self.button2)

			self.logger = wx.TextCtrl(self, style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_DONTWRAP, size=(680,125), pos=(10, 245))

			self.CreateStatusBar()

			self.Centre()

			self.Show(True)

			self.estado=0

			self.hilo=threading.Thread(target=self.ventanalog)
			self.hilo.setDaemon(1)

			self.conectar()

			self.packages = []
			self.crea_lista_packages()

		def SerialCheck(self,dev):
			num = 0
			for _ in range(99):
				s = dev + str(num)
				d = os.path.exists(s)
				if d == True:
					self.SerDevLs.append(s)      
				num = num + 1

		def conectar(self):
			try:
				self.s2 = socket.socket()
				self.s2.connect(("localhost", 10110))
				if not self.hilo.isAlive():
					self.hilo.start()
				self.estado=1
				self.SetStatusText('Kplex started')
			except socket.error, error_msg:
				self.SetStatusText('Failed to connect with localhost:10110. '+'Error code: ' + str(error_msg[0]))

		def desconectar(self):
			self.logger.Clear()
			self.estado=0
			self.s2.close()
			subprocess.Popen(["pkill", "kplex"])
			self.SetStatusText('Kplex stopped')
			time.sleep(1)

		def reiniciar(self):
			self.desconectar()
			subprocess.Popen('kplex')
			self.SetStatusText('Kplex starting. Please wait...')
			time.sleep(7)
			self.conectar()

		def OnClick2(self,event):
			self.reiniciar()
			self.crea_lista_packages()

		def OnClick3(self,event):
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

		def OnClick4(self,event):
			subprocess.Popen(['lxterminal', '-e', 'sudo dpkg-reconfigure tzdata'])
			self.SetStatusText('Set time zone in the new window')

		def crea_lista_packages(self):
			try:
				file=open(home+'/.kplex.conf', 'r')
				data=file.readlines()
				file.close()
				self.packages = []
				for index,item in enumerate(data):
					data[index]=item.strip()
					if '[serial]' in item or '[broadcast]' in item:
						device=''
						port=''
						bauds=''
						if '#' in data[index-1]: 
							device=data[index-1].strip('#')
						cont=1
						while True:
							if data[index+cont]==None: break
							if '[' in data[index+cont]: break
							if '=' in data[index+cont]: 
								opcion, valor =data[index+cont].split('=')
								if opcion=='filename': port= valor.strip()
								if opcion=='address': port= valor.strip()+':10110'
								if opcion=='baud': bauds= valor.strip()
							cont=cont+1
						self.add_item_packages(device,port,bauds)
				self.construye_lista()
			except IOError:
				self.SetStatusText('Configuration file does not exist. Add inputs and apply changes')

		def add_item_packages(self,device,port,bauds):
			if device=='': device='Unknow'
			if port=='': port='Unknow'
			if bauds=='': bauds='Unknow'
			temp_list = []
			temp_list.append(device)
			temp_list.append(port)
			temp_list.append(bauds)
			self.packages.append(temp_list)

		def construye_lista(self):
			self.list.DeleteAllItems()
			for i in self.packages:
				index = self.list.InsertStringItem(sys.maxint, i[0])
				self.list.SetStringItem(index, 1, i[1])
				self.list.SetStringItem(index, 2, i[2])

		def OnClick_borrar_input(self,event):
			num = len(self.packages)
			for i in range(num):
				if self.list.IsSelected(i):
					del self.packages[i]
			self.construye_lista()

		def OnClick_add_new(self,event):
			device=self.device.GetValue()
			port=self.deviceComboBox.GetValue()
			bauds=self.baudComboBox.GetValue()
			self.add_item_packages(device,port,bauds)
			self.construye_lista()

		def OnClick_apply(self,event):
			data='# For advanced manual configuration, please visit: http://www.stripydog.com/kplex/configuration.html\n# Editing this file by openplotter GUI, can eliminate manual settings.\n# You should not modify Output.\n\n'
			file = open(home+'/.kplex.conf', 'w')
			for index,item in enumerate(self.packages):
				if item[0]!='localhost UDP in':data=data+'#'+item[0]+'\n[serial]\nfilename='+item[1]+'\nbaud='+item[2]+'\ndirection=in\noptional=yes\n\n'
			data = data + '#localhost UDP in\n[broadcast]\naddress=127.0.0.1\nport=10110\ndirection=in\noptional=yes\n\n'
			data = data + '#Output\n[tcp]\nmode=server\nport=10110\ndirection=out\n'
			file.write(data)
			file.close()
			self.reiniciar()
			self.crea_lista_packages()

		def ventanalog(self):
			while True:
				if self.estado==1:
					frase_nmea = self.s2.recv(512)
					wx.MutexGuiEnter()
					self.logger.AppendText(frase_nmea)
					wx.MutexGuiLeave()
				else:
					pass
		
		def OnClick_nmea_server(self,event):
			subprocess.Popen(['lxterminal', '-e', 'sudo '+home+'/.config/openplotter/nmea_wifi_server/switch_access_point.sh'])
			self.SetStatusText('Set NMEA server in the new window')

		def OnClick_network_man(self,event):
			subprocess.Popen('/usr/sbin/wpa_gui')
			self.SetStatusText('Manage networks in the new window')

app = wx.App(False)
frame = MyFrame(None, 'OpenPlotter Settings')
app.MainLoop()
