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
import re

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
		self.okBtn = wx.Button(panel, wx.ID_OK, pos=(180, 180))
		self.okBtn.Hide()
		self.ok = wx.Button(panel, label=_('OK'), pos=(180, 180))
		self.Bind(wx.EVT_BUTTON, self.ok_conf, self.ok)
				

	def onSelectIO(self, e):
		selected = self.io_select.GetValue()
		if selected == _('input'): self.pull_select.Enable()
		if selected == _('output'): self.pull_select.Disable()

	def ok_conf(self,e):
		name = self.name.GetValue()
		io_selection = self.io_select.GetValue()
		gpio_selection = self.gpio_select.GetValue()
		pull_selection = self.pull_select.GetValue()
		if io_selection == _('output'):
			io = 'out'
		else:
			io = 'in'
		if io == 'out':
			dlg2 = wx.MessageDialog(None, _(
				'CAUTION. If you connect a closed switch or some inappropriate circuit, you could short out and damage your board when this output becomes "High". Are you sure to enable this output?'),
									_('Question'), wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION)
			if dlg2.ShowModal() == wx.ID_YES:
				dlg2.Destroy()
			else:
				dlg2.Destroy()
				return
		if not name or not io_selection or not gpio_selection or (not pull_selection and io == 'in'):
			self.ShowMessage(_('Failed. You must fill in all fields.'))
			return
		if not re.match('^[0-9a-zA-Z]+$', name):
			self.ShowMessage(_('Failed. The name must contain only letters and numbers.'))
			return

		evt = wx.PyCommandEvent(wx.EVT_BUTTON.typeId,self.okBtn.GetId())
		wx.PostEvent(self, evt)
		
	def ShowMessage(self, w_msg):
		wx.MessageBox(w_msg, 'Info', wx.OK | wx.ICON_INFORMATION)		