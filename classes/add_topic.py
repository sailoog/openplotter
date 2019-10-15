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
import wx, re
from select_key import selectKey

class addTopic(wx.Dialog):
	def __init__(self, edit):

		if edit == 0: title = _('Add MQTT topic')
		else: title = _('Edit MQTT topic')

		wx.Dialog.__init__(self, None, title = title, size=(430, 280))
		self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))

		panel = wx.Panel(self)

		self.topiclabel = wx.StaticText(panel, label=_('Topic'), pos=(10, 10))
		wx.StaticText(panel, label=_('allowed characters: 0-9, a-z, A-Z'), pos=(150, 10))
		self.topic = wx.TextCtrl(panel, size=(410, 30), pos=(10, 30))

		list_type = [_('General'), _('Signal K key input'), _('Signal K delta input')]
		wx.StaticText(panel, label=_('Type'), pos=(10, 70))
		self.type = wx.ComboBox(panel, choices=list_type, style=wx.CB_READONLY, size=(200, 32), pos=(10, 90))
		self.type.Bind(wx.EVT_COMBOBOX, self.onSelect_type)

		self.skkeylabel = wx.StaticText(panel, label=_('Signal K key'), pos=(10, 130))
		self.skkey = wx.TextCtrl(panel, style=wx.CB_READONLY, size=(300, 30), pos=(10, 150))

		self.edit_skkey = wx.Button(panel, label=_('Edit'), pos=(320, 147))
		self.edit_skkey.Bind(wx.EVT_BUTTON, self.onEditSkkey)

		self.skkeylabel.Disable()
		self.skkey.Disable()
		self.edit_skkey.Disable()

		if edit != 0:
			self.topic.SetValue(edit[1][0])
			if edit[1][1] == 0: 
				self.type.SetValue(_('General'))
			elif edit[1][1] == 1:
				self.type.SetValue(_('Signal K key input'))
				self.skkey.SetValue(edit[1][2])
				self.skkeylabel.Enable()
				self.skkey.Enable()
				self.edit_skkey.Enable()
			elif edit[1][1] == 2:
				self.type.SetValue(_('Signal K delta input'))

		cancelBtn = wx.Button(panel, wx.ID_CANCEL, pos=(120, 210))
		okBtn = wx.Button(panel, wx.ID_OK, pos=(230, 210))

	def onEditSkkey(self,e):
		key = self.skkey.GetValue()
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
		self.skkey.SetValue(key)

	def onSelect_type(self,e):
		if self.type.GetValue() == _('Signal K key input'):
			self.skkeylabel.Enable()
			self.skkey.Enable()
			self.edit_skkey.Enable()
		else:
			self.skkeylabel.Disable()
			self.skkey.Disable()
			self.edit_skkey.Disable()

	def ShowMessage(self, w_msg):
		wx.MessageBox(w_msg, 'Info', wx.OK | wx.ICON_INFORMATION)