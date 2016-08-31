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


class addTopic(wx.Dialog):
	def __init__(self, edit):
		wx.Dialog.__init__(self, None, title=_('Add MQTT topic'), size=(330, 200))

		panel = wx.Panel(self)

		wx.StaticText(panel, label=_('Topic'), pos=(10, 10))
		self.topic = wx.TextCtrl(panel, size=(310, 30), pos=(10, 35))

		wx.StaticText(panel, label=_('allowed characters: 0-9, /, a-z, A-Z.'), pos=(10, 70))

		if edit != 0:
			self.topic.SetValue(edit[1])

		cancelBtn = wx.Button(panel, wx.ID_CANCEL, pos=(70, 115))
		okBtn = wx.Button(panel, wx.ID_OK, pos=(180, 115))
