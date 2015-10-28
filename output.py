#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

import wx, socket, os, threading, time, gettext, sys, webbrowser
from classes.datastream import DataStream

pathname = os.path.dirname(sys.argv[0])
currentpath = os.path.abspath(pathname)

class MyFrame(wx.Frame):
		
		def __init__(self, parent, title):

			gettext.install('openplotter', currentpath+'/locale', unicode=False)
			self.presLan_en = gettext.translation('openplotter', currentpath+'/locale', languages=['en'])
			self.presLan_ca = gettext.translation('openplotter', currentpath+'/locale', languages=['ca'])
			self.presLan_es = gettext.translation('openplotter', currentpath+'/locale', languages=['es'])
			self.presLan_fr = gettext.translation('openplotter', currentpath+'/locale', languages=['fr'])

			language=sys.argv[1]
			if language=='en':self.presLan_en.install()
			if language=='ca':self.presLan_ca.install()
			if language=='es':self.presLan_es.install()
			if language=='fr':self.presLan_fr.install()


			wx.Frame.__init__(self, parent, title=title, size=(650,400))
			
			self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
			
			self.icon = wx.Icon(currentpath+'/openplotter.ico', wx.BITMAP_TYPE_ICO)
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

			self.hilo=threading.Thread(target=self.ventanalog)

			self.connect()

		def connect(self):
			try:
				self.s2 = socket.socket()
				self.s2.connect(("localhost", 10110))
				self.s2.settimeout(10)
				self.error_message=""
			except socket.error, error_msg:
				self.error_message=str(error_msg[0])
			if not self.hilo.isAlive():
				self.hilo.start()

		def ventanalog(self):
			while True:
				frase_nmea=""
				if not self.error_message:
					try:
						frase_nmea = self.s2.recv(1024)
					except socket.error, error_msg:
						self.error_message=str(error_msg[0])
				if frase_nmea:
					wx.MutexGuiEnter()
					self.a.parse_nmea(frase_nmea)
					if self.pause_all==0: self.logger.AppendText(frase_nmea)
					self.SetStatusText(_('Multiplexer started'))
					wx.MutexGuiLeave()
				else:
					wx.MutexGuiEnter()
					if self.error_message:
						self.SetStatusText(_('Failed to connect with localhost:10110. ')+_('Error code: ') + self.error_message)
						time.sleep(3)
					else:
						self.SetStatusText(_('No data, trying to reconnect...'))
						time.sleep(3)
					self.SetStatusText(_('No data, trying to reconnect...'))
					wx.MutexGuiLeave()
					time.sleep(4)
					self.connect()

				if self.pause_all==0:
					index=0
					for i in self.a.DataList:
						timestamp=eval('self.a.'+i+'[4]')
						if timestamp:
							now=time.time()
							age=now-timestamp
							if age < 5:
								value=eval('self.a.'+i+'[2]')
								if i=='Lat': value='%02d°%07.4f′' % (int(value[:2]), float(value[2:]))
								if i=='Lon': value='%02d°%07.4f′' % (int(value[:3]), float(value[3:]))
								unit=eval('self.a.'+i+'[3]')
								data= str(value)+' '+str(unit)
								talker=eval('self.a.'+i+'[5]')
								if talker=='OP': talker='OpenPlotter'
								sentence=eval('self.a.'+i+'[6]')
								wx.MutexGuiEnter()
								self.list.SetStringItem(index,1,data)
								self.list.SetStringItem(index,2,talker)
								self.list.SetStringItem(index,3,sentence)
								self.list.SetStringItem(index,4,str(round(age,1)))
								wx.MutexGuiLeave()
							else:
								wx.MutexGuiEnter()
								self.list.SetStringItem(index,4,str(round(age,1)))
								wx.MutexGuiLeave()
						index=index+1

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

		def nmea_info(self, e):
			url = currentpath+'/docs/NMEA.html'
			webbrowser.open(url,new=2)


app = wx.App(False)
frame = MyFrame(None, 'TCP localhost:10110')
app.MainLoop()

