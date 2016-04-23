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

	def __init__(self,edit):

		wx.Dialog.__init__(self, None, title=_('Add MQTT topic'), size=(330,250))

		panel = wx.Panel(self)

		wx.StaticText(panel, label=_('short'), pos=(10, 10))
		self.short = wx.TextCtrl(panel, size=(100, 30), pos=(10, 35))

		wx.StaticText(panel, label=_('topic'), pos=(10, 70))
		self.topic = wx.TextCtrl(panel, size=(310, 30), pos=(10, 95))

		if edit != 0:
			self.short.SetValue(edit[1])
			self.topic.SetValue(edit[2])

		cancelBtn = wx.Button(panel, wx.ID_CANCEL, pos=(70, 165))
		okBtn = wx.Button(panel, wx.ID_OK, pos=(180, 165))