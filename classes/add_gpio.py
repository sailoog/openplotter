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


class addGPIO(wx.Dialog):
	def __init__(self, avalaible_gpio, edit):

		wx.Dialog.__init__(self, None, title=_('Add GPIO sensor'), size=(330, 265))

		panel = wx.Panel(self)

		wx.StaticText(panel, label=_('Name'), pos=(10, 10))
		self.name = wx.TextCtrl(panel, size=(310, 30), pos=(10, 35))

		wx.StaticText(panel, label=_('allowed characters: 0-9, a-z, A-Z'), pos=(10, 70))

		list_io = [_('input'), _('output')]
		wx.StaticText(panel, label=_('I/O'), pos=(10, 100))
		self.io_select = wx.ComboBox(panel, choices=list_io, style=wx.CB_READONLY, size=(100, 32), pos=(10, 125))
		self.io_select.Bind(wx.EVT_COMBOBOX, self.onSelectIO)

		wx.StaticText(panel, label=_('GPIO'), pos=(115, 100))
		self.gpio_select = wx.ComboBox(panel, choices=avalaible_gpio, style=wx.CB_READONLY, size=(100, 32),
									   pos=(115, 125))

		list_pull = ['down', 'up']
		wx.StaticText(panel, label=_('Pull'), pos=(220, 100))
		self.pull_select = wx.ComboBox(panel, choices=list_pull, style=wx.CB_READONLY, size=(100, 32), pos=(220, 125))

		if edit != 0:
			self.name.SetValue(edit[1])
			if edit[2] == 'out':
				io = _('output')
				self.pull_select.Disable()
			else:
				io = _('input')
				self.pull_select.Enable()
			self.io_select.SetValue(io)
			self.gpio_select.SetValue(str(edit[3]))
			self.pull_select.SetValue(edit[4])

		cancelBtn = wx.Button(panel, wx.ID_CANCEL, pos=(70, 180))
		okBtn = wx.Button(panel, wx.ID_OK, pos=(180, 180))

	def onSelectIO(self, e):
		selected = self.io_select.GetValue()
		if selected == _('input'): self.pull_select.Enable()
		if selected == _('output'): self.pull_select.Disable()
