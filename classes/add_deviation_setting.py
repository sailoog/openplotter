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


class adddeviationsetting(wx.Dialog):
	def __init__(self, parent):
		self.parent = parent
		self.conf = parent.conf

		wx.Dialog.__init__(self, None, title=_('Deviation Table'),
						   size=(460, 450))
		self.Bind(wx.EVT_CLOSE, self.on_close)

		panel = wx.Panel(self)

		self.list = wx.ListCtrl(panel, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
		self.list.InsertColumn(0, _('CH'), width=65)
		self.list.InsertColumn(1, _('MH'), width=65)
		self.list.InsertColumn(2, _('deviation'), width=90)
		self.list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_edit)

		variation_t = wx.StaticText(panel, label=_('Magnetic Variation'))
		self.variation = wx.TextCtrl(panel)

		self.fix = wx.Button(panel, label=_('Fix'))
		self.fix.Bind(wx.EVT_BUTTON, self.on_fix)

		rawvalue_t = wx.StaticText(panel, label=_('Compass Heading'))
		self.rawvalue = wx.TextCtrl(panel, size=(150, 30))

		mag_head_t = wx.StaticText(panel, label=_('Magnetic Heading'))
		self.mag_head = wx.TextCtrl(panel, size=(150, 30))

		unitvalue_t = wx.StaticText(panel, label=_('True Heading'))
		self.unitvalue = wx.TextCtrl(panel, size=(150, 30))
		
		self.change = wx.Button(panel, label=_('change'))
		self.change.Bind(wx.EVT_BUTTON, self.on_change)	

		reset = wx.Button(panel, label=_('Reset'))
		reset.Bind(wx.EVT_BUTTON, self.on_reset)

		close = wx.Button(panel, label=_('Close'))
		close.Bind(wx.EVT_BUTTON, self.on_close)

		graph = wx.Button(panel, label=_('graph'))
		graph.Bind(wx.EVT_BUTTON, self.on_graph)

		hvar = wx.BoxSizer(wx.HORIZONTAL)
		hvar.Add(self.variation, 0, wx.ALL | wx.EXPAND, 5)
		hvar.Add(self.fix, 0, wx.ALL | wx.EXPAND, 5)

		vb1 = wx.BoxSizer(wx.VERTICAL)
		vb1.Add(rawvalue_t, 0, wx.ALL | wx.EXPAND, 5)
		vb1.Add(self.rawvalue, 0, wx.ALL | wx.EXPAND, 5)
		vb1.Add(mag_head_t, 0, wx.ALL | wx.EXPAND, 5)
		vb1.Add(self.mag_head, 0, wx.ALL | wx.EXPAND, 5)
		vb1.Add(variation_t, 0, wx.ALL | wx.EXPAND, 5)
		vb1.Add(hvar, 0, wx.ALL | wx.EXPAND, 0)
		vb1.Add(unitvalue_t, 0, wx.ALL | wx.EXPAND, 5)
		vb1.Add(self.unitvalue, 0, wx.ALL | wx.EXPAND, 5)
		vb1.AddSpacer(10)
		vb1.Add(self.change, 0, wx.ALL | wx.EXPAND, 5)
		

		hlistbox = wx.BoxSizer(wx.HORIZONTAL)
		hlistbox.Add(self.list, 1, wx.ALL | wx.EXPAND, 5)
		hlistbox.Add(vb1, 0, wx.ALL | wx.EXPAND, 5)

		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add((0, 0), 1, wx.ALL | wx.EXPAND, 5)
		hbox.Add(reset, 0, wx.ALL | wx.EXPAND, 5)
		hbox.Add(graph, 0, wx.ALL | wx.EXPAND, 5)
		hbox.Add(close, 0, wx.ALL | wx.EXPAND, 5)

		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.AddSpacer(5)
		vbox.Add(hlistbox, 1, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)
		vbox.AddSpacer(5)
		vbox.Add((0, 0), 1, wx.ALL | wx.EXPAND, 0)
		vbox.Add(hbox, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)

		panel.SetSizer(vbox)
		self.rawvalue.Disable()
		self.mag_head.Disable()

		self.read_list()

	def read_list(self):
		try:
			self.list.DeleteAllItems()
		except:
			pass
		data = self.conf.get('COMPASS', 'deviation')
		if not data:
			temp_list = []
			for i in range(37):
				temp_list.append([i*10,i*10])
			self.conf.set('COMPASS', 'deviation', str(temp_list))
			data = self.conf.get('COMPASS', 'deviation')
		try:
			self.edit = eval(data)
		except:
			self.edit = []
		for ii in self.edit:
			iii = ii[1] - ii[0]
			self.list.Append([str(ii[0]), str(ii[1]), str(iii)])

		self.rawvalue.SetValue('')
		self.unitvalue.SetValue('')
		self.mag_head.SetValue('')

		var = self.conf.get('COMPASS', 'variation')
		self.variation.SetValue(var)
		if not var:
			self.fixed = False
			self.unitvalue.Disable()
			self.change.Disable()
			self.variation.Enable()
			self.fix.SetLabel(_('Fix'))
		else:
			self.fixed = True
			self.unitvalue.Enable()
			self.change.Enable()
			self.variation.Disable()
			self.fix.SetLabel(_('Set'))

	def on_edit(self, e):
		if not self.fixed: return
		self.selected = self.list.GetFirstSelected()
		if self.selected < 1 or self.selected >35:
			return
		
		self.rawvalue.SetValue(str(self.edit[self.selected][0]))
		self.mag_head.SetValue(str(self.edit[self.selected][1]))
		var = float(self.variation.GetValue())
		self.unitvalue.SetValue(str(self.edit[self.selected][1] + var))

	def on_change(self, e):
		if self.selected < 1 or self.selected >35:
			return
		u = self.unitvalue.GetValue()
		r = self.rawvalue.GetValue()
		if u and r:
			var = float(self.variation.GetValue())
			try:
				u = float(u)
			except:
				self.ShowMessage(_('This value is not a number.'))
				return
			self.edit[self.selected][1] = u	- var 	
			self.conf.set('COMPASS', 'deviation', str(self.edit))
			self.read_list()

	def on_fix(self, e):
		if self.fixed:
			self.fixed = False
			self.unitvalue.Disable()
			self.change.Disable()
			self.variation.Enable()
			self.fix.SetLabel(_('Fix'))
			self.ShowMessage(_('Deviation table will be calculated with this variation. If you change this value you will have to define the complete table again.'))
		else:
			try:
				var = float(self.variation.GetValue())
			except:
				self.ShowMessage(_('This value is not a number.'))
				return
			self.fixed = True
			self.unitvalue.Enable()
			self.change.Enable()
			self.variation.Disable()
			self.fix.SetLabel(_('Set'))
			self.conf.set('COMPASS', 'variation', str(var))
			temp_list = []
			for i in range(37):
				temp_list.append([i*10,i*10])
			self.conf.set('COMPASS', 'deviation', str(temp_list))
			self.read_list()

	def on_reset(self, e):
		self.conf.set('COMPASS', 'deviation', '')
		self.read_list()

	def on_graph(self, e):
   		subprocess.Popen(['python', self.parent.currentpath+'/show_deviation_table.py', str(self.edit)])

	def on_close(self, e):
		subprocess.call(['pkill', '-f', 'SK-base_d.py'])
		subprocess.Popen(['python', self.parent.currentpath+'/SK-base_d.py'])
		self.Destroy()

	def ShowMessage(self, w_msg):
		wx.MessageBox(w_msg, 'Info', wx.OK | wx.ICON_WARNING)
