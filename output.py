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

import wx, socket, os, threading, time, gettext, sys

pathname = os.path.dirname(sys.argv[0])
currentpath = os.path.abspath(pathname)

class MyFrame(wx.Frame):
		
		def __init__(self, parent, title):

			gettext.install('openplotter', currentpath+'/locale', unicode=False)
			self.presLan_en = gettext.translation('openplotter', currentpath+'/locale', languages=['en'])
			self.presLan_ca = gettext.translation('openplotter', currentpath+'/locale', languages=['ca'])
			self.presLan_es = gettext.translation('openplotter', currentpath+'/locale', languages=['es'])

			language=sys.argv[1]
			if language=='en':self.presLan_en.install()
			if language=='ca':self.presLan_ca.install()
			if language=='es':self.presLan_es.install()


			wx.Frame.__init__(self, parent, title=title, size=(500,200))
			
			self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
			
			self.icon = wx.Icon(currentpath+'/openplotter.ico', wx.BITMAP_TYPE_ICO)
			self.SetIcon(self.icon)

			self.logger = wx.TextCtrl(self, style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_DONTWRAP, size=(500,200), pos=(0,0))

			self.CreateStatusBar()

			self.Centre()

			self.Show(True)

			self.hilo=threading.Thread(target=self.ventanalog)
			self.hilo.setDaemon(1)

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
						frase_nmea = self.s2.recv(512)
					except socket.error, error_msg:
						self.error_message=str(error_msg[0])
				if frase_nmea:
					wx.MutexGuiEnter()
					self.logger.AppendText(frase_nmea)
					self.SetStatusText(_('Kplex started'))
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
					

app = wx.App(False)
frame = MyFrame(None, 'TCP localhost:10110')
app.MainLoop()

