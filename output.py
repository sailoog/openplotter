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

import wx, socket, threading, time, webbrowser
from classes.datastream import DataStream
from classes.paths import Paths
from classes.conf import Conf
from classes.language import Language
from classes.mqtt import Mqtt

class MyFrame(wx.Frame):
		
		def __init__(self):

			paths=Paths()
			self.currentpath=paths.currentpath

			self.conf=Conf()

			Language(self.conf.get('GENERAL','lang'))

			wx.Frame.__init__(self, None, title="Inspector", size=(650,435))
			self.Bind(wx.EVT_CLOSE, self.OnClose)
			
			self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
			
			self.icon = wx.Icon(self.currentpath+'/openplotter.ico', wx.BITMAP_TYPE_ICO)
			self.SetIcon(self.icon)

			self.logger = wx.TextCtrl(self, style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_DONTWRAP, size=(650,150), pos=(0,0))

			self.list = wx.ListCtrl(self, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER, size=(540, 220), pos=(5, 155))
			self.list.InsertColumn(0, _('Short'), width=50)
			self.list.InsertColumn(1, _('Magnitude'), width=175)
			self.list.InsertColumn(2, _('Value'), width=120)
			self.list.InsertColumn(3, _('Source'), width=80)
			self.list.InsertColumn(4, _('NMEA'), width=50)
			self.list.InsertColumn(5, _('Age'), width=59)

			self.button_pause =wx.Button(self, label=_('Pause'), pos=(555, 160))
			self.Bind(wx.EVT_BUTTON, self.pause, self.button_pause)

			self.button_reset =wx.Button(self, label=_('Reset'), pos=(555, 200))
			self.Bind(wx.EVT_BUTTON, self.reset, self.button_reset)

			self.button_nmea =wx.Button(self, label=_('NMEA info'), pos=(555, 240))
			self.Bind(wx.EVT_BUTTON, self.nmea_info, self.button_nmea)

			self.mqtt=''

			self.reset(0)

			self.pause_all=0

			self.CreateStatusBar()

			self.Centre()

			self.Show(True)

			self.t1_stop= threading.Event()
			self.thread1=threading.Thread(target=self.parse_data, args=(1,self.t1_stop))
			self.t2_stop= threading.Event()
			self.thread2=threading.Thread(target=self.refresh_loop, args=(1,self.t2_stop))
			
			self.s2=''
			self.error=''
			self.frase_nmea_log=''
			self.data=[]

			if not self.thread1.isAlive(): self.thread1.start()
			if not self.thread2.isAlive(): self.thread2.start()

 		# thread 1
		def connect(self):
			try:
				self.s2 = socket.socket()
				self.s2.connect(("localhost", 10110))
				self.s2.settimeout(5)
			except socket.error, error_msg:
				self.error= _('Failed to connect with localhost:10110. Error: ')+ str(error_msg[0])+_(', trying to reconnect...')
				self.s2=''
				time.sleep(7)
			else: self.error=''
			

		def parse_data(self,arg1,stop_event):
			while (not stop_event.is_set()):
				if not self.s2: self.connect()
				else:
					frase_nmea=''
					try:
						frase_nmea = self.s2.recv(1024)
					except socket.error, error_msg:
						self.error= _('Connected with localhost:10110. Error: ')+ str(error_msg[0])+_(', waiting for data...')
					else:
						if frase_nmea and self.pause_all==0:
							self.a.parse_nmea(frase_nmea)
							self.frase_nmea_log+=frase_nmea
							self.error = _('Connected with localhost:10110.')
						else:
							self.s2=''
		# end thread 1

		# thread 2
		def refresh_loop(self,arg1,stop_event):
			while (not stop_event.is_set()):
				if self.pause_all==0:
					self.a.checkinputs()
					self.a.checkoutputs()
					index=0
					for i in self.a.DataList:
						timestamp=i[4]
						if timestamp:
							now=time.time()
							age=now-timestamp
							value=''
							unit=''
							talker=''
							sentence=''
							value=i[2]
							unit=i[3]
							talker=i[5]
							sentence=i[6]
							if talker=='OC': talker=_('Calculated')
							if talker=='OS': talker=_('Sensor')
							if unit: data = str(value)+' '+str(unit)
							else: data = str(value)
							self.data=[index,2,data]
							wx.CallAfter(self.refresh_data)
							time.sleep(0.001)
							if talker:
								self.data=[index,3,talker]
								wx.CallAfter(self.refresh_data)
								time.sleep(0.001)
							if sentence: 
								self.data=[index,4,sentence]
								wx.CallAfter(self.refresh_data)
								time.sleep(0.001)
							self.data=[index,5,str(round(age,1))]
							wx.CallAfter(self.refresh_data)
							time.sleep(0.001)
						index=index+1
					wx.CallAfter(self.refresh_data)
					time.sleep(0.001)
					
				else: time.sleep(0.001)
		# end thread 2

		def refresh_data(self):
			if self.data: self.list.SetStringItem(self.data[0],self.data[1],self.data[2])
			if self.frase_nmea_log: 
				self.logger.AppendText(self.frase_nmea_log)
				self.frase_nmea_log=''
			self.SetStatusText(self.error)

		def pause(self, e):
			if self.pause_all==0: 
				self.pause_all=1
				self.button_pause.SetLabel(_('Resume'))
			else: 
				self.pause_all=0
				self.button_pause.SetLabel(_('Pause'))

		def reset(self, e):
			self.pause_all=1
			self.list.DeleteAllItems()
			self.logger.SetValue('')
			time.sleep(1)
			self.conf.read()
			self.a=DataStream(self.conf)
			if self.mqtt: self.mqtt.stop()
			self.mqtt=Mqtt(self.conf,self.a)
			index=0
			for i in self.a.DataList:
				short=i[1]
				name=i[0]
				self.list.InsertStringItem(index,short)
				self.list.SetStringItem(index,1,name)
				index=index+1

			self.pause_all=0

		def nmea_info(self, e):
			url = self.currentpath+'/docs/NMEA.html'
			webbrowser.open(url,new=2)
					
		def OnClose(self, event):
			self.t1_stop.set()
			self.t2_stop.set()
			if self.mqtt: self.mqtt.stop()
			while (self.thread1.isAlive() or self.thread2.isAlive()):
				time.sleep(0.1)
			self.Destroy()

app = wx.App()
MyFrame().Show()
app.MainLoop()