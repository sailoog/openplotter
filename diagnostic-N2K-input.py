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

import wx, sys, socket, threading, time, serial
from classes.conf import Conf
from classes.language import Language

class MyFrame(wx.Frame):
		
	def __init__(self):
		self.ttimer=40

		self.conf = Conf()
		self.home = self.conf.home
		self.currentpath = self.home+self.conf.get('GENERAL', 'op_folder')+'/openplotter'
		
		try:
			self.ser = serial.Serial(self.conf.get('N2K', 'can_usb'), 115200, timeout=0.5)
		except:
			print 'failed to start N2K input diagnostic on '+self.conf.get('N2K', 'can_usb')
			sys.exit(0)
					
		Language(self.conf)

		list_N2K_txt=[]
		self.list_N2K=[]
		with open(self.currentpath+'/classes/N2K_PGN.csv') as f:
			list_N2K_txt = [x.strip('\n\r').split(',') for x in f.readlines()]
		
		for ii in list_N2K_txt:
			pgn=int(ii[0])
			self.list_N2K.append([pgn,ii[1]])
		
		self.Buffer = [0] * 500
		self.Zustand=6
		self.list_iter=[]

		wx.Frame.__init__(self, None, title='diagnostic N2K input', size=(650,435))
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		panel = wx.Panel(self, wx.ID_ANY)
		
		self.timer = wx.Timer(self)
		self.Bind(wx.EVT_TIMER, self.timer_act, self.timer)
					
		self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
		
		self.icon = wx.Icon(self.currentpath+'/openplotter.ico', wx.BITMAP_TYPE_ICO)
		self.SetIcon(self.icon)

		self.list = wx.ListCtrl(panel, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
		self.list.InsertColumn(0, _('PGN'), wx.LIST_FORMAT_RIGHT, width=62)
		self.list.InsertColumn(1, _('SRC'), wx.LIST_FORMAT_RIGHT, width=38)
		self.list.InsertColumn(2, _('DST'), wx.LIST_FORMAT_RIGHT, width=38)
		self.list.InsertColumn(3, _('Name'), width=180)
		self.list.InsertColumn(4, _('Interval'), wx.LIST_FORMAT_RIGHT, width=45)
		self.list.InsertColumn(5, _('Data'), width=350)

		sort_SRC =wx.Button(panel, label=_('Sort SRC'))
		sort_SRC.Bind(wx.EVT_BUTTON, self.on_sort_SRC)

		sort_PGN =wx.Button(panel, label=_('Sort PGN'))
		sort_PGN.Bind(wx.EVT_BUTTON, self.on_sort_PGN)
		
		hlistbox = wx.BoxSizer(wx.HORIZONTAL)
		hlistbox.Add(self.list, 1, wx.ALL|wx.EXPAND, 5)

		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(sort_SRC, 0, wx.RIGHT|wx.LEFT, 5)
		hbox.Add(sort_PGN, 0, wx.RIGHT|wx.LEFT, 5)

		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.Add(hlistbox, 1, wx.ALL|wx.EXPAND, 0)
		vbox.Add(hbox, 0, wx.ALL|wx.EXPAND, 0)	
		panel.SetSizer(vbox)

		self.CreateStatusBar()

		self.Show(True)

		self.status=''
		self.data=[]
		self.baudc=0
		self.baud=0

		self.timer.Start(self.ttimer)
		
	def timer_act(self, event):
		if self.ser: 
			frase_nmea=''
			self.getCharfromSerial()
		
	def on_sort_PGN(self, e):
		self.timer.Stop()
		self.list_iter.sort()
		self.list.DeleteAllItems()
		self.init2()
		self.timer.Start(self.ttimer)

	def on_sort_SRC(self, e):
		self.timer.Stop()
		self.list.DeleteAllItems()

		list_new=[]
		for i in sorted(self.list_iter, key=lambda item: (item[1], item[0])):
			list_new.append(i)
		self.list_iter=list_new
		self.init2()
		self.timer.Start(self.ttimer)
		
	def init2(self):
		index=0		
		for i in self.list_iter:
			self.list.InsertStringItem(index, str(i[0]))
			self.list.SetStringItem(index, 1, str(i[1]))
			self.list.SetStringItem(index, 2, str(i[2]))
			self.list.SetStringItem(index, 3, str(i[3]))
			self.list.SetStringItem(index, 4, str(i[4]))
			self.list.SetStringItem(index, 5, '')
			index+=1
							
	def OnClose(self, event):
		self.timer.Stop()
		self.Destroy()

	def getCharfromSerial(self):
		bytesToRead = self.ser.inWaiting()
		if bytesToRead>0:
			buffer=self.ser.read(bytesToRead)			
			for i in buffer:
				#sys.stdout.write(' '+hex(ord(i)))
				self.parse(ord(i))

	def parse(self, b):
		if self.Zustand == 6: # zu Beginn auf 0x10 warten
			if b == 0x10:
				self.Zustand = 0x10
		elif self.Zustand == 0x10:
			if b == 0x10: # 0x10 Schreiben wenn zweimal hintereinander
				self.Buffer[self.p] = b
				self.p += 1
				self.Zustand = 0
			elif b == 0x02: # Anfang gefunden
				self.p = 0
				self.Zustand = 0
			elif b == 0x03: # Ende gefunden
				if self.crcCheck():
					#print "CRC"
					self.output()
				self.p = 0
				self.Zustand = 6 # Auf Anfang zuruecksetzen
		elif self.Zustand == 0:
			if b == 0x10:
				self.Zustand = 0x10
			else:
				self.Buffer[self.p] = b
				self.p += 1

	def crcCheck(self):
		crc = 0
		i = 0
		while i < self.p:
			crc =(crc+ self.Buffer[i]) & 255
			i += 1
		return (crc == 0)

	def output(self):
		k = 0
		if self.Buffer[0] == 0x93 and self.Buffer[1] == self.p - 3:				
			nPriority = self.Buffer[2]
			lPGN=self.Buffer[3]+self.Buffer[4]*256+self.Buffer[5]*256*256
			nDestAddr = self.Buffer[6];
			nSrcAddr = self.Buffer[7]
			length = self.Buffer[12];

			datap=''
			data=0
			for i in range(13,13+length):
				data=data+self.Buffer[i];
				datap+=' '+('0'+hex(self.Buffer[i])[2:])[-2:]
				
			#print lPGN, nSrcAddr, nDestAddr, datap
			
			exist=0
			index=0
			tt=time.time()
			for i in self.list_iter:
				if nSrcAddr==i[1]:
					if lPGN==i[0]:
						td=round(i[4]*0.3+0.7*(tt-i[5]),1)
						self.list_iter[index][4]=td
						self.list_iter[index][5]=tt							
						self.list.SetStringItem(index,4,str(td))
						self.list.SetStringItem(index,5,datap)
						exist=1
				index+=1						
			if exist==0:				
				self.list.InsertStringItem(index, str(lPGN))
				self.list.SetStringItem(index, 1, str(nSrcAddr))
				self.list.SetStringItem(index, 2, str(nDestAddr))
				for ii in self.list_N2K:
					if lPGN==ii[0]:
						self.list.SetStringItem(index, 3, ii[1])
				self.list.SetStringItem(index, 4, 'X')
				self.list.SetStringItem(index, 5, datap)
				self.list_iter.append([lPGN,nSrcAddr,nDestAddr,self.list.GetItem(index, 3).GetText(),0,tt])
										
app = wx.App()
MyFrame().Show()
app.MainLoop()