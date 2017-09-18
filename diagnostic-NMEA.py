#!/usr/bin/env python

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

import wx, sys, socket, threading, time, webbrowser
from classes.conf import Conf
from classes.language import Language

class MyFrame(wx.Frame):
		
	def __init__(self):
		self.ttimer=100
		
		self.conf = Conf()
		self.home = self.conf.home
		self.currentpath = self.home+self.conf.get('GENERAL', 'op_folder')+'/openplotter'

		Language(self.conf)

		self.list_iter=[]

		titleadd=''
		if len(sys.argv)>2:
			titleadd=sys.argv[2]
		
		wx.Frame.__init__(self, None, title=titleadd, size=(650,435))
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		panel = wx.Panel(self, wx.ID_ANY)		
		
		self.timer = wx.Timer(self)
		self.Bind(wx.EVT_TIMER, self.timer_act, self.timer)
					
		self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
		
		self.icon = wx.Icon(self.currentpath+'/openplotter.ico', wx.BITMAP_TYPE_ICO)
		self.SetIcon(self.icon)

		self.logger = wx.TextCtrl(panel, style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_DONTWRAP|wx.LC_SORT_ASCENDING)

		self.list = wx.ListCtrl(panel, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
		self.list.InsertColumn(0, _('Device'), width=50)
		self.list.InsertColumn(1, _('Type'), width=50)
		self.list.InsertColumn(2, _('Interval'), wx.LIST_FORMAT_RIGHT, width=50)
		self.list.InsertColumn(3, _('Data'), width=500)

		self.button_pause =wx.Button(panel, label=_('Pause'), pos=(555, 160))
		self.button_pause.Bind(wx.EVT_BUTTON, self.pause)

		sort =wx.Button(panel, label=_('Sort'), pos=(555, 200))
		sort.Bind(wx.EVT_BUTTON, self.sort)

		nmea =wx.Button(panel, label=_('NMEA info'), pos=(555, 240))
		nmea.Bind(wx.EVT_BUTTON, self.nmea_info)

		self.pause_all=0
		
		htextbox = wx.BoxSizer(wx.HORIZONTAL)
		htextbox.Add(self.logger, 1, wx.ALL|wx.EXPAND, 5)
		
		hlistbox = wx.BoxSizer(wx.HORIZONTAL)
		hlistbox.Add(self.list, 1, wx.ALL|wx.EXPAND, 5)

		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.button_pause, 0, wx.RIGHT|wx.LEFT, 5)
		hbox.Add(sort, 0, wx.RIGHT|wx.LEFT, 5)
		hbox.Add(nmea, 0, wx.RIGHT|wx.LEFT, 5)

		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.Add(htextbox, 1, wx.ALL|wx.EXPAND, 0)
		vbox.Add(hlistbox, 1, wx.ALL|wx.EXPAND, 0)
		vbox.Add(hbox, 0, wx.ALL|wx.EXPAND, 0)	
		panel.SetSizer(vbox)
		

		self.CreateStatusBar()

		self.Show(True)

		self.s2=''
		self.status=''
		self.data=[]
		self.baudc=0
		self.baud=0

		self.timer.Start(self.ttimer)

	def connect(self):
		port=10113
		try:
			if len(sys.argv)>0:
				port=int(sys.argv[1])
			self.s2 = socket.socket()
			self.s2.connect(("localhost", port))
			self.s2.settimeout(5)
			self.status= _('connected to:')+str(port)
		except socket.error, error_msg:
			self.status= _('Failed to connect with localhost:10113. Error: ')+ str(error_msg[0])+_(', trying to reconnect...')
			self.s2=''
			time.sleep(7)
		else: self.status=''
		
	def timer_act(self, event):
		frase_nmea_log=''
		if not self.s2: 
			self.connect()
		else:
			frase_nmea=''
			self.timer.Stop()
			try:
				frase_nmea = self.s2.recv(1024)
			except Exception as ex:
				#except error_msg:
				#	self.status= _('Connected with localhost:10110. Error: ')+ str(error_msg[0])+_(', waiting for data...')
				template = "An exception of type {0} occured. Arguments:\n{1!r}"
				self.status = template.format(type(ex).__name__, ex.args)
				self.SetStatusText(self.status)

			else:
				if frase_nmea and self.pause_all==0:
					self.baud+=10*len(frase_nmea)
					tt=time.time()
					
					if self.baudc+1<tt:
						self.baud = round(self.baud/(tt-self.baudc))
						self.status = 'transfer speed '+str(self.baud)+' baud'
						self.SetStatusText(self.status)
						self.baud=0
						self.baudc=tt
					nmea_list=frase_nmea.split()
					for i in nmea_list:
						device=i[1:3]
						sentence=i[3:6].encode('utf-8')
						dat=i[6:-2]
						index=0
						exist=0
						for i in self.list_iter:
							if sentence==i[1]:
								if device==i[0]:
									td=round(i[2]*0.5+0.5*(tt-i[4]),1)
									self.list_iter[index][2]=td
									self.list_iter[index][4]=tt
									self.list.SetStringItem(index,2,str(td))
									self.list.SetStringItem(index,3,dat)
									exist=1
							index+=1						
						if exist==0:
							self.list_iter.append([device,sentence,0,dat,time.time()])
							self.list.InsertStringItem(index, device)
							self.list.SetStringItem(index, 1, sentence)
							self.list.SetStringItem(index, 2, str(0))
							self.list.SetStringItem(index, 3, dat)
					frase_nmea_log+=frase_nmea
		if frase_nmea_log:
			self.logger.AppendText(frase_nmea_log)
		self.timer.Start(self.ttimer)
		
	def pause(self, e):
		if self.pause_all==0: 
			self.pause_all=1
			self.button_pause.SetLabel(_('Resume'))
		else: 
			self.pause_all=0
			self.button_pause.SetLabel(_('Pause'))

	def sort(self, e):
		self.timer.Stop()
		index=0
		self.list_iter.sort()
		self.list.DeleteAllItems()
		for i in self.list_iter:
			self.list.InsertStringItem(index, i[0])
			self.list.SetStringItem(index, 1, i[1])
			self.list.SetStringItem(index, 2, str(i[2]))
			self.list.SetStringItem(index, 3, i[3])
			index+=1
		self.timer.Start(self.ttimer)
			
	def nmea_info(self, e):
		url = self.currentpath+'/docs/NMEA.html'
		webbrowser.open(url,new=2)
				
	def OnClose(self, event):
		self.timer.Stop()
		self.Destroy()

app = wx.App()
MyFrame().Show()
app.MainLoop()