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
import wx
import re
from select_key import selectKey

if platform.machine()[0:3] == 'arm':
	from w1thermsensor import W1ThermSensor
else:
	from emulator.w1thermsensor import W1ThermSensor


class addDS18B20(wx.Dialog):
	def __init__(self, edit):

		if edit == 0: title = _('Add 1W temperature sensor')
		else: title = _('Edit 1W temperature sensor')

		wx.Dialog.__init__(self, None, title = title, size=(430, 250))

		panel = wx.Panel(self)

		wx.StaticText(panel, label=_('Signal K key'), pos=(10, 10))
		self.SKkey = wx.TextCtrl(panel, style=wx.CB_READONLY, size=(300, 30), pos=(10, 35))

		self.edit_skkey = wx.Button(panel, label=_('Edit'), pos=(320, 32))
		self.edit_skkey.Bind(wx.EVT_BUTTON, self.onEditSkkey)

		wx.StaticText(panel, label=_('Name'), pos=(10, 75))
		self.name = wx.TextCtrl(panel, size=(150, 30), pos=(10, 100))

		wx.StaticText(panel, label=_('allowed characters: 0-9, a-z, A-Z'), pos=(10, 135))

		list_id = []
		for sensor in W1ThermSensor.get_available_sensors():
			list_id.append(sensor.id)
		wx.StaticText(panel, label=_('Sensor ID'), pos=(190, 75))
		self.id_select = wx.ComboBox(panel, choices=list_id, style=wx.CB_READONLY, size=(150, 32), pos=(190, 100))

		wx.StaticText(panel, label=_('Offset'), pos=(370, 75))
		self.offset = wx.TextCtrl(panel, size=(50, 30), pos=(370, 100))

		if edit != 0:
			self.name.SetValue(edit[1])
			self.SKkey.SetValue(edit[2])
			self.id_select.SetValue(edit[3])
			self.offset.SetValue(edit[4])

		cancelBtn = wx.Button(panel, wx.ID_CANCEL, pos=(115, 175))
		self.okBtn = wx.Button(panel, wx.ID_OK, pos=(235, 175))
		self.okBtn.Hide()
		self.ok = wx.Button(panel, label=_('OK'), pos=(235, 175))
		self.Bind(wx.EVT_BUTTON, self.ok_conf, self.ok)
										 

	def onEditSkkey(self,e):
		key = self.SKkey.GetValue()
		dlg = selectKey(key,'self')
		res = dlg.ShowModal()
		if res == wx.OK:
			key = dlg.selected_key
			self.SKkey.SetValue(key)
		dlg.Destroy()

	def ok_conf(self,e):
		if not self.SKkey.GetValue():
			self.ShowMessage(_('Failed. Select a Signal K key.'))
			return
			
		name =self.name.GetValue()
		if not name:
			self.ShowMessage(_('Failed. Provide a name.'))
			return
		
		if not re.match('^[0-9a-zA-Z]+$', name):
			self.ShowMessage(_('Failed. Name must contain only letters and numbers.'))
			return
		
		if self.id_select.GetValue() == '':
			self.ShowMessage(_('Failed. Select sensor ID.'))
			return
		try:
			float(self.offset.GetValue())
		except:
			self.offset.SetValue('0.0')
		evt = wx.PyCommandEvent(wx.EVT_BUTTON.typeId,self.okBtn.GetId())
		wx.PostEvent(self, evt)
		
	def ShowMessage(self, w_msg):
		wx.MessageBox(w_msg, 'Info', wx.OK | wx.ICON_INFORMATION)