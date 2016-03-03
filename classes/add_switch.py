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

class addSwitch(wx.Dialog):

	def __init__(self,edit):

		wx.Dialog.__init__(self, None, title=_('Add Switch'), size=(330,235))

		panel = wx.Panel(self)

		wx.StaticText(panel, label=_('name'), pos=(10, 10))
		self.name = wx.TextCtrl(panel, size=(310, 30), pos=(10, 35))

		wx.StaticText(panel, label=_('short name'), pos=(10, 70))
		self.short = wx.TextCtrl(panel, size=(100, 30), pos=(10, 95))

		list_gpio=['5', '6', '12', '13','16', '17', '18', '19','20', '21', '22', '23','24', '25', '26', '27']
		wx.StaticText(panel, label=_('GPIO'), pos=(115, 70))
		self.gpio_select= wx.ComboBox(panel, choices=list_gpio, style=wx.CB_READONLY, size=(100, 32), pos=(115, 95))
		
		list_pull=['down', 'up']
		wx.StaticText(panel, label=_('pull'), pos=(220, 70))
		self.id_select= wx.ComboBox(panel, choices=list_pull, style=wx.CB_READONLY, size=(100, 32), pos=(220, 95))
		'''
		if edit != 0:
			self.name.SetValue(edit[1])
			self.short.SetValue(edit[2])
			if edit[3]=='C': unit_selection='Celsius'
			if edit[3]=='F': unit_selection='Fahrenheit'
			if edit[3]=='K': unit_selection='Kelvin'
			self.gpio_select.SetValue(unit_selection)
			self.id_select.SetValue(edit[4])
		'''
		cancelBtn = wx.Button(panel, wx.ID_CANCEL, pos=(70, 150))
		okBtn = wx.Button(panel, wx.ID_OK, pos=(180, 150))