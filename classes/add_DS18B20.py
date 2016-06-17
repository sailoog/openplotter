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
import wx, subprocess, json
from w1thermsensor import W1ThermSensor
from classes.paths import Paths

paths=Paths()
home=paths.home

class addDS18B20(wx.Dialog):

	def __init__(self,edit):

		wx.Dialog.__init__(self, None, title=_('Add 1W temperature sensor'), size=(430,290))

		panel = wx.Panel(self)

		list_tmp=[]
		response = subprocess.check_output(home+'/.config/signalk-server-node/node_modules/signalk-schema/scripts/extractKeysAndMeta.js')
		self.data = json.loads(response)
		for i in self.data:
			if 'temperature' in i or 'Temperature' in i:
				if not 'electrical.' in i:
					list_tmp.append(i)
		list_sk_path=sorted(list_tmp)

		wx.StaticText(panel, label='Signal K', pos=(10, 10))
		self.SKkey= wx.ComboBox(panel, choices=list_sk_path, style=wx.CB_READONLY, size=(410, 30), pos=(10, 35))
 		self.SKkey.Bind(wx.EVT_COMBOBOX, self.onSelect)
 		self.description = wx.TextCtrl(panel, -1, style=wx.TE_MULTILINE|wx.TE_READONLY, size=(410, 45), pos=(10, 70))
		self.description.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_INACTIVECAPTION))

		wx.StaticText(panel, label=_('Name (no symbols)'), pos=(10, 125))
		self.name = wx.TextCtrl(panel, size=(150, 30), pos=(10, 150))

		list_id=[]
		for sensor in W1ThermSensor.get_available_sensors():
			list_id.append(sensor.id)
		wx.StaticText(panel, label=_('Sensor ID'), pos=(190, 125))
		self.id_select= wx.ComboBox(panel, choices=list_id, style=wx.CB_READONLY, size=(150, 32), pos=(190, 150))

		wx.StaticText(panel, label=_('Offset'), pos=(370, 125))
		self.offset = wx.TextCtrl(panel, size=(50, 30), pos=(370, 150))
		
		if edit != 0:
			self.name.SetValue(edit[1])
			self.SKkey.SetValue(edit[2])
			for i in self.data:
				if edit[2]==i:
					try: self.description.SetValue(self.data[i]['description'])
					except: self.description.SetValue('')
			self.id_select.SetValue(edit[3])
			self.offset.SetValue(edit[4])
			
		cancelBtn = wx.Button(panel, wx.ID_CANCEL, pos=(115, 210))
		okBtn = wx.Button(panel, wx.ID_OK, pos=(235, 210))

	def onSelect(self,e):
		selected= self.SKkey.GetValue()
		for i in self.data:
			if selected==i:
				try: self.description.SetValue(self.data[i]['description'])
				except: self.description.SetValue('')
