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
import json
import wx
import requests
import datetime


class addTrigger(wx.Dialog):
	def __init__(self, parent, edit):

		wx.Dialog.__init__(self, None, title=_('Add trigger'), size=(430, 350))

		panel = wx.Panel(self)

		self.parent = parent

		self.always = wx.CheckBox(panel, label = _('Always'))
		self.always.Bind(wx.EVT_CHECKBOX, self.on_always)

		titl = wx.StaticText(panel, label=_('Signal K trigger'))

		self.list_skgroups=[]
		try:
			response = requests.get('http://localhost:3000/signalk/v1/api/vessels/self')
			self.data = response.json()
		except:self.data=None
		list_temp=[_('--group')]
		if self.data:
			for k,v in self.data.items():
				if isinstance(v, dict):
					if k not in list_temp: list_temp.append(k)
		self.list_skgroups=sorted(list_temp)

		self.skgroups= wx.ComboBox(panel, choices=self.list_skgroups, style=wx.CB_READONLY)
		self.skgroups.Bind(wx.EVT_COMBOBOX, self.onSelect_group)

		self.list_signalk=[_('--key')]
		self.signalk= wx.ComboBox(panel, choices=self.list_signalk, style=wx.CB_READONLY)
		self.signalk.Bind(wx.EVT_COMBOBOX, self.onSelect_key)

		self.operators_list = []
		self.operator_t = wx.StaticText(panel, label=_('operator'))
		self.operator = wx.ComboBox(panel, choices=self.operators_list, style=wx.CB_READONLY)
		self.operator.Bind(wx.EVT_COMBOBOX, self.onSelect_operator)

		self.value_t = wx.StaticText(panel, label=_('value'))
		self.value = wx.TextCtrl(panel)

		self.format_t = wx.StaticText(panel, label=_('Format: ')+str( datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f') )[0:23]+'Z')

		cancelBtn = wx.Button(panel, wx.ID_CANCEL)
		okBtn = wx.Button(panel, wx.ID_OK)

		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add((0, 0), 1, wx.ALL | wx.EXPAND, 5)
		hbox.Add(cancelBtn, 0, wx.ALL | wx.EXPAND, 5)
		hbox.Add(okBtn, 0, wx.ALL | wx.EXPAND, 5)

		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.AddSpacer(5)
		vbox.Add(self.always, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)
		vbox.AddSpacer(5)
		vbox.Add(titl, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)
		vbox.Add(self.skgroups, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)
		vbox.Add(self.signalk, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)
		vbox.AddSpacer(5)
		vbox.Add(self.operator_t, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)
		vbox.Add(self.operator, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)
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
			else:
				sk = edit[1].split('.')
				group = sk[0]
				self.skgroups.SetValue(group)
				self.onSelect_group(0)
				key = edit[1].replace(group+'.', '')
				self.signalk.SetValue(key)
				self.onSelect_key(0)
				self.operator.SetValue(self.parent.operators_list[edit[2]])
				self.value.SetValue(edit[3].encode('utf8'))
				self.onSelect_operator(0)
		else:
			self.skgroups.SetSelection(0)
			self.signalk.SetSelection(0)
			self.operator.Disable()
			self.value.Disable()
			self.format_t.Hide()

	def on_always(self, e):
		if self.always.GetValue():
			self.reset_group_key()
			self.skgroups.Disable()
			self.signalk.Disable()
		else:
			self.skgroups.Enable()
			self.signalk.Enable()

	def reset_group_key(self):
		self.skgroups.SetSelection(0)
		self.signalk.Clear()
		self.list_signalk=[_('--key')]
		self.signalk.AppendItems(self.list_signalk)
		self.signalk.SetSelection(0)
		self.reset_operator_value()

	def onSelect_group(self, e):
		group=self.skgroups.GetValue()
		if '--' in group:
			self.reset_group_key()
			return
		group=group+'.'
		self.signalk.Clear()
		self.list_signalk=[_('--key')]
		self.path = []
		self.data_keys=[]
		self.keys(self.data)
		list_tmp2=sorted(self.data_keys)
		for i in list_tmp2:
			if group == i[:len(group)]:
				self.list_signalk.append(i.replace(group,'',1))
		self.signalk.AppendItems(self.list_signalk)
		self.signalk.SetSelection(0)
		self.reset_operator_value()

	def keys(self,d):
		for k,v in d.items():
			if isinstance(v, dict):
				self.path.append(k)
				self.keys(v)
				self.path.pop()
			else:
				self.path.append(k)
				self.data_keys.append(".".join(self.path))
				self.path.pop()

	def onSelect_key(self, e):
		key=self.signalk.GetValue()
		self.reset_operator_value()
		if '--' in key:
			return
		self.operator.Enable()
		self.value.Enable()
		self.operator.Clear()
		if '.$source' in key:
			self.operators_list = [self.parent.operators_list[2], self.parent.operators_list[9]]
		elif '.timestamp' in key:
			self.operators_list = [self.parent.operators_list[0], self.parent.operators_list[1], self.parent.operators_list[2], self.parent.operators_list[3], self.parent.operators_list[4], self.parent.operators_list[5], self.parent.operators_list[6]]
		elif 'gpio.' in key:
			self.operators_list = [self.parent.operators_list[7], self.parent.operators_list[8]]
			self.value.Disable()
		else:
			self.operators_list = [self.parent.operators_list[2], self.parent.operators_list[3], self.parent.operators_list[4], self.parent.operators_list[5], self.parent.operators_list[6], self.parent.operators_list[9]]
		
		self.operator.AppendItems(self.operators_list)

	def reset_operator_value(self):
			self.operator.Disable()
			self.value.Disable()
			self.operator.Clear()
			self.operators_list = ['']
			self.operator.AppendItems(self.operators_list)
			self.operator.SetSelection(0)
			self.value.SetValue('')
			self.format_t.Hide()
			self.panel.Layout()

	def onSelect_operator(self, e):
		key = self.signalk.GetValue()
		operator = self.operator.GetValue()
		if '.timestamp' in key and operator != self.parent.operators_list[0] and operator != self.parent.operators_list[1]:
			self.format_t.Show() 
		else: 
			self.format_t.Hide()
		self.panel.Layout()
