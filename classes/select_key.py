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
import wx, ujson, re
from conf import Conf

class selectKey(wx.Dialog):
	def __init__(self, oldkey):
		wx.Dialog.__init__(self, None, title=_('Select Signal K key'), size=(710, 460))
		self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
		panel = wx.Panel(self)

		conf = Conf()
		sk_folder = conf.get('GENERAL', 'sk_folder')
		data = ""
		try:
			with open(sk_folder+'/node_modules/@signalk/signalk-schema/dist/keyswithmetadata.json') as data_file:
				data = ujson.load(data_file)
		except: self.ShowMessage(_('Error. File not found: ')+'keyswithmetadata.json')

		self.list_groups = wx.ListCtrl(panel, style=wx.LC_REPORT)
		self.list_groups.InsertColumn(0, _('Groups'), width=200)
		self.list_groups.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnSelectGroup)

		self.list_skpaths = wx.ListCtrl(panel, style=wx.LC_REPORT)
		self.list_skpaths.InsertColumn(0, _('Keys'), width=310)
		self.list_skpaths.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnSelectPath)

		self.list_skproperties = wx.ListCtrl(panel, style=wx.LC_REPORT)
		self.list_skproperties.InsertColumn(0, _('Properties'), width=200)
		self.list_skproperties.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnSelectProperty)

		self.key_description = wx.TextCtrl(panel, -1, style=wx.TE_MULTILINE | wx.TE_READONLY)
		self.key_description.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_INACTIVECAPTION))

		wildcard_label = wx.StaticText(panel, label=_('Replace * (allowed characters: 0-9, a-z, A-Z)'))
		self.wildcard = wx.TextCtrl(panel)
		addBtn = wx.Button(panel, label=_('Replace'))
		addBtn.Bind(wx.EVT_BUTTON, self.OnAdd)

		selected_key_label = wx.StaticText(panel, label=_('Selected key'))
		self.SKkey = wx.TextCtrl(panel, style=wx.CB_READONLY)

		cancelBtn = wx.Button(panel, wx.ID_CANCEL)
		okBtn = wx.Button(panel, wx.ID_OK)
		okBtn.Bind(wx.EVT_BUTTON, self.OnOk)


		lists = wx.BoxSizer(wx.HORIZONTAL)
		lists.Add(self.list_groups, 0, wx.ALL | wx.EXPAND, 0)
		lists.Add(self.list_skpaths, 1, wx.ALL | wx.EXPAND, 0)
		lists.Add(self.list_skproperties, 0, wx.ALL | wx.EXPAND, 0)

		wildcard = wx.BoxSizer(wx.HORIZONTAL)
		wildcard.Add(wildcard_label, 0, wx.ALL, 5)
		wildcard.Add(self.wildcard, 1, wx.ALL, 5)
		wildcard.Add(addBtn, 0, wx.ALL, 5)

		key = wx.BoxSizer(wx.HORIZONTAL)
		key.Add(selected_key_label, 0, wx.ALL, 5)
		key.Add(self.SKkey, 1, wx.ALL, 5)

		okcancel = wx.BoxSizer(wx.HORIZONTAL)
		okcancel.Add((0, 0), 1, wx.ALL, 0)
		okcancel.Add(okBtn, 0, wx.ALL, 5)
		okcancel.Add(cancelBtn, 0, wx.ALL, 5)

		main = wx.BoxSizer(wx.VERTICAL)
		main.Add(lists, 2, wx.ALL | wx.EXPAND, 0)
		main.Add(self.key_description, 1, wx.ALL | wx.EXPAND, 0)
		main.AddSpacer(10)
		main.Add(wildcard, 0, wx.ALL | wx.EXPAND, 0)
		main.Add(key, 0, wx.ALL | wx.EXPAND, 0)
		main.Add(okcancel, 0, wx.ALL | wx.EXPAND, 0)

		panel.SetSizer(main)
		self.Centre()

		clean_data = {}
		for i in data:
			if '/vessels/*/' in i:
				new = i.replace('/vessels/*/','')
				new = new.replace('RegExp','*')
				new = new.replace('[A-Za-z0-9]+','*')
				new = new.replace('/','.')
				clean_data[new] = data[i]
		
		self.grouped_data = [{'name': 'ungrouped', 'description': 'Keys that do not belong to any group', 'keys':[]}]
		groups_tmp = []
		for i in clean_data:
			items = i.split('.')
			first_key = items[0]
			if first_key in groups_tmp:
				exist = False
				for ii in self.grouped_data:
					if ii['name'] == first_key: exist = True
				if not exist:
					description = '[missing]'
					if clean_data[first_key].has_key('description'): description = clean_data[first_key]['description']
					self.grouped_data.append({'name': first_key, 'description': description, 'keys':[]})
			else: groups_tmp.append(first_key)
		
		self.grouped_data = sorted(self.grouped_data, key=lambda k: k['name'])

		for i in clean_data:
			items = i.split('.')
			first_key = items[0]
			rest = items
			rest.pop(0)
			keyname = '.'.join(rest)
			exist = False
			for ii in self.grouped_data:
				if ii['name'] == first_key:
					exist = True
					if i != first_key: ii['keys'].append({'name':keyname, 'content':clean_data[i]})
			if not exist:
				for ii in self.grouped_data:
					if ii['name'] == 'ungrouped':
						ii['keys'].append({'name':first_key, 'content':clean_data[i]})
			for i in self.grouped_data:
				i['keys'] = sorted(i['keys'], key=lambda k: k['name'])

		for i in self.grouped_data:
			self.list_groups.Append([i["name"]])

		self.selected_group = False
		self.selected_path = False
		self.selected_property = False

		if oldkey: 
			self.SKkey.SetValue(oldkey)

	def OnSelectGroup(self,e):
		self.selected_group = e.GetIndex()
		self.selected_path = False
		self.selected_property = False
		self.list_skpaths.DeleteAllItems()
		self.list_skproperties.DeleteAllItems()

		if 'description' in self.grouped_data[self.selected_group]:
			self.key_description.SetValue('\n  '+self.grouped_data[self.selected_group]['description'])

		for i in self.grouped_data[self.selected_group]['keys']:
			self.list_skpaths.Append([i["name"]])

		self.SKkey.SetValue(self.list_groups.GetItemText(self.selected_group))

	def OnSelectPath(self,e):
		self.selected_path = e.GetIndex()
		self.selected_property = False
		self.list_skproperties.DeleteAllItems()

		if 'description' in self.grouped_data[self.selected_group]['keys'][self.selected_path]['content']:
			self.key_description.SetValue('\n  '+self.grouped_data[self.selected_group]['keys'][self.selected_path]['content']['description'])
		if 'units' in self.grouped_data[self.selected_group]['keys'][self.selected_path]['content']:
			self.key_description.AppendText('\n\n  '+'Units: '+self.grouped_data[self.selected_group]['keys'][self.selected_path]['content']['units'])
		if 'enum' in self.grouped_data[self.selected_group]['keys'][self.selected_path]['content']:
			enum = self.grouped_data[self.selected_group]['keys'][self.selected_path]['content']['enum']
			new = [m.encode('utf-8') for m in enum]
			self.key_description.AppendText('\n\n  '+'Enum: '+str(new))
	
		if 'properties' in self.grouped_data[self.selected_group]['keys'][self.selected_path]['content']:
			for i in self.grouped_data[self.selected_group]['keys'][self.selected_path]['content']['properties']:
				self.list_skproperties.Append([i])

		self.SKkey.SetValue(self.list_groups.GetItemText(self.selected_group)+'.'+self.list_skpaths.GetItemText(self.selected_path))

	def OnSelectProperty(self,e):
		self.selected_property = e.GetIndex()
		self.selected_text = self.list_skproperties.GetItemText(self.selected_property)

		if 'properties' in self.grouped_data[self.selected_group]['keys'][self.selected_path]['content']:
			if 'description' in self.grouped_data[self.selected_group]['keys'][self.selected_path]['content']['properties'][self.selected_text]:
				self.key_description.SetValue('\n  '+self.grouped_data[self.selected_group]['keys'][self.selected_path]['content']['properties'][self.selected_text]['description'])
			if 'units' in self.grouped_data[self.selected_group]['keys'][self.selected_path]['content']['properties'][self.selected_text]:
				self.key_description.AppendText('\n\n  '+'Units: '+self.grouped_data[self.selected_group]['keys'][self.selected_path]['content']['properties'][self.selected_text]['units'])
			if 'enum' in self.grouped_data[self.selected_group]['keys'][self.selected_path]['content']['properties'][self.selected_text]:
				enum = self.grouped_data[self.selected_group]['keys'][self.selected_path]['content']['properties'][self.selected_text]['enum']
				new = [m.encode('utf-8') for m in enum]
				self.key_description.AppendText('\n\n  '+'Enum: '+str(new))
			if 'items' in self.grouped_data[self.selected_group]['keys'][self.selected_path]['content']['properties'][self.selected_text]:
				enum = self.grouped_data[self.selected_group]['keys'][self.selected_path]['content']['properties'][self.selected_text]['items']['enum']
				new = [m.encode('utf-8') for m in enum]
				self.key_description.AppendText('\n\n  '+'Enum: '+str(new))

		self.SKkey.SetValue(self.list_groups.GetItemText(self.selected_group)+'.'+self.list_skpaths.GetItemText(self.selected_path)+':'+self.list_skproperties.GetItemText(self.selected_property))

	def OnAdd(self,e):
		wildcard = self.wildcard.GetValue()
		if wildcard:
			if not re.match('^[0-9a-zA-Z]+$', wildcard):
				self.ShowMessage(_('Failed. Characters not allowed.'))
				return
			key = self.SKkey.GetValue()
			key = key.replace('*', wildcard, 1)
			self.SKkey.SetValue(key)

	def OnOk(self,e):
		self.selected_key = self.SKkey.GetValue()
		if '*' in self.selected_key:
			self.ShowMessage(_('Failed. Replace * by some text.'))
			return
		self.EndModal(wx.OK)

	def ShowMessage(self, w_msg):
		wx.MessageBox(w_msg, 'Info', wx.OK | wx.ICON_INFORMATION)
		
		
		
