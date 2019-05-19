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
import ujson, uuid, os, wx, re, requests, time, webbrowser
from select_key import selectKey
from datetime import datetime

class Nodes:
	def __init__(self,parent,actions_flow_id):
		home = parent.home
		self.flows_file = home+'/.signalk/red/flows_openplotter.json'
		self.actions_flow_id = actions_flow_id
		self.allowed_pins = ['22','29','31','32','33','35','36','37','38','40']
		self.enable_node_template = '''
		    {
		        "id": "",
		        "type": "function",
		        "z": "",
		        "name": "",
		        "func": "return msg;",
		        "outputs": 1,
		        "noerr": 0,
		        "x": 380,
		        "y": 120,
		        "wires": [[]]
		    }'''
	
	def get_node_id(self, subid=0):
		uuid_tmp = str(uuid.uuid4())
		if subid: node_id = subid+'.'+uuid_tmp[-6:]
		else: node_id = uuid_tmp[:8]+'.'+uuid_tmp[-6:]
		return node_id

	def get_actions_flow_data(self):
		self.commentnodeid = 'openplot.comme'		
		actions_flow_template = '''
			[
				{
					"id": "",
					"type": "tab",
					"label": "OpenPlotter Filter",
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
				i['id'] = self.commentnodeid
		return actions_flow_data

	def get_flow(self):
		tree = []
		triggers_flow_nodes = []
		conditions_flow_nodes = []
		actions_flow_nodes = []
		others_flow_nodes = []
		no_actions_nodes = []
		data = self.read_flow()
		flow_nodes = []
		'''
		triggers: t|node_out_id|type
		conditions: c|node_out_id|operator
		actions: a|node_out_id|type
		[
			{
				"trigger_node_out_id": "xxx",
				"type": "0",
				"conditions": [
					{
						"condition_node_out_id": "xxx",
						"operator": "0",
						"actions": [
							{
								"action_node_out_id": "xxx",
								"type": "0"
							}
						]
					}
				]
			}
		]
		'''
		for i in data:
			if 'z' in i and i['z'] == self.actions_flow_id: 
				if 'type' in i and i['type'] != 'comment': flow_nodes.append(i)
			elif 'id' in i and i['id'] == self.actions_flow_id: pass
			else: no_actions_nodes.append(i)
			
		for node in flow_nodes:
			name = ''
			if 'dname' in node and node['dname']: name = node['dname'].split('|')
			elif 'name' in node and node['name']: name = node['name'].split('|')
			elif 'openplot.' in node['id']: name = ['o']
			elif not 'name' in node:
				subid0 = node['id'].split('.')
				subid = subid0[0]
				for i in flow_nodes:
					subidi = i['id'].split('.')
					if 'name' in i and subid == subidi[0]: name = i['name'].split('|')
			if name:
				if name[0] == 't': triggers_flow_nodes.append(node)
				if name[0] == 'c': conditions_flow_nodes.append(node)
				if name[0] == 'a': actions_flow_nodes.append(node)
				if name[0] == 'o': others_flow_nodes.append(node)

		for node in triggers_flow_nodes:
			if "name" in node: 
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
								if 'name' in node2: 
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
									if 'name' in node2: 
										name = node2['name'].split('|')
										exist = False
										for i in condition["actions"]:
											if i["action_node_out_id"] == name[1]: exist = True
										if not exist:
											action = {"action_node_out_id": name[1],"type": name[2]}
											condition["actions"].append(action)

		return (tree, triggers_flow_nodes, conditions_flow_nodes, actions_flow_nodes, no_actions_nodes, others_flow_nodes)
	
	def read_flow(self):
		try:
			with open(self.flows_file) as data_file:
				data = ujson.load(data_file)
			return data
		except:
			print "ERROR reading flows file"
			return []
			
	def write_flow(self, all_flows):
		actions_flow_data = self.get_actions_flow_data()
		tab = False
		comment = False
		for i in all_flows:
			if i['id'] == self.actions_flow_id: tab = True
			if i['id'] == self.commentnodeid: comment = True
		if not tab: all_flows.append(actions_flow_data[0])
		if not comment: all_flows.append(actions_flow_data[1])

		try:
			data = ujson.dumps(all_flows, indent=4)
			with open(self.flows_file, "w") as outfile:
				outfile.write(data)
		except: print "ERROR writing flows file"

	def edit_flow(self, add, remove):
		save = False
		data = self.read_flow()
		if add:
			for i in add:
				exist = False
				for ii in data: 
					if ii['id'] == i['id']:
						ii = i
						exist = True
						save = True
				if not exist: 
					data.append(i)
					save = True
		if remove:
			data2 = []
			for i in data:
				if i['id'] in remove: save = True
				else: data2.append(i)
		else: data2 = data
		if save: self.write_flow(data2)
	
	def get_subscription(self, value):
		self.subscribtion_node_template = '''
		    {
		        "id": "",
		        "type": "signalk-subscribe",
		        "z": "",
		        "name": "",
		        "mode": "sendChanges",
		        "flatten": true,
		        "context": "",
		        "path": "",
		        "source": "",
		        "period": "1000",
		        "x": 380,
		        "y": 120,
		        "wires": [[]]
		    }'''
		self.function_node_template = '''
		    {
		        "id": "",
		        "type": "function",
		        "z": "",
		        "name": "",
		        "func": "",
		        "outputs": 1,
		        "noerr": 0,
		        "x": 380,
		        "y": 120,
		        "wires": [[]]
		    }'''

		value_list = value.split('.')
		vessel = value_list[0]
		value_list.pop(0)
		skkey = '.'.join(value_list)

		subscribe_node = ujson.loads(self.subscribtion_node_template)
		subscribe_node['id'] = self.get_node_id()
		subscribe_node['z'] = self.actions_flow_id
		subscribe_node['context'] = 'vessels.'+vessel
		function_node = ujson.loads(self.function_node_template)
		function_node['id'] = self.get_node_id()
		function_node['z'] = self.actions_flow_id
		subscribe_node['wires'] = [[function_node['id']]]
		subscribe_node['name'] = value
		function_node['name'] = value
		if ':' in skkey:
			path = skkey.split(':')
			subscribe_node['path'] = path[0]
			function = 'msg.payload=msg.payload.'+path[1]+';msg.topic="'+vessel+'.'+skkey+'";flow.set(msg.topic, msg.payload);'
			function_node['func'] = function
		else:
			subscribe_node['path'] = skkey
			function = 'msg.topic="'+vessel+'.'+skkey+'";flow.set(msg.topic, msg.payload);'
			function_node['func'] = function

		return [subscribe_node,function_node]

# triggers
class TriggerFilterSK(wx.Dialog):
	def __init__(self,parent,edit,trigger):
		self.nodes = parent.nodes
		help_bmp = parent.help_bmp
		self.currentpath = parent.currentpath
		self.actions_flow_id = parent.actions_flow_id
		self.trigger_type = trigger

		if edit == 0: title = _('Add Signal K trigger')
		else: title = _('Edit Signal K trigger')

		wx.Dialog.__init__(self, None, title = title, size=(400, 350))
		self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))

		self.subscribtion_node_template = '''
			{
				"id": "",
				"type": "signalk-input-handler",
				"z": "",
				"name": "",
				"context": "",
				"path": "",
				"source": "",
				"x": 380,
				"y": 120,
				"wires": [[]]
		    }'''

		panel = wx.Panel(self)

		vessellabel = wx.StaticText(panel, label=_('Vessel'))
		self.vessel = wx.TextCtrl(panel, size=(290,-1))

		skkeylabel = wx.StaticText(panel, label=_('Signal K key'))
		self.skkey = wx.TextCtrl(panel, size=(290,-1))
		if edit == 0: edit_skkey = wx.Button(panel, label=_('Add'))
		else: edit_skkey = wx.Button(panel, label=_('Edit'))
		edit_skkey.Bind(wx.EVT_BUTTON, self.onEditSkkey)

		sourcelabel = wx.StaticText(panel, label=_('Source'))
		self.source = wx.TextCtrl(panel, size=(290,-1))
		sourcetext = wx.StaticText(panel, label=_('Leave blank to listen to any source.\nAllowed characters: . 0-9 a-z A-Z'), size=(300,-1))

		hline1 = wx.StaticLine(panel)
		help_button = wx.BitmapButton(panel, bitmap=help_bmp, size=(help_bmp.GetWidth()+40, help_bmp.GetHeight()+10))
		help_button.Bind(wx.EVT_BUTTON, self.on_help)
		cancelBtn = wx.Button(panel, wx.ID_CANCEL)
		okBtn = wx.Button(panel, wx.ID_OK)
		okBtn.Bind(wx.EVT_BUTTON, self.OnOk)

		vessel = wx.BoxSizer(wx.HORIZONTAL)
		vessel.Add(vessellabel, 1, wx.RIGHT | wx.ALL | wx.EXPAND, 6)
		vessel.Add(self.vessel, 0, wx.RIGHT, 10)

		skkey = wx.BoxSizer(wx.HORIZONTAL)
		skkey.Add(skkeylabel, 1, wx.RIGHT | wx.ALL | wx.EXPAND, 6)
		skkey.Add(self.skkey, 0, wx.RIGHT, 10)

		editskkey = wx.BoxSizer(wx.HORIZONTAL)
		editskkey.Add((0, 0), 1, wx.ALL, 6)
		editskkey.Add(edit_skkey, 0, wx.RIGHT, 10)

		source = wx.BoxSizer(wx.HORIZONTAL)
		source.Add(sourcelabel, 1, wx.RIGHT | wx.ALL | wx.EXPAND, 6)
		source.Add(self.source, 0, wx.RIGHT, 10)

		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(help_button, 0, wx.ALL, 10)
		hbox.Add((0, 0), 1, wx.ALL, 0)
		hbox.Add(cancelBtn, 0, wx.ALL, 10)
		hbox.Add(okBtn, 0, wx.ALL, 10)

		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.AddSpacer(10)
		vbox.Add(vessel, 0, wx.LEFT | wx.EXPAND, 5)
		vbox.Add(skkey, 0, wx.LEFT | wx.EXPAND, 5)
		vbox.AddSpacer(3)
		vbox.Add(editskkey, 0, wx.ALL | wx.EXPAND, 0)
		vbox.AddSpacer(10)
		vbox.Add(source, 0, wx.LEFT | wx.EXPAND, 5)
		vbox.Add(sourcetext, 0, wx.LEFT, 10)
		vbox.Add((0, 0), 1, wx.ALL, 0)
		vbox.Add(hline1, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
		vbox.Add(hbox, 0, wx.ALL | wx.EXPAND, 0)

		panel.SetSizer(vbox)

		if edit:
			subkey = ''
			for i in edit:
				if i['type'] == 'signalk-input-handler':
					vessel = i['context'].replace('vessels.','')
					key = i['path']
					source = i['source']
				elif i['type'] == 'function' and i['func'] != 'return msg;':
					subkey = i['func'].split(';')
					subkey = subkey[0].split('.')
					subkey = ':'+subkey[3]
			self.vessel.SetValue(vessel)
			self.skkey.SetValue(key+subkey)
			self.source.SetValue(source)
		else:
			self.vessel.SetValue('self')


	def on_help(self, e):
		url = self.currentpath+"/docs/html/actions/triggers.html"
		webbrowser.open(url, new=2)

	def onEditSkkey(self,e):
		oldkey = False
		if self.skkey.GetValue(): oldkey = self.skkey.GetValue()
		dlg = selectKey(oldkey,1)
		res = dlg.ShowModal()
		if res == wx.OK: 
			self.skkey.SetValue(dlg.selected_key)
			self.vessel.SetValue(dlg.selected_vessel)
		dlg.Destroy()

	def OnOk(self,e):
		skkey = self.skkey.GetValue()
		vessel = self.vessel.GetValue()
		source = self.source.GetValue()
		if not skkey:
			wx.MessageBox(_('You have to provide a Signal K key.'), 'Info', wx.OK | wx.ICON_INFORMATION)
			return
		elif not vessel:
			wx.MessageBox(_('You have to provide a vessel ID.'), 'Info', wx.OK | wx.ICON_INFORMATION)
			return
		elif source and not re.match('^[.0-9a-zA-Z]+$', source):
			wx.MessageBox(_('Failed. Characters not allowed.'), 'Info', wx.OK | wx.ICON_INFORMATION)
			return
		self.TriggerNodes = []
		sk_input_node = ujson.loads(self.subscribtion_node_template)
		sk_input_node['id'] = self.nodes.get_node_id()
		sk_input_node['z'] = self.actions_flow_id
		sk_input_node['name'] = 't|'+sk_input_node['id']+'|'+str(self.trigger_type)
		sk_input_node['path'] = skkey
		sk_input_node['wires'] = [[]]
		sk_input_node['context'] = 'vessels.'+self.vessel.GetValue()
		sk_input_node['source'] = source
		self.TriggerNodes.append(sk_input_node)
		self.EndModal(wx.OK)

# conditions
class Condition(wx.Dialog):
	def __init__(self,parent,edit):
		self.nodes = parent.nodes
		help_bmp = parent.help_bmp
		self.currentpath = parent.currentpath
		self.actions_flow_id = parent.actions_flow_id
		self.available_operators = parent.available_operators
		self.available_conditions = parent.available_conditions
		if edit:
			self.operator = edit['t']
		else:
			self.operator = self.available_operators[0]
		self.condition_node_template = '''
		    {
		        "id": "",
		        "type": "switch",
		        "z": "",
		        "name": "",
		        "property": "payload",
		        "propertyType": "msg",
		        "rules": [],
		        "checkall": "true",
		        "repair": false,
		        "outputs": 1,
		        "x": 380,
		        "y": 120,
		        "wires": [[]]
		    }'''

		if edit == 0: title = _('Add condition')
		else: title = _('Edit condition')

		wx.Dialog.__init__(self, None, title = title, size=(600, 270))
		self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))

		panel = wx.Panel(self)

		operatorlabel = wx.StaticText(panel, label=_('Operator'))
		self.available_operators_select = wx.Choice(panel, choices=self.available_conditions, style=wx.CB_READONLY)
		self.available_operators_select.Bind(wx.EVT_CHOICE, self.on_available_operators_select)

		type_list = [_('Number'), _('String'), _('Signal K key'), _('Date and time')]
		self.type_list = ['num', 'str', 'flow', 'num']

		type1label = wx.StaticText(panel, label=_('Type'))
		self.type1 = wx.Choice(panel, choices=type_list, style=wx.CB_READONLY)
		self.type1.Bind(wx.EVT_CHOICE, self.on_select_type1)

		value1label = wx.StaticText(panel, label=_('Value'))
		self.value1 = wx.TextCtrl(panel)
		self.edit_value1 = wx.Button(panel, label=_('Add'))
		self.edit_value1.Bind(wx.EVT_BUTTON, self.onEditSkkey1)

		value2label = wx.StaticText(panel, label=_('Value'))
		self.value2 = wx.TextCtrl(panel)
		self.edit_value2 = wx.Button(panel, label=_('Add'))
		self.edit_value2.Bind(wx.EVT_BUTTON, self.onEditSkkey2)
		
		hline1 = wx.StaticLine(panel)
		help_button = wx.BitmapButton(panel, bitmap=help_bmp, size=(help_bmp.GetWidth()+40, help_bmp.GetHeight()+10))
		help_button.Bind(wx.EVT_BUTTON, self.on_help)
		cancelBtn = wx.Button(panel, wx.ID_CANCEL)
		okBtn = wx.Button(panel, wx.ID_OK)
		okBtn.Bind(wx.EVT_BUTTON, self.OnOk)

		typeoperator = wx.BoxSizer(wx.HORIZONTAL)
		typeoperator.Add(operatorlabel, 0, wx.TOP | wx.BOTTOM, 6)
		typeoperator.Add(self.available_operators_select, 0, wx.LEFT, 5)

		typevalue = wx.BoxSizer(wx.HORIZONTAL)
		typevalue.Add(type1label, 0, wx.TOP | wx.BOTTOM, 6)
		typevalue.Add(self.type1, 0, wx.LEFT, 5)

		value1 = wx.BoxSizer(wx.HORIZONTAL)
		value1.Add(value1label, 0, wx.TOP | wx.BOTTOM, 9)
		value1.AddSpacer(5)
		value1.Add(self.value1, 1, wx.TOP | wx.BOTTOM, 3)
		value1.Add(self.edit_value1, 0, wx.LEFT, 10)

		value2 = wx.BoxSizer(wx.HORIZONTAL)
		value2.Add(value2label, 0, wx.TOP | wx.BOTTOM, 9)
		value2.AddSpacer(5)
		value2.Add(self.value2, 1, wx.TOP | wx.BOTTOM, 3)
		value2.Add(self.edit_value2, 0, wx.LEFT, 10)

		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(help_button, 0, wx.ALL, 10)
		hbox.AddStretchSpacer(1)
		hbox.Add(cancelBtn, 0, wx.ALL, 10)
		hbox.Add(okBtn, 0, wx.ALL, 10)

		main = wx.BoxSizer(wx.VERTICAL)
		main.Add(typeoperator, 0, wx.ALL, 10)
		main.Add(typevalue, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
		main.Add(value1, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)
		main.Add(value2, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)
		main.AddStretchSpacer(1)
		main.Add(hline1, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
		main.Add(hbox, 0, wx.EXPAND, 0)

		panel.SetSizer(main)

		if self.operator == 'true' or self.operator == 'false' or self.operator == 'null' or self.operator == 'nnull' or self.operator == 'empty' or self.operator == 'nempty':
			self.type1.Disable()
			self.value1.Disable()
			self.value2.Disable()
		elif self.operator != 'btwn':			
			self.value2.Disable()
			
		if edit:
			operator_value = self.available_operators.index(edit['t'])
			type_list_value = self.type_list.index(edit['vt'])
			self.available_operators_select.SetSelection(operator_value)
			self.type1.SetSelection(type_list_value)

			if type_list_value == 0:	#num is for date and num
				if '-' in edit['v']:
					self.type1.SetSelection(3)

			self.value1.SetValue(edit['v'])
			if operator_value == 6:
				self.value2.SetValue(edit['v2'])				

		self.Set_SK_add()

	def on_help(self, e):
		url = self.currentpath+"/docs/html/xxx/xxx.html"
		webbrowser.open(url, new=2)

	def onEditSkkey1(self,e):
		oldkey = False
		if self.value1.GetValue(): oldkey = self.value1.GetValue()
		dlg = selectKey(oldkey,1)
		res = dlg.ShowModal()
		if res == wx.OK: self.value1.SetValue(dlg.selected_vessel+'.'+dlg.selected_key)
		dlg.Destroy()

	def onEditSkkey2(self,e):
		oldkey = False
		if self.value2.GetValue(): oldkey = self.value2.GetValue()
		dlg = selectKey(oldkey,1)
		res = dlg.ShowModal()
		if res == wx.OK: self.value2.SetValue(dlg.selected_vessel+'.'+dlg.selected_key)
		dlg.Destroy()

	def on_available_operators_select(self,e):
		self.operator = self.available_operators[self.available_operators_select.GetSelection()]
		
		self.type1.Enable()
		self.value1.Enable()
		self.value2.Enable()
		if self.operator in ['true','false','null','nnull','empty','nempty']:
			self.type1.Disable()
			self.value1.Disable()
			self.value2.Disable()
		elif self.operator != 'btwn':			
			self.value2.Disable()
		
		self.Set_SK_add()

	def Set_SK_add(self):
		if self.type1.GetSelection() == 2: 
			self.edit_value1.Enable()
			if self.operator == 'btwn': self.edit_value2.Enable()
		else: 
			self.edit_value1.Disable()
			self.edit_value2.Disable()

	def on_select_type1(self,e):
		self.Set_SK_add()
		if self.type1.GetSelection() == 3:
			now = datetime.now()
			self.value1.SetValue(now.strftime("%Y-%m-%d %H:%M:%S"))
			if self.operator == 'btwn': self.value2.SetValue(now.strftime("%Y-%m-%d %H:%M:%S"))
		else: 
			self.value1.SetValue('')
			self.value2.SetValue('')

	def OnOk(self,e):
		condition_node = ujson.loads(self.condition_node_template)
		condition_node['id'] = self.nodes.get_node_id()
		condition_node['z'] = self.actions_flow_id
		self.connector_id = condition_node['id']
		condition_node['name'] = 'c|'+condition_node['id']+'|'+str(self.available_operators.index(self.operator))
		if self.operator == 'true' or self.operator == 'false' or self.operator == 'null' or self.operator == 'nnull' or self.operator == 'empty' or self.operator == 'nempty':
			condition_node['rules'].append({"t": self.operator})
		else:
			type1 = self.type1.GetSelection()
			value1 = self.value1.GetValue()
			if type1 == -1:
				wx.MessageBox(_('You have to select a value type.'), 'Info', wx.OK | wx.ICON_INFORMATION)
				return
			if not value1:
				wx.MessageBox(_('You have to provide a value.'), 'Info', wx.OK | wx.ICON_INFORMATION)
				return
			if type1 == 3:
				try:
					timestamp = time.mktime(time.strptime(value1, '%Y-%m-%d %H:%M:%S'))
					value1 = str(timestamp*1000)
				except:
					wx.MessageBox(_('Use this date and time format: YYYY-MM-DD HH:MM:SS'), 'Info', wx.OK | wx.ICON_INFORMATION)
					return
			if self.operator == 'eq' or self.operator == 'neq' or self.operator == 'lt' or self.operator == 'lte' or self.operator == 'gt' or self.operator == 'gte' or self.operator == 'cont':
				condition_node['rules'].append({"t": self.operator, "v": value1, "vt": self.type_list[type1]})
			if self.operator == 'btwn':
				value2 = self.value2.GetValue()
				if not value2:
					wx.MessageBox(_('You have to provide 2 values.'), 'Info', wx.OK | wx.ICON_INFORMATION)
					return
				if type1 == 3:
					try: 
						timestamp = time.mktime(time.strptime(value2, '%Y-%m-%d %H:%M:%S'))
						value2 = str(timestamp*1000)
					except:
						wx.MessageBox(_('Use this date and time format: YYYY-MM-DD HH:MM:SS'), 'Info', wx.OK | wx.ICON_INFORMATION)
						return
				condition_node['rules'].append({"t": self.operator, "v": value1, "vt": self.type_list[type1], "v2": value2, "v2t": self.type_list[type1]})
		self.ConditionNode = condition_node
		self.EndModal(wx.OK)

class RepeatOptions():
	def __init__(self):
		self.rateUnit = [_('Seconds'),_('Minutes'),_('Hours'),_('Days')]
		self.rateUnit2 = ['second','minute','hour','day']
		self.rate_limit_template = '''
		    {
		        "id": "",
		        "type": "delay",
		        "z": "",
		        "name": "",
		        "pauseType": "rate",
		        "timeout": "5",
		        "timeoutUnits": "seconds",
		        "rate": "",
		        "nbRateUnits": "",
		        "rateUnits": "",
		        "randomFirst": "1",
		        "randomLast": "5",
		        "randomUnits": "seconds",
		        "drop": true,
		        "x": 380,
		        "y": 120,
		        "wires": [
		            [
		                ""
		            ]
		        ]
		    }'''
		self.intervalUnit = [_('MilliSeconds'),_('Seconds'),_('Minutes'),_('Hours')]
		self.intervalUnit2 = ['msecs','secs','mins','hours']
		self.repeat_template = '''
		    {
		        "id": "",
		        "type": "msg-resend",
		        "z": "",
		        "interval": "",
		        "intervalUnit": "",
		        "maximum": "",
		        "bytopic": false,
		        "clone": false,
		        "firstDelayed": false,
		        "addCounters": false,
		        "highRate": true,
		        "outputCountField": "",
		        "outputMaxField": "",
		        "name": "",
		        "x": 380,
		        "y": 120,
		        "wires": [
		            []
		        ]
		    }'''

# actions
class ActionEndFilterSignalk(wx.Dialog):
	def __init__(self, parent, edit):
		self.credentials = ''
		self.nodes = parent.nodes
		help_bmp = parent.help_bmp
		self.currentpath = parent.currentpath
		self.actions_flow_id = parent.actions_flow_id
		self.action_id = parent.available_actions_select.GetSelection()
		self.sk_node_template = '''
		    {			
		        "id": "",
				"type": "signalk-input-handler-next",
		        "z": "",
		        "name": "",
		        "x": 380,
		        "y": 120,
		        "wires": []
		    }'''

		if edit == 0: title = _('Set Signal K key')
		else: title = _('Edit Signal K key')

		wx.Dialog.__init__(self, None, title = title, size=(350, 100))
		self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))

		panel = wx.Panel(self)

		okBtn = wx.Button(panel, wx.ID_OK)
		okBtn.Bind(wx.EVT_BUTTON, self.OnOk)

		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.AddStretchSpacer(1)
		hbox.Add(okBtn, 0, wx.ALL, 10)

		main = wx.BoxSizer(wx.VERTICAL)
		main.AddStretchSpacer(1)
		main.Add(hbox, 0, wx.ALL | wx.EXPAND, 0)

		panel.SetSizer(main)

	def OnOk(self,e):
		self.ActionNodes = []
		sk_node = ujson.loads(self.sk_node_template)
		sk_node['id'] = self.nodes.get_node_id()
		sk_node['z'] = self.actions_flow_id
		sk_node['name'] = 'a|'+sk_node['id']+'|'+str(self.action_id)
		self.ActionNodes.append(sk_node)
		self.connector_id = sk_node['id']
		self.EndModal(wx.OK)
