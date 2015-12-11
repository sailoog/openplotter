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



class MyFrame(wx.Frame):
		
		def __init__(self, parent, title):

			paths=Paths()
			self.currentpath=paths.currentpath

			self.conf=Conf()

			Language(self.conf.get('GENERAL','lang'))

			wx.Frame.__init__(self, parent, title=title, size=(650,435))
			
			self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
			
			self.icon = wx.Icon(self.currentpath+'/openplotter.ico', wx.BITMAP_TYPE_ICO)
			self.SetIcon(self.icon)

			self.logger = wx.TextCtrl(self, style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_DONTWRAP, size=(650,150), pos=(0,0))

			wx.StaticText(self, label=_('NMEA inspector'), pos=(525, 160))

			self.button_pause =wx.Button(self, label=_('Pause'), pos=(530, 190))
			self.Bind(wx.EVT_BUTTON, self.pause, self.button_pause)

			self.button_reset =wx.Button(self, label=_('Reset'), pos=(530, 230))
			self.Bind(wx.EVT_BUTTON, self.reset, self.button_reset)

			self.button_nmea =wx.Button(self, label=_('NMEA info'), pos=(530, 270))
			self.Bind(wx.EVT_BUTTON, self.nmea_info, self.button_nmea)

			self.list = wx.ListCtrl(self, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER, size=(500, 220), pos=(5, 155))
			self.list.InsertColumn(0, _('Type'), width=165)
			self.list.InsertColumn(1, _('Value'), width=130)
			self.list.InsertColumn(2, _('Source'), width=90)
			self.list.InsertColumn(3, _('NMEA'), width=50)
			self.list.InsertColumn(4, _('Age'), width=59)

			self.a=DataStream()

			index=0
			for i in self.a.DataList:
				data=eval('self.a.'+i+'[0]')
				self.list.InsertStringItem(index,data)
				index=index+1

			self.pause_all=0

			self.CreateStatusBar()

			self.Centre()

			self.Show(True)

			self.thread1=threading.Thread(target=self.parse_data)
			self.thread2=threading.Thread(target=self.refresh_loop)
			
			self.s2=''
			self.error=''
			self.frase_nmea_log=''
			self.data=[]
			self.read_conf=0

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
			

		def parse_data(self):
			while True:
				if not self.s2: self.connect()
				else:
					frase_nmea=''
					try:
						frase_nmea = self.s2.recv(1024)
					except socket.error, error_msg:
						self.error= _('Connected with localhost:10110. Error: ')+ str(error_msg[0])+_(', waiting for data...')
					else:
						if frase_nmea:
							self.a.parse_nmea(frase_nmea)
							self.frase_nmea_log+=frase_nmea
							self.error = _('Connected with localhost:10110.')
						else:
							self.s2=''
		# end thread 1

		# thread 2
		def refresh_loop(self):
			while True:	
				if self.pause_all==0:
					if self.conf.get('SWITCH1', 'enable')=='1': self.a.switches_status(1, self.conf.get('SWITCH1', 'gpio'), self.conf.get('SWITCH1', 'pull_up_down'))
					if self.conf.get('SWITCH2', 'enable')=='1': self.a.switches_status(2, self.conf.get('SWITCH2', 'gpio'), self.conf.get('SWITCH2', 'pull_up_down'))
					if self.conf.get('SWITCH3', 'enable')=='1': self.a.switches_status(3, self.conf.get('SWITCH3', 'gpio'), self.conf.get('SWITCH3', 'pull_up_down'))
					if self.conf.get('SWITCH4', 'enable')=='1': self.a.switches_status(4, self.conf.get('SWITCH4', 'gpio'), self.conf.get('SWITCH4', 'pull_up_down'))
					if self.conf.get('SWITCH5', 'enable')=='1': self.a.switches_status(5, self.conf.get('SWITCH5', 'gpio'), self.conf.get('SWITCH5', 'pull_up_down'))
					if self.conf.get('SWITCH6', 'enable')=='1': self.a.switches_status(6, self.conf.get('SWITCH6', 'gpio'), self.conf.get('SWITCH6', 'pull_up_down'))
					if self.read_conf==1: 
						self.conf.read()
						self.read_conf=0
					index=0
					for i in self.a.DataList:
						timestamp=eval('self.a.'+i+'[4]')
						if timestamp:
							now=time.time()
							age=now-timestamp
							value=''
							unit=''
							talker=''
							sentence=''
							value=eval('self.a.'+i+'[2]')
							unit=eval('self.a.'+i+'[3]')
							talker=eval('self.a.'+i+'[5]')
							sentence=eval('self.a.'+i+'[6]')
							if talker=='OP': talker='OpenPlotter'
							if unit: data = str(value)+' '+str(unit)
							else: data = str(value)
							self.data=[index,1,data]
							wx.CallAfter(self.refresh_data)
							time.sleep(0.001)
							if talker:
								self.data=[index,2,talker]
								wx.CallAfter(self.refresh_data)
								time.sleep(0.001)
							if sentence: 
								self.data=[index,3,sentence]
								wx.CallAfter(self.refresh_data)
								time.sleep(0.001)
							self.data=[index,4,str(round(age,1))]
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
			for i in range(self.list.GetItemCount()):
				self.list.SetStringItem(i,1,'')
				self.list.SetStringItem(i,2,'')
				self.list.SetStringItem(i,3,'')
				self.list.SetStringItem(i,4,'')
			self.logger.SetValue('')
			self.read_conf=1

		def nmea_info(self, e):
			url = self.currentpath+'/docs/NMEA.html'
			webbrowser.open(url,new=2)

app = wx.App(False)
frame = MyFrame(None, 'TCP localhost:10110')
app.MainLoop()