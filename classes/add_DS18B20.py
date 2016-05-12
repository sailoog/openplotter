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
import wx
from w1thermsensor import W1ThermSensor
from classes.paths import Paths

paths=Paths()
home=paths.home

class addDS18B20(wx.Dialog):

	def __init__(self,edit):

		wx.Dialog.__init__(self, None, title=_('Add DS18B20 sensor'), size=(330,320))

		panel = wx.Panel(self)

		with open(home+'/.config/openplotter/classes/SK_temp.txt') as f:
			list_sk_path = [x.strip('\n\r') for x in f.readlines()]
			#list_sk_path = f.readlines()


		wx.StaticText(panel, label=_('SignalK name'), pos=(10, 10))
		#self.name = wx.TextCtrl(panel, size=(310, 30), pos=(10, 35))
		self.name= wx.ComboBox(panel, choices=list_sk_path, style=wx.CB_READONLY, size=(310, 30), pos=(10, 35))

		wx.StaticText(panel, label=_('short name'), pos=(10, 70))
		self.short = wx.TextCtrl(panel, size=(100, 30), pos=(10, 95))
		list_units=['Celsius','Fahrenheit','Kelvin']
		wx.StaticText(panel, label=_('unit'), pos=(120, 70))
		self.unit_select= wx.ComboBox(panel, choices=list_units, style=wx.CB_READONLY, size=(200, 32), pos=(120, 95))
		list_id=[]
		for sensor in W1ThermSensor.get_available_sensors():
			list_id.append(sensor.id)
		wx.StaticText(panel, label=_('sensor ID'), pos=(10, 130))
		self.id_select= wx.ComboBox(panel, choices=list_id, style=wx.CB_READONLY, size=(190, 32), pos=(10, 155))

		wx.StaticText(panel, label=_('offset'), pos=(220, 130))
		self.offset = wx.TextCtrl(panel, size=(100, 30), pos=(220, 155))	
		
		self.sk_enable = wx.CheckBox(panel, label=_('SignalK enable'), pos=(20, 205))
		self.n2k_enable = wx.CheckBox(panel, label=_('N2K enable'), pos=(20, 235))
		
		if edit != 0:
			self.name.SetValue(edit[1])
			self.short.SetValue(edit[2])
			if edit[3]=='C': unit_selection='Celsius'
			elif edit[3]=='F': unit_selection='Fahrenheit'
			elif edit[3]=='K': unit_selection='Kelvin'
			self.unit_select.SetValue(unit_selection)
			self.id_select.SetValue(edit[4])
			self.sk_enable.SetValue(edit[5]=='1')
			self.n2k_enable.SetValue(edit[6]=='1')
			self.offset.SetValue(edit[7])
			
		cancelBtn = wx.Button(panel, wx.ID_CANCEL, pos=(235, 200))
		okBtn = wx.Button(panel, wx.ID_OK, pos=(235, 240))