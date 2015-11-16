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
from classes.actions import Actions

class addAction(wx.Dialog):

	def __init__(self,actions_options,time_units):

		wx.Dialog.__init__(self, None, title=_('Add action'), size=(330,365))

		panel = wx.Panel(self)

		
		wx.StaticText(panel, label=_('action'), pos=(10, 10))
		self.action_select= wx.ComboBox(panel, choices=actions_options, style=wx.CB_READONLY, size=(310, 32), pos=(10, 35))
		self.action_select.Bind(wx.EVT_COMBOBOX, self.onSelect)
		wx.StaticText(panel, label=_('data'), pos=(10, 70))
		self.data = wx.TextCtrl(panel, size=(310, 32), pos=(10, 95))
		wx.StaticText(panel, label=_('repeat after'), pos=(10, 130))
		self.repeat = wx.TextCtrl(panel, size=(150, 32), pos=(10, 155))
		self.repeat.SetValue('0')
		self.repeat_unit= wx.ComboBox(panel, choices=time_units, style=wx.CB_READONLY, size=(150, 32), pos=(170, 155))
		self.repeat_unit.SetValue(_('no repeat'))
		wx.StaticText(panel, label=_('times'), pos=(10, 190))
		self.times = wx.TextCtrl(panel, size=(50, 32), pos=(10, 215))
		self.times.SetValue('0')
		wx.StaticText(panel, label=_('0 if you want the action to repeat\nindefinitely until the trigger is false'), pos=(70, 215))

		cancelBtn = wx.Button(panel, wx.ID_CANCEL, pos=(70, 280))
		okBtn = wx.Button(panel, wx.ID_OK, pos=(180, 280))

	def onSelect(self,e):
		actions=Actions()
		res=actions.data_message(self.action_select.GetCurrentSelection())
		if res:
			wx.MessageBox(res, 'Info', wx.OK | wx.ICON_INFORMATION)
			self.data.SetFocus() 
					