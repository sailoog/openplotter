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
from getkeys import GetKeys


class selectKey(wx.Dialog):
	def __init__(self, SKkey):
		wx.Dialog.__init__(self, None, title=_('Select Signal K key'), size=(430, 370))
		
		group = _('ungrouped')
		if len(SKkey)>0:
			SKkeySP = SKkey.split('.')
			group = SKkeySP[0]
			
		self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
		panel = wx.Panel(self)

		self.keys = GetKeys()
		self.skkeys = self.keys.keys
		self.groups = self.keys.groups
		self.ungrouped = self.keys.ungrouped

		wx.StaticText(panel, label=_('Groups'), pos=(10, 10))
		self.groups_list = wx.ComboBox(panel, choices=self.groups , style=wx.CB_READONLY, size=(250, 32), pos=(10, 30))
		self.groups_list.Bind(wx.EVT_COMBOBOX, self.onSelect_group)
		self.group_description = wx.TextCtrl(panel, -1, style=wx.TE_MULTILINE | wx.TE_READONLY, size=(410, 50), pos=(10, 65))
		self.group_description.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_INACTIVECAPTION))
		self.groups_list.SetValue(group)

		self.list_sk_keys = []
		wx.StaticText(panel, label=_('Keys'), pos=(10, 125))
		self.keys_list = wx.ComboBox(panel, choices=self.list_sk_keys , style=wx.CB_READONLY, size=(410, 32), pos=(10, 145))
		self.keys_list.Bind(wx.EVT_COMBOBOX, self.onSelect_key)
		self.key_description = wx.TextCtrl(panel, -1, style=wx.TE_MULTILINE | wx.TE_READONLY, size=(410, 50), pos=(10, 180))
		self.key_description.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_INACTIVECAPTION))

		self.wildcardlabel = wx.StaticText(panel, label=_('*'), pos=(10, 240))
		self.wildcardlabel2 = wx.StaticText(panel, label=_('allowed characters: 0-9, a-z, A-Z'), pos=(150, 240))
		self.wildcard = wx.TextCtrl(panel, size=(410, 30), pos=(10, 260))
		
		cancelBtn = wx.Button(panel, wx.ID_CANCEL, pos=(120, 300))
		okBtn = wx.Button(panel, wx.ID_OK, pos=(230, 300))
		
		self.onSelect_group(0)

		if len(SKkey)>0:
			keylist=[]
			keylist.append(SKkey)
			index = 0
			for keystar in SKkeySP:
				if index != 0:
					SKkeySP[index]='*'
					newkey=''
					
					for keystar2 in SKkeySP:
						newkey+=keystar2+'.'
					keylist.append(newkey[:-1])
					SKkeySP = SKkey.split('.')
				index+=1
			
			for keystar3 in self.list_sk_keys:
				if keystar3 in keylist:
					key = keystar3
					self.keys_list.SetValue(key)
					
			if '*' in key:
				keylist = key.split('.')
				for i in range(len(SKkeySP)):
					if keylist[i] == '*':
						self.wildcard.SetValue(SKkeySP[i])
		
	def onSelect_group(self,e):
		selected = self.groups_list.GetValue()
		self.keys_list.Clear()
		if selected == _('ungrouped'):
			self.list_sk_keys = self.ungrouped
			self.group_description.SetValue(_('Ungrouped Signal K keys.'))
		else:
			tmp_list = []
			for i in self.skkeys:
				if selected == i[0]:
					self.group_description.SetValue(i[1])
				else:
					items=i[0].split('.')
					if selected == items[0]:
						tmp_list.append(i[0])
			self.list_sk_keys = tmp_list
		self.keys_list.AppendItems(self.list_sk_keys)
		self.keys_list.SetSelection(0)
		self.onSelect_key(0)

	def onSelect_key(self,e):
		selected = self.keys_list.GetValue()
		for i in self.skkeys:
			if selected == i[0]:
				self.key_description.SetValue(i[1])
		if '*' in selected:
			self.wildcardlabel.Enable()
			self.wildcardlabel2.Enable()
			self.wildcard.Enable()
		else:
			self.wildcardlabel.Disable()
			self.wildcardlabel2.Disable()
			self.wildcard.Disable()