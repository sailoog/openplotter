#!/usr/bin/env python

# This file is part of Openplotter.
# Copyright (C) 2019 by sailoog <https://github.com/sailoog/openplotter>
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
import wx, os, sys, subprocess, ConfigParser, webbrowser, time
from wx.lib.mixins.listctrl import CheckListCtrlMixin, ListCtrlAutoWidthMixin

op_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../..')
sys.path.append(op_folder+'/classes')
from conf import Conf
from language import Language
from SK_settings import SK_settings
from opencpnSettings import opencpnSettings
from nodes_SK_filter import Nodes, TriggerFilterSK, Condition, ActionEndFilterSignalk

class CheckListCtrl(wx.ListCtrl, CheckListCtrlMixin, ListCtrlAutoWidthMixin):
	def __init__(self, parent, width, height):
		wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER, size=(width, height))
		CheckListCtrlMixin.__init__(self)
		ListCtrlAutoWidthMixin.__init__(self)

class MyFrame(wx.Frame):
		
	def __init__(self):

		self.conf = Conf()
		self.home = self.conf.home
		self.op_folder = self.conf.get('GENERAL', 'op_folder')
		self.currentpath = self.op_folder
		self.help_bmp = wx.Bitmap(self.op_folder + "/static/icons/help-browser.png", wx.BITMAP_TYPE_ANY)
		Language(self.conf)
		self.SK_settings = SK_settings(self.conf)
		self.opencpnSettings = opencpnSettings()
		
		
		self.available_operators = ['eq', 'neq', 'lt', 'lte', 'gt', 'gte','btwn', 'cont', 'true', 'false', 'null', 'nnull', 'empty', 'nempty']
		self.available_conditions = ['=', '!=', '<', '<=', '>', '>=', _('is between'), _('contains'), _('is true'), ('is false'), _('is null'), _('is not null'), _('is empty'), _('is not empty')]		

		wx.Frame.__init__(self, None, title=_('SignalK input filter (uses node-red)'), size=(710,460))
		
		self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
		
		self.icon = wx.Icon(self.op_folder+'/static/icons/openplotter.ico', wx.BITMAP_TYPE_ICO)
		self.SetIcon(self.icon)

		self.list_triggers = CheckListCtrl(self, -1,90)
		self.list_triggers.InsertColumn(0, _('Filter begin'), width=120)
		self.list_triggers.InsertColumn(1, _(' '), width= 130)
		self.list_triggers.InsertColumn(2, _(' '), width= 130)
		self.list_triggers.InsertColumn(3, _(' '), width= 100)
		self.list_triggers.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_print_conditions)
		self.list_triggers.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.on_deselected_triggers)
		self.list_triggers.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_edit_triggers)
		self.list_triggers.OnCheckItem = self.on_check_item

		self.available_triggers = [_('Signal K Filter')]

		self.available_triggers_select = wx.Choice(self, choices=self.available_triggers, style=wx.CB_READONLY)

		add_trigger = wx.Button(self, label=_('add'))
		add_trigger.Bind(wx.EVT_BUTTON, self.on_add_trigger)

		delete_trigger = wx.Button(self, label=_('delete'))
		delete_trigger.Bind(wx.EVT_BUTTON, self.on_delete_trigger)

		self.available_operators = ['eq', 'neq', 'lt', 'lte', 'gt', 'gte','btwn', 'cont', 'true', 'false', 'null', 'nnull', 'empty', 'nempty']
		self.available_conditions = ['=', '!=', '<', '<=', '>', '>=', _('is between'), _('contains'), _('is true'), ('is false'), _('is null'), _('is not null'), _('is empty'), _('is not empty')]
		#self.available_operators_select = wx.Choice(self, choices=self.available_conditions, style=wx.CB_READONLY)

		self.list_conditions = wx.ListCtrl(self, style=wx.LC_REPORT | wx.SUNKEN_BORDER, size=(-1,90))
		self.list_conditions.InsertColumn(0, _('Conditions'), width= 100)
		self.list_conditions.InsertColumn(1, _(' '), width= 150)
		self.list_conditions.InsertColumn(2, _(' '), width= 150)
		self.list_conditions.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_print_actions)
		self.list_conditions.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.on_deselected_conditions)
		self.list_conditions.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.edit_conditions)


		add_condition = wx.Button(self, label=_('add'))
		add_condition.Bind(wx.EVT_BUTTON, self.on_add_condition)

		delete_condition = wx.Button(self, label=_('delete'))
		delete_condition.Bind(wx.EVT_BUTTON, self.on_delete_condition)

		self.list_actions = wx.ListCtrl(self, style=wx.LC_REPORT | wx.SUNKEN_BORDER, size=(-1,90))
		self.list_actions.InsertColumn(0, _('Filter end'), width= 150)
		self.list_actions.InsertColumn(1, _(' '), width= 170)
		self.list_actions.InsertColumn(2, _(' '), width= 100)
		self.list_actions.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_select_actions)
		self.list_actions.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.on_deselected_actions)
		self.list_actions.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_edit_actions)

		self.available_actions = [_('End Filter Signal K')]

		self.available_actions_select = wx.Choice(self, choices=self.available_actions, style=wx.CB_READONLY)
		add_action = wx.Button(self, label=_('add'))
		add_action.Bind(wx.EVT_BUTTON, self.on_add_action)

		delete_action = wx.Button(self, label=_('delete'))
		delete_action.Bind(wx.EVT_BUTTON, self.on_delete_action)

		help_button = wx.BitmapButton(self, bitmap=self.help_bmp, size=(self.help_bmp.GetWidth()+40, self.help_bmp.GetHeight()+10))
		help_button.Bind(wx.EVT_BUTTON, self.on_help_action)

		apply_changes = wx.Button(self, label=_('Apply changes'))
		apply_changes.Bind(wx.EVT_BUTTON, self.on_apply_changes_actions)
		cancel_changes = wx.Button(self, label=_('Cancel changes'))
		cancel_changes.Bind(wx.EVT_BUTTON, self.on_cancel_changes_actions)

		hlistbox_but = wx.BoxSizer(wx.HORIZONTAL)
		hlistbox_but.Add(add_trigger, 0, wx.ALL, 5)
		hlistbox_but.Add(delete_trigger, 0, wx.ALL, 5)

		vlistbox_trig = wx.BoxSizer(wx.VERTICAL)
		vlistbox_trig.Add(self.available_triggers_select, 0, wx.ALL | wx.EXPAND, 5)
		vlistbox_trig.Add(hlistbox_but, 0, wx.ALL, 0)

		hlistbox = wx.BoxSizer(wx.HORIZONTAL)
		hlistbox.Add(self.list_triggers, 1, wx.ALL | wx.EXPAND, 5)
		hlistbox.Add(vlistbox_trig, 0, wx.RIGHT | wx.LEFT, 0)

		hlistbox_but2 = wx.BoxSizer(wx.HORIZONTAL)
		hlistbox_but2.Add(add_condition, 0, wx.ALL, 5)
		hlistbox_but2.Add(delete_condition, 0, wx.ALL, 5)

		vlistbox_cond = wx.BoxSizer(wx.VERTICAL)
		vlistbox_cond.AddSpacer(35)
		#vlistbox_cond.Add(self.available_operators_select, 0, wx.ALL | wx.EXPAND, 5)
		vlistbox_cond.Add(hlistbox_but2, 0, wx.ALL, 0)

		hlistbox2 = wx.BoxSizer(wx.HORIZONTAL)
		hlistbox2.Add(self.list_conditions, 1, wx.ALL | wx.EXPAND, 5)
		hlistbox2.Add(vlistbox_cond, 0, wx.RIGHT | wx.LEFT, 0)

		hlistbox_but3 = wx.BoxSizer(wx.HORIZONTAL)
		hlistbox_but3.Add(add_action, 0, wx.ALL, 5)
		hlistbox_but3.Add(delete_action, 0, wx.ALL, 5)

		vlistbox_act = wx.BoxSizer(wx.VERTICAL)
		vlistbox_act.Add(self.available_actions_select, 0, wx.ALL | wx.EXPAND, 5)
		vlistbox_act.Add(hlistbox_but3, 0, wx.ALL, 0)

		hlistbox3 = wx.BoxSizer(wx.HORIZONTAL)
		hlistbox3.Add(self.list_actions, 1, wx.ALL | wx.EXPAND, 5)
		hlistbox3.Add(vlistbox_act, 0, wx.RIGHT | wx.LEFT, 0)

		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(help_button, 0, wx.ALL, 0)
		hbox.AddStretchSpacer(1)
		hbox.Add(apply_changes, 0, wx.RIGHT | wx.LEFT, 5)
		hbox.Add(cancel_changes, 0, wx.RIGHT | wx.LEFT, 5)

		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.Add(hlistbox, 1, wx.ALL | wx.EXPAND, 0)
		vbox.Add(hlistbox2, 1, wx.ALL | wx.EXPAND, 0)
		vbox.Add(hlistbox3, 1, wx.ALL | wx.EXPAND, 0)
		vbox.Add(hbox, 0, wx.ALL | wx.EXPAND, 5)
		self.SetStatusText = wx.StaticText(self, label=_(' '))
		vbox.Add(self.SetStatusText, 0, wx.ALL | wx.EXPAND, 5)

		self.SetSizer(vbox)
		self.read_triggers()

	def read_triggers(self):
		self.actions_flow_id = 'openplot.filter'
		self.selected_trigger = -1
		self.selected_condition = -1
		self.selected_action = -1
		self.nodes = Nodes(self,self.actions_flow_id)
		result = self.nodes.get_flow()
		self.actions_flow_tree = result[0]
		self.triggers_flow_nodes = result[1]
		self.conditions_flow_nodes = result[2]
		self.actions_flow_nodes = result[3]
		self.no_actions_nodes = result[4]
		self.add_credentials = {}
		self.remove_credentials = []
		self.on_print_triggers()

	def on_print_triggers(self):	
		self.list_triggers.DeleteAllItems()
		self.list_conditions.DeleteAllItems()
		self.list_actions.DeleteAllItems()
		self.selected_trigger = -1
		self.selected_condition = -1
		self.selected_action = -1
		for trigger in self.actions_flow_tree:
			enabled = False
			name = "t|"+trigger["trigger_node_out_id"]+"|"+trigger["type"]
			field2 = ''
			field3 = ''
			field4 = ''
			path = ''
			path_property = ''
			for node in self.triggers_flow_nodes:
				if 'name' in node and name == node['name']:
					if trigger["type"] == '0':
						if node['type'] == 'signalk-subscribe': 
							path = node['path']
							field2 = node['context']
							field4 = node['source']
						if node['type'] == 'function' and node['func'] and node['func'] != 'return msg;':
							items = node['func'].split(';')
							items2 = items[0].split('.')
							path_property = ':'+items2[-1]
						field3 = path+path_property
					if trigger["type"] == '1':
						if node['type'] == 'signalk-input-handler': 
							path = node['path']
							field2 = node['context']
							field3 = path
							field4 = node['source']
					if trigger["type"] == '2' and node['type'] == 'signalk-geofence': 
						field2 = node['context']
						if node['myposition']: field3 = _('Use My Position')
						else: field3 = node['lat']+', '+node['lon']
						field4 = node['distance']
					if trigger["type"] == '3' and node['type'] == 'rpi-gpio in': 
						field2 = node['pin']
						field3 = node['intype']
						if node['read']: field4 = _('initial state')
					if trigger["type"] == '4' and node['type'] == 'mqtt in':
						if node['broker'] == self.localbrokerid: field2 = _('local broker')
						elif node['broker'] == self.remotebrokerid: field2 = _('remote broker')
						field3 = node['topic']
					if trigger["type"] == '6' and node['type'] == 'inject':
						field2 = node['repeat']
						field3 = _('Seconds')
				if node['id'] == trigger["trigger_node_out_id"]:
					if 'func' in node:
						if 	node['func'] == 'return msg;': enabled = True
					else:
						enabled = True
			self.list_triggers.Append([self.available_triggers[int(trigger["type"])].decode('utf8'), field2.decode('utf8'), field3.decode('utf8'), field4.decode('utf8')])
			last = self.list_triggers.GetItemCount()-1
			if enabled: self.list_triggers.CheckItem(last)

	def on_check_item(self, index, flag):
		trigger_node_out_id = self.actions_flow_tree[index]['trigger_node_out_id']
		for node in self.triggers_flow_nodes:
			if node['id'] == trigger_node_out_id:
				if flag: node['func'] = 'return msg;'
				else: node['func'] = ''

	def on_print_conditions(self, e):
		self.list_conditions.DeleteAllItems()
		self.list_actions.DeleteAllItems()
		self.selected_condition = -1
		self.selected_action = -1
		self.selected_trigger = self.list_triggers.GetFirstSelected()
		self.list_triggers.Focus(self.list_triggers.GetFirstSelected())
		if self.selected_trigger == -1: return
		conditions = self.actions_flow_tree[self.selected_trigger]["conditions"]
		triggertype = self.actions_flow_tree[self.selected_trigger]["type"]
		for condition in conditions:
			name = "c|"+condition["condition_node_out_id"]+"|"+condition["operator"]
			field2 = ''
			field3 = ''
			for node in self.conditions_flow_nodes:
				if 'name' in node and name == node['name']:
					if node['type'] == 'switch':
						if 'v' in node['rules'][0]:
							if triggertype == '5':
								try:
									seconds = float(node['rules'][0]['v'])/1000
									local_time = datetime.fromtimestamp(seconds)
									field2 = local_time.strftime("%Y-%m-%d %H:%M:%S")
								except: pass
							else: field2 = node['rules'][0]['v']
						if 't' in node['rules'][0] and node['rules'][0]['t'] == 'btwn':
							if 'v2' in node['rules'][0]:
								if triggertype == '5':
									try:
										seconds = float(node['rules'][0]['v2'])/1000
										local_time = datetime.fromtimestamp(seconds)
										field3 = local_time.strftime("%Y-%m-%d %H:%M:%S")
									except: pass
								else: field3 = node['rules'][0]['v2']
			self.list_conditions.Append([self.available_conditions[int(condition["operator"])].decode('utf8'), field2.decode('utf8'), field3.decode('utf8')])

	def on_print_actions(self, e):
		self.list_actions.DeleteAllItems()
		self.selected_action = -1
		self.selected_condition = self.list_conditions.GetFirstSelected()
		if self.selected_condition == -1: return
		actions = self.actions_flow_tree[self.selected_trigger]["conditions"][self.selected_condition]["actions"]
		for action in actions:
			name = "a|"+action["action_node_out_id"]+"|"+action["type"]
			field2 = ''
			field3 = ''
			for node in self.actions_flow_nodes:
				namenode = ''
				if 'dname' in node: namenode = node['dname']
				elif 'name' in node: namenode = node['name']
				if name == namenode:
					if action["type"] == '0' and node['type'] == 'change': 
						field2 = node['rules'][0]['to']
						field3 = node['rules'][1]['to']
					if action["type"] == '1': 
						if node['type'] == 'rpi-gpio out': field2 = node['pin']
						if node['type'] == 'change': field3 = node['rules'][0]['to']
					if action["type"] == '2':
						if node['type'] == 'mqtt out':
							if node['broker'] == self.localbrokerid: field2 = _('local broker')
							elif node['broker'] == self.remotebrokerid: field2 = _('remote broker')
							field3 = node['topic']
					if action["type"] == '3':
						if node['type'] == 'template': field2 = node['template']
						if node['type'] == 'msg-resend': field3 = _('repeat')
						if node['type'] == 'delay': field3 = _('rate limit')
					if action["type"] == '4':
						if node['type'] == 'template' and node['field'] == 'topic': field2 = node['template']
						if node['type'] == 'msg-resend': field3 = _('repeat')
						if node['type'] == 'delay': field3 = _('rate limit')
					if action["type"] == '5':
						if node['type'] == 'exec': field2 = node['append']
						if node['type'] == 'msg-resend': field3 = _('repeat')
						if node['type'] == 'delay': field3 = _('rate limit')
					if action["type"] == '6' or action["type"] == '7' or action["type"] == '8':
						if node['type'] == 'exec': 
							field2 = node['command']
							field2 += ' '+node['append']
						if node['type'] == 'msg-resend': field3 = _('repeat')
						if node['type'] == 'delay': field3 = _('rate limit')
					if action["type"] == '9':
						if node['type'] == 'template': field2 = node['template']
						if node['type'] == 'usbcamera': field2 = _('take picture')
						if node['type'] == 'chatbot-image' and not field2: field2 = node['image']
						if node['type'] == 'msg-resend': field3 = _('repeat')
						if node['type'] == 'delay': field3 = _('rate limit')
			self.list_actions.Append([self.available_actions[int(action["type"])].decode('utf8'), field2.decode('utf8'), field3.decode('utf8')])

	def on_select_actions(self, e):
		self.selected_action = self.list_actions.GetFirstSelected()

	def on_deselected_triggers(self, e):
		self.on_print_triggers()

	def on_deselected_conditions(self, e):
		self.on_print_conditions(0)

	def on_deselected_actions(self, e):
		self.selected_action = -1

	def on_edit_triggers(self, e):
		if self.selected_trigger == -1: return
		node = self.actions_flow_tree[self.selected_trigger]['trigger_node_out_id']
		triggertype = self.actions_flow_tree[self.selected_trigger]['type']
		name = 't|'+node+'|'+triggertype
		edit = []
		for i in self.triggers_flow_nodes:
			if 'name' in i:
				if i['name'] == name: edit.append(i)
			else:
				subid0 = i['id'].split('.')
				subid = subid0[0]
				for ii in self.triggers_flow_nodes:
					subid0 = ii['id'].split('.')
					subid2 = subid0[0]
					if subid2 == subid and name == ii['name']: edit.append(i)
		self.edit_add_trigger(edit)

	def on_add_trigger(self, e):
		self.edit_add_trigger(0)

	def edit_add_trigger(self, edit):
		if not edit: trigger = self.available_triggers_select.GetSelection()
		else: trigger = int(self.actions_flow_tree[self.selected_trigger]['type'])
		if trigger == 0: dlg = TriggerFilterSK(self,edit,trigger)
		else:
			self.ShowStatusBarRED(_('Select a trigger type.'))
			return
		res = dlg.ShowModal()
		if res == wx.OK:
			if not edit:
				for i in dlg.TriggerNodes:
					self.triggers_flow_nodes.append(i)
					if 'name' in i: items = i['name'].split('|')
				self.actions_flow_tree.append({"trigger_node_out_id": items[1],"type": items[2],"conditions": []})
				self.on_print_triggers()
				last = self.list_triggers.GetItemCount()-1
				self.list_triggers.Select(last)
			else:
				tmplist = []
				nodeout = self.actions_flow_tree[self.selected_trigger]['trigger_node_out_id']
				for i in self.triggers_flow_nodes:
					exist = False
					for ii in edit:
						if i['id'] == ii['id']: 
							exist = True
							if ii['id'] == nodeout: wires = ii['wires']
					if not exist: tmplist.append(i)
				self.triggers_flow_nodes = tmplist
				for i in dlg.TriggerNodes:
					if 'name' in i: items = i['name'].split('|')
					self.triggers_flow_nodes.append(i)
				for i in self.triggers_flow_nodes:
					if i['id'] == items[1]: i['wires'] = wires
				self.actions_flow_tree[self.selected_trigger]['trigger_node_out_id'] = items[1]
				self.actions_flow_tree[self.selected_trigger]['type'] = items[2]
				selected_trigger = self.selected_trigger
				self.on_print_triggers()
				self.selected_trigger = selected_trigger
				self.list_triggers.Select(self.selected_trigger)
		dlg.Destroy()

	def edit_conditions(self, e):
		#find connected condition
		if self.selected_condition == -1: return
		nodec = self.actions_flow_tree[self.selected_trigger]['conditions'][self.selected_condition]['condition_node_out_id']
		typec = self.actions_flow_tree[self.selected_trigger]['conditions'][self.selected_condition]['operator']
		name = 'c|'+nodec+'|'+typec
		edit = ''
		for i in self.conditions_flow_nodes:
			if 'name' in i:
				if i['name'] == name: 
					edit = i['rules'][0]
					self.edit_cond = i
		self.edit_add_condition(edit)

	def on_add_condition(self, e):
		self.edit_add_condition(0)

	def edit_add_condition(self, edit):
		if not edit:
			if self.selected_trigger == -1:
				self.ShowStatusBarRED(_('Select a trigger.'))
				return
		dlg = Condition(self,edit)
			
		res = dlg.ShowModal()
		if res == wx.OK:
			if not edit:
				#when filter SK (type 1) property is src not payload
				if self.actions_flow_tree[self.selected_trigger]['type'] == '1':
					dlg.ConditionNode['property'] = 'source.src'
				self.conditions_flow_nodes.append(dlg.ConditionNode)
				items = dlg.ConditionNode['name'].split('|')
				self.actions_flow_tree[self.selected_trigger]['conditions'].append({"condition_node_out_id": items[1],"operator": items[2],"actions": []})
				trigger_id = self.actions_flow_tree[self.selected_trigger]['trigger_node_out_id']
				for i in self.triggers_flow_nodes:
					if i['id'] == trigger_id: i['wires'][0].append(dlg.connector_id)
			else:
				self.edit_cond['rules'] = dlg.ConditionNode['rules']
				namesplit = self.edit_cond['name'].split('|')
				operator = self.available_operators.index(self.edit_cond['rules'][0]['t'])
				self.edit_cond['name'] = namesplit[0]+'|'+namesplit[1]+'|'+str(operator)

				for i in self.actions_flow_tree[self.selected_trigger]['conditions']:
					if 'condition_node_out_id' in i:
						if i['condition_node_out_id'] == namesplit[1]:
							i['operator'] = str(operator)

			self.on_print_conditions(0)
			last = self.list_conditions.GetItemCount()-1
			self.list_conditions.Select(last)

		dlg.Destroy()

	def on_edit_actions(self, e):
		#find connected action
		if self.selected_action == -1: return
		node = self.actions_flow_tree[self.selected_trigger]['conditions'][self.selected_condition]['actions']
		nodea = node[self.selected_action]['action_node_out_id']
		typea = node[self.selected_action]['type']
		name = 'a|'+nodea+'|'+typea
		edit = []
		for i in self.actions_flow_nodes:
			#print 1,i
			if 'dname' in i:
				#print 0,i['name']
				if i['dname'] == name: 
					#print -3
					edit.append(i)
				self.edit_cond = i
			elif 'name' in i:
				#print 0,i['name']
				if i['name'] == name: 
					#print -3
					edit.append(i)
				self.edit_cond = i
		
		#print 'edit'
		#for i in edit:
		#	print i
		
		self.edit_add_action(edit)
		
	def on_add_action(self, e):
		self.edit_add_action(0)

	def edit_add_action(self, edit):
		if not edit:
			if self.selected_condition == -1:
				self.ShowStatusBarRED(_('Select a condition.'))
				return
		else:
			if 'dname' in edit[0]:
				typesplit = edit[0]['dname'].split('|')
			else:	
				typesplit = edit[0]['name'].split('|')
			type = int(typesplit[2])
			self.available_actions_select.SetSelection(type)
		action = self.available_actions_select.GetSelection()
		if action == 0: dlg = ActionEndFilterSignalk(self,edit)
		else:
			self.ShowStatusBarRED(_('Select an action.'))
			return
		res = dlg.ShowModal()
		if res == wx.OK:
			if edit:
				self.on_delete_action(0)
			for i in dlg.ActionNodes:
				self.actions_flow_nodes.append(i)
				if 'dname' in i: items = i['dname'].split('|')
				elif 'name' in i: items = i['name'].split('|')
			self.actions_flow_tree[self.selected_trigger]['conditions'][self.selected_condition]['actions'].append({"action_node_out_id": items[1],"type": items[2]})
			condition_id = self.actions_flow_tree[self.selected_trigger]['conditions'][self.selected_condition]['condition_node_out_id']
			for i in self.conditions_flow_nodes:
				if i['id'] == condition_id: i['wires'][0].append(dlg.connector_id)
			self.on_print_actions(0)
			last = self.list_actions.GetItemCount()-1
			self.list_actions.Select(last)
			if dlg.credentials:
				for i in dlg.credentials:
					self.add_credentials[i] = dlg.credentials[i]
		dlg.Destroy()

	def on_delete_trigger(self, e):
		if self.selected_trigger == -1:
			self.ShowStatusBarRED(_('Select an item to delete'))
			return
		node = self.actions_flow_tree[self.selected_trigger]['trigger_node_out_id']
		triggertype = self.actions_flow_tree[self.selected_trigger]['type']
		name = 't|'+node+'|'+triggertype
		conditions = self.actions_flow_tree[self.selected_trigger]['conditions']

		for condition in conditions:
			nodec = condition['condition_node_out_id']
			operatortype = condition['operator']
			namec = 'c|'+nodec+'|'+operatortype
			actions = condition['actions']
			for action in actions:
				nameaction = 'a|'+action['action_node_out_id']+'|'+action['type']
				self.delete_action_nodes(nameaction,action['type'],nodec)
			self.delete_condition_nodes(namec,node)

		self.delete_trigger_nodes(name)
		del self.actions_flow_tree[self.selected_trigger]
		self.on_print_triggers()

	def delete_trigger_nodes(self,name):
		tmplist = []
		for i in self.triggers_flow_nodes:
			name2 = ''
			if 'name' in i: name2 = i['name']
			elif not 'name' in i:
				subid0 = i['id'].split('.')
				subid = subid0[0]
				for ii in self.triggers_flow_nodes:
					subidii = ii['id'].split('.')
					if 'name' in ii and subid == subidii[0]: name2 = ii['name']
			if name != name2: tmplist.append(i)
		self.triggers_flow_nodes = tmplist

	def on_delete_condition(self, e):
		if self.selected_condition == -1:
			self.ShowStatusBarRED(_('Select an item to delete'))
			return
		node = self.actions_flow_tree[self.selected_trigger]['conditions'][self.selected_condition]['condition_node_out_id']
		operatortype = self.actions_flow_tree[self.selected_trigger]['conditions'][self.selected_condition]['operator']
		name = 'c|'+node+'|'+operatortype
		triggernode = self.actions_flow_tree[self.selected_trigger]['trigger_node_out_id']
		actions = self.actions_flow_tree[self.selected_trigger]['conditions'][self.selected_condition]['actions']
		for i in actions:
			nameaction = 'a|'+i['action_node_out_id']+'|'+i['type']
			self.delete_action_nodes(nameaction,i['type'],node)
		self.delete_condition_nodes(name,triggernode)
		del self.actions_flow_tree[self.selected_trigger]['conditions'][self.selected_condition]
		self.on_print_conditions(0)

	def delete_condition_nodes(self,name,triggernode):
		tmplist = []
		for i in self.conditions_flow_nodes:
			name2 = ''
			if 'name' in i: name2 = i['name']
			if name != name2: tmplist.append(i)
			else:
				for ii in self.triggers_flow_nodes:
					if ii['id'] == triggernode:
						if i['id'] in ii['wires'][0]: ii['wires'][0].remove(i['id'])
		self.conditions_flow_nodes = tmplist

	def on_delete_action(self, e):
		if self.selected_action == -1:
			self.ShowStatusBarRED(_('Select an item to delete'))
			return
		node = self.actions_flow_tree[self.selected_trigger]['conditions'][self.selected_condition]['actions'][self.selected_action]['action_node_out_id']
		actiontype = self.actions_flow_tree[self.selected_trigger]['conditions'][self.selected_condition]['actions'][self.selected_action]['type']
		name = 'a|'+node+'|'+actiontype
		conditionnode = self.actions_flow_tree[self.selected_trigger]['conditions'][self.selected_condition]['condition_node_out_id']
		self.delete_action_nodes(name,actiontype,conditionnode)
		del self.actions_flow_tree[self.selected_trigger]['conditions'][self.selected_condition]['actions'][self.selected_action]
		self.on_print_actions(0)
		
	def delete_action_nodes(self,name,actiontype,conditionnode):
		tmplist = []
		for i in self.actions_flow_nodes:
			name2 = ''
			if 'dname' in i: name2 = i['dname']
			elif 'name' in i: name2 = i['name']
			elif not 'name' in i:
				subid0 = i['id'].split('.')
				subid = subid0[0]
				for ii in self.actions_flow_nodes:
					subidii = ii['id'].split('.')
					if 'name' in ii and subid == subidii[0]: name2 = ii['name']
			if name != name2: tmplist.append(i)
			else:
				for ii in self.conditions_flow_nodes:
					if ii['id'] == conditionnode:
						if i['id'] in ii['wires'][0]: ii['wires'][0].remove(i['id'])
				if actiontype == '4' and 'type' in i:
					if i['type'] == 'e-mail': self.remove_credentials.append(i['id'])
		self.actions_flow_nodes = tmplist

	def on_apply_changes_actions(self, e):
		all_flows = []
		result = self.nodes.get_flow()
		no_actions_nodes = result[4]
		others_flow_nodes = result[5]

		for i in no_actions_nodes:
			all_flows.append(i)
		for i in others_flow_nodes:
			all_flows.append(i)
		for i in self.triggers_flow_nodes:
			all_flows.append(i)
		for i in self.conditions_flow_nodes:
			all_flows.append(i)
			if i["type"] == "switch":
				result = []
				if 'vt' in i['rules'][0] and i['rules'][0]['vt'] == 'flow':
					result = self.nodes.get_subscription(i['rules'][0]['v'])
					name = result[0]['name']
					exists = False
					for ii in all_flows:
						if 'name' in ii and ii['name'] == name: exists = True
					if not exists:
						for iii in result: all_flows.append(iii)
				if 'v2t' in i['rules'][0] and i['rules'][0]['v2t'] == 'flow':
					result = self.nodes.get_subscription(i['rules'][0]['v2'])
					name = result[0]['name']
					exists = False
					for ii in all_flows:
						if 'name' in ii and ii['name'] == name: exists = True
					if not exists:
						for iii in result: all_flows.append(iii)

		for i in self.actions_flow_nodes:
			all_flows.append(i)
			if i["type"] == "change":
				result = []
				c = len(i['rules'])
				if c == 1 and 'tot' in i['rules'][0] and i['rules'][0]['tot'] == 'flow':
					result = self.nodes.get_subscription(i['rules'][0]['to'])
				if c > 1 and 'tot' in i['rules'][1] and i['rules'][1]['tot'] == 'flow':
					result = self.nodes.get_subscription(i['rules'][1]['to'])
				if result:
					name = result[0]['name']
					exists = False
					for ii in all_flows:
						if 'name' in ii and ii['name'] == name: exists = True
					if not exists:
						for iii in result: all_flows.append(iii)
			if i["type"] == "template":
				result = []
				if 'template' in i: 
					matches = re.findall("{{(.*?)}}", i['template'])
					for ii in matches:
						value_list = ii.split('.')
						value_list.pop(0)
						skkey = '.'.join(value_list)
						result = self.nodes.get_subscription(skkey)
						name = result[0]['name']
						exists = False
						for iii in all_flows:
							if 'name' in iii and iii['name'] == name: exists = True
						if not exists:
							for iiii in result: all_flows.append(iiii)

		shortcut = []
		idabs = []
		idabs_parent = []
		line = 0
		absline = 0
		treeline = 0
		
		#create list of shortcuts
		for i in all_flows:
			if 'type' in i and 'wires' in i and 'id' in i and i['z'] == self.actions_flow_id:
				if i['wires'] in [[],[[]],[[],[]],[[],[],[]]]:
					#line,tree,parent,x,y,idnum,wiresnum,id,wires
					# 0     1    2    3 4   5       6     7   8
					shortcut.append([line,-1,-1,-1,-1,absline,-1,i['id'],''])
					line += 1
				else:
					treeline = 0
					for ii in i['wires'][0]:
						shortcut.append([line,treeline,-1,-1,-1,absline,-1,i['id'],ii])
						line += 1
						treeline += 1
				idabs.append(i['id'])
				idabs_parent.append(absline)
				absline += 1
			#print absline,line,i

		#print 'idabs'
		#for i in idabs: print idabs.index(i),i

		#print 'idabs_parent'
		#for i in idabs_parent: print idabs_parent.index(i),i

		#find idnum for id
		for i in shortcut:
			if i[8] <> '':
				i[6] = idabs.index(i[8])			
				idabs_parent[i[6]] = -1				

		#print 'idabs_parent'
		#for i in idabs_parent: print idabs_parent.index(i),i
			
		parentlist = []
		parentnum = 0
		#create parentlist
		for i in idabs_parent:
			if i > -1:
				parentlist.append(i)
				for j in shortcut:
					if j[5] == i:
						j[2]=parentnum
						j[3]=0
						j[4]=0
				parentnum += 1
			
		#print 'shortcut'
		#for i in shortcut: print i
		
		#identify x position of following nodes
		for j in range(10):
			for i in shortcut:
				if i[3] == j:
					for ii in shortcut:
						if ii[5] == i[6]:
							if ii[3] == -1:						
								ii[3] = j+1
								ii[2] = i[2]

		for j in range(len(parentlist)):
			y = 1
			#find all forks and set y
			for i in shortcut:
				if i[2] == j and i[1] >= 1:
					i[4] = y
					y += 1

		#print 'shortcut'
		#for i in shortcut: print i
		
		for j in range(10):
			for i in shortcut:
				#x -1
				if i[3] == j:
					for ii in shortcut:
						#x -1
						if ii[5] == i[6]:
							if ii[4] == -1:
								ii[4] = i[4]

		fork = []
		for j in range(len(parentlist)):
			for i in shortcut:
				#x -1
				if i[2] == j and i[1] >= 1:
					# line,linenum,mainfork(y),subfork(y),x
					fork.append([i[2],i[0],shortcut[i[0]-1][4],i[4],i[3]])
					i[4] = shortcut[i[0]-1][4]
		
		fork=sorted(fork, key=lambda x: (x[0], x[2], -x[4]))

		#print 'fork'
		#for i in fork: print i

		#set lines with fork in right direction
		#build a converting table
		convert = []
		for j in range(len(parentlist)):
			convert.append([0])
			for i in fork:
				if i[0] == j:
					convert[j].append(0)

		#set values to converting table
		for j in range(len(parentlist)):
			y = 1
			for i in fork:
				if i[0] == j:
					convert[j][i[3]] = y
					y += 1
		
		#print 'convert'
		#for i in convert: print i

		#convert every line
		for i in shortcut:
			i[4] = convert[i[2]][i[4]]

		#print 'shortcut'
		#for i in shortcut: print i

		xstart = 140
		ystart = 60
		xstep = 220
		ystep = 55
		ymax = 0
		for j in range(len(parentlist)):
			if ymax >= ystart:
				ystart = ymax + ystep

			for i in all_flows:
				if 'type' in i and 'wires' in i and 'id' in i and i['z'] == self.actions_flow_id:
					for ii in reversed(shortcut):
						if i['id'] == ii[7] and ii[2] == j:
							i['x'] = xstart + xstep * ii[3]
							i['y'] = ystart + ystep * ii[4]
							if i['y'] > ymax:
								ymax = i['y']						
					
		self.nodes.write_flow(all_flows)
		self.restart_SK()
		seconds = 15
		for i in range(seconds, 0, -1):
			self.ShowStatusBarGREEN(_('Signal K server restarted')+' | '+_('Starting Node-Red... ')+str(i))
			time.sleep(1)
		self.ShowStatusBarGREEN(_('Signal K server restarted')+' | '+_('Node-Red restarted'))

	def on_cancel_changes_actions(self, e):
		self.read_triggers()

	def on_help_action(self, e):
		url = self.currentpath+"/docs/html/filter/what_are_filter.html"
		webbrowser.open(url, new=2)
		
	def start_SK(self):
		subprocess.call(['sudo', 'systemctl', 'start', 'signalk.socket'])
		subprocess.call(['sudo', 'systemctl', 'start', 'signalk.service'])

	def stop_SK(self):
		subprocess.call(['sudo', 'systemctl', 'stop', 'signalk.service'])
		subprocess.call(['sudo', 'systemctl', 'stop', 'signalk.socket'])
		
	def ShowStatusBarRED(self, w_msg):
		self.ShowStatusBar(w_msg, wx.RED)

	def ShowStatusBarGREEN(self, w_msg):
		self.ShowStatusBar(w_msg, wx.GREEN)

	def ShowStatusBarBLACK(self, w_msg):
		self.ShowStatusBar(w_msg, wx.BLACK)	

	def ShowStatusBar(self, w_msg, colour):
		#self.GetStatusBar().SetForegroundColour(colour)
		self.SetStatusText.value = w_msg

	def restart_SK(self):
		seconds = 12
		# stopping sk server
		self.stop_SK()
		# restarting sk server
		self.start_SK()
		for i in range(seconds, 0, -1):
			self.ShowStatusBarRED(_('Restarting Signal K server... ')+str(i))
			time.sleep(1)
		self.ShowStatusBarGREEN(_('Signal K server restarted'))
		

app = wx.App()
MyFrame().Show()
app.MainLoop()
