#!/usr/bin/env python

# This file is part of Openplotter.
# Copyright (C) 2015 by sailoog <https://github.com/sailoog/openplotter>
#                       e-sailing <https://github.com/e-sailing/openplotter>
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
import logging
import wx
import subprocess
import os
from classes.conf import Conf
from classes.language import Language



class MyFrame(wx.Frame):
	def __init__(self):
		self.list_SK = []
		self.data_SK_unit_private = []
		self.SK_unit = ''
		self.SK_description = ''

		self.conf = Conf()
		self.home = self.conf.home
		self.currentpath = self.home+self.conf.get('GENERAL', 'op_folder')+'/openplotter'

		Language(self.conf)

		logging.basicConfig()
		self.buffer = []
		self.sortCol = 0

		wx.Frame.__init__(self, None, title='diagnostic SignalK input', size=(650, 435))
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		panel = wx.Panel(self, wx.ID_ANY)

		self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))

		self.icon = wx.Icon(self.currentpath + '/openplotter.ico', wx.BITMAP_TYPE_ICO)
		self.SetIcon(self.icon)

		self.list = wx.ListCtrl(panel, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
		self.list.InsertColumn(0, 'SignalK', width=400)
		self.list.InsertColumn(1, _('SK Unit'), width=80)
		self.list.InsertColumn(2, _('Unit'), width=80)
		self.list.InsertColumn(3, _('Description'), width=500)

		self.sort_UnitSK = wx.Button(panel, label=_('Sort SK Unit'))
		self.sort_UnitSK.Bind(wx.EVT_BUTTON, self.on_sort_UnitSK)

		self.sort_Unit = wx.Button(panel, label=_('Sort Unit'))
		self.Bind(wx.EVT_BUTTON, self.on_sort_Unit, self.sort_Unit)

		self.sort_SK = wx.Button(panel, label=_('Sort SK'))
		self.sort_SK.Bind(wx.EVT_BUTTON, self.on_sort_SK)

		self.change_selected = wx.Button(panel, label=_('change selected'))
		self.change_selected.Bind(wx.EVT_BUTTON, self.on_change_selected)

		list_convert = [
						'Hz', 'Hz RPM', 
						'J', 'J Ah(12V)', 'J Ah(24V)',
						'K', 'K C',	'K F',
						'm', 'm ft', 'm nm', 'm km',
						'm/s', 'm/s kn','m/s kmh', 'm/s mph',
						'm3', 'm3 dm3', 'm3 gal',
						'm3/s', 'm3/s l/h', 'm3/s gal/h',
						'Pa', 'Pa hPa', 'Pa Bar',
						'rad', 'rad deg',
						's', 's h', 's d', 's y',
						'ratio', 'ratio %'
						]
		self.select_Unit_t = wx.StaticText(panel, label=_('convert'))
		self.select_Unit = wx.ComboBox(panel, choices=list_convert, style=wx.CB_READONLY, size=(150, 32))

		vbox = wx.BoxSizer(wx.VERTICAL)
		hlistbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hlistbox.Add(self.list, 1, wx.ALL | wx.EXPAND, 5)
		hbox.Add(self.sort_SK, 0, wx.RIGHT | wx.LEFT, 5)
		hbox.Add(self.sort_UnitSK, 0, wx.RIGHT | wx.LEFT, 5)
		hbox.Add(self.sort_Unit, 0, wx.RIGHT | wx.LEFT, 5)
		hbox.Add((0,0), 1, wx.RIGHT | wx.LEFT, 5)
		hbox.Add(self.change_selected, 0, wx.RIGHT | wx.LEFT, 5)
		hbox.Add(self.select_Unit_t, 0, wx.LEFT | wx.TOP, 5)
		hbox.Add(self.select_Unit, 0, wx.RIGHT | wx.LEFT, 5)
		vbox.Add(hlistbox, 1, wx.ALL | wx.EXPAND, 0)
		vbox.Add(hbox, 0, wx.ALL | wx.EXPAND, 0)
		panel.SetSizer(vbox)

		self.CreateStatusBar()

		self.read()
		self.sorting()

		self.Show(True)

	def read(self):
		self.list_SK = []

		with open(self.home+'/.config/signalk-server-node/node_modules/signalk-schema/keyswithmetadata.json') as data_file:
			data = json.load(data_file)

		self.data_SK_unit_private = []
		if os.path.isfile(self.home+'/.openplotter/private_unit.json'):
			with open(self.home+'/.openplotter/private_unit.json') as data_file:
				self.data_SK_unit_private = json.load(data_file)

		for i in data:
			if 'units' in data[i].keys():
				if 'description' in data[i].keys():
					ii = i.replace('/vessels/*/','')
					ii = ii.replace('RegExp','*')
					ii = ii.replace('/','.')
					self.list_SK.append([str(ii), str(data[i]['units']), '', str(data[i]['description'])])
				else:
					self.list_SK.append([str(ii), str(data[i]['units']), '', ''])
		for j in self.data_SK_unit_private:
			for i in self.list_SK:
				if j[0] == i[0]:
					i[2] = j[2]

		self.list_SK.sort(key=lambda tup: tup[0])
		self.list_SK.sort(key=lambda tup: tup[1])

	def lookup_star(self, name):
		skip = -1
		index = 0
		st = ''
		for i in name.split('.'):
			if index > -1:
				if skip == 0:
					st += '.*'
				else:
					if i in ['propulsion', 'inventory']:
						skip = 1
					elif i == 'resources':
						skip = 2
					st += '.' + i
			index += 1
			skip -= 1

		st = st[1:]
		self.SK_unit = ''
		self.SK_description = ''
		exist = False
		for j in self.list_SK:
			if j[2] == st:
				self.SK_unit = j[0]
				self.SK_description = j[3]
				exist = True
				break
		if not exist:
			print 'no unit for ', st

	def on_sort_Unit(self, e):
		self.sortCol = 2
		self.sorting()

	def on_sort_UnitSK(self, e):
		self.sortCol = 1
		self.sorting()

	def on_sort_SK(self, e):
		self.sortCol = 0
		self.sorting()

	def on_change_selected(self, e):
		orig_unit = self.select_Unit.GetValue().split(' ')
		if len(orig_unit) == 1:
			orig_unit = [orig_unit[0], '']
		if orig_unit[0] != '':
			list_select = []
			item = self.list.GetFirstSelected()
			while item != -1:
				# do something with the item
				self.list_SK[item][2] = orig_unit[1]

				list_select.append(self.get_by_index(item))
				item = self.list.GetNextSelected(item)

			self.data_SK_unit_private = []
			for i in self.list_SK:
				if i[2] != '':
					self.data_SK_unit_private.append([i[0], i[1], i[2]])
			with open(self.home+'/.openplotter/private_unit.json', 'w') as data_file:
				json.dump(self.data_SK_unit_private, data_file)

			self.data_SK_unit_private = []
			with open(self.home+'/.openplotter/private_unit.json') as data_file:
				self.data_SK_unit_private = json.load(data_file)
			self.read()
			self.sorting()

	def get_by_index(self, item):
		index = 0
		for i in self.list_SK:
			if index == item:
				return i
			index += 1
		return False

	def sorting(self):
		self.list.DeleteAllItems()
		self.list_SK.sort(key=lambda tup: tup[self.sortCol])
		index = 0
		for i in self.list_SK:
			self.list.InsertStringItem(index, i[0])
			self.list.SetStringItem(index, 1, i[1])
			self.list.SetStringItem(index, 2, i[2])
			self.list.SetStringItem(index, 3, i[3])
			index += 1

	def OnClose(self, e):
		self.Destroy()


app = wx.App()
MyFrame().Show()
app.MainLoop()
