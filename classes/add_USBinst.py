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

	def __init__(self):
		'''
		first_tty_without_udev = 0

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
		'''
		wx.Dialog.__init__(self, None, title=_('Rename USB serial port'), size=(580,300))

		self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))

		panel = wx.Panel(self)

		self.list_devices = wx.ListCtrl(panel, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER, size=(565, 120))
		self.list_devices.SetPosition((5, 5))
		self.list_devices.InsertColumn(0, _('name'), width=113)
		self.list_devices.InsertColumn(1, _('vendor'), width=60)
		self.list_devices.InsertColumn(2, _('product'), width=65)
		self.list_devices.InsertColumn(3, _('port'), width=100)
		self.list_devices.InsertColumn(4, _('serial'), width=230)
		self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.select_device, self.list_devices)
		'''
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
		'''
		wx.StaticText(panel, label=_('new name'), pos=(15, 140))
		self.OPname_label=wx.StaticText(panel, label='/dev/ttyOP_', pos=(15, 170))
		self.OPname_select= wx.TextCtrl(panel, size=(100, 30), pos=(90, 160))
		self.OPname_select.Disable()
		self.OPname_label.Disable()

		self.rem_dev = wx.CheckBox(panel, label=_('Remember device'), pos=(245, 140))
		self.rem_dev.Bind(wx.EVT_CHECKBOX, self.on_enable_dev)
		self.rem_dev.Disable()
		self.rem_dev.SetValue(True)
		self.rem='dev'

		self.rem_port = wx.CheckBox(panel, label=_('Remember port'), pos=(245, 165))	
		self.rem_port.Bind(wx.EVT_CHECKBOX, self.on_enable_port)
		self.rem_port.Disable()


		context = pyudev.Context()
		for device in context.list_devices(subsystem='tty'):
			i=device['DEVNAME']
			if '/dev/ttyACM' in i or '/dev/ttyUSB' in i:
				ii=device['DEVLINKS']
				if '/dev/ttyOP' in ii: pass
				else:
					value=device['DEVPATH']
					value_DEVPATH = value[value.rfind('/usb1/')+6:-(len(value)-value.find('/tty'))]
					value_DEVPATH = value_DEVPATH[value_DEVPATH.rfind('/')+1:]
					self.list_devices.Append([i,device['ID_VENDOR_ID'],device['ID_MODEL_ID'],value_DEVPATH,device['ID_SERIAL']])

		cancelBtn = wx.Button(panel, wx.ID_CANCEL, pos=(195, 220))
		okBtn = wx.Button(panel, wx.ID_OK, pos=(305, 220))

	def on_enable_dev(self,e):
		if self.rem_dev.GetValue(): 
			self.rem_port.SetValue(False)
			self.rem='dev'
		else: 
			self.rem_port.SetValue(True)
			self.rem='port'

	def on_enable_port(self,e):
		if self.rem_port.GetValue(): 
			self.rem_dev.SetValue(False)
			self.rem='port'
		else: 
			self.rem_dev.SetValue(True)
			self.rem='dev'

	def select_device(self,e):
		selected_device=e.GetIndex()
		item = self.list_devices.GetItem(selected_device, 1)
		self.vendor=item.GetText()
		item = self.list_devices.GetItem(selected_device, 2)
		self.product=item.GetText()
		item = self.list_devices.GetItem(selected_device, 3)
		self.con_port=item.GetText()		
		item = self.list_devices.GetItem(selected_device, 4)
		self.serial=item.GetText()
		self.OPname_select.Enable()
		self.OPname_label.Enable()
		self.rem_dev.Enable()
		self.rem_port.Enable()