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
import json
import subprocess
import wx

class addMCP(wx.Dialog):
	def __init__(self, edit, parent):
		self.conf = parent.conf
		self.edit = edit

		wx.Dialog.__init__(self, None, title=_('Edit MCP analog input ').decode('utf8') + str(edit[2]), size=(430, 350))

		panel = wx.Panel(self)

		list_tmp = []
		
		try:
			with open(self.home+'/.config/signalk-server-node/node_modules/@signalk/signalk-schema/dist/keyswithmetadata.json') as data_file:
				data = json.load(data_file)
		except:
			#old signalk
			with open(self.home+'/.config/signalk-server-node/node_modules/@signalk/signalk-schema/src/keyswithmetadata.json') as data_file:
				data = json.load(data_file)
		for i in self.data:
			ii = i.replace('/vessels/*/','')
			ii = ii.replace('RegExp','*')
			ii = ii.replace('/','.')
			list_tmp.append(ii)
		list_sk_path = sorted(list_tmp)

		titl = wx.StaticText(panel, label='Signal K')
		self.SKkey = wx.ComboBox(panel, choices=list_sk_path, style=wx.CB_READONLY)
		self.SKkey.Bind(wx.EVT_COMBOBOX, self.on_SKkey)
		self.description = wx.TextCtrl(panel, -1, style=wx.TE_MULTILINE | wx.TE_READONLY)
		self.description.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_INACTIVECAPTION))

		self.asterix_t = wx.StaticText(panel, label=_('*'))
		self.asterix = wx.TextCtrl(panel, size=(150, -1))
		self.asterix_t2 = wx.StaticText(panel, label=_('allowed characters: 0-9, a-z, A-Z'))

		self.aktiv = wx.CheckBox(panel, label=_('aktiv'))
		self.convert = wx.CheckBox(panel, label=_('convert'))
		self.convert.Bind(wx.EVT_CHECKBOX, self.on_convert)

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

		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.Add(self.aktiv, 0, wx.ALL | wx.EXPAND, 5)
		vbox.AddSpacer(5)
		vbox.Add(titl, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)
		vbox.Add(self.SKkey, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)
		vbox.Add(self.description, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)
		vbox.AddSpacer(5)
		vbox.Add(hboxb, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)
		vbox.Add((0, 0), 1, wx.ALL | wx.EXPAND, 0)
		vbox.Add(self.convert, 0, wx.ALL | wx.EXPAND, 5)
		vbox.Add(hbox, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)

		panel.SetSizer(vbox)
		self.panel = panel

		self.SKkey.SetValue(edit[3])
		self.find_description(edit[3])
		self.star_enable(edit[3])
		self.asterix.SetValue(edit[4])
		state = False
		if edit[1] == 1: state = True
		self.aktiv.SetValue(state)
		state = False
		if edit[5] == 1: state = True
		self.convert.SetValue(state)


	def find_description(self, SK):
		for i in self.data:
			ii = i.replace('/vessels/*/','')
			ii = ii.replace('RegExp','*')
			ii = ii.replace('/','.')
			if SK == ii:
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


	def on_convert(self, e):
		convert = 0
		if self.convert.GetValue():
			convert = 1
			if self.conf.has_option('SPI', 'value_' + str(self.edit[2])):
				data = self.conf.get('SPI', 'value_' + str(self.edit[2]))
				try:
					temp_list = eval(data)
				except:
					temp_list = []
				min = 1023
				max = 0
				for ii in temp_list:
					if ii[0] > max: max = ii[0]
					if ii[0] < min: min = ii[0]
				if min > 0:
					wx.MessageBox(_('minimum raw value in setting table > 0'), 'info', wx.OK | wx.ICON_INFORMATION)
					convert = 0
				if max < 1023:
					wx.MessageBox(_('maximum raw value in setting table < 1023'), 'info', wx.OK | wx.ICON_INFORMATION)
					convert = 0
			else:
				wx.MessageBox(_('no option value ').decode('utf8') + str(self.edit[2]) + _(' in openplotter.conf').decode('utf8'), 'info',
							  wx.OK | wx.ICON_INFORMATION)
				convert = 0

		self.convert.SetValue(convert)
