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

from select_key import selectKey

class editI2c(wx.Dialog):
	def __init__(self,name,magn,sk,rate,offset):

		title = _('Edit')+(' '+name+' - '+magn).encode('utf-8')

		wx.Dialog.__init__(self, None, title=title, size=(450, 250))

		panel = wx.Panel(self)

		titl = wx.StaticText(panel, label=_('Signal K key'))
		self.SKkey = wx.TextCtrl(panel, style=wx.CB_READONLY)
		self.SKkey.SetValue(sk)

		self.edit_skkey = wx.Button(panel, label=_('Edit'))
		self.edit_skkey.Bind(wx.EVT_BUTTON, self.onEditSkkey)

		self.clean_skkey = wx.Button(panel, label=_('Clean'))
		self.clean_skkey.Bind(wx.EVT_BUTTON, self.onCleanSkkey)

		hline1 = wx.StaticLine(panel)

		self.rate_list = ['0.1', '0.25', '0.5', '0.75', '1.0', '5.0', '30.0', '60.0', '300.0']
		self.rate_label = wx.StaticText(panel, label=_('Rate (seconds)'))
		self.rate = wx.ComboBox(panel, choices=self.rate_list, style=wx.CB_READONLY)
		self.rate.SetValue(rate)

		hline2 = wx.StaticLine(panel)

		self.offset_label = wx.StaticText(panel, label=_('Offset'))
		self.offset = wx.TextCtrl(panel)
		self.offset.SetValue(offset)

		cancelBtn = wx.Button(panel, wx.ID_CANCEL)
		okBtn = wx.Button(panel, wx.ID_OK)

		hbox2 = wx.BoxSizer(wx.HORIZONTAL)
		hbox2.Add(self.clean_skkey, 0, wx.LEFT | wx.EXPAND, 5)
		hbox2.Add(self.edit_skkey, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)

		hbox3 = wx.BoxSizer(wx.HORIZONTAL)
		hbox3.Add(self.rate_label, 0, wx.ALL | wx.EXPAND, 5)
		hbox3.Add(self.rate, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)

		hbox4 = wx.BoxSizer(wx.HORIZONTAL)
		hbox4.Add(self.offset_label, 0, wx.ALL| wx.EXPAND, 5)
		hbox4.Add(self.offset, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)

		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add((0, 0), 1, wx.ALL | wx.EXPAND, 5)
		hbox.Add(cancelBtn, 0, wx.ALL | wx.EXPAND, 5)
		hbox.Add(okBtn, 0, wx.ALL | wx.EXPAND, 5)

		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.AddSpacer(5)
		vbox.Add(titl, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)
		vbox.Add(self.SKkey, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)
		vbox.Add(hbox2, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 0)
		vbox.Add(hline1, 0, wx.ALL | wx.EXPAND, 5)
		vbox.Add(hbox3, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 0)
		vbox.Add(hline2, 0, wx.ALL | wx.EXPAND, 5)
		vbox.Add(hbox4, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 0)
		vbox.Add((0, 0), 1, wx.ALL | wx.EXPAND, 0)
		vbox.Add(hbox, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)

		panel.SetSizer(vbox)
		self.panel = panel

	def onCleanSkkey(self,e):
		self.SKkey.SetValue('')

	def onEditSkkey(self,e):
		key = self.SKkey.GetValue()
		dlg = selectKey(key)
		
		res = dlg.ShowModal()
		if res == wx.ID_OK:
			key = dlg.keys_list.GetValue()
			if '*' in key:
				wildcard = dlg.wildcard.GetValue()
				if wildcard:
					if not re.match('^[0-9a-zA-Z]+$', wildcard):
						self.ShowMessage(_('Failed. * must contain only allowed characters.'))
						dlg.Destroy()
						return
					key = key.replace('*',wildcard)
				else:
					self.ShowMessage(_('Failed. You have to provide a name for *.'))
					dlg.Destroy()
					return
		dlg.Destroy()
		self.SKkey.SetValue(key)

	def ShowMessage(self, w_msg):
		wx.MessageBox(w_msg, 'Info', wx.OK | wx.ICON_INFORMATION)


