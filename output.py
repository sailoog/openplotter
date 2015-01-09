#!/usr/bin/env python

import wx, socket, os, threading, time, gettext, sys

home = os.path.expanduser('~')

class MyFrame(wx.Frame):
		
		def __init__(self, parent, title):

			gettext.install('openplotter', home+'/.config/openplotter/locale', unicode=False)
			self.presLan_en = gettext.translation('openplotter', home+'/.config/openplotter/locale', languages=['en'])
			self.presLan_ca = gettext.translation('openplotter', home+'/.config/openplotter/locale', languages=['ca'])
			self.presLan_es = gettext.translation('openplotter', home+'/.config/openplotter/locale', languages=['es'])

			language=sys.argv[1]
			if language=='en':self.presLan_en.install()
			if language=='ca':self.presLan_ca.install()
			if language=='es':self.presLan_es.install()


			wx.Frame.__init__(self, parent, title=title, size=(500,200))
			
			self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
			
			self.icon = wx.Icon(home+'/.config/openplotter/openplotter.ico', wx.BITMAP_TYPE_ICO)
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

