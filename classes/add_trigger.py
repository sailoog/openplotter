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
import subprocess
import wx


class addTrigger(wx.Dialog):
	def __init__(self, parent, edit):

		wx.Dialog.__init__(self, None, title=_('Add trigger'), size=(430, 350))

		panel = wx.Panel(self)

		self.parent = parent

		list_tmp = []
		response = subprocess.Popen(
			[parent.home + '/.config/signalk-server-node/node_modules/signalk-schema/scripts/extractKeysAndMeta.js'],
			stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		self.data = json.loads(response.communicate()[0])
		for i in self.data:
			list_tmp.append(i)
		list_sk_path = sorted(list_tmp)
		list_sk_path.append(_('notifications.*'))
		list_sk_path.append(_('None (always true)'))

		titl = wx.StaticText(panel, label=_('trigger'))
		self.SKkey = wx.ComboBox(panel, choices=list_sk_path, style=wx.CB_READONLY)
		self.SKkey.Bind(wx.EVT_COMBOBOX, self.on_SKkey)

		self.description = wx.TextCtrl(panel, -1, style=wx.TE_MULTILINE | wx.TE_READONLY)
		self.description.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_INACTIVECAPTION))

		self.asterix_t = wx.StaticText(panel, label=_('*'))
		self.asterix = wx.TextCtrl(panel, size=(150, -1))
		self.asterix_t2 = wx.StaticText(panel, label=_('allowed characters: 0-9, a-z, A-Z.'))

		self.operator_t = wx.StaticText(panel, label=_('operator'))
		self.operator = wx.ComboBox(panel, choices=self.parent.operators_list, style=wx.CB_READONLY)
		self.value_t = wx.StaticText(panel, label=_('value'))
		self.value = wx.TextCtrl(panel)

		cancelBtn = wx.Button(panel, wx.ID_CANCEL)
		okBtn = wx.Button(panel, wx.ID_OK)

		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add((0, 0), 1, wx.ALL | wx.EXPAND, 5)
		hbox.Add(cancelBtn, 0, wx.ALL | wx.EXPAND, 5)
		hbox.Add(okBtn, 0, wx.ALL | wx.EXPAND, 5)

		hboxb = wx.BoxSizer(wx.HORIZONTAL)
		hboxb.Add(self.asterix_t, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)
		hboxb.Add(self.asterix, 0, wx.RIGHT | wx.LEFT, 5)
		hboxb.Add(self.asterix_t2, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)

		vboxa = wx.BoxSizer(wx.VERTICAL)
		vboxa.Add(self.operator_t, 1, wx.ALL | wx.EXPAND, 5)
		vboxa.Add(self.value_t, 1, wx.ALL | wx.EXPAND, 5)

		vboxb = wx.BoxSizer(wx.VERTICAL)
		vboxb.Add(self.operator, 1, wx.ALL | wx.EXPAND, 5)
		vboxb.Add(self.value, 1, wx.ALL | wx.EXPAND, 5)

		hboxc = wx.BoxSizer(wx.HORIZONTAL)
		hboxc.Add(vboxa, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)
		hboxc.Add(vboxb, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)

		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.AddSpacer(5)
		vbox.Add(titl, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)
		vbox.Add(self.SKkey, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)
		vbox.Add(self.description, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)
		vbox.AddSpacer(5)
		vbox.Add(hboxb, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)
		vbox.AddSpacer(5)
		vbox.Add(hboxc, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)
		vbox.Add((0, 0), 1, wx.ALL | wx.EXPAND, 0)
		vbox.Add(hbox, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)

		panel.SetSizer(vbox)
		self.panel = panel

		if edit != 0:
			if edit[1] == -1:
				self.SKkey.SetValue(_('None (always true)'))
			else:
				self.SKkey.SetValue(edit[1])
				self.find_description(edit[1])
				self.star_enable(edit[1])

			self.asterix.SetValue(str(edit[2]))
			self.operator.SetValue(self.parent.operators_list[edit[3]])

			self.value.SetValue(str(edit[4]))

	def find_description(self, SK):
		for i in self.data:
			if SK == i:
				try:
					value_str = self.data[i]['description']
				except:
					value_str = ''
				self.description.SetValue(value_str)
				if value_str == '':
					self.description.Hide()
				else:
					self.description.Show()
				self.panel.Layout()

	def star_enable(self, SK):
		if '*' in SK:
			self.asterix.Enable()
			self.asterix_t.Show()
			self.asterix.Show()
			self.asterix_t2.Show()
		else:
			self.asterix.Disable()
			self.asterix_t.Hide()
			self.asterix.Hide()
			self.asterix_t2.Hide()
		self.panel.Layout()

	def on_SKkey(self, e):
		selected = self.SKkey.GetValue()
		self.find_description(selected)
		self.star_enable(selected)


'''
	def onSelect(self,e):
		if (self.trigger_select.GetCurrentSelection())+1==len(self.list_sk_path):
			#self.operator_select.Disable()
			self.value.Disable()
			wx.MessageBox(_('The actions of this trigger will always be executed.'), 'Info', wx.OK | wx.ICON_INFORMATION)
		else:
			#self.print_operators_list()
			trigger=self.a.DataList[self.trigger_select.GetCurrentSelection()]
			print 1
			self.operator_select.SetSelection(0)
			disable_field=trigger[8]
			print 2
			self.value.SetValue('')
			if disable_field==1: self.value.Enable()
			if disable_field==0: self.value.Disable()
			if trigger[9]=='SW1' or trigger=='SW2' or trigger=='SW3' or trigger=='SW4' or trigger=='SW5' or trigger=='SW6':
				wx.MessageBox(_('Be sure you have filled in GPIO and Pull Down/Up fields in "Switches" tab and enabled the desired switch.'), 'Info', wx.OK | wx.ICON_INFORMATION)
			print 3


	def print_operators_list(self):
		trigger=self.trigger_select.GetCurrentSelection()
		print trigger
		#operators_valid_list=trigger[7]
		operators_valid_list=[]
		new_list=[]
		for i in operators_valid_list:
			new_list.append(self.parent.operators_list[i])
		self.operator_select.Enable()
		self.operator_select.Clear()
		self.operator_select.AppendItems(new_list)
'''
