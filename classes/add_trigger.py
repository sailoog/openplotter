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
import datetime
from select_key import selectKey

class addTrigger(wx.Dialog):
	def __init__(self, parent, edit):

		if edit == 0: title = _('Add trigger')
		else: title = _('Edit trigger')

		wx.Dialog.__init__(self, None, title=title, size=(430, 350))

		panel = wx.Panel(self)

		self.parent = parent

		self.always = wx.CheckBox(panel, label = _('Date'))
		self.always.Bind(wx.EVT_CHECKBOX, self.on_always)

		hline1 = wx.StaticLine(panel)

		titl = wx.StaticText(panel, label=_('Signal K key'))
		self.SKkey = wx.TextCtrl(panel, style=wx.CB_READONLY)

		self.edit_skkey = wx.Button(panel, label=_('Edit'))
		self.edit_skkey.Bind(wx.EVT_BUTTON, self.onEditSkkey)

		self.skvalue = wx.CheckBox(panel, label = 'value')
		self.skvalue.Bind(wx.EVT_CHECKBOX, self.on_skmagnitude)

		self.sktimestamp = wx.CheckBox(panel, label = 'timestamp')
		self.sktimestamp.Bind(wx.EVT_CHECKBOX, self.on_skmagnitude)

		self.sksource = wx.CheckBox(panel, label = 'source')
		self.sksource.Bind(wx.EVT_CHECKBOX, self.on_skmagnitude)

		hline2 = wx.StaticLine(panel)

		self.operators_list = []
		self.operator_t = wx.StaticText(panel, label=_('Operator'))
		self.operator = wx.ComboBox(panel, choices=self.operators_list, style=wx.CB_READONLY)
		self.operator.Bind(wx.EVT_COMBOBOX, self.onSelect_operator)

		hline3 = wx.StaticLine(panel)

		self.value_t = wx.StaticText(panel, label=_('Value'))
		self.value = wx.TextCtrl(panel)

		self.format_t = wx.StaticText(panel, label=_('format: ').decode('utf8')+str( datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')))

		cancelBtn = wx.Button(panel, wx.ID_CANCEL)
		okBtn = wx.Button(panel, wx.ID_OK)

		hbox2 = wx.BoxSizer(wx.HORIZONTAL)
		hbox2.Add(self.SKkey, 1, wx.LEFT | wx.EXPAND, 5)
		hbox2.Add(self.edit_skkey, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)

		hbox3 = wx.BoxSizer(wx.HORIZONTAL)
		hbox3.Add(self.skvalue, 0, wx.LEFT | wx.EXPAND, 5)
		hbox3.Add(self.sktimestamp, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)
		hbox3.Add(self.sksource, 0, wx.RIGHT | wx.EXPAND, 5)

		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add((0, 0), 1, wx.ALL | wx.EXPAND, 5)
		hbox.Add(cancelBtn, 0, wx.ALL | wx.EXPAND, 5)
		hbox.Add(okBtn, 0, wx.ALL | wx.EXPAND, 5)

		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.AddSpacer(5)
		vbox.Add(self.always, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)
		vbox.Add(hline1, 0, wx.ALL | wx.EXPAND, 5)
		vbox.Add(titl, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)
		vbox.Add(hbox2, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 0)
		vbox.AddSpacer(5)
		vbox.Add(hbox3, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 0)
		vbox.Add(hline2, 0, wx.ALL | wx.EXPAND, 5)
		vbox.Add(self.operator_t, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)
		vbox.Add(self.operator, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)
		vbox.Add(hline3, 0, wx.ALL | wx.EXPAND, 5)
		vbox.Add(self.value_t, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)
		vbox.Add(self.value, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)
		vbox.Add(self.format_t, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)
		vbox.Add((0, 0), 1, wx.ALL | wx.EXPAND, 0)
		vbox.Add(hbox, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)

		panel.SetSizer(vbox)
		self.panel = panel

		if edit != 0:
			if edit[1] == -1:
				self.always.SetValue(True)
				self.on_always(0)
				self.operator.SetValue(self.parent.operators_list[edit[2]])
				self.value.SetValue(edit[3].decode('utf8'))
			else:
				sk = edit[1].split('.')
				magnitude = sk.pop()
				self.SKkey.SetValue('.'.join(sk))
				if magnitude == 'value': self.skvalue.SetValue(True)
				elif magnitude == 'timestamp': self.sktimestamp.SetValue(True)
				elif magnitude == 'source': self.sksource.SetValue(True)
				self.onSelectMagn()
				self.operator.SetValue(self.parent.operators_list[edit[2]])
				self.value.SetValue(edit[3].decode('utf8'))
				self.onSelect_operator(0)
		else:
			self.skvalue.SetValue(True)
			self.sktimestamp.SetValue(False)
			self.sksource.SetValue(False)
			self.onSelectMagn()

	def on_always(self, e):
		if self.always.GetValue():
			self.SKkey.Disable()
			self.edit_skkey.Disable()
			self.skvalue.Disable()
			self.sktimestamp.Disable()
			self.sksource.Disable()
			self.operator.Enable()
			self.value.Enable()
			self.onSelectMagn()
		else:
			self.SKkey.Enable()
			self.edit_skkey.Enable()
			self.skvalue.Enable()
			self.sktimestamp.Enable()
			self.sksource.Enable()
			self.onSelectMagn()

	def on_skmagnitude(self, e):
		sender = e.GetEventObject()
		self.skvalue.SetValue(False)
		self.sktimestamp.SetValue(False)
		self.sksource.SetValue(False)
		sender.SetValue(True)
		self.onSelectMagn()

	def onSelectMagn(self):
		self.operator.Enable()
		self.value.Enable()
		self.operator.Clear()
		if self.always.GetValue():
			self.operators_list = [self.parent.operators_list[4], self.parent.operators_list[6]]
			self.operators_ref = [4,6]
		elif self.skvalue.GetValue():
			self.operators_list = [self.parent.operators_list[2], self.parent.operators_list[3], self.parent.operators_list[4], self.parent.operators_list[5], self.parent.operators_list[6], self.parent.operators_list[7]]
			self.operators_ref = [2,3,4,5,6,7]
		elif self.sktimestamp.GetValue():
			self.operators_list = [self.parent.operators_list[0], self.parent.operators_list[1], self.parent.operators_list[2], self.parent.operators_list[3], self.parent.operators_list[4], self.parent.operators_list[5], self.parent.operators_list[6]]
			self.operators_ref = [0,1,2,3,4,5,6]
		elif self.sksource.GetValue():
			self.operators_list = [self.parent.operators_list[2], self.parent.operators_list[7]]
			self.operators_ref = [2,7]
		self.operator.AppendItems(self.operators_list)
		self.operator.SetSelection(0)
		self.onSelect_operator(0)

	def onSelect_operator(self, e):
		operator = self.operator.GetSelection()
		if self.always.GetValue() or (self.sktimestamp.GetValue() and operator != 0 and operator != 1):
			self.format_t.Show() 
		else: 
			self.format_t.Hide()
		self.panel.Layout()

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