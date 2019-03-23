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

import wx, time, serial, sys, os
from classes.conf import Conf
from classes.language import Language

class MyFrame(wx.Frame):

	def __init__(self):
		self.ttimer=40
		self.conf = Conf()
		self.home = self.conf.home
		self.currentpath = self.conf.get('GENERAL', 'op_folder')
		
		data = self.conf.get('UDEV', 'Serialinst')
		try:
			Serialinst = eval(data)
		except:
			Serialinst = {}

		self.can_device = ''
		for name in Serialinst:
			if Serialinst[name]['assignment'] == 'CAN-USB':
				self.can_device = '/dev/ttyOP_'+name
				break
				
		try:
			self.ser = serial.Serial(self.can_device, 115200, timeout=0.5)
		except:
			print 'failed to start N2K output setting on '+self.can_device
			sys.exit(0)
					
		Language(self.conf)

		wx.Frame.__init__(self, None, title="CAN-USB reset", size=(300,130))
		self.Bind(wx.EVT_CLOSE, self.OnClose)
	
		self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
		
		self.icon = wx.Icon(self.currentpath+'/openplotter.ico', wx.BITMAP_TYPE_ICO)
		self.SetIcon(self.icon)
		
		panel = wx.Panel(self, 100)
		
		wx.StaticText(panel, wx.ID_ANY, label='!!!'+_('You know that all settings')+'\n'+_('on your CAN-USB will be cleared')+'!!!', style=wx.ALIGN_CENTER, pos=(10,60))
		
		self.reset_b = wx.Button(panel, label=_('reset'),size=(70, 32), pos=(10, 10))
		self.Bind(wx.EVT_BUTTON, self.reset, self.reset_b)
		
		self.Centre()
		self.Show(True)
		
	def reset(self,e):
		try:
			self.ser = serial.Serial(self.can_device, 115200, timeout=0.5)
		except:
			wx.MessageBox(_('There is no active serial device (CAN-USB) connected on: '+self.can_device), 'Info', wx.OK | wx.ICON_ERROR)
			sys.exit(0)
		self.ser.close()
		
		text = _('Please disconnect CAN-USB from USB-cable and then reconnect it')
		wx.MessageBox(text, 'Info', wx.OK | wx.ICON_INFORMATION)
		time.sleep(0.2)
		i=0
		disconnected=True
		while disconnected:
			time.sleep(0.2)
			i+=1
			if os.path.exists(self.can_device) or i>100:
				disconnected=False
		try:
			self.ser = serial.Serial(self.can_device, 9600, timeout=0.5)
		except:
			wx.MessageBox(_('Can not open serial device (CAN-USB) connected on: '+self.can_device), 'Info', wx.OK | wx.ICON_ERROR)
			sys.exit(0)
		self.ser.write('0')
		time.sleep(0.2)
		sertext=self.ser.readline()
		if len(sertext)>5:
			time.sleep(0.2)
			self.ser.write('1')
			time.sleep(1)
			self.ser.write('9')
			wx.MessageBox(_('Firmware reset finished\n'+text), 'Info', wx.OK | wx.ICON_INFORMATION)
			self.OnClose(0)
	
	def OnClose(self, event):
		self.Destroy()
						
			
app = wx.App()
MyFrame().Show()
app.MainLoop()
