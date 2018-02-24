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

class addTool10(wx.Dialog):

	def __init__(self):

		wx.Dialog.__init__(self, None, title=_('Standalone tool'), size=(130,230))

		self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
		
		panel = wx.Panel(self)
		self.settings_b = wx.Button(panel,label=_('settings') , pos=(20, 20))
		self.start_b = wx.Button(panel, label=_('start'), pos=(20, 60))
		self.stop_b = wx.Button(panel, label=_('stop'), pos=(20, 100))
		self.cancel_b = wx.Button(panel, label=_('cancel'), pos=(20, 140))
		self.Bind(wx.EVT_BUTTON, self.on_Button)

	def on_Button(self,event):
		if self.settings_b.Id==event.Id:
			self.ButtonNr=1
		if self.start_b.Id==event.Id:
			self.ButtonNr=2
		if self.stop_b.Id==event.Id:
			self.ButtonNr=3
		if self.cancel_b.Id==event.Id:
			self.ButtonNr=4
		self.Close()