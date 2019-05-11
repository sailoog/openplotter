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
from add_value_setting import addvaluesetting

class editMCP(wx.Dialog):
	def __init__(self,aktiv,channel,sk,convert,parent):
		self.conf = parent.conf
		self.channel = channel

		title = _('Edit').decode('utf8')+(' MCP3008-channel '+str(channel)).encode('utf-8')

		wx.Dialog.__init__(self, None, title=title, size=(450, 270))

		panel = wx.Panel(self)

		titl = wx.StaticText(panel, label=_('Signal K key'))
		self.SKkey = wx.TextCtrl(panel, style=wx.CB_READONLY)
		self.SKkey.SetValue(sk)

		self.edit_skkey = wx.Button(panel, label=_('Edit'))
		self.edit_skkey.Bind(wx.EVT_BUTTON, self.onEditSkkey)

		self.clean_skkey = wx.Button(panel, label=_('Clean'))
		self.clean_skkey.Bind(wx.EVT_BUTTON, self.onCleanSkkey)

		hline1 = wx.StaticLine(panel)

		self.aktiv = wx.CheckBox(panel, label=_('aktiv'))
		aktivB = False
		if aktiv == 1: aktivB = True
		self.aktiv.SetValue(aktivB)
		
		hline2 = wx.StaticLine(panel)

		self.convert = wx.CheckBox(panel, label=_('convert'))
		self.convert.Bind(wx.EVT_CHECKBOX, self.on_convert)
		convertB = False
		if convert == 1: convertB = True
		self.convert.SetValue(convertB)

		self.value_setting = wx.Button(panel, label=_('value setting'))
		self.value_setting.Bind(wx.EVT_BUTTON, self.on_value_setting)	
		
		cancelBtn = wx.Button(panel, wx.ID_CANCEL)
		okBtn = wx.Button(panel, wx.ID_OK)

		hbox2 = wx.BoxSizer(wx.HORIZONTAL)
		hbox2.Add(self.clean_skkey, 0, wx.LEFT | wx.EXPAND, 5)
		hbox2.Add(self.edit_skkey, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)

		hbox3 = wx.BoxSizer(wx.HORIZONTAL)
		hbox3.Add(self.aktiv, 0, wx.ALL | wx.EXPAND, 5)

		hbox4 = wx.BoxSizer(wx.HORIZONTAL)
		hbox4.Add(self.convert, 0, wx.ALL| wx.EXPAND, 5)
		hbox4.Add(self.value_setting, 0, wx.ALL| wx.EXPAND, 5)

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
		dlg = selectKey(key,'self')
		
		res = dlg.ShowModal()
		if res == wx.OK:
			key = dlg.selected_key
			self.SKkey.SetValue(key)
		dlg.Destroy()
		
	def on_convert(self, e):
		convert = 0
		if self.convert.GetValue():
			convert = 1
			if self.conf.has_option('SPI', 'value_' + str(self.channel)):
				data = self.conf.get('SPI', 'value_' + str(self.channel))
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
				wx.MessageBox(_('no option value_').decode('utf8') + str(self.channel) + _(' in openplotter.conf').decode('utf8'), 'info',
							  wx.OK | wx.ICON_INFORMATION)
				convert = 0

		self.convert.SetValue(convert)
		
	def on_value_setting(self, e):
		edit = self.channel
		if edit == -1:
			return
		dlg = addvaluesetting(edit, self)
		dlg.ShowModal()

		if self.convert.GetValue():
			convert = 1
			self.conf.read()
			data = self.conf.get('SPI', 'value_' + str(edit))
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
			if convert == 0:
				self.MCP[edit][4] = convert
				self.conf.set('SPI', 'mcp', str(self.MCP))
				self.read_MCP()
				wx.MessageBox(_('convert disabled'), 'info', wx.OK | wx.ICON_INFORMATION)

	def ShowMessage(self, w_msg):
		wx.MessageBox(w_msg, 'Info', wx.OK | wx.ICON_INFORMATION)


