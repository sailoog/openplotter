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
import wx


class addUSBinst(wx.Dialog):
	def __init__(self, edit, parent):

		self.parent = parent

		wx.Dialog.__init__(self, None, title=_('Add individual name to serial port'), size=(580, 300))

		self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))

		panel = wx.Panel(self)

		self.list_devices = wx.ListCtrl(panel, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER, size=(565, 120))
		self.list_devices.SetPosition((5, 5))
		self.list_devices.InsertColumn(0, _('random name'), width=113)
		self.list_devices.InsertColumn(1, _('vendor'), width=60)
		self.list_devices.InsertColumn(2, _('product'), width=65)
		self.list_devices.InsertColumn(3, _('port'), width=90)
		self.list_devices.InsertColumn(4, _('serial'), width=65)
		self.list_devices.InsertColumn(5, _('info'), width=600)
		self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.select_device, self.list_devices)

		wx.StaticText(panel, label=_('new name'), pos=(15, 140))
		self.OPname_label = wx.StaticText(panel, label='/dev/ttyOP_', pos=(15, 170))
		self.OPname_select = wx.TextCtrl(panel, size=(100, 30), pos=(90, 160))
		self.OPname_select.Disable()
		self.OPname_label.Disable()

		self.rem_dev = wx.CheckBox(panel, label=_('Remember device (by vendor, product,(serial))'), pos=(245, 140))
		self.rem_dev.Bind(wx.EVT_CHECKBOX, self.on_enable_dev)
		self.rem_dev.Disable()
		self.rem_dev.SetValue(True)
		self.rem = 'dev'

		self.rem_port = wx.CheckBox(panel, label=_('Remember port (positon on the USB-hub)'), pos=(245, 165))
		self.rem_port.Bind(wx.EVT_CHECKBOX, self.on_enable_port)
		self.rem_port.Disable()

		if edit != 0:
			self.OPname_select.SetValue(edit[1][6:])
			self.rem_dev.SetValue(edit[6] == 'dev')
			self.rem_port.SetValue(edit[6] == 'port')
			self.rem = edit[6]

			self.vendor = edit[2]
			self.product = edit[3]
			self.serial = edit[4]
			self.con_port = edit[5]
			self.device = edit[7]

			self.OPname_select.Enable()
			self.rem_dev.Enable()
			self.rem_port.Enable()
			wx.StaticText(panel,
						  label=self.vendor + '    ' + self.product + '    ' + self.con_port + '    ' + self.serial,
						  pos=(15, 200))

		else:
			# context = pyudev.Context()
			context = self.parent.context

			for device in context.list_devices(subsystem='tty'):
				i = device['DEVNAME']
				if '/dev/ttyACM' in i or '/dev/ttyUSB' in i:
					ii = device['DEVLINKS']
					if '/dev/ttyOP' in ii:
						pass
					else:
						value = device['DEVPATH']
						value_DEVPATH = value[value.rfind('/usb1/') + 6:-(len(value) - value.find('/tty'))]
						value_DEVPATH = value_DEVPATH[value_DEVPATH.rfind('/') + 1:]
						try:
							serial = device['ID_SERIAL_SHORT']
						except:
							serial = ''
						try:
							vendor_db = device['ID_VENDOR_FROM_DATABASE']
						except:
							vendor_db = ''
						try:
							model_db = device['ID_MODEL_FROM_DATABASE']
						except:
							model_db = ''
						self.list_devices.Append(
							[i, device['ID_VENDOR_ID'], device['ID_MODEL_ID'], value_DEVPATH, serial,
							 vendor_db + ' ' + model_db])

		cancelBtn = wx.Button(panel, wx.ID_CANCEL, pos=(195, 220))
		okBtn = wx.Button(panel, wx.ID_OK, pos=(305, 220))

	def on_enable_dev(self, e):
		if self.rem_dev.GetValue():
			self.rem_port.SetValue(False)
			self.rem = 'dev'
		else:
			self.rem_port.SetValue(True)
			self.rem = 'port'

	def on_enable_port(self, e):
		if self.rem_port.GetValue():
			self.rem_dev.SetValue(False)
			self.rem = 'port'
		else:
			self.rem_dev.SetValue(True)
			self.rem = 'dev'

	def select_device(self, e):
		selected_device = e.GetIndex()
		item = self.list_devices.GetItem(selected_device, 0)
		self.device = item.GetText()[5:-1]
		item = self.list_devices.GetItem(selected_device, 1)
		self.vendor = item.GetText()
		item = self.list_devices.GetItem(selected_device, 2)
		self.product = item.GetText()
		item = self.list_devices.GetItem(selected_device, 3)
		self.con_port = item.GetText()
		item = self.list_devices.GetItem(selected_device, 4)
		self.serial = item.GetText()
		self.OPname_select.Enable()
		self.OPname_label.Enable()
		self.rem_dev.Enable()
		self.rem_port.Enable()
