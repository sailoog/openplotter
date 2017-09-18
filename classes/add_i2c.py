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
import platform
import wx, subprocess, os

if platform.machine()[0:3] == 'arm':
	import smbus


class addI2c(wx.Dialog):
	def __init__(self, parent):

		title = _('Add I2C sensor')

		wx.Dialog.__init__(self, None, title=title, size=(450, 400))

		panel = wx.Panel(self)
		self.conf = parent.conf
		self.home = parent.home
		self.currentpath = parent.currentpath
		self.parent = parent
		label_detected = wx.StaticText(panel, label=_('detected'))

		self.list_detected = wx.ListCtrl(panel, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
		self.list_detected.InsertColumn(0, _('Name'), width=210)
		self.list_detected.InsertColumn(1, _('Address'), width=116)
		self.list_detected.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSelectDetected)

		self.reset = wx.Button(panel, label=_('Reset'))
		self.reset.Bind(wx.EVT_BUTTON, self.onReset)

		self.check_addresses = wx.Button(panel, label=_('Addresses'))
		self.check_addresses.Bind(wx.EVT_BUTTON, self.onCheckAddresses)

		hline1 = wx.StaticLine(panel)

		label_add = wx.StaticText(panel, label=_('add/update sensor'))

		self.list_sensors = []
		for i in parent.i2c_sensors_def:
			self.list_sensors.append(i[0])
		self.sensor_select = wx.ComboBox(panel, choices=self.list_sensors, style=wx.CB_READONLY)
		self.sensor_select.Bind(wx.EVT_COMBOBOX, self.onSelectSensor)

		self.address = wx.TextCtrl(panel)

		cancelBtn = wx.Button(panel, wx.ID_CANCEL)
		okBtn = wx.Button(panel, wx.ID_OK)

		vbox1 = wx.BoxSizer(wx.VERTICAL)
		vbox1.Add(self.reset, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)
		vbox1.Add(self.check_addresses, 0, wx.RIGHT | wx.LEFT | wx.UP | wx.EXPAND, 5)
		vbox1.Add((0, 0), 1, wx.ALL | wx.EXPAND, 5)

		hbox2 = wx.BoxSizer(wx.HORIZONTAL)
		hbox2.Add(self.list_detected, 1, wx.LEFT | wx.EXPAND, 5)
		hbox2.Add(vbox1, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)

		hbox3 = wx.BoxSizer(wx.HORIZONTAL)
		hbox3.Add(self.sensor_select, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)
		hbox3.Add(self.address, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)

		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add((0, 0), 1, wx.ALL | wx.EXPAND, 5)
		hbox.Add(cancelBtn, 0, wx.ALL | wx.EXPAND, 5)
		hbox.Add(okBtn, 0, wx.ALL | wx.EXPAND, 5)

		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.AddSpacer(5)
		vbox.Add(label_detected, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)
		vbox.Add(hbox2, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)	
		vbox.Add(hline1, 0, wx.ALL | wx.EXPAND, 5)
		vbox.Add(label_add, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)
		vbox.Add(hbox3, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)
		vbox.Add((0, 0), 1, wx.ALL | wx.EXPAND, 0)
		vbox.Add(hbox, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)

		panel.SetSizer(vbox)
		self.panel = panel

		self.detection()

	def onSelectDetected(self, e):
		selectedDetected = self.list_detected.GetFirstSelected()
		name = self.list_detected.GetItem(selectedDetected, 0)
		address = self.list_detected.GetItem(selectedDetected, 1)
		self.sensor_select.SetValue(name.GetText())
		if name.GetText() in self.list_sensors: self.address.SetValue(address.GetText())

	def onSelectSensor(self, e):
		self.address.SetValue('')

	def onReset(self, e):
		dlg = wx.MessageDialog(None, _('If your sensors are not detected right, try resetting system or forcing name and address.\n\nDo you want to try auto detection again?'),_('Question'), wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
		if dlg.ShowModal() == wx.ID_YES:
			try:
				os.remove(self.home + '/.pypilot/RTIMULib2.ini')
			except: pass
			self.detection()
		dlg.Destroy()

	def onCheckAddresses(self, e):
		addresses = ''
		try:
			addresses = subprocess.check_output(['i2cdetect', '-y', '1'])
		except: 
			addresses = subprocess.check_output(['i2cdetect', '-y', '2'])
		wx.MessageBox(addresses, _('Detected I2C addresses'), wx.OK | wx.ICON_INFORMATION)

	def detection(self):
		if platform.machine()[0:3] == 'arm':		
			self.list_detected.DeleteAllItems()
			#RTIMULIB sensors
			rtimulib = self.parent.check_i2c()
			self.printRtimulibResults(rtimulib)
			#others
			bus = smbus.SMBus(1)
			for addr in range(3, 178):
				try:
					bus.write_quick(addr)
					addr = hex(addr)
					if addr == '0x76': self.list_detected.Append(['BME280', addr])
				except IOError: pass

	def printRtimulibResults(self,rtimulib):
		try:
			temp_list = eval(rtimulib)
		except:
			temp_list = []
		if temp_list:
			if temp_list[0][0] and temp_list[0][1]: self.list_detected.Append([temp_list[0][0], temp_list[0][1]])
			if temp_list[1][0] and temp_list[1][1]: self.list_detected.Append([temp_list[1][0], temp_list[1][1]])
			if temp_list[2][0] and temp_list[2][1]: self.list_detected.Append([temp_list[2][0], temp_list[2][1]])



