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

class addTrigger(wx.Dialog):

	def __init__(self,datastream_list,operators_list):

		wx.Dialog.__init__(self, None, title=_('Add trigger'), size=(330,290))

		panel = wx.Panel(self)

		
		wx.StaticText(panel, label=_('trigger'), pos=(10, 10))
		self.trigger_select= wx.ComboBox(panel, choices=datastream_list, style=wx.CB_READONLY, size=(310, 32), pos=(10, 35))
		wx.StaticText(panel, label=_('operator'), pos=(10, 70))
		self.operator_select= wx.ComboBox(panel, choices=operators_list, style=wx.CB_READONLY, size=(310, 32), pos=(10, 95))
		wx.StaticText(panel, label=_('value'), pos=(10, 130))
		self.value = wx.TextCtrl(panel, size=(310, 32), pos=(10, 155))

		cancelBtn = wx.Button(panel, wx.ID_CANCEL, pos=(70, 205))
		okBtn = wx.Button(panel, wx.ID_OK, pos=(180, 205))

