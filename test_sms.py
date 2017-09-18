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

import wx, sys, subprocess, gammu
from classes.conf import Conf
from classes.language import Language

class MainFrame(wx.Frame):
		
		def __init__(self):

			self.option=sys.argv[1]
			self.text_sms=sys.argv[2]
			self.text_sms=unicode(self.text_sms,'utf-8')
			self.phone=sys.argv[3]

			self.conf = Conf()
			self.home = self.conf.home
			self.currentpath = self.home+self.conf.get('GENERAL', 'op_folder')+'/openplotter'

			Language(self.conf)

			wx.Frame.__init__(self, None, title=_('Test SMS'), size=(500,260))

			self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
			
			self.icon = wx.Icon(self.currentpath+'/openplotter.ico', wx.BITMAP_TYPE_ICO)
			self.SetIcon(self.icon)

			self.CreateStatusBar()

			self.text=wx.StaticText(self, label=_('Error'), pos=(10, 10))

			self.output = wx.TextCtrl(self, style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_DONTWRAP, size=(480,110), pos=(10,50))
			
			self.button_close =wx.Button(self, label=_('Close'), pos=(300, 170))
			self.Bind(wx.EVT_BUTTON, self.close, self.button_close)

			self.button_calculate =wx.Button(self, label=_('Start'), pos=(400, 170))
			self.Bind(wx.EVT_BUTTON, self.calculate, self.button_calculate)

			if self.option=='i': 
				self.text.SetLabel(_('Press start to check the settings and connect to the GSM device'))

			if self.option=='t':
				self.text.SetLabel(_('Press start to send the text "')+self.text_sms+_('"\nto the number "')+self.phone+'"')

			self.Centre()

		def calculate(self,e):
			self.output.SetValue('')
			output=''
			if self.option=='i': 
				self.SetStatusText(_('Connecting...'))
				try:
					output=subprocess.check_output(['gammu', 'identify'])
				except: output= _('Error opening device. Check settings.')	
			if self.option=='t':
				self.SetStatusText(_('Sending...'))
				try:
					sm = gammu.StateMachine()
					sm.ReadConfig()
					sm.Init()
					netinfo = sm.GetNetworkInfo()
					output+= 'Network name: %s' % netinfo['NetworkName']
					output+= '\nNetwork code: %s' % netinfo['NetworkCode']
					output+= '\nLAC: %s' % netinfo['LAC']
					output+= '\nCID: %s' % netinfo['CID']
					message = {
						'Text': self.text_sms, 
						'SMSC': {'Location': 1},
						'Number': self.phone,
					}
					sm.SendSMS(message)
					output+='\nSMS "'+self.text_sms+_('" sent succesfully to ')+self.phone
				except Exception,e: output= str(e)

			self.output.SetValue(output)
			self.SetStatusText(_('Finished'))

		def close(self,e):
			self.Destroy()

if __name__ == "__main__":
	app = wx.App()
	MainFrame().Show()
	app.MainLoop()