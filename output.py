#!/usr/bin/env python

import wx, socket, threading, time

class MyFrame(wx.Frame):
		
		def __init__(self, parent, title):

			wx.Frame.__init__(self, parent, title=title, size=(500,200))

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
				self.error_message=""
			except socket.error, error_msg:
				self.error_message=str(error_msg[0])
			if not self.hilo.isAlive():
				self.hilo.start()

		def ventanalog(self):
			while True:
				frase_nmea=""
				if not self.error_message:
					frase_nmea = self.s2.recv(512)
				if frase_nmea:
					wx.MutexGuiEnter()
					self.logger.AppendText(frase_nmea)
					self.SetStatusText('Kplex started')
					wx.MutexGuiLeave()
				else:
					wx.MutexGuiEnter()
					if self.error_message:
						self.SetStatusText('Failed to connect with localhost:10110. '+'Error code: ' + self.error_message)
						time.sleep(3)
					else:
						self.SetStatusText('No data, trying to reconnect...')
						time.sleep(3)
					self.SetStatusText('No data, trying to reconnect...')
					wx.MutexGuiLeave()
					time.sleep(4)
					self.connect()
					
			
			




app = wx.App(False)
frame = MyFrame(None, 'Output TCP localhost:10110')
app.MainLoop()

