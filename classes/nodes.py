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
from select_key import selectKey

class Nodes:
	def __init__(self,parent,actions_flow_id):
		home = parent.home
		self.flows_file = home+'/.signalk/red/flows_openplotter.json'
		self.actions_flow_id = actions_flow_id
	
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

	def read_flow(self):
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
			if 'z' in i and i['z'] == self.actions_flow_id: 
				if 'type' in i and i['type'] != 'comment': flow_nodes.append(i)
			elif 'id' in i and i['id'] == self.actions_flow_id: pass
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
		        "z": "",
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

class TriggerSK(wx.Dialog):
	def __init__(self,parent,edit):
		self.nodes = parent.nodes
		self.actions_flow_id = parent.actions_flow_id
		self.trigger_type = parent.available_triggers_select.GetSelection()

		if edit == 0: title = _('Add Signal K trigger')
		else: title = _('Edit Signal K trigger')

		wx.Dialog.__init__(self, None, title = title, size=(500, 350))
		self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))

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
		        "period": "",
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
		        "z": "",
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

		periodlabel = wx.StaticText(panel, label=_('Checking period (ms)'))
		self.period = wx.SpinCtrl(panel, min=100, max=100000000, initial=1000)

		vessellabel = wx.StaticText(panel, label=_('Vessel'))
		self.vessel = wx.TextCtrl(panel)

		skkeylabel = wx.StaticText(panel, label=_('Signal K key'))
		self.skkey = wx.TextCtrl(panel)
		edit_skkey = wx.Button(panel, label=_('Edit'))
		edit_skkey.Bind(wx.EVT_BUTTON, self.onEditSkkey)

		sourcelabel = wx.StaticText(panel, label=_('Source'))
		self.source = wx.TextCtrl(panel)
		sourcetext = wx.StaticText(panel, label=_('Leave blank to listen to any source.\nAllowed characters: . 0-9 a-z A-Z'))

		cancelBtn = wx.Button(panel, wx.ID_CANCEL)
		okBtn = wx.Button(panel, wx.ID_OK)
		okBtn.Bind(wx.EVT_BUTTON, self.OnOk)

		period = wx.BoxSizer(wx.HORIZONTAL)
		period.Add(periodlabel, 0, wx.ALL, 5)
		period.Add(self.period, 0, wx.ALL, 5)

		vessel = wx.BoxSizer(wx.HORIZONTAL)
		vessel.Add(vessellabel, 0, wx.ALL, 5)
		vessel.Add(self.vessel, 1, wx.ALL, 5)

		skkey = wx.BoxSizer(wx.HORIZONTAL)
		skkey.Add(skkeylabel, 0, wx.ALL, 5)
		skkey.Add(self.skkey, 1, wx.ALL, 5)

		editskkey = wx.BoxSizer(wx.HORIZONTAL)
		editskkey.Add((0, 0), 1, wx.ALL, 5)
		editskkey.Add(edit_skkey, 0, wx.ALL, 5)

		source = wx.BoxSizer(wx.HORIZONTAL)
		source.Add(sourcelabel, 0, wx.ALL, 5)
		source.Add(self.source, 1, wx.ALL, 5)

		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add((0, 0), 1, wx.ALL, 0)
		hbox.Add(okBtn, 0, wx.ALL, 10)
		hbox.Add(cancelBtn, 0, wx.ALL, 10)
		hbox.Add((0, 0), 1, wx.ALL, 0)

		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.AddSpacer(5)
		vbox.Add(period, 0, wx.ALL, 0)
		vbox.AddSpacer(15)
		vbox.Add(vessel, 0, wx.ALL | wx.EXPAND, 0)
		vbox.Add(skkey, 0, wx.ALL | wx.EXPAND, 0)
		vbox.Add(editskkey, 0, wx.ALL | wx.EXPAND, 0)
		vbox.AddSpacer(15)
		vbox.Add(source, 0, wx.ALL | wx.EXPAND, 0)
		vbox.Add(sourcetext, 0, wx.ALL, 0)
		vbox.Add((0, 0), 1, wx.ALL, 0)
		vbox.Add(hbox, 0, wx.ALL | wx.EXPAND, 0)

		panel.SetSizer(vbox)

	def onEditSkkey(self,e):
		oldkey = False
		if self.skkey.GetValue(): oldkey = self.skkey.GetValue()
		dlg = selectKey(oldkey)
		res = dlg.ShowModal()
		if res == wx.OK: 
			self.skkey.SetValue(dlg.selected_key)
			self.vessel.SetValue(dlg.selected_vessel)
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
			subscribe_node['z'] = self.actions_flow_id
			subscribe_node['context'] = 'vessels.'+self.vessel.GetValue()
			subscribe_node['source'] = source
			subscribe_node['period'] = str(self.period.GetValue())
			if ':' in skkey:
				function_node = ujson.loads(self.function_node_template)
				function_node['id'] = self.nodes.get_node_id()
				function_node['z'] = self.actions_flow_id
				subscribe_node['name'] = 't|'+function_node['id']+'|'+str(self.trigger_type)
				path = skkey.split(':')
				subscribe_node['path'] = path[0]
				subscribe_node['wires'] = [[function_node['id']]]
				function_node['name'] = 't|'+function_node['id']+'|'+str(self.trigger_type)
				function = 'msg.payload=msg.payload.'+path[1]+';msg.topic=msg.topic+".'+path[1]+'";return msg;'
				function_node['func'] = function
				self.TriggerNodes = [subscribe_node,function_node]
			else:
				subscribe_node['name'] = 't|'+subscribe_node['id']+'|'+str(self.trigger_type)
				subscribe_node['path'] = skkey
				self.TriggerNodes = [subscribe_node]
		self.EndModal(wx.OK)

class TriggerGPIO(wx.Dialog):
	def __init__(self,parent,edit):
		self.nodes = parent.nodes
		self.actions_flow_id = parent.actions_flow_id
		self.trigger_type = parent.available_triggers_select.GetSelection()

		if edit == 0: title = _('Add GPIO trigger')
		else: title = _('Edit GPIO trigger')

		wx.Dialog.__init__(self, None, title = title, size=(400, 180))
		self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))

		self.gpio_node_template = '''
		    {
		        "id": "",
		        "type": "rpi-gpio in",
		        "z": "",
		        "name": "",
		        "pin": "",
		        "intype": "",
		        "debounce": "25",
		        "read": false,
		        "x": 380,
		        "y": 120,
		        "wires": [
		            []
		        ]
		    }'''

		panel = wx.Panel(self)

		allowed_pins = ['22','29','31','32','33','35','36','37','38','40']
		in_use_pins =[]
		for i in parent.no_actions_nodes:
			if 'type' in i:
			 if i['type'] == 'rpi-gpio in' or i['type'] == 'rpi-gpio out':
			 	if 'pin' in i: in_use_pins.append(i['pin'])
		for i in parent.triggers_flow_nodes:
			if 'type' in i:
			 if i['type'] == 'rpi-gpio in' or i['type'] == 'rpi-gpio out':
			 	if 'pin' in i: in_use_pins.append(i['pin'])
		for i in parent.actions_flow_nodes:
			if 'type' in i:
			 if i['type'] == 'rpi-gpio in' or i['type'] == 'rpi-gpio out':
			 	if 'pin' in i: in_use_pins.append(i['pin'])
		self.avalaible_gpio = []
		for i in allowed_pins:
			if not i in in_use_pins: self.avalaible_gpio.append(i)
			
		pinlabel = wx.StaticText(panel, label=_('Pin'))
		self.pin = wx.Choice(panel, choices=self.avalaible_gpio, style=wx.CB_READONLY)

		self.resistor_select = [_('none'),_('pullup'),_('pulldown')]
		self.resistor_select2 = ['tri','up','down']

		resitorlabel = wx.StaticText(panel, label=_('Resistor'))
		self.resistor = wx.Choice(panel, choices=self.resistor_select, style=wx.CB_READONLY)

		self.read = wx.CheckBox(panel, label=_('Read initial state of pin on restart?'))

		cancelBtn = wx.Button(panel, wx.ID_CANCEL)
		okBtn = wx.Button(panel, wx.ID_OK)
		okBtn.Bind(wx.EVT_BUTTON, self.OnOk)

		pinh = wx.BoxSizer(wx.HORIZONTAL)
		pinh.Add(pinlabel, 0, wx.ALL, 5)
		pinh.Add(self.pin, 0, wx.ALL, 10)
		pinh.Add(resitorlabel, 0, wx.ALL, 5)
		pinh.Add(self.resistor, 0, wx.ALL, 10)

		okcancel = wx.BoxSizer(wx.HORIZONTAL)
		okcancel.Add((0, 0), 1, wx.ALL, 0)
		okcancel.Add(okBtn, 0, wx.ALL, 10)
		okcancel.Add(cancelBtn, 0, wx.ALL, 10)
		okcancel.Add((0, 0), 1, wx.ALL, 0)

		main = wx.BoxSizer(wx.VERTICAL)
		main.Add(pinh, 0, wx.ALL, 0)
		main.Add(self.read, 0, wx.ALL, 10)
		main.Add((0, 0), 1, wx.ALL, 0)
		main.Add(okcancel, 0, wx.ALL | wx.EXPAND, 0)

		panel.SetSizer(main)

	def OnOk(self,e):
		
		pin = self.pin.GetStringSelection()
		resistor = self.resistor.GetStringSelection()
		read = self.read.GetValue()

		if not pin:
			wx.MessageBox(_('Select a pin.'), 'Info', wx.OK | wx.ICON_INFORMATION)
			return
		elif not resistor:
			wx.MessageBox(_('Select a resistor.'), 'Info', wx.OK | wx.ICON_INFORMATION)
			return
		else:
			gpio_node = ujson.loads(self.gpio_node_template)
			gpio_node['id'] = self.nodes.get_node_id()
			gpio_node['z'] = self.actions_flow_id
			gpio_node['name'] = 't|'+gpio_node['id']+'|'+str(self.trigger_type)
			gpio_node['pin'] = pin
			gpio_node['intype'] = self.resistor_select2[self.resistor.GetSelection()]
			gpio_node['read'] = read
			self.TriggerNodes = [gpio_node]
			self.EndModal(wx.OK)

class Condition(wx.Dialog):
	def __init__(self,parent,edit):
		self.nodes = parent.nodes
		self.actions_flow_id = parent.actions_flow_id
		self.available_operators = ['eq', 'neq', 'lt', 'lte', 'gt', 'gte','btwn', 'cont', 'true', 'false', 'null', 'nnull', 'empty', 'nempty']
		self.operator_id = parent.available_operators_select.GetSelection()
		self.operator = self.available_operators[self.operator_id]
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

			operatorlabel = wx.StaticText(panel, label=_('Operator: ')+parent.available_conditions[self.operator_id])

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
		if res == wx.OK: self.value1.SetValue(dlg.selected_vessel+'.'+dlg.selected_key)
		dlg.Destroy()

	def onEditSkkey2(self,e):
		oldkey = False
		if self.value2.GetValue(): oldkey = self.value2.GetValue()
		dlg = selectKey(oldkey)
		res = dlg.ShowModal()
		if res == wx.OK: self.value2.SetValue(dlg.selected_vessel+'.'+dlg.selected_key)
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
		condition_node['z'] = self.actions_flow_id
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
			condition_node['rules'].append({"t": self.operator, "v": value1, "vt": self.type_list[type1], "v2": value2, "v2t": self.type_list[type2]})
		self.ConditionNode = condition_node
		self.EndModal(wx.OK)

class RepeatOptions():
	def __init__(self):
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
		self.repeat_template = '''
		    {
		        "id": "",
		        "type": "msg-resend",
		        "z": "",
		        "interval": ,
		        "intervalUnit": "",
		        "maximum": ,
		        "bytopic": false,
		        "clone": false,
		        "firstDelayed": false,
		        "addCounters": false,
		        "highRate": false,
		        "outputCountField": "",
		        "outputMaxField": "",
		        "name": "",
		        "x": 380,
		        "y": 120,
		        "wires": [
		            []
		        ]
		    }'''

class ActionPlaySound(wx.Dialog):
	def __init__(self, parent, edit):
		self.currentpath = parent.currentpath
		self.nodes = parent.nodes
		self.actions_flow_id = parent.actions_flow_id
		self.action_id = parent.available_actions_select.GetSelection()
		self.play_sound_node_template = '''
		    {
		        "id": "",
		        "type": "exec",
		        "z": "",
		        "command": "omxplayer",
		        "addpay": false,
		        "append": "",
		        "useSpawn": "false",
		        "timer": "",
		        "oldrc": false,
		        "name": "",
		        "x": 380,
		        "y": 120,
		        "wires": [
		            [],
		            [],
		            []
		        ]
		    }'''

		if edit == 0: title = _('Add sound file')
		else: title = _('Edit sound file')

		wx.Dialog.__init__(self, None, title = title, size=(500, 140))
		self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))

		panel = wx.Panel(self)

		self.path_sound = wx.TextCtrl(panel)
		self.button_select_sound = wx.Button(panel, label=_('File'))
		self.button_select_sound.Bind(wx.EVT_BUTTON, self.on_select_sound)

		okBtn = wx.Button(panel, wx.ID_OK)
		okBtn.Bind(wx.EVT_BUTTON, self.OnOk)
		cancelBtn = wx.Button(panel, wx.ID_CANCEL)

		file = wx.BoxSizer(wx.HORIZONTAL)
		file.Add(self.path_sound, 1, wx.ALL, 5)
		file.Add(self.button_select_sound, 0, wx.ALL, 5)

		ok_cancel = wx.BoxSizer(wx.HORIZONTAL)
		ok_cancel.Add((0, 0), 1, wx.ALL, 0)
		ok_cancel.Add(okBtn, 0, wx.RIGHT | wx.LEFT, 10)
		ok_cancel.Add(cancelBtn, 0, wx.RIGHT | wx.LEFT, 10)
		ok_cancel.Add((0, 0), 1, wx.ALL, 0)

		main = wx.BoxSizer(wx.VERTICAL)
		main.Add(file, 1, wx.ALL | wx.EXPAND, 0)
		main.Add((0, 0), 1, wx.ALL, 0)
		main.Add(ok_cancel, 0, wx.ALL | wx.EXPAND, 10)

		panel.SetSizer(main)

	def on_select_sound(self, e):
		dlg = wx.FileDialog(self, message=_('Choose a file'), defaultDir=self.currentpath + '/sounds', defaultFile='',
							wildcard=_('Audio files').decode('utf8') + ' (*.mp3)|*.mp3|' + _('All files').decode('utf8') + ' (*.*)|*.*',
							style=wx.OPEN | wx.CHANGE_DIR)
		if dlg.ShowModal() == wx.ID_OK:
			file_path = dlg.GetPath()
			self.path_sound.SetValue(file_path)
		dlg.Destroy()

	def OnOk(self,e):
		file = self.path_sound.GetValue()
		if not file:
			wx.MessageBox(_('You have to select a sound file.'), 'Info', wx.OK | wx.ICON_INFORMATION)
			return
		action_node = ujson.loads(self.play_sound_node_template)
		action_node['id'] = self.nodes.get_node_id()
		action_node['z'] = self.actions_flow_id
		action_node['name'] = 'a|'+action_node['id']+'|'+str(self.action_id)
		action_node['append'] = file
		self.connector_id = action_node['id']
		self.ActionNodes = [action_node]
		self.EndModal(wx.OK)