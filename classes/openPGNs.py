#!/usr/bin/env python

# This file is part of Openplotter.
# Copyright (C) 2019 by sailoog <https://github.com/sailoog/openplotter>
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

import wx, time, serial, codecs
from wx.lib.mixins.listctrl import CheckListCtrlMixin, ListCtrlAutoWidthMixin
from classes.language import Language

class CheckListCtrl(wx.ListCtrl, CheckListCtrlMixin, ListCtrlAutoWidthMixin):
	def __init__(self, parent, width,height):
		wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT, size=(width, height))
		CheckListCtrlMixin.__init__(self)
		ListCtrlAutoWidthMixin.__init__(self)

class openPGNs(wx.Dialog):
		
	def __init__(self,parent,alias,bauds):
		self.error = ''
		self.can_device = alias
		self.baud_ = bauds								
		self.parent = parent
		self.conf = parent.conf
		self.currentpath = parent.currentpath
		self.ttimer = 100	
		Language(self.conf)
		Buf_ = (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0)
		self.Buffer = bytearray(Buf_)
		self.Zustand=6
		self.buffer=0
		self.PGN_list=[]
		self.list_N2K_txt=[]
		self.list_count=[]
		self.p=0

		wx.Dialog.__init__(self, None, title=_('Open device PGNs'), size=(650,430))
		self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
		icon = wx.Icon(self.currentpath+'/static/icons/openplotter.ico', wx.BITMAP_TYPE_ICO)
		self.SetIcon(icon)

		self.timer = wx.Timer(self)
		self.Bind(wx.EVT_TIMER, self.timer_act, self.timer)

		panel = wx.Panel(self, 100)
		self.list_N2K = CheckListCtrl(panel, -1,240)
		self.list_N2K.SetBackgroundColour((230,230,230))
		self.list_N2K.SetPosition((10, 25))
		self.list_N2K.InsertColumn(0, _('TX PGN'), width=100)
		self.list_N2K.InsertColumn(1, _('info'), width=220)
		self.txLabel = wx.StaticText(panel, wx.ID_ANY, style=wx.ALIGN_CENTER)
		self.printing = wx.TextCtrl(panel, -1, style=wx.TE_MULTILINE | wx.TE_READONLY, size=(-1,50))
		self.printing.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_INACTIVECAPTION))
		
		apply_b = wx.Button(panel, label=_('Apply'))
		self.Bind(wx.EVT_BUTTON, self.apply, apply_b)
		close_b = wx.Button(panel, label=_('Close'))
		self.Bind(wx.EVT_BUTTON, self.OnClose, close_b)

		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.AddStretchSpacer(1)
		hbox.Add(apply_b, 0, wx.LEFT, 10)
		hbox.Add(close_b, 0, wx.LEFT, 10)

		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.Add(self.list_N2K, 1, wx.ALL | wx.EXPAND, 10)
		vbox.Add(self.txLabel, 0, wx.LEFT, 10)
		vbox.Add(self.printing, 1, wx.ALL | wx.EXPAND, 10)
		vbox.Add(hbox, 1, wx.ALL | wx.EXPAND, 10)

		panel.SetSizer(vbox)
		self.Centre()

		try:
			self.ser = serial.Serial(self.can_device, self.baud_, timeout=0.5)
		except:
			self.printing.SetValue(_('Error connecting with device ')+self.can_device)
			apply_b.Disable()
			self.list_N2K.Disable()
		else:
			self.read_N2K()
			self.check(0)
			self.timer.Start(self.ttimer)
		
	def check(self,e):
		self.printing.SetValue('')

		self.Send_Command(1, 0x01, 0)
		time.sleep(0.2)

		counter=0
		for ii in self.list_N2K_txt:
			self.list_N2K.CheckItem(counter,False)
			counter+=1

		self.PGN_list=[]
		self.work = True
		self.Send_Command(1, 0x49, 0)
		i=0
		while (self.work):
			self.getCharfromSerial()
			time.sleep(0.01)
			i+=1
			if i>200:
				self.work = False
		self.read_stick_check()
		if len(self.PGN_list)<1: self.printing.SetValue(_('The list of enabled PGNs is empty, you may need to try a different baudrate or reset your device to 115200 bauds'))
	
	def apply(self,e):
		new = _('open PGNs: ')
		close = _('close PGNs: ')
		msg = ''
		counter = 0
		maxpgns = False
		st=''
		for ii in self.list_N2K_txt:
			if self.list_N2K.IsChecked(counter):
				exist=0
				for jj in self.PGN_list:
					if ii[0]==str(jj):
						exist=1
				if exist==0:
					st+=ii[0]+' '
					if len(self.PGN_list)<30:
						self.sendTX_PGN(int(ii[0]),1)
						self.PGN_list.append(ii[0])
						time.sleep(0.2)
					else: maxpgns = True		
			counter+=1		
		new += st

		st=''
		for jj in self.PGN_list:
			counter=0
			for ii in self.list_N2K_txt:
				exist=0
				if ii[0]==str(jj):
					if not self.list_N2K.IsChecked(counter):
						exist=1
					if exist==1:
						st+=ii[0]+' '
						self.sendTX_PGN(int(ii[0]),0)
						time.sleep(0.2)
				counter+=1		
		close += st

		self.Send_Command(1, 0x01, 0)
		if maxpgns: msg += _('You can not activate more than 30 PGNs\n\n')
		msg += new+'\n'+close
		wx.MessageBox(msg, 'Info', wx.OK | wx.ICON_INFORMATION)
		self.check(0)
		
	def sendTX_PGN(self,lPGN,add):
		if add:
			data_ = (0,0,0,0,1,0xFE,0xFF,0xFF,0xFF,0xFE,0xFF,0xFF,0xFF)
		else:
			data_ = (0,0,0,0,0,0,0,0,0,0,0,0,0)
		data = bytearray(data_)
		data[0]=lPGN&255
		data[1]=(lPGN >> 8)&255
		data[2]=(lPGN >> 16)&255
		
		self.Send_Command(14, 0x47, data)
		
	def Send_Command(self, length, command, arg):
		data_ = (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0)
		data = bytearray(data_)

		data[0] = 0xa1 #command
		data[1] = length #Actisense length
		data[2] = command
		i=3
		while i<length+2:
			data[i] = arg[i-3]
			i+=1
		self.SendCommandtoSerial(data)
		
	def timer_act(self,e):
		self.getCharfromSerial()

	def OnClose(self, event):
		self.timer.Stop()
		self.EndModal(wx.OK)
					
	def SendCommandtoSerial(self, TXs):
		crc = 0
		#start = codecs.decode('1002', 'hex_codec')
		start = (0x10, 0x02)
		ende = codecs.decode('1003', 'hex_codec')
		ende = (0x10, 0x03)
		i = 0
		while i < TXs[1] + 2:
			crc += TXs[i]
			i += 1
		crc = (256 - crc) & 255
		TXs[TXs[1] + 2] = crc
		i = 0
		self.ser.write(chr(start[0]))
		self.ser.write(chr(start[1]))
		while i < TXs[1] + 3:
			self.ser.write(chr(TXs[i]))
			if TXs[i] == 0x10:
				self.ser.write(chr(TXs[i]))
			i += 1
		self.ser.write(chr(ende[0]))
		self.ser.write(chr(ende[1]))

	def getCharfromSerial(self):
		bytesToRead = self.ser.inWaiting()
		if bytesToRead>0:
			buffer=self.ser.read(bytesToRead)			
			for i in buffer:
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
		if self.Buffer[0] == 0x93 and self.Buffer[1] == self.p - 3:
			pass
		else:
			if self.Buffer[2] == 0x49 and self.Buffer[3] == 0x01:
				j = 0
				st=''
				self.PGN_list=[]
				while j < self.Buffer[14]:
					i=j*4
					lPGN=self.Buffer[15+i]+self.Buffer[16+i]*256+self.Buffer[17+i]*256*256
					if lPGN in self.PGN_list:
						print lPGN,'already exists'
					else:
						self.PGN_list.append(lPGN)
						st+=str(lPGN)+' '
						
					j+=1
				self.printing.SetValue(st)
				self.txLabel.SetLabel(str(j)+_(" enabled transmission PGNs (max. 30):"))
				self.work = False
				
	def getCommandfromSerial(self, RXs):
		crc = 0
		start = (0x10, 0x02)
		ende = (0x10, 0x03)
		i = 0
		while i < RXs[1] + 2:
			crc += RXs[i]
			i += 1
		crc = (256 - crc) & 255
		RXs[RXs[1] + 2] = crc
		i = 0
		self.ser.write(chr(start[0]))
		self.ser.write(chr(start[1]))
		while i < RXs[1] + 3:
			self.ser.write(chr(RXs[i]))
			#print format(RXs[i], '02x')
			if RXs[i] == 0x10:
				self.ser.write(chr(RXs[i]))
			i += 1
		self.ser.write(chr(ende[0]))
		self.ser.write(chr(ende[1]))
		
	def read_N2K(self):
		if self.list_N2K.GetItemCount()<3:
			while self.list_N2K.GetItemCount()>3:
				self.list_N2K.DeleteItem(self.list_N2K.GetItemCount()-1)
			
			self.list_N2K_txt=[]
			with open(self.currentpath+'/classes/N2K_PGN.csv') as f:
				self.list_N2K_txt = [x.strip('\n\r').split(',') for x in f.readlines()]
			
			for ii in self.list_N2K_txt:
				pgn=int(ii[0])
				self.list_N2K.Append([pgn,ii[1]])

	def read_stick_check(self):		
		counter=0
		self.list_N2K.CheckItem(0,False)
		for ii in self.list_N2K_txt:
			for jj in self.PGN_list:
				if ii[0]==str(jj):
					self.list_N2K.CheckItem(counter)					
			counter+=1
		self.list_N2K.Update()
		