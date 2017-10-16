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
import subprocess


class addvaluesetting(wx.Dialog):
	def __init__(self, edit, parent):
		self.parent = parent
		self.conf = parent.conf
		self.edit = edit
		self.listsave = []

		wx.Dialog.__init__(self, None, title=_('convert analog value to expected value of input ').decode('utf8') + str(edit),
						   size=(460, 350))

		panel = wx.Panel(self)

		self.list = wx.ListCtrl(panel, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
		self.list.InsertColumn(0, _('adc value'), width=80)
		self.list.InsertColumn(1, _('value in unit'), width=100)

		rawvalue_t = wx.StaticText(panel, label=_('raw adc value'))
		self.rawvalue = wx.TextCtrl(panel, size=(150, 30))

		unitvalue_t = wx.StaticText(panel, label=_('value in required unit'))
		self.unitvalue = wx.TextCtrl(panel, size=(150, 30))

		add = wx.Button(panel, label=_('add'))
		add.Bind(wx.EVT_BUTTON, self.on_add)

		delete = wx.Button(panel, label=_('delete'))
		delete.Bind(wx.EVT_BUTTON, self.on_delete)

		close = wx.Button(panel, label=_('Close'))
		close.Bind(wx.EVT_BUTTON, self.on_close)

		graph = wx.Button(panel, label=_('graph'))
		graph.Bind(wx.EVT_BUTTON, self.on_graph)

		vb1 = wx.BoxSizer(wx.VERTICAL)
		vb1.Add(rawvalue_t, 0, wx.ALL | wx.EXPAND, 5)
		vb1.Add(self.rawvalue, 0, wx.ALL | wx.EXPAND, 5)
		vb1.AddSpacer(10)
		vb1.Add(unitvalue_t, 0, wx.ALL | wx.EXPAND, 5)
		vb1.Add(self.unitvalue, 0, wx.ALL | wx.EXPAND, 5)

		hlistbox = wx.BoxSizer(wx.HORIZONTAL)
		hlistbox.Add(self.list, 1, wx.ALL | wx.EXPAND, 5)
		hlistbox.Add(vb1, 0, wx.ALL | wx.EXPAND, 5)

		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(add, 0, wx.ALL | wx.EXPAND, 5)
		hbox.Add(delete, 0, wx.ALL | wx.EXPAND, 5)
		hbox.Add((0, 0), 1, wx.ALL | wx.EXPAND, 5)
		hbox.Add(close, 0, wx.ALL | wx.EXPAND, 5)
		hbox.Add(graph, 0, wx.ALL | wx.EXPAND, 5)

		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.AddSpacer(5)
		vbox.Add(hlistbox, 1, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)
		vbox.AddSpacer(5)
		vbox.Add((0, 0), 1, wx.ALL | wx.EXPAND, 0)
		vbox.Add(hbox, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)

		panel.SetSizer(vbox)

		self.read_list()

	def read_list(self):
		try:
			self.list.DeleteAllItems()
		except:
			pass

		self.listsave = []

		if not self.conf.has_option('SPI', 'value_' + str(self.edit)):
			temp_list = [[0, 0], [1023, 1023]]
			self.conf.set('SPI', 'value_' + str(self.edit), str(temp_list))
			self.conf.read()

		data = self.conf.get('SPI', 'value_' + str(self.edit))
		try:
			temp_list = eval(data)
		except:
			temp_list = []
		for ii in temp_list:
			self.list.Append([str(int(ii[0])), str(ii[1])])
			self.listsave.append(ii)

	def on_delete(self, e):
		selected = self.list.GetFirstSelected()
		if selected == -1:
			self.parent.ShowMessage(_('nothing selected'))
			return

		temp_list = []
		index = 0
		for i in self.listsave:
			if not index == selected:
				temp_list.append(i)
			index += 1

		self.conf.set('SPI', 'value_' + str(self.edit), str(temp_list))
		self.read_list()

	def on_add(self, e):
		r = self.rawvalue.GetValue()
		u = self.unitvalue.GetValue()
		try:
			r = float(r)
			u = float(u)
			if r != float(int(r)):
				self.parent.ShowMessage(_('adc value must be a number without dec point'))
				return
		except:
			self.parent.ShowMessage(_('value isn\'t a number'))
			return

		self.listsave.append([r, u])

		temp_list = []
		for i in sorted(self.listsave, key=lambda item: (item[0])):
			temp_list.append(i)

		self.conf.set('SPI', 'value_' + str(self.edit), str(temp_list))
		self.read_list()

	def on_graph(self, e):
   		subprocess.Popen(['python', self.parent.currentpath+'/show_raw_adc_convert.py', str(self.edit)])

	def on_close(self, e):
		self.Destroy()
