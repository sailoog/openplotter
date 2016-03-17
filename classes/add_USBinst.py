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
import wx, pyudev

class addUSBinst(wx.Dialog):

	def __init__(self,edit):
	
		first_tty_without_udev = 0
		context = pyudev.Context()
		print context

		for device in context.list_devices(subsystem='tty'):
			if first_tty_without_udev == 1: break
			for key, value in device.iteritems():
				if first_tty_without_udev == 1: break
			
				if key == 'DEVNAME':
					value_DEVNAME = value
				if key == 'DEVLINKS':
					value_DEVLINKSR= value[value.rfind('/dev/t'):]			
				if key == 'ID_SERIAL_SHORT':
					value_ID_SERIAL = value
				if key == 'ID_SERIAL':
					value_ID_SERIAL = value
				if key == 'ID_MODEL_ID':
					value_ID_MODEL_ID = value
				if key == 'DEVPATH':
					value_DEVPATH = value[value.rfind('/usb1/')+6:-(len(value)-value.find('/tty'))]
					value_DEVPATH = value_DEVPATH[value_DEVPATH.rfind('/')+1:]
				if key == 'ID_VENDOR_ID':
					value_ID_VENDOR_ID = value
					if value_DEVLINKSR == '0':
						first_tty_without_udev = 1
						break
						
		if first_tty_without_udev == 0:
			value_DEVNAME=''
			value_DEVLINKSR=''
			value_ID_SERIAL=''
			value_ID_MODEL_ID=''
			value_DEVPATH=''
			value_ID_VENDOR_ID = '' 

		wx.Dialog.__init__(self, None, title=_('Add USB serial port'), size=(330,340))

		panel = wx.Panel(self)

		list_OPnames=['ttyOP_Plotter','ttyOP_Radio','ttyOP_AIS','ttyOP_GPS','ttyOP_AUTOPILOT','ttyOP_NMEA1','ttyOP_NMEA2','ttyOP_NMEA3','ttyOP_SEATALK','ttyOP_NMEA2000',' ']
		
		wx.StaticText(panel, label=_('OP name'), pos=(10, 10))
		self.OPname_select= wx.ComboBox(panel, choices=list_OPnames, style=wx.CB_READONLY, size=(310, 30), pos=(10, 35))

		wx.StaticText(panel, label=_('vendor'), pos=(10, 70))
		self.vendor = wx.TextCtrl(panel, value=value_ID_VENDOR_ID, style=wx.CB_READONLY, size=(100, 30), pos=(10, 95))
		
		wx.StaticText(panel, label=_('serial'), pos=(160, 70))
		if value_ID_SERIAL[:len(value_ID_VENDOR_ID)] == value_ID_VENDOR_ID:
			value_ID_SERIAL = ''
		self.serial = wx.TextCtrl(panel, value=value_ID_SERIAL, style=wx.CB_READONLY, size=(100, 30), pos=(160, 95))

		wx.StaticText(panel, label=_('product'), pos=(10, 130))
		self.product = wx.TextCtrl(panel, value=value_ID_MODEL_ID, style=wx.CB_READONLY, size=(100, 30), pos=(10, 155))

		wx.StaticText(panel, label=_('connect port'), pos=(160, 130))
		self.con_port = wx.TextCtrl(panel, value=value_DEVPATH, style=wx.CB_READONLY, size=(100, 30), pos=(160, 155))
		
		self.con_port_enable = wx.CheckBox(panel, label=_('Enable udev on port'), pos=(10, 200))	

		if edit != 0:
			self.OPname_select.SetValue(edit[1])
			self.vendor.SetValue(edit[2])
			self.product.SetValue(edit[3])
			self.serial.SetValue(edit[4])
			self.con_port.SetValue(edit[5])
			self.con_port_enable.SetValue(edit[6])
			
		cancelBtn = wx.Button(panel, wx.ID_CANCEL, pos=(70, 255))
		okBtn = wx.Button(panel, wx.ID_OK, pos=(180, 255))