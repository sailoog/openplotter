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
import wx, os, re
from select_key import selectKey

class addAction(wx.Dialog):
	def __init__(self, parent, actions_options, time_units, edit):

		if edit == 0: title = _('Add action')
		else: title = _('Edit action')

		wx.Dialog.__init__(self, None, title=title, size=(450, 400))

		panel = wx.Panel(self)
		self.conf = parent.conf
		self.actions_options = actions_options

		self.home = parent.home
		self.currentpath = parent.currentpath

		list_actions = []
		for i in self.actions_options:
			list_actions.append(i[0])

		label_action = wx.StaticText(panel, label=_('action'))
		self.action_select = wx.ComboBox(panel, choices=list_actions, style=wx.CB_READONLY)
		self.action_select.Bind(wx.EVT_COMBOBOX, self.onSelect)

		hline1 = wx.StaticLine(panel)

		label_data = wx.StaticText(panel, label=_('data'))
		self.data = wx.TextCtrl(panel, style=wx.TE_MULTILINE)

		self.edit_skkey = wx.Button(panel, label=_('Add Signal K key'))
		self.edit_skkey.Bind(wx.EVT_BUTTON, self.onEditSkkey)

		hline2 = wx.StaticLine(panel)

		label_repeat = wx.StaticText(panel, label=_('repeat after'))
		self.repeat = wx.TextCtrl(panel)
		self.repeat.Disable()

		self.repeat_unit = wx.ComboBox(panel, choices=time_units, style=wx.CB_READONLY)
		self.repeat_unit.Bind(wx.EVT_COMBOBOX, self.onSelectUnit)
		self.repeat_unit.SetValue(_('no repeat'))

		cancelBtn = wx.Button(panel, wx.ID_CANCEL)
		okBtn = wx.Button(panel, wx.ID_OK)

		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add((0, 0), 1, wx.ALL | wx.EXPAND, 5)
		hbox.Add(cancelBtn, 0, wx.ALL | wx.EXPAND, 5)
		hbox.Add(okBtn, 0, wx.ALL | wx.EXPAND, 5)

		hbox2 = wx.BoxSizer(wx.HORIZONTAL)
		hbox2.Add(self.repeat, 1, wx.LEFT | wx.EXPAND, 5)
		hbox2.Add(self.repeat_unit, 1, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)

		hbox3 = wx.BoxSizer(wx.HORIZONTAL)
		hbox3.Add((0, 0), 1, wx.ALL | wx.EXPAND, 5)
		hbox3.Add(self.edit_skkey, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)

		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.AddSpacer(5)
		vbox.Add(label_action, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)
		vbox.Add(self.action_select, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)
		vbox.Add(hline1, 0, wx.ALL | wx.EXPAND, 5)
		vbox.Add(label_data, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)
		vbox.Add(self.data, 4, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)
		vbox.AddSpacer(5)
		vbox.Add(hbox3, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)	
		vbox.Add(hline2, 0, wx.ALL | wx.EXPAND, 5)
		vbox.Add(label_repeat, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)
		vbox.Add(hbox2, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 0)
		vbox.Add((0, 0), 1, wx.ALL | wx.EXPAND, 0)
		vbox.Add(hbox, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)

		panel.SetSizer(vbox)
		self.panel = panel

		if edit != 0:
			self.action_select.SetValue(list_actions[edit[1]])
			self.data.SetValue(edit[2])
			if edit[3] != 0.0:
				self.repeat.SetValue(str(edit[3]))
				self.repeat.Enable()
			self.repeat_unit.SetValue(time_units[edit[4]])

	def onSelect(self, e):
		option = self.actions_options[self.action_select.GetCurrentSelection()][0]
		msg = self.actions_options[self.action_select.GetCurrentSelection()][1]
		field = self.actions_options[self.action_select.GetCurrentSelection()][2]
		if field == 0:
			self.data.Disable()
			self.data.SetValue('')
			self.edit_skkey.Disable()
		if field == 1:
			self.data.Enable()
			self.data.SetFocus()
			self.edit_skkey.Enable()
		if msg:
			if msg == 'OpenFileDialog':
				dlg = wx.FileDialog(self, message=_('Choose a file'), defaultDir=self.currentpath + '/sounds',
									defaultFile='',
									wildcard=_('Audio files') + ' (*.mp3)|*.mp3|' + _('All files') + ' (*.*)|*.*',
									style=wx.OPEN | wx.CHANGE_DIR)
				if dlg.ShowModal() == wx.ID_OK:
					file_path = dlg.GetPath()
					self.data.SetValue(file_path)
				print self.currentpath
				os.chdir(self.currentpath)			
				dlg.Destroy()
			else:
				if msg == 0:
					pass
				else:
					if field == 1 and option != _('wait'): 
						msg = msg+ _('\n\nYou can add the current value of any Signal K key typing its name between angle brackets, e.g: <navigation.position.latitude>')
					wx.MessageBox(msg, 'Info', wx.OK | wx.ICON_INFORMATION)

	def onSelectUnit(self, e):
		if self.repeat_unit.GetCurrentSelection() == 0:
			self.repeat.Disable()
			self.repeat.SetValue('')
		else:
			self.repeat.Enable()

	def onEditSkkey(self,e):
		
		dlg = selectKey('')
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
			self.data.SetValue(self.data.GetValue()+'<'+key+'>')
		dlg.Destroy()

	def ShowMessage(self, w_msg):
		wx.MessageBox(w_msg, 'Info', wx.OK | wx.ICON_INFORMATION)
