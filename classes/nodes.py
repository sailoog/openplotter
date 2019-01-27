#!/usr/bin/env python

# This file is part of Openplotter.
# Copyright (C) 2015 by sailoog <https://github.com/sailoog/openplotter>
#						e-sailing <https://github.com/e-sailing/openplotter>
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
import ujson, uuid, os, wx, re
from conf import Conf
from select_key import selectKey

class Nodes:
	def __init__(self):
		conf = Conf()
		self.home = conf.home
		self.flows_file = self.home+'/.signalk/red/flows_openplotter.json'
		self.actions_flow_id = 'openplot.actio'
	
	def get_node_id(self):
		uuid_tmp = str(uuid.uuid4())
		node_id = uuid_tmp[:8]+'.'+uuid_tmp[-6:]
		return node_id

	def get_actions_flow_data(self):		
		actions_flow_template = '''
			[
				{
					"id": "",
					"type": "tab",
					"label": "OpenPlotter Actions",
					"disabled": false,
					"info": ""
				},
				{
					"id": "",
					"type": "comment",
					"z": "",
					"name": "",
					"info": "",
					"x": 310,
					"y": 20,
					"wires": []
				}
			]'''
		actions_flow_data = ujson.loads(actions_flow_template)
		actions_flow_comment = 'Please do not edit this flow. Use the OpenPlotter interface to make changes on it.'
		
		for i in actions_flow_data:
			if i['type'] == 'tab':
				i['id'] = self.actions_flow_id
				i['info'] = actions_flow_comment
			elif i['type'] == 'comment':
				i['z'] = self.actions_flow_id
				i['name'] = actions_flow_comment
				i['id'] = self.get_node_id()
		return actions_flow_data

	def read_flow(self, flow_id):
		tree = []
		triggers_flow_nodes = []
		conditions_flow_nodes = []
		actions_flow_nodes = []
		no_actions_nodes = []

		if os.path.isfile(self.flows_file):
			with open(self.flows_file) as data_file:
				data = ujson.load(data_file)
		else: data = {}
		flow_nodes = []
		for i in data:
			if 'z' in i and i['z'] == flow_id: 
				if 'type' in i and i['type'] != 'comment': flow_nodes.append(i)
			elif 'id' in i and i['id'] == flow_id: pass
			else: no_actions_nodes.append(i)
			
		for node in flow_nodes:
			if "name" in node:
				name = node['name'].split('|')
				if name[0] == 't': triggers_flow_nodes.append(node)
				if name[0] == 'c': conditions_flow_nodes.append(node)
				if name[0] == 'a': actions_flow_nodes.append(node)

		for node in triggers_flow_nodes:
			name = node['name'].split('|')
			exist = False
			for i in tree:
				if i["trigger_node_out_id"] == name[1]: exist = True
			if not exist:
				trigger = {"trigger_node_out_id": name[1],"type": name[2],"conditions": []}
				tree.append(trigger)

		for trigger in tree:
			for node in triggers_flow_nodes:
				if node["id"] == trigger["trigger_node_out_id"]:
					wires = node["wires"][0]
					for wire in wires:
						for node2 in conditions_flow_nodes:
							if wire == node2["id"]:
								name = node2['name'].split('|')
								exist = False
								for i in trigger["conditions"]:
									if i["condition_node_out_id"] == name[1]: exist = True
								if not exist:
									condition = {"condition_node_out_id": name[1],"operator": name[2],"actions": []}
									trigger["conditions"].append(condition)

		for trigger in tree:
			for condition in trigger["conditions"]:
				for node in conditions_flow_nodes:
					if node["id"] == condition["condition_node_out_id"]:
						wires = node["wires"][0]
						for wire in wires:
							for node2 in actions_flow_nodes:
								if wire == node2["id"]:
									name = node2['name'].split('|')
									exist = False
									for i in condition["actions"]:
										if i["action_node_out_id"] == name[1]: exist = True
									if not exist:
										action = {"action_node_out_id": name[1],"type": name[2]}
										condition["actions"].append(action)
		return (tree, triggers_flow_nodes, conditions_flow_nodes, actions_flow_nodes, no_actions_nodes)

class TriggerSK(wx.Dialog):
	def __init__(self, edit):
		self.nodes = Nodes()
		if edit == 0: title = _('Add Signal K trigger')
		else: title = _('Edit Signal K trigger')

		wx.Dialog.__init__(self, None, title = title, size=(430, 300))
		self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))

		self.trigger_type = '0'

		self.subscribtion_node_template = '''
		    {
		        "id": "",
		        "type": "signalk-subscribe",
		        "z": "openplot.actio",
		        "name": "",
		        "mode": "sendChanges",
		        "flatten": true,
		        "context": "vessels.self",
		        "path": "",
		        "source": "",
		        "period": "500",
		        "x": 380,
		        "y": 120,
		        "wires": [
		            [
		                ""
		            ]
		        ]
		    }'''

		self.function_node_template = '''
		    {
		        "id": "",
		        "type": "function",
		        "z": "openplot.actio",
		        "name": "",
		        "func": "",
		        "outputs": 1,
		        "noerr": 0,
		        "x": 380,
		        "y": 120,
		        "wires": [
		            [
		                ""
		            ]
		        ]
		    }'''


		panel = wx.Panel(self)

		skkeylabel = wx.StaticText(panel, label=_('Signal K key'))
		self.skkey = wx.TextCtrl(panel, style=wx.CB_READONLY)
		edit_skkey = wx.Button(panel, label=_('Edit'))
		edit_skkey.Bind(wx.EVT_BUTTON, self.onEditSkkey)

		sourcelabel = wx.StaticText(panel, label=_('Source'))
		self.source = wx.TextCtrl(panel)
		sourcetext = wx.StaticText(panel, label=_('Leave blank to listen to any source.\nAllowed characters: . 0-9 a-z A-Z'))
		

		cancelBtn = wx.Button(panel, wx.ID_CANCEL)
		okBtn = wx.Button(panel, wx.ID_OK)
		okBtn.Bind(wx.EVT_BUTTON, self.OnOk)

		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add((0, 0), 1, wx.ALL, 0)
		hbox.Add(okBtn, 0, wx.RIGHT | wx.LEFT, 10)
		hbox.Add(cancelBtn, 0, wx.RIGHT | wx.LEFT, 10)
		hbox.Add((0, 0), 1, wx.ALL, 0)

		hbox1 = wx.BoxSizer(wx.HORIZONTAL)
		hbox1.Add(self.skkey, 1, wx.RIGHT | wx.LEFT, 10)
		hbox1.Add(edit_skkey, 0, wx.RIGHT | wx.LEFT, 10)

		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.AddSpacer(10)
		vbox.Add(skkeylabel, 0, wx.ALL, 10)
		vbox.Add(hbox1, 0, wx.ALL | wx.EXPAND, 0)
		vbox.AddSpacer(10)
		vbox.Add(sourcelabel, 0, wx.ALL, 10)
		vbox.Add(self.source, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 10)
		vbox.Add(sourcetext, 0, wx.ALL, 10)
		vbox.Add((0, 0), 1, wx.ALL, 0)
		vbox.Add(hbox, 0, wx.ALL | wx.EXPAND, 0)
		vbox.AddSpacer(10)

		panel.SetSizer(vbox)

	def onEditSkkey(self,e):
		oldkey = False
		if self.skkey.GetValue(): oldkey = self.skkey.GetValue()
		dlg = selectKey(oldkey)
		res = dlg.ShowModal()
		if res == wx.OK: self.skkey.SetValue(dlg.selected_key)
		dlg.Destroy()

	def OnOk(self,e):
		skkey = self.skkey.GetValue()
		source = self.source.GetValue()
		if not skkey:
			wx.MessageBox(_('You have to provide a Signal K key.'), 'Info', wx.OK | wx.ICON_INFORMATION)
			return
		elif source and not re.match('^[.0-9a-zA-Z]+$', source):
			wx.MessageBox(_('Failed. Characters not allowed.'), 'Info', wx.OK | wx.ICON_INFORMATION)
			return
		else:
			subscribe_node = ujson.loads(self.subscribtion_node_template)
			subscribe_node['id'] = self.nodes.get_node_id()
			subscribe_node['source'] = source
			if ':' in skkey:
				function_node = ujson.loads(self.function_node_template)
				function_node['id'] = self.nodes.get_node_id()
				subscribe_node['name'] = 't|'+function_node['id']+'|'+self.trigger_type
				path = skkey.split(':')
				subscribe_node['path'] = path[0]
				subscribe_node['wires'] = [[function_node['id']]]
				function_node['name'] = 't|'+function_node['id']+'|'+self.trigger_type
				function = 'msg.payload=msg.payload.'+path[1]+';msg.topic=msg.topic+".'+path[1]+'";return msg;'
				function_node['func'] = function
				self.TriggerNodes = [subscribe_node,function_node]
			else:
				subscribe_node['name'] = 't|'+subscribe_node['id']+'|'+self.trigger_type
				subscribe_node['path'] = skkey
				self.TriggerNodes = [subscribe_node]
		self.EndModal(wx.OK)



class Condition(wx.Dialog):
	def __init__(self, edit,operator):
		self.nodes = Nodes()
		self.available_operators = ['eq', 'neq', 'lt', 'lte', 'gt', 'gte','btwn', 'cont', 'true', 'false', 'null', 'nnull', 'empty', 'nempty']
		self.operator_id = operator
		self.operator = self.available_operators[operator]
		self.condition_node_template = '''
		    {
		        "id": "",
		        "type": "switch",
		        "z": "openplot.actio",
		        "name": "",
		        "property": "payload",
		        "propertyType": "msg",
		        "rules": [],
		        "checkall": "true",
		        "repair": false,
		        "outputs": 1,
		        "x": 380,
		        "y": 120,
		        "wires": [
		            [
		                ""
		            ]
		        ]
		    }'''

		if self.operator == 'true' or self.operator == 'false' or self.operator == 'null' or self.operator == 'nnull' or self.operator == 'empty' or self.operator == 'nempty':
			self.OnOk()
		else:
			if edit == 0: title = _('Add condition')
			else: title = _('Edit condition')

			wx.Dialog.__init__(self, None, title = title, size=(600, 200))
			self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))

			panel = wx.Panel(self)

			available_operators = ['=', '!=', '<', '<=', '>', '>=', _('is between'), _('contains'), _('is true'), ('is false'), _('is null'), _('is not null'), _('is empty'), _('is not empty')]
			operatorlabel = wx.StaticText(panel, label=_('Operator: ')+available_operators[operator])

			type_list = [_('Number'), _('String'), _('Signal K key')]
			self.type_list = ['num', 'str', 'flow']

			type1label = wx.StaticText(panel, label=_('Type'))
			self.type1 = wx.Choice(panel, choices=type_list, style=wx.CB_READONLY)
			self.type1.Bind(wx.EVT_CHOICE, self.on_select_type1)

			value1label = wx.StaticText(panel, label=_('Value'))
			self.value1 = wx.TextCtrl(panel)
			self.edit_value1 = wx.Button(panel, label=_('Edit'))
			self.edit_value1.Bind(wx.EVT_BUTTON, self.onEditSkkey1)

			type2label = wx.StaticText(panel, label=_('Type'))
			self.type2 = wx.Choice(panel, choices=type_list, style=wx.CB_READONLY)
			self.type2.Bind(wx.EVT_CHOICE, self.on_select_type2)

			value2label = wx.StaticText(panel, label=_('Value'))
			self.value2 = wx.TextCtrl(panel)
			self.edit_value2 = wx.Button(panel, label=_('Edit'))
			self.edit_value2.Bind(wx.EVT_BUTTON, self.onEditSkkey2)
			
			okBtn = wx.Button(panel, wx.ID_OK)
			okBtn.Bind(wx.EVT_BUTTON, self.OnOk)
			cancelBtn = wx.Button(panel, wx.ID_CANCEL)

			value1 = wx.BoxSizer(wx.HORIZONTAL)
			value1.Add(type1label, 0, wx.ALL, 5)
			value1.Add(self.type1, 0, wx.ALL, 5)
			value1.Add(value1label, 0, wx.ALL, 5)
			value1.Add(self.value1, 1, wx.ALL, 5)
			value1.Add(self.edit_value1, 0, wx.ALL, 5)

			value2 = wx.BoxSizer(wx.HORIZONTAL)
			value2.Add(type2label, 0, wx.ALL, 5)
			value2.Add(self.type2, 0, wx.ALL, 5)
			value2.Add(value2label, 0, wx.ALL, 5)
			value2.Add(self.value2, 1, wx.ALL, 5)
			value2.Add(self.edit_value2, 0, wx.ALL, 5)

			ok_cancel = wx.BoxSizer(wx.HORIZONTAL)
			ok_cancel.Add((0, 0), 1, wx.ALL, 0)
			ok_cancel.Add(okBtn, 0, wx.RIGHT | wx.LEFT, 10)
			ok_cancel.Add(cancelBtn, 0, wx.RIGHT | wx.LEFT, 10)
			ok_cancel.Add((0, 0), 1, wx.ALL, 0)

			main = wx.BoxSizer(wx.VERTICAL)
			main.Add(operatorlabel, 0, wx.ALL, 5)
			main.Add(value1, 0, wx.ALL | wx.EXPAND, 0)
			main.Add(value2, 0, wx.ALL | wx.EXPAND, 0)
			main.Add((0, 0), 1, wx.ALL, 0)
			main.Add(ok_cancel, 0, wx.ALL | wx.EXPAND, 0)

			panel.SetSizer(main)

			self.edit_value1.Disable()
			self.edit_value2.Disable()
			if self.operator != 'btwn':			
				self.type2.Disable()
				self.value2.Disable()

	def onEditSkkey1(self,e):
		oldkey = False
		if self.value1.GetValue(): oldkey = self.value1.GetValue()
		dlg = selectKey(oldkey)
		res = dlg.ShowModal()
		if res == wx.OK: self.value1.SetValue(dlg.selected_key)
		dlg.Destroy()

	def onEditSkkey2(self,e):
		oldkey = False
		if self.value2.GetValue(): oldkey = self.value2.GetValue()
		dlg = selectKey(oldkey)
		res = dlg.ShowModal()
		if res == wx.OK: self.value2.SetValue(dlg.selected_key)
		dlg.Destroy()

	def on_select_type1(self,e):
		type1 = self.type_list[self.type1.GetSelection()]
		if type1 == 'flow': self.edit_value1.Enable()
		else: self.edit_value1.Disable()

	def on_select_type2(self,e):
		type2 = self.type_list[self.type2.GetSelection()]
		if type2 == 'flow': self.edit_value2.Enable()
		else: self.edit_value2.Disable()

	def OnOk(self,e):
		condition_node = ujson.loads(self.condition_node_template)
		condition_node['id'] = self.nodes.get_node_id()
		self.connector_id = condition_node['id']
		condition_node['name'] = 'c|'+condition_node['id']+'|'+str(self.operator_id)
		if self.operator == 'true' or self.operator == 'false' or self.operator == 'null' or self.operator == 'nnull' or self.operator == 'empty' or self.operator == 'nempty':
			condition_node['rules'].append({"t": self.operator})
		type1 = self.type1.GetSelection()
		value1 = self.value1.GetValue()
		if type1 == -1:
			wx.MessageBox(_('You have to select a value type.'), 'Info', wx.OK | wx.ICON_INFORMATION)
			return
		if not value1:
			wx.MessageBox(_('You have to provide a value.'), 'Info', wx.OK | wx.ICON_INFORMATION)
			return
		if self.operator == 'eq' or self.operator == 'neq' or self.operator == 'lt' or self.operator == 'lte' or self.operator == 'gt' or self.operator == 'gte' or self.operator == 'cont':
			condition_node['rules'].append({"t": self.operator, "v": value1, "vt": self.type_list[type1]})
		if self.operator == 'btwn':
			type2 = self.type2.GetSelection()
			value2 = self.value2.GetValue()
			if type2 == -1:
				wx.MessageBox(_('You have to select a value type.'), 'Info', wx.OK | wx.ICON_INFORMATION)
				return
			if not value2:
				wx.MessageBox(_('You have to provide a value.'), 'Info', wx.OK | wx.ICON_INFORMATION)
				return
			condition_node['rules'].append({"t": self.operator, "v": value1, "vt": self.type_list[type1]})
		self.ConditionNode = condition_node
		self.EndModal(wx.OK)

class ActionPlaySound(wx.Dialog):
	def __init__(self, edit):
		self.nodes = Nodes()