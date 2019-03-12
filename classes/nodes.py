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
import ujson, uuid, os, wx, re, requests, time
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
		vbox.AddSpacer(10)
		vbox.Add(period, 0, wx.LEFT, 5)
		vbox.AddSpacer(10)
		vbox.Add(vessel, 0, wx.LEFT | wx.EXPAND, 5)
		vbox.Add(skkey, 0, wx.LEFT | wx.EXPAND, 5)
		vbox.Add(editskkey, 0, wx.ALL | wx.EXPAND, 0)
		vbox.AddSpacer(10)
		vbox.Add(source, 0, wx.LEFT | wx.EXPAND, 5)
		vbox.Add(sourcetext, 0, wx.LEFT, 10)
		vbox.Add((0, 0), 1, wx.ALL, 0)
		vbox.Add(hbox, 0, wx.ALL | wx.EXPAND, 0)

		panel.SetSizer(vbox)

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
		enable_node = ujson.loads(self.nodes.enable_node_template)
		enable_node['id'] = self.nodes.get_node_id()
		enable_node['z'] = self.actions_flow_id
		enable_node['func'] = 'return msg;'
		enable_node['name'] = 't|'+enable_node['id']+'|'+str(self.trigger_type)
		self.TriggerNodes.append(enable_node)
		if ':' in skkey:
			function_node = ujson.loads(self.function_node_template)
			function_node['id'] = self.nodes.get_node_id()
			function_node['z'] = self.actions_flow_id
			function_node['name'] = enable_node['name']
			path = skkey.split(':')
			function = 'msg.payload=msg.payload.'+path[1]+';msg.topic=msg.topic+".'+path[1]+'";return msg;'
			function_node['func'] = function
			function_node['wires'] = [[enable_node['id']]]
			self.TriggerNodes.append(function_node)
		subscribe_node = ujson.loads(self.subscribtion_node_template)
		subscribe_node['id'] = self.nodes.get_node_id()
		subscribe_node['z'] = self.actions_flow_id
		subscribe_node['name'] = enable_node['name']
		if ':' in skkey:
			path = skkey.split(':')
			subscribe_node['path'] = path[0]
			subscribe_node['wires'] = [[function_node['id']]]
		else:
			subscribe_node['path'] = skkey
			subscribe_node['wires'] = [[enable_node['id']]]
		subscribe_node['context'] = 'vessels.'+self.vessel.GetValue()
		subscribe_node['source'] = source
		subscribe_node['period'] = str(self.period.GetValue())
		self.TriggerNodes.append(subscribe_node)
		self.EndModal(wx.OK)

class TriggerGeofence(wx.Dialog):
	def __init__(self,parent,edit):
		self.nodes = parent.nodes
		self.actions_flow_id = parent.actions_flow_id
		self.trigger_type = parent.available_triggers_select.GetSelection()

		SK_ = parent.SK_settings
		self.port = SK_.aktport
		self.http = SK_.http

		if edit == 0: title = _('Add Geofence trigger')
		else: title = _('Edit Geofence trigger')

		wx.Dialog.__init__(self, None, title = title, size=(500, 300))
		self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))

		self.geofence_node_template = '''
		    {
		        "id": "",
		        "type": "signalk-geofence",
		        "z": "",
		        "name": "",
		        "mode": "sendAll",
		        "context": "",
		        "period": 10000,
		        "myposition": false,
		        "lat": 0,
		        "lon": 0,
		        "distance": 10,
		        "x": 380,
		        "y": 120,
		        "wires": [[],[],[]]
		    }'''

		panel = wx.Panel(self)

		periodlabel = wx.StaticText(panel, label=_('Checking period (ms)'))
		self.period = wx.SpinCtrl(panel, min=100, max=100000000, initial=10000)

		self.list_vessels = []
		vessellabel = wx.StaticText(panel, label=_('Vessel'))
		self.vessel = wx.ComboBox(panel, choices=self.list_vessels)
		self.refreshBtn = wx.Button(panel, label=_('Refresh'))
		self.refreshBtn.Bind(wx.EVT_BUTTON, self.OnRefreshBtn)

		distancelabel = wx.StaticText(panel, label=_('Distance (m)'))
		self.distance = wx.SpinCtrl(panel, min=1, max=100000, initial=10)

		self.mypos = wx.CheckBox(panel, label=_('Use My Position'))
		self.mypos.Bind(wx.EVT_CHECKBOX, self.on_mypos)

		latlabel = wx.StaticText(panel, label=_('Latitude'))
		self.lat = wx.SpinCtrlDouble(panel, min=-90, max=90, initial=0)
		self.lat.SetDigits(10)

		lonlabel = wx.StaticText(panel, label=_('Longitude'))
		self.lon = wx.SpinCtrlDouble(panel, min=-180, max=180, initial=0)
		self.lon.SetDigits(10)

		cancelBtn = wx.Button(panel, wx.ID_CANCEL)
		okBtn = wx.Button(panel, wx.ID_OK)
		okBtn.Bind(wx.EVT_BUTTON, self.OnOk)

		period = wx.BoxSizer(wx.HORIZONTAL)
		period.Add(periodlabel, 0, wx.ALL, 5)
		period.Add(self.period, 0, wx.ALL, 5)

		vessel = wx.BoxSizer(wx.HORIZONTAL)
		vessel.Add(vessellabel, 0, wx.ALL, 5)
		vessel.Add(self.vessel, 1, wx.ALL, 5)
		vessel.Add(self.refreshBtn, 0, wx.ALL, 5)

		distance = wx.BoxSizer(wx.HORIZONTAL)
		distance.Add(distancelabel, 0, wx.ALL, 5)
		distance.Add(self.distance, 0, wx.ALL, 5)

		latlon = wx.BoxSizer(wx.HORIZONTAL)
		latlon.Add(latlabel, 0, wx.ALL, 5)
		latlon.Add(self.lat, 1, wx.ALL, 5)
		latlon.Add(lonlabel, 0, wx.ALL, 5)
		latlon.Add(self.lon, 1, wx.ALL, 5)

		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add((0, 0), 1, wx.ALL, 0)
		hbox.Add(okBtn, 0, wx.ALL, 10)
		hbox.Add(cancelBtn, 0, wx.ALL, 10)
		hbox.Add((0, 0), 1, wx.ALL, 0)

		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.AddSpacer(10)
		vbox.Add(period, 0, wx.LEFT, 5)
		vbox.Add(vessel, 0, wx.LEFT | wx.EXPAND, 5)
		vbox.AddSpacer(5)
		vbox.Add(self.mypos, 0, wx.LEFT, 10)
		vbox.AddSpacer(5)
		vbox.Add(latlon, 0, wx.LEFT | wx.EXPAND, 5)
		vbox.Add(distance, 0, wx.LEFT, 5)
		vbox.Add((0, 0), 1, wx.ALL, 0)
		vbox.Add(hbox, 0, wx.ALL | wx.EXPAND, 0)

		panel.SetSizer(vbox)

		self.OnRefreshBtn(0)

	def OnRefreshBtn(self,e):
		self.list_vessels = ['self']
		try:
			response = requests.get(self.http+'localhost:'+str(self.port)+'/signalk/v1/api/vessels')
			data = response.json()
		except:data = None
		if data:
			for i in data:
				self.list_vessels.append(i)
		self.vessel.Clear()
		self.vessel.AppendItems(self.list_vessels)
		self.vessel.SetSelection(0)

	def on_mypos(self,e):
		if self.mypos.GetValue():
			self.lat.Disable()
			self.lon.Disable()
		else:
			self.lat.Enable()
			self.lon.Enable()

	def OnOk(self,e):
		self.TriggerNodes = []
		enable_node = ujson.loads(self.nodes.enable_node_template)
		enable_node['id'] = self.nodes.get_node_id()
		enable_node['z'] = self.actions_flow_id
		enable_node['func'] = 'return msg;'
		enable_node['name'] = 't|'+enable_node['id']+'|'+str(self.trigger_type)
		self.TriggerNodes.append(enable_node)
		geofence_node = ujson.loads(self.geofence_node_template)
		geofence_node['id'] = self.nodes.get_node_id()
		geofence_node['z'] = self.actions_flow_id
		geofence_node['name'] = enable_node['name']
		geofence_node['context'] = 'vessels.'+self.vessel.GetValue()
		geofence_node['period'] = str(self.period.GetValue())
		geofence_node['myposition'] = self.mypos.GetValue()
		geofence_node['lat'] = str(self.lat.GetValue())
		geofence_node['lon'] = str(self.lon.GetValue())
		geofence_node['distance'] = str(self.distance.GetValue())
		geofence_node['wires'] = [[],[],[enable_node['id']]]
		self.TriggerNodes.append(geofence_node)
		self.EndModal(wx.OK)

class TriggerGPIO(wx.Dialog):
	def __init__(self,parent,edit):
		self.nodes = parent.nodes
		self.actions_flow_id = parent.actions_flow_id
		self.trigger_type = parent.available_triggers_select.GetSelection()

		if edit == 0: title = _('Add GPIO trigger')
		else: title = _('Edit GPIO trigger')

		wx.Dialog.__init__(self, None, title = title, size=(400, 220))
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
		        "wires": [[]]
		    }'''

		panel = wx.Panel(self)

		in_use_pins =[]
		for i in parent.no_actions_nodes:
			if 'type' in i:
			 if i['type'] == 'rpi-gpio in' or i['type'] == 'rpi-gpio out':
			 	if 'pin' in i and not i['pin'] in in_use_pins: in_use_pins.append(i['pin'])
		for i in parent.triggers_flow_nodes:
			if 'type' in i:
			 if i['type'] == 'rpi-gpio in':
			 	if 'pin' in i and not i['pin'] in in_use_pins: in_use_pins.append(i['pin'])
		for i in parent.actions_flow_nodes:
			if 'type' in i:
			 if i['type'] == 'rpi-gpio out':
			 	if 'pin' in i and not i['pin'] in in_use_pins: in_use_pins.append(i['pin'])

		pinsinuse = wx.StaticText(panel, label=_('Pins in use: ')+str([x.encode('UTF8') for x in in_use_pins]))
		pinlabel = wx.StaticText(panel, label=_('Pin'))
		self.pin = wx.Choice(panel, choices=self.nodes.allowed_pins, style=wx.CB_READONLY)

		self.resistor_select = [_('none'),_('pullup'),_('pulldown')]
		self.resistor_select2 = ['tri','up','down']

		resitorlabel = wx.StaticText(panel, label=_('Resistor'))
		self.resistor = wx.Choice(panel, choices=self.resistor_select, style=wx.CB_READONLY)

		self.read = wx.CheckBox(panel, label=_('Read initial state of pin on restart?'))

		cancelBtn = wx.Button(panel, wx.ID_CANCEL)
		okBtn = wx.Button(panel, wx.ID_OK)
		okBtn.Bind(wx.EVT_BUTTON, self.OnOk)

		pinh = wx.BoxSizer(wx.HORIZONTAL)
		pinh.Add(pinlabel, 0, wx.ALL, 10)
		pinh.Add(self.pin, 0, wx.ALL, 10)
		pinh.Add(resitorlabel, 0, wx.ALL, 10)
		pinh.Add(self.resistor, 0, wx.ALL, 10)

		okcancel = wx.BoxSizer(wx.HORIZONTAL)
		okcancel.Add((0, 0), 1, wx.ALL, 0)
		okcancel.Add(okBtn, 0, wx.ALL, 10)
		okcancel.Add(cancelBtn, 0, wx.ALL, 10)
		okcancel.Add((0, 0), 1, wx.ALL, 0)

		main = wx.BoxSizer(wx.VERTICAL)
		main.Add(pinsinuse, 0, wx.ALL, 10)
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
		self.TriggerNodes = []
		enable_node = ujson.loads(self.nodes.enable_node_template)
		enable_node['id'] = self.nodes.get_node_id()
		enable_node['z'] = self.actions_flow_id
		enable_node['func'] = 'return msg;'
		enable_node['name'] = 't|'+enable_node['id']+'|'+str(self.trigger_type)
		self.TriggerNodes.append(enable_node)
		gpio_node = ujson.loads(self.gpio_node_template)
		gpio_node['id'] = self.nodes.get_node_id()
		gpio_node['z'] = self.actions_flow_id
		gpio_node['name'] = enable_node['name']
		gpio_node['pin'] = pin
		gpio_node['intype'] = self.resistor_select2[self.resistor.GetSelection()]
		gpio_node['read'] = read
		gpio_node['wires'] = [[enable_node['id']]]
		self.TriggerNodes.append(gpio_node)
		self.EndModal(wx.OK)

class TriggerMQTT(wx.Dialog):
	def __init__(self,parent,edit,local,remote):
		self.nodes = parent.nodes
		self.localbrokerid = parent.localbrokerid
		self.remotebrokerid = parent.remotebrokerid
		self.actions_flow_id = parent.actions_flow_id
		self.trigger_type = parent.available_triggers_select.GetSelection()

		if edit == 0: title = _('Add MQTT trigger')
		else: title = _('Edit MQTT trigger')

		wx.Dialog.__init__(self, None, title = title, size=(450, 240))
		self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))

		self.mqtt_node_template = '''
		    {
		        "id": "",
		        "type": "mqtt in",
		        "z": "",
		        "name": "",
		        "topic": "topic1",
		        "qos": "2",
		        "broker": "",
		        "x": 380,
		        "y": 120,
		        "wires": [[]]
		    }'''

		panel = wx.Panel(self)

		self.local = wx.CheckBox(panel, label=_('Local MQTT broker'))
		self.local.Bind(wx.EVT_CHECKBOX, self.on_local)
		self.remote = wx.CheckBox(panel, label=_('Remote MQTT broker'))
		self.remote.Bind(wx.EVT_CHECKBOX, self.on_remote)

		topiclabel = wx.StaticText(panel, label=_('Topic'))
		self.topic = wx.TextCtrl(panel)
		
		okBtn = wx.Button(panel, wx.ID_OK)
		okBtn.Bind(wx.EVT_BUTTON, self.OnOk)
		cancelBtn = wx.Button(panel, wx.ID_CANCEL)

		topic = wx.BoxSizer(wx.HORIZONTAL)
		topic.Add(topiclabel, 0, wx.ALL, 10)
		topic.Add(self.topic, 1, wx.ALL, 10)

		ok_cancel = wx.BoxSizer(wx.HORIZONTAL)
		ok_cancel.Add((0, 0), 1, wx.ALL, 0)
		ok_cancel.Add(okBtn, 0, wx.ALL, 10)
		ok_cancel.Add(cancelBtn, 0, wx.ALL, 10)
		ok_cancel.Add((0, 0), 1, wx.ALL, 0)

		main = wx.BoxSizer(wx.VERTICAL)
		main.Add(self.local, 0, wx.ALL, 10)
		main.Add(self.remote, 0, wx.ALL, 10)
		main.Add(topic, 0, wx.ALL | wx.EXPAND, 0)
		main.Add((0, 0), 1, wx.ALL, 0)
		main.Add(ok_cancel, 0, wx.ALL | wx.EXPAND, 0)

		panel.SetSizer(main)

		if not local: self.local.Disable()
		if not remote: self.remote.Disable()


	def on_local(self, e):
		self.local.SetValue(True)
		self.remote.SetValue(False)

	def on_remote(self, e):
		self.local.SetValue(False)
		self.remote.SetValue(True)

	def OnOk(self,e):
		local = self.local.GetValue()
		remote = self.remote.GetValue()
		topic = self.topic.GetValue()
		if not local and not remote:
			wx.MessageBox(_('Select a MQTT broker'), 'Info', wx.OK | wx.ICON_INFORMATION)
			return
		elif not topic:
			wx.MessageBox(_('Provide a topic'), 'Info', wx.OK | wx.ICON_INFORMATION)
			return
		self.TriggerNodes = []
		enable_node = ujson.loads(self.nodes.enable_node_template)
		enable_node['id'] = self.nodes.get_node_id()
		enable_node['z'] = self.actions_flow_id
		enable_node['func'] = 'return msg;'
		enable_node['name'] = 't|'+enable_node['id']+'|'+str(self.trigger_type)
		self.TriggerNodes.append(enable_node)
		mqtt_node = ujson.loads(self.mqtt_node_template)
		mqtt_node['id'] = self.nodes.get_node_id()
		mqtt_node['z'] = self.actions_flow_id
		mqtt_node['name'] = enable_node['name']
		mqtt_node['topic'] = topic
		if local: mqtt_node['broker'] = self.localbrokerid
		elif remote: mqtt_node['broker'] = self.remotebrokerid
		mqtt_node['wires'] = [[enable_node['id']]]
		self.TriggerNodes.append(mqtt_node)
		self.EndModal(wx.OK)

class TriggerTelegram(wx.Dialog):
	def __init__(self,parent):
		self.nodes = parent.nodes
		self.actions_flow_id = parent.actions_flow_id
		self.trigger_type = parent.available_triggers_select.GetSelection()
		self.telegramid = parent.telegramid
		
		title = _('Add Telegram trigger')

		wx.Dialog.__init__(self, None, title = title, size=(350, 80))
		self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))

		self.telegram_node_template = '''
		    {
		        "id": "",
		        "type": "chatbot-telegram-receive",
		        "z": "",
		        "bot": "",
		        "botProduction": "",
		        "x": 380,
		        "y": 120,
		        "wires": [[]]
		    }'''
		self.authorized_node_template = '''
		    {
		        "id": "",
		        "type": "chatbot-authorized",
		        "z": "",
		        "x": 380,
		        "y": 120,
		        "wires": [[],[]]
		    }'''
		self.function_node_template = '''
		    {
		        "id": "",
		        "type": "function",
		        "z": "",
		        "name": "",
		        "func": "if (msg.payload.content!='/start'){return msg;}",
		        "outputs": 1,
		        "noerr": 0,
		        "x": 380,
		        "y": 120,
		        "wires": [[]]
		    }'''
		self.change_node_template = '''
		    {
		        "id": "",
		        "type": "change",
		        "z": "",
		        "name": "",
		        "rules": [
		            {
		                "t": "set",
		                "p": "payload",
		                "pt": "msg",
		                "to": "payload.content",
		                "tot": "msg"
		            }
		        ],
		        "action": "",
		        "property": "",
		        "from": "",
		        "to": "",
		        "reg": false,
		        "x": 380,
		        "y": 120,
		        "wires": [[]]
    }'''

		panel = wx.Panel(self)
		
		okBtn = wx.Button(panel, wx.ID_OK)
		okBtn.Bind(wx.EVT_BUTTON, self.OnOk)
		cancelBtn = wx.Button(panel, wx.ID_CANCEL)

		ok_cancel = wx.BoxSizer(wx.HORIZONTAL)
		ok_cancel.Add((0, 0), 1, wx.ALL, 0)
		ok_cancel.Add(okBtn, 0, wx.ALL, 10)
		ok_cancel.Add(cancelBtn, 0, wx.ALL, 10)
		ok_cancel.Add((0, 0), 1, wx.ALL, 0)

		main = wx.BoxSizer(wx.VERTICAL)
		main.Add((0, 0), 1, wx.ALL, 0)
		main.Add(ok_cancel, 0, wx.ALL | wx.EXPAND, 0)

		panel.SetSizer(main)

	def OnOk(self,e):
		self.TriggerNodes = []
		enable_node = ujson.loads(self.nodes.enable_node_template)
		enable_node['id'] = self.nodes.get_node_id()
		enable_node['z'] = self.actions_flow_id
		enable_node['func'] = 'return msg;'
		enable_node['name'] = 't|'+enable_node['id']+'|'+str(self.trigger_type)
		subid0 = enable_node['id'].split('.')
		subid = subid0[0]
		self.TriggerNodes.append(enable_node)
		change_node = ujson.loads(self.change_node_template)
		change_node['id'] = self.nodes.get_node_id()
		change_node['z'] = self.actions_flow_id
		change_node['name'] = enable_node['name']
		change_node['wires'] = [[enable_node['id']]]
		self.TriggerNodes.append(change_node)
		function_node = ujson.loads(self.function_node_template)
		function_node['id'] = self.nodes.get_node_id()
		function_node['z'] = self.actions_flow_id
		function_node['name'] = enable_node['name']
		function_node['wires'] = [[change_node['id']]]
		self.TriggerNodes.append(function_node)
		authorized_node = ujson.loads(self.authorized_node_template)
		authorized_node['id'] = self.nodes.get_node_id(subid)
		authorized_node['z'] = self.actions_flow_id
		authorized_node['wires'] = [[function_node['id']],[]]
		self.TriggerNodes.append(authorized_node)
		telegram_node = ujson.loads(self.telegram_node_template)
		telegram_node['id'] = self.nodes.get_node_id(subid)
		telegram_node['z'] = self.actions_flow_id
		telegram_node['bot'] = self.telegramid
		telegram_node['wires'] = [[authorized_node['id']]]
		self.TriggerNodes.append(telegram_node)
		self.EndModal(wx.OK)

class TriggerTime(wx.Dialog):
	def __init__(self,parent,edit):
		self.nodes = parent.nodes
		self.actions_flow_id = parent.actions_flow_id
		self.trigger_type = parent.available_triggers_select.GetSelection()
		self.telegramid = parent.telegramid
		
		if edit == 0: title = _('Add Time trigger')
		else: title = _('Edit Time trigger')

		wx.Dialog.__init__(self, None, title = title, size=(450, 150))
		self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))

		self.time_node_template = '''
		    {
		        "id": "",
		        "type": "inject",
		        "z": "",
		        "name": "",
		        "topic": "",
		        "payload": "",
		        "payloadType": "date",
		        "repeat": "",
		        "crontab": "",
		        "once": true,
		        "onceDelay": 0.1,
		        "x": 380,
		        "y": 120,
		        "wires": [[]]
		    }'''

		panel = wx.Panel(self)
		
		periodlabel = wx.StaticText(panel, label=_('Checking period'))
		self.period = wx.SpinCtrl(panel, min=1, max=100000000, initial=1)

		periodunits = [_('Seconds'),_('Minutes'),_('Hours')]
		self.periodunit = wx.Choice(panel, choices=periodunits, style=wx.CB_READONLY)
		self.periodunit.SetSelection(0)

		okBtn = wx.Button(panel, wx.ID_OK)
		okBtn.Bind(wx.EVT_BUTTON, self.OnOk)
		cancelBtn = wx.Button(panel, wx.ID_CANCEL)

		period = wx.BoxSizer(wx.HORIZONTAL)
		period.Add(periodlabel, 0, wx.ALL, 5)
		period.Add(self.period, 0, wx.ALL, 5)
		period.Add(self.periodunit, 0, wx.ALL, 5)

		ok_cancel = wx.BoxSizer(wx.HORIZONTAL)
		ok_cancel.Add((0, 0), 1, wx.ALL, 0)
		ok_cancel.Add(okBtn, 0, wx.ALL, 10)
		ok_cancel.Add(cancelBtn, 0, wx.ALL, 10)
		ok_cancel.Add((0, 0), 1, wx.ALL, 0)

		main = wx.BoxSizer(wx.VERTICAL)
		main.AddSpacer(10)
		main.Add(period, 0, wx.RIGHT | wx.LEFT, 5)
		main.Add((0, 0), 1, wx.ALL, 0)
		main.Add(ok_cancel, 0, wx.ALL | wx.EXPAND, 0)

		panel.SetSizer(main)

	def OnOk(self,e):
		self.TriggerNodes = []
		enable_node = ujson.loads(self.nodes.enable_node_template)
		enable_node['id'] = self.nodes.get_node_id()
		enable_node['z'] = self.actions_flow_id
		enable_node['func'] = 'return msg;'
		enable_node['name'] = 't|'+enable_node['id']+'|'+str(self.trigger_type)
		self.TriggerNodes.append(enable_node)
		time_node = ujson.loads(self.time_node_template)
		time_node['id'] = self.nodes.get_node_id()
		time_node['z'] = self.actions_flow_id
		time_node['name'] = enable_node['name']
		if self.periodunit.GetSelection() == 0: time_node['repeat'] = str(self.period.GetValue())
		elif self.periodunit.GetSelection() == 1: time_node['repeat'] = str(self.period.GetValue()*60)
		elif self.periodunit.GetSelection() == 2: time_node['repeat'] = str(self.period.GetValue()*60*60)
		time_node['wires'] = [[enable_node['id']]]
		self.TriggerNodes.append(time_node)
		self.EndModal(wx.OK)

# conditions
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
		        "wires": [[]]
		    }'''

		if edit == 0: title = _('Add condition')
		else: title = _('Edit condition')

		wx.Dialog.__init__(self, None, title = title, size=(600, 250))
		self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))

		panel = wx.Panel(self)

		operatorlabel = wx.StaticText(panel, label=_('Operator: ')+parent.available_conditions[self.operator_id])

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
		
		okBtn = wx.Button(panel, wx.ID_OK)
		okBtn.Bind(wx.EVT_BUTTON, self.OnOk)
		cancelBtn = wx.Button(panel, wx.ID_CANCEL)

		typevalue = wx.BoxSizer(wx.HORIZONTAL)
		typevalue.Add(type1label, 0, wx.ALL, 5)
		typevalue.Add(self.type1, 0, wx.ALL, 5)

		value1 = wx.BoxSizer(wx.HORIZONTAL)
		value1.Add(value1label, 0, wx.ALL, 5)
		value1.Add(self.value1, 1, wx.ALL, 5)
		value1.Add(self.edit_value1, 0, wx.ALL, 5)

		value2 = wx.BoxSizer(wx.HORIZONTAL)
		value2.Add(value2label, 0, wx.ALL, 5)
		value2.Add(self.value2, 1, wx.ALL, 5)
		value2.Add(self.edit_value2, 0, wx.ALL, 5)

		ok_cancel = wx.BoxSizer(wx.HORIZONTAL)
		ok_cancel.Add((0, 0), 1, wx.ALL, 0)
		ok_cancel.Add(okBtn, 0, wx.ALL, 10)
		ok_cancel.Add(cancelBtn, 0, wx.ALL, 10)
		ok_cancel.Add((0, 0), 1, wx.ALL, 0)

		main = wx.BoxSizer(wx.VERTICAL)
		main.Add(operatorlabel, 0, wx.ALL, 10)
		main.Add(typevalue, 0, wx.ALL, 0)
		main.Add(value1, 0, wx.ALL | wx.EXPAND, 0)
		main.Add(value2, 0, wx.ALL | wx.EXPAND, 0)
		main.Add((0, 0), 1, wx.ALL, 0)
		main.Add(ok_cancel, 0, wx.ALL | wx.EXPAND, 0)

		panel.SetSizer(main)

		self.edit_value1.Disable()
		self.edit_value2.Disable()
		if self.operator == 'true' or self.operator == 'false' or self.operator == 'null' or self.operator == 'nnull' or self.operator == 'empty' or self.operator == 'nempty':
			self.type1.Disable()
			self.value1.Disable()
			self.value2.Disable()
		elif self.operator != 'btwn':			
			self.value2.Disable()

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

	def on_select_type1(self,e):
		if self.type1.GetSelection() == 2: 
			self.edit_value1.Enable()
			if self.operator == 'btwn': self.edit_value2.Enable()
		else: 
			self.edit_value1.Disable()
			self.edit_value2.Disable()
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
		condition_node['name'] = 'c|'+condition_node['id']+'|'+str(self.operator_id)
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
		self.intervalUnit = [_('MiliSeconds'),_('Seconds'),_('Minutes'),_('Hours')]
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
class ActionSetSignalkKey(wx.Dialog):
	def __init__(self, parent, edit):
		self.credentials = ''
		self.nodes = parent.nodes
		self.actions_flow_id = parent.actions_flow_id
		self.action_id = parent.available_actions_select.GetSelection()
		self.sk_node_template = '''
		    {
		        "id": "",
		        "type": "signalk-send-pathvalue",
		        "z": "",
		        "name": "",
		        "source": "openplotter.actions",
		        "x": 380,
		        "y": 120,
		        "wires": []
		    }'''
		self.change_node_template = '''
			{
		        "id": "",
		        "type": "change",
		        "z": "",
		        "name": "",
		        "rules": [
		            {
		                "t": "set",
		                "p": "topic",
		                "pt": "msg",
		                "to": "",
		                "tot": "str"
		            },
		            {
		                "t": "set",
		                "p": "payload",
		                "pt": "msg",
		                "to": "",
		                "tot": ""
		            }
		        ],
		        "action": "",
		        "property": "",
		        "from": "",
		        "to": "",
		        "reg": false,
		        "x": 380,
		        "y": 120,
		        "wires": [
		            [
		                ""
		            ]
		        ]
		    }'''

		if edit == 0: title = _('Set Signal K key')
		else: title = _('Edit Signal K key')

		wx.Dialog.__init__(self, None, title = title, size=(550, 180))
		self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))

		panel = wx.Panel(self)

		skkeylabel = wx.StaticText(panel, label=_('Set Signal K key'))
		self.skkey1 = wx.TextCtrl(panel)
		self.edit_skkey1 = wx.Button(panel, label=_('Edit'))
		self.edit_skkey1.Bind(wx.EVT_BUTTON, self.onEditSkkey1)

		self.type_list = [_('Trigger value'), _('Number'), _('String'), _('Signal K key value')]

		tolabel = wx.StaticText(panel, label=_('to'))
		self.type = wx.Choice(panel, choices=self.type_list, style=wx.CB_READONLY)
		self.type.Bind(wx.EVT_CHOICE, self.on_select_type)
		self.value = wx.TextCtrl(panel)
		self.edit_skkey2 = wx.Button(panel, label=_('Edit'))
		self.edit_skkey2.Bind(wx.EVT_BUTTON, self.onEditSkkey2)

		okBtn = wx.Button(panel, wx.ID_OK)
		okBtn.Bind(wx.EVT_BUTTON, self.OnOk)
		cancelBtn = wx.Button(panel, wx.ID_CANCEL)

		skkey1 = wx.BoxSizer(wx.HORIZONTAL)
		skkey1.Add(skkeylabel, 0, wx.ALL, 5)
		skkey1.Add(self.skkey1, 1, wx.ALL, 5)
		skkey1.Add(self.edit_skkey1, 0, wx.ALL, 5)

		value = wx.BoxSizer(wx.HORIZONTAL)
		value.Add(tolabel, 0, wx.ALL, 5)
		value.Add(self.type, 0, wx.ALL, 5)
		value.Add(self.value, 1, wx.ALL, 5)
		value.Add(self.edit_skkey2, 0, wx.ALL, 5)

		ok_cancel = wx.BoxSizer(wx.HORIZONTAL)
		ok_cancel.Add((0, 0), 1, wx.ALL, 0)
		ok_cancel.Add(okBtn, 0, wx.RIGHT | wx.LEFT, 10)
		ok_cancel.Add(cancelBtn, 0, wx.RIGHT | wx.LEFT, 10)
		ok_cancel.Add((0, 0), 1, wx.ALL, 0)

		main = wx.BoxSizer(wx.VERTICAL)
		main.Add(skkey1, 1, wx.ALL | wx.EXPAND, 0)
		main.AddSpacer(5)
		main.Add(value, 1, wx.ALL | wx.EXPAND, 0)
		main.Add((0, 0), 1, wx.ALL, 0)
		main.Add(ok_cancel, 0, wx.ALL | wx.EXPAND, 10)

		panel.SetSizer(main)

		self.type.SetSelection(1)
		self.edit_skkey2.Disable()

	def on_select_type(self,e):
		selected = self.type.GetSelection()
		if selected == 0:
			self.value.Disable()
			self.edit_skkey2.Disable()
		elif selected == 1 or selected == 2:
			self.value.Enable()
			self.edit_skkey2.Disable()
		elif selected == 3:
			self.value.Enable()
			self.edit_skkey2.Enable()
		self.value.SetValue('')

	def onEditSkkey1(self,e):
		oldkey = False
		if self.skkey1.GetValue(): oldkey = self.skkey1.GetValue()
		dlg = selectKey(oldkey,0)
		res = dlg.ShowModal()
		if res == wx.OK:
			selected_key = dlg.selected_key.replace(':','.')
			self.skkey1.SetValue(selected_key)
		dlg.Destroy()

	def onEditSkkey2(self,e):
		oldkey = False
		if self.value.GetValue(): oldkey = self.value.GetValue()
		dlg = selectKey(oldkey,1)
		res = dlg.ShowModal()
		if res == wx.OK:
			self.value.SetValue(dlg.selected_vessel+'.'+dlg.selected_key)
		dlg.Destroy()

	def OnOk(self,e):
		skkey1 = self.skkey1.GetValue()
		value = self.value.GetValue()
		selected_type = self.type.GetSelection()
		if not skkey1:
			wx.MessageBox(_('Provide a Signal K key.'), 'Info', wx.OK | wx.ICON_INFORMATION)
			return
		if not value and selected_type != 0:
			wx.MessageBox(_('Provide a value.'), 'Info', wx.OK | wx.ICON_INFORMATION)
			return
		self.ActionNodes = []
		sk_node = ujson.loads(self.sk_node_template)
		sk_node['id'] = self.nodes.get_node_id()
		sk_node['z'] = self.actions_flow_id
		sk_node['name'] = 'a|'+sk_node['id']+'|'+str(self.action_id)
		self.ActionNodes.append(sk_node)
		change_node = ujson.loads(self.change_node_template)
		change_node['id'] = self.nodes.get_node_id()
		change_node['z'] = self.actions_flow_id
		change_node['name'] = sk_node['name']
		change_node['rules'][0]['to'] = skkey1
		if selected_type == 0:
			change_node['rules'][1]['to'] = "payload"
			change_node['rules'][1]['tot'] = "msg"
		if selected_type == 1:
			change_node['rules'][1]['to'] = value
			change_node['rules'][1]['tot'] = "num"
		if selected_type == 2:
			change_node['rules'][1]['to'] = value
			change_node['rules'][1]['tot'] = "str"
		if selected_type == 3:
			change_node['rules'][1]['to'] = value
			change_node['rules'][1]['tot'] = "flow"
		change_node['wires'] = [[sk_node['id']]]
		self.ActionNodes.append(change_node)
		self.connector_id = change_node['id']
		self.EndModal(wx.OK)

class ActionSetGPIO(wx.Dialog):
	def __init__(self, parent, edit):
		self.credentials = ''
		self.nodes = parent.nodes
		self.actions_flow_id = parent.actions_flow_id
		self.action_id = parent.available_actions_select.GetSelection()
		self.gpio_node_template = '''
		    {
		        "id": "",
		        "type": "rpi-gpio out",
		        "z": "",
		        "name": "",
		        "pin": "",
		        "set": true,
		        "level": "0",
		        "freq": "",
		        "out": "out",
		        "x": 380,
		        "y": 120,
		        "wires": []
		    }'''
		self.change_node_template = '''
		    {
		        "id": "",
		        "type": "change",
		        "z": "",
		        "name": "",
		        "rules": [
		            {
		                "t": "set",
		                "p": "payload",
		                "pt": "msg",
		                "to": "",
		                "tot": "num"
		            }
		        ],
		        "action": "",
		        "property": "",
		        "from": "",
		        "to": "",
		        "reg": false,
		        "x": 380,
		        "y": 120,
		        "wires": [
		            [
		                ""
		            ]
		        ]
		    }'''
		if edit == 0: title = _('Set GPIO output')
		else: title = _('Edit GPIO output')

		wx.Dialog.__init__(self, None, title = title, size=(320, 330))
		self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))

		panel = wx.Panel(self)

		in_use_pins =[]
		for i in parent.no_actions_nodes:
			if 'type' in i:
			 if i['type'] == 'rpi-gpio in' or i['type'] == 'rpi-gpio out':
			 	if 'pin' in i and not i['pin'] in in_use_pins: in_use_pins.append(i['pin'])
		for i in parent.triggers_flow_nodes:
			if 'type' in i:
			 if i['type'] == 'rpi-gpio in':
			 	if 'pin' in i and not i['pin'] in in_use_pins: in_use_pins.append(i['pin'])
		for i in parent.actions_flow_nodes:
			if 'type' in i:
			 if i['type'] == 'rpi-gpio out':
			 	if 'pin' in i and not i['pin'] in in_use_pins: in_use_pins.append(i['pin'])

		pinsinuse = wx.StaticText(panel, label=_('Pins in use: ')+str([x.encode('UTF8') for x in in_use_pins]))
		pinlabel = wx.StaticText(panel, label=_('Pin'))
		self.pin = wx.Choice(panel, choices=self.nodes.allowed_pins, style=wx.CB_READONLY)

		self.low = wx.CheckBox(panel, label=_('Set pin to 0'))
		self.low.Bind(wx.EVT_CHECKBOX, self.on_low)
		self.high = wx.CheckBox(panel, label=_('Set pin to 1'))
		self.high.Bind(wx.EVT_CHECKBOX, self.on_high)

		self.init = wx.CheckBox(panel, label=_('Set initial state'))
		self.init.Bind(wx.EVT_CHECKBOX, self.on_init)
		self.initlow = wx.CheckBox(panel, label='0')
		self.initlow.Bind(wx.EVT_CHECKBOX, self.on_initlow)
		self.inithigh = wx.CheckBox(panel, label='1')
		self.inithigh.Bind(wx.EVT_CHECKBOX, self.on_inithigh)

		okBtn = wx.Button(panel, wx.ID_OK)
		okBtn.Bind(wx.EVT_BUTTON, self.OnOk)
		cancelBtn = wx.Button(panel, wx.ID_CANCEL)

		pin = wx.BoxSizer(wx.HORIZONTAL)
		pin.Add(pinlabel, 0, wx.LEFT, 10)
		pin.Add(self.pin, 0, wx.LEFT, 10)

		ok_cancel = wx.BoxSizer(wx.HORIZONTAL)
		ok_cancel.Add((0, 0), 1, wx.ALL, 0)
		ok_cancel.Add(okBtn, 0, wx.RIGHT | wx.LEFT, 10)
		ok_cancel.Add(cancelBtn, 0, wx.RIGHT | wx.LEFT, 10)
		ok_cancel.Add((0, 0), 1, wx.ALL, 0)

		main = wx.BoxSizer(wx.VERTICAL)
		main.AddSpacer(10)
		main.Add(pinsinuse, 0, wx.LEFT, 10)
		main.AddSpacer(5)
		main.Add(pin, 0, wx.ALL, 0)
		main.AddSpacer(15)
		main.Add(self.low, 0, wx.LEFT, 10)
		main.AddSpacer(5)
		main.Add(self.high, 0, wx.LEFT, 10)
		main.AddSpacer(15)
		main.Add(self.init, 0, wx.LEFT, 10)
		main.AddSpacer(5)
		main.Add(self.initlow, 0, wx.LEFT, 20)
		main.AddSpacer(5)
		main.Add(self.inithigh, 0, wx.LEFT, 20)
		main.Add((0, 0), 1, wx.ALL, 0)
		main.Add(ok_cancel, 0, wx.ALL | wx.EXPAND, 10)

		panel.SetSizer(main)

		self.on_low(0)
		self.init.SetValue(True)
		self.initlow.SetValue(True)

	def on_low(self, e):
		self.low.SetValue(True)
		self.high.SetValue(False)

	def on_high(self, e):
		self.low.SetValue(False)
		self.high.SetValue(True)

	def on_init(self, e):
		if self.init.GetValue():
			self.initlow.Enable()
			self.inithigh.Enable()
		else:
			self.initlow.Disable()
			self.inithigh.Disable()

	def on_initlow(self, e):
		self.initlow.SetValue(True)
		self.inithigh.SetValue(False)

	def on_inithigh(self, e):
		self.initlow.SetValue(False)
		self.inithigh.SetValue(True)

	def OnOk(self,e):
		pin = self.pin.GetStringSelection()
		if not pin:
			wx.MessageBox(_('Select a pin.'), 'Info', wx.OK | wx.ICON_INFORMATION)
			return
		self.ActionNodes = []
		gpio_node = ujson.loads(self.gpio_node_template)
		gpio_node['id'] = self.nodes.get_node_id()
		gpio_node['z'] = self.actions_flow_id
		gpio_node['name'] = 'a|'+gpio_node['id']+'|'+str(self.action_id)
		gpio_node['pin'] = pin
		if self.init.GetValue():
			gpio_node['set'] = True
			if self.initlow.GetValue(): gpio_node['level'] = '0'
			if self.inithigh.GetValue(): gpio_node['level'] = '1'
		else: 
			gpio_node['set'] = False
			gpio_node['level'] = ''
		self.ActionNodes.append(gpio_node)
		change_node = ujson.loads(self.change_node_template)
		change_node['id'] = self.nodes.get_node_id()
		change_node['z'] = self.actions_flow_id
		change_node['name'] = 'a|'+gpio_node['id']+'|'+str(self.action_id)
		if self.low.GetValue(): change_node['rules'][0]['to'] = '0'
		if self.high.GetValue(): change_node['rules'][0]['to'] = '1'
		change_node['wires'] = [[gpio_node['id']]]
		self.ActionNodes.append(change_node)
		self.connector_id = change_node['id']
		self.EndModal(wx.OK)

class ActionSetMQTT(wx.Dialog):
	def __init__(self, parent, edit, local, remote):
		self.credentials = ''
		self.nodes = parent.nodes
		self.localbrokerid = parent.localbrokerid
		self.remotebrokerid = parent.remotebrokerid
		self.actions_flow_id = parent.actions_flow_id
		self.action_id = parent.available_actions_select.GetSelection()
		self.mqtt_node_template = '''
		    {
		        "id": "",
		        "type": "mqtt out",
		        "z": "",
		        "name": "",
		        "topic": "",
		        "qos": "",
		        "retain": "",
		        "broker": "",
		        "x": 380,
		        "y": 120,
		        "wires": []
		    }'''
		self.change_node_template = '''
			{
		        "id": "",
		        "type": "change",
		        "z": "",
		        "name": "",
		        "rules": [
		            {
		                "t": "set",
		                "p": "payload",
		                "pt": "msg",
		                "to": "",
		                "tot": ""
		            }
		        ],
		        "action": "",
		        "property": "",
		        "from": "",
		        "to": "",
		        "reg": false,
		        "x": 380,
		        "y": 120,
		        "wires": [
		            [
		                ""
		            ]
		        ]
		    }'''

		if edit == 0: title = _('Add MQTT action')
		else: title = _('Edit MQTT action')

		wx.Dialog.__init__(self, None, title = title, size=(550, 280))
		self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))

		panel = wx.Panel(self)

		self.local = wx.CheckBox(panel, label=_('Local MQTT broker'))
		self.local.Bind(wx.EVT_CHECKBOX, self.on_local)
		self.remote = wx.CheckBox(panel, label=_('Remote MQTT broker'))
		self.remote.Bind(wx.EVT_CHECKBOX, self.on_remote)

		topiclabel = wx.StaticText(panel, label=_('Set topic'))
		self.topic = wx.TextCtrl(panel)

		self.type_list = [_('Trigger value'), _('Fix value'), _('Signal K key value')]

		tolabel = wx.StaticText(panel, label=_('to'))
		self.type = wx.Choice(panel, choices=self.type_list, style=wx.CB_READONLY)
		self.type.Bind(wx.EVT_CHOICE, self.on_select_type)
		self.value = wx.TextCtrl(panel)
		self.edit_skkey2 = wx.Button(panel, label=_('Edit'))
		self.edit_skkey2.Bind(wx.EVT_BUTTON, self.onEditSkkey2)

		value = wx.BoxSizer(wx.HORIZONTAL)
		value.Add(tolabel, 0, wx.ALL, 5)
		value.Add(self.type, 0, wx.ALL, 5)
		value.Add(self.value, 1, wx.ALL, 5)
		value.Add(self.edit_skkey2, 0, wx.ALL, 5)
	
		okBtn = wx.Button(panel, wx.ID_OK)
		okBtn.Bind(wx.EVT_BUTTON, self.OnOk)
		cancelBtn = wx.Button(panel, wx.ID_CANCEL)

		topic = wx.BoxSizer(wx.HORIZONTAL)
		topic.Add(topiclabel, 0, wx.ALL, 10)
		topic.Add(self.topic, 1, wx.ALL, 10)

		ok_cancel = wx.BoxSizer(wx.HORIZONTAL)
		ok_cancel.Add((0, 0), 1, wx.ALL, 0)
		ok_cancel.Add(okBtn, 0, wx.ALL, 10)
		ok_cancel.Add(cancelBtn, 0, wx.ALL, 10)
		ok_cancel.Add((0, 0), 1, wx.ALL, 0)

		main = wx.BoxSizer(wx.VERTICAL)
		main.Add(self.local, 0, wx.ALL, 10)
		main.Add(self.remote, 0, wx.ALL, 10)
		main.Add(topic, 0, wx.ALL | wx.EXPAND, 0)
		main.Add(value, 0, wx.ALL | wx.EXPAND, 0)
		main.Add((0, 0), 1, wx.ALL, 0)
		main.Add(ok_cancel, 0, wx.ALL | wx.EXPAND, 0)

		panel.SetSizer(main)

		if not local: self.local.Disable()
		if not remote: self.remote.Disable()
		self.edit_skkey2.Disable()

	def on_local(self, e):
		self.local.SetValue(True)
		self.remote.SetValue(False)

	def on_remote(self, e):
		self.local.SetValue(False)
		self.remote.SetValue(True)

	def on_select_type(self,e):
		selected = self.type.GetSelection()
		if selected == 0:
			self.value.Disable()
			self.edit_skkey2.Disable()
		elif selected == 1:
			self.value.Enable()
			self.edit_skkey2.Disable()
		elif selected == 2:
			self.value.Enable()
			self.edit_skkey2.Enable()
		self.value.SetValue('')

	def onEditSkkey2(self,e):
		oldkey = False
		if self.value.GetValue(): oldkey = self.value.GetValue()
		dlg = selectKey(oldkey,1)
		res = dlg.ShowModal()
		if res == wx.OK:
			self.value.SetValue(dlg.selected_vessel+'.'+dlg.selected_key)
		dlg.Destroy()

	def OnOk(self,e):
		local = self.local.GetValue()
		remote = self.remote.GetValue()
		topic = self.topic.GetValue()
		value = self.value.GetValue()
		selected_type = self.type.GetSelection()
		if not local and not remote:
			wx.MessageBox(_('Select a MQTT broker'), 'Info', wx.OK | wx.ICON_INFORMATION)
			return
		elif not topic:
			wx.MessageBox(_('Provide a topic'), 'Info', wx.OK | wx.ICON_INFORMATION)
			return
		elif not value and selected_type != 0:
			wx.MessageBox(_('Provide a value.'), 'Info', wx.OK | wx.ICON_INFORMATION)
			return
		self.ActionNodes = []
		mqtt_node = ujson.loads(self.mqtt_node_template)
		mqtt_node['id'] = self.nodes.get_node_id()
		mqtt_node['z'] = self.actions_flow_id
		mqtt_node['name'] = 'a|'+mqtt_node['id']+'|'+str(self.action_id)
		mqtt_node['topic'] = topic
		if local: mqtt_node['broker'] = self.localbrokerid
		elif remote: mqtt_node['broker'] = self.remotebrokerid
		self.ActionNodes.append(mqtt_node)
		change_node = ujson.loads(self.change_node_template)
		change_node['id'] = self.nodes.get_node_id()
		change_node['z'] = self.actions_flow_id
		change_node['name'] = mqtt_node['name']
		if selected_type == 0:
			change_node['rules'][0]['to'] = "payload"
			change_node['rules'][0]['tot'] = "msg"
		if selected_type == 1:
			change_node['rules'][0]['to'] = value
			change_node['rules'][0]['tot'] = "str"
		if selected_type == 2:
			change_node['rules'][0]['to'] = value
			change_node['rules'][0]['tot'] = "flow"
		change_node['wires'] = [[mqtt_node['id']]]
		self.ActionNodes.append(change_node)
		self.connector_id = change_node['id']
		self.EndModal(wx.OK)

class ActionPublishTwitter(wx.Dialog):
	def __init__(self, parent, edit):
		self.credentials = ''
		self.nodes = parent.nodes
		self.actions_flow_id = parent.actions_flow_id
		self.action_id = parent.available_actions_select.GetSelection()
		self.twitterid = parent.twitterid
		self.RepeatOptions = RepeatOptions()
		self.twitter_node_template = '''
		    {
		        "id": "",
		        "type": "twitter out",
		        "z": "",
		        "name": "",
		        "twitter": "",
		        "x": 380,
		        "y": 120,
		        "wires": []
		    }'''
		self.payload_node_template = '''
		    {
		        "id": "",
		        "type": "template",
		        "z": "",
		        "name": "",
		        "field": "payload",
		        "fieldType": "msg",
		        "format": "handlebars",
		        "syntax": "mustache",
		        "template": "",
		        "output": "str",
		        "x": 380,
		        "y": 120,
		        "wires": [
		            []
		        ]
		    }'''
		if edit == 0: title = _('Add Twitter action')
		else: title = _('Edit Twitter action')

		wx.Dialog.__init__(self, None, title = title, size=(710, 390))
		self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))

		panel = wx.Panel(self)

		bodylabel = wx.StaticText(panel, label=_('Tweet'))
		self.body = wx.TextCtrl(panel, style=wx.TE_MULTILINE, size=(-1,60))

		self.addsk = wx.Button(panel, label=_('Add Signal K key value'))
		self.addsk.Bind(wx.EVT_BUTTON, self.on_addsk)

		self.repeat = wx.CheckBox(panel, label=_('Repeat'))
		self.repeat.Bind(wx.EVT_CHECKBOX, self.on_repeat)
		intervallabel = wx.StaticText(panel, label=_('Interval'))
		self.interval = wx.SpinCtrl(panel, min=1, max=100000, initial=1)
		self.unit = wx.Choice(panel, choices=self.RepeatOptions.intervalUnit, style=wx.CB_READONLY)
		self.unit.SetSelection(1)
		maxlabel = wx.StaticText(panel, label=_('Max.'))
		self.max = wx.SpinCtrl(panel, min=1, max=100000, initial=1)

		self.rate = wx.CheckBox(panel, label=_('Rate limit'))
		self.rate.Bind(wx.EVT_CHECKBOX, self.on_rate)
		ratelabel = wx.StaticText(panel, label=_('Rate'))
		self.amount = wx.SpinCtrl(panel, min=1, max=100000, initial=1)
		ratelabel2 = wx.StaticText(panel, label=_('time(s) per'))
		self.time = wx.SpinCtrl(panel, min=1, max=100000, initial=1)
		self.timeunit = wx.Choice(panel, choices=self.RepeatOptions.rateUnit, style=wx.CB_READONLY)
		self.timeunit.SetSelection(2)
		
		self.interval.Disable()
		self.unit.Disable()
		self.max.Disable()
		self.amount.Disable()
		self.time.Disable()
		self.timeunit.Disable()

		okBtn = wx.Button(panel, wx.ID_OK)
		okBtn.Bind(wx.EVT_BUTTON, self.OnOk)
		cancelBtn = wx.Button(panel, wx.ID_CANCEL)

		body = wx.BoxSizer(wx.HORIZONTAL)
		body.Add(bodylabel, 0, wx.ALL, 5)
		body.Add(self.body, 1, wx.ALL, 5)

		addsk = wx.BoxSizer(wx.HORIZONTAL)
		addsk.Add((0, 0), 1, wx.ALL, 5)
		addsk.Add(self.addsk, 1, wx.ALL, 5)

		repeath = wx.BoxSizer(wx.HORIZONTAL)
		repeath.Add(intervallabel, 0, wx.ALL, 5)
		repeath.Add(self.interval, 0, wx.ALL, 5)
		repeath.Add(self.unit, 0, wx.ALL, 5)
		repeath.Add(maxlabel, 0, wx.ALL, 5)
		repeath.Add(self.max, 0, wx.ALL, 5)

		rate = wx.BoxSizer(wx.HORIZONTAL)
		rate.Add(ratelabel, 0, wx.ALL, 5)
		rate.Add(self.amount, 0, wx.ALL, 5)
		rate.Add(ratelabel2, 0, wx.ALL, 5)
		rate.Add(self.time, 0, wx.ALL, 5)
		rate.Add(self.timeunit, 0, wx.ALL, 5)

		ok_cancel = wx.BoxSizer(wx.HORIZONTAL)
		ok_cancel.Add((0, 0), 1, wx.ALL, 0)
		ok_cancel.Add(okBtn, 0, wx.RIGHT | wx.LEFT, 10)
		ok_cancel.Add(cancelBtn, 0, wx.RIGHT | wx.LEFT, 10)
		ok_cancel.Add((0, 0), 1, wx.ALL, 0)

		main = wx.BoxSizer(wx.VERTICAL)
		main.Add(body, 1, wx.ALL | wx.EXPAND, 0)
		main.Add(addsk, 1, wx.ALL | wx.EXPAND, 0)
		main.AddSpacer(10)
		main.Add(self.repeat, 1, wx.RIGHT | wx.LEFT, 5)
		main.Add(repeath, 1, wx.RIGHT | wx.LEFT, 5)
		main.AddSpacer(10)
		main.Add(self.rate, 1, wx.RIGHT | wx.LEFT, 5)
		main.Add(rate, 1, wx.RIGHT | wx.LEFT, 5)
		main.Add((0, 0), 1, wx.ALL, 0)
		main.Add(ok_cancel, 0, wx.ALL | wx.EXPAND, 10)

		panel.SetSizer(main)
		self.Centre()

	def on_addsk(self, e):
		oldkey = False
		dlg = selectKey(oldkey,1)
		res = dlg.ShowModal()
		if res == wx.OK:
			self.body.AppendText('{{flow.'+dlg.selected_vessel+'.'+dlg.selected_key+'}}')
		dlg.Destroy()

	def on_repeat(self, e):
		if self.repeat.GetValue():
			self.interval.Enable()
			self.unit.Enable()
			self.max.Enable()
			self.rate.SetValue(False)
			self.amount.Disable()
			self.time.Disable()
			self.timeunit.Disable()
		else:
			self.interval.Disable()
			self.unit.Disable()
			self.max.Disable()

	def on_rate(self, e):
		if self.rate.GetValue():
			self.amount.Enable()
			self.time.Enable()
			self.timeunit.Enable()
			self.repeat.SetValue(False)
			self.interval.Disable()
			self.unit.Disable()
			self.max.Disable()

		else:
			self.amount.Disable()
			self.time.Disable()
			self.timeunit.Disable()

	def OnOk(self,e):
		body = self.body.GetValue()
		if not body:
			wx.MessageBox(_('You must provide something to publish.'), 'Info', wx.OK | wx.ICON_INFORMATION)
			return
		self.ActionNodes = []
		twitter_node = ujson.loads(self.twitter_node_template)
		twitter_node['id'] = self.nodes.get_node_id()
		twitter_node['z'] = self.actions_flow_id
		twitter_node['name'] = 'a|'+twitter_node['id']+'|'+str(self.action_id)
		twitter_node['twitter'] = self.twitterid
		self.ActionNodes.append(twitter_node)
		payload_node = ujson.loads(self.payload_node_template)
		payload_node['id'] = self.nodes.get_node_id()
		payload_node['z'] = self.actions_flow_id
		payload_node['name'] = twitter_node['name']
		payload_node['template'] = body
		payload_node['wires'] = [[twitter_node['id']]]
		self.ActionNodes.append(payload_node)
		if not self.repeat.GetValue() and not self.rate.GetValue():
			self.connector_id = payload_node['id']
		elif self.repeat.GetValue():
			repeat_node = ujson.loads(self.RepeatOptions.repeat_template)
			repeat_node['id'] = self.nodes.get_node_id()
			repeat_node['z'] = self.actions_flow_id
			repeat_node['name'] = twitter_node['name']
			repeat_node['interval'] = str(self.interval.GetValue())
			repeat_node['intervalUnit'] = self.RepeatOptions.intervalUnit2[self.unit.GetSelection()]
			repeat_node['maximum'] = str(self.max.GetValue())
			repeat_node['wires'] = [[payload_node['id']]]
			self.connector_id = repeat_node['id']
			self.ActionNodes.append(repeat_node)
		elif self.rate.GetValue():
			rate_node = ujson.loads(self.RepeatOptions.rate_limit_template)
			rate_node['id'] = self.nodes.get_node_id()
			rate_node['z'] = self.actions_flow_id
			rate_node['name'] = twitter_node['name']
			rate_node['rate'] = str(self.amount.GetValue())
			rate_node['nbRateUnits'] = str(self.time.GetValue())
			rate_node['rateUnits'] = self.RepeatOptions.rateUnit2[self.timeunit.GetSelection()]
			rate_node['wires'] = [[payload_node['id']]]
			self.connector_id = rate_node['id']
			self.ActionNodes.append(rate_node)
		self.EndModal(wx.OK)

class ActionSendEmail(wx.Dialog):
	def __init__(self, parent, edit):
		self.credentials = ''
		self.nodes = parent.nodes
		self.actions_flow_id = parent.actions_flow_id
		self.action_id = parent.available_actions_select.GetSelection()
		self.RepeatOptions = RepeatOptions()
		self.email_node_template = '''
		    {
		        "id": "",
		        "type": "e-mail",
		        "z": "",
		        "server": "",
		        "port": "",
		        "secure": true,
		        "name": "",
		        "dname": "",
		        "x": 380,
		        "y": 120,
		        "wires": []
		    }'''
		self.payload_node_template = '''
		    {
		        "id": "",
		        "type": "template",
		        "z": "",
		        "name": "",
		        "field": "payload",
		        "fieldType": "msg",
		        "format": "handlebars",
		        "syntax": "mustache",
		        "template": "",
		        "output": "str",
		        "x": 380,
		        "y": 120,
		        "wires": [
		            []
		        ]
		    }'''
		self.topic_node_template = '''
		    {
		        "id": "",
		        "type": "template",
		        "z": "",
		        "name": "",
		        "field": "topic",
		        "fieldType": "msg",
		        "format": "handlebars",
		        "syntax": "mustache",
		        "template": "",
		        "output": "str",
		        "x": 380,
		        "y": 120,
		        "wires": [
		            []
		        ]
		    }'''
		if edit == 0: title = _('Add email action')
		else: title = _('Edit email action')

		wx.Dialog.__init__(self, None, title = title, size=(710, 460))
		self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))

		panel = wx.Panel(self)

		tolabel = wx.StaticText(panel, label=_('To'))
		self.to = wx.TextCtrl(panel)

		serverlabel = wx.StaticText(panel, label=_('Server'))
		self.server = wx.TextCtrl(panel)

		portlabel = wx.StaticText(panel, label=_('Port'))
		self.port = wx.SpinCtrl(panel, min=1, max=65000, initial=465)

		self.secure = wx.CheckBox(panel, label=_('secure connection'))

		useridlabel = wx.StaticText(panel, label=_('User ID'))
		self.userid = wx.TextCtrl(panel)

		passwordlabel = wx.StaticText(panel, label=_('Password'))
		self.password = wx.TextCtrl(panel, style=wx.TE_PASSWORD)

		subjectlabel = wx.StaticText(panel, label=_('Subject'))
		self.subject = wx.TextCtrl(panel)

		bodylabel = wx.StaticText(panel, label=_('Body'))
		self.body = wx.TextCtrl(panel, style=wx.TE_MULTILINE, size=(-1,60))

		self.addsk = wx.Button(panel, label=_('Add Signal K key value'))
		self.addsk.Bind(wx.EVT_BUTTON, self.on_addsk)

		self.repeat = wx.CheckBox(panel, label=_('Repeat'))
		self.repeat.Bind(wx.EVT_CHECKBOX, self.on_repeat)
		intervallabel = wx.StaticText(panel, label=_('Interval'))
		self.interval = wx.SpinCtrl(panel, min=1, max=100000, initial=1)
		self.unit = wx.Choice(panel, choices=self.RepeatOptions.intervalUnit, style=wx.CB_READONLY)
		self.unit.SetSelection(1)
		maxlabel = wx.StaticText(panel, label=_('Max.'))
		self.max = wx.SpinCtrl(panel, min=1, max=100000, initial=1)

		self.rate = wx.CheckBox(panel, label=_('Rate limit'))
		self.rate.Bind(wx.EVT_CHECKBOX, self.on_rate)
		ratelabel = wx.StaticText(panel, label=_('Rate'))
		self.amount = wx.SpinCtrl(panel, min=1, max=100000, initial=1)
		ratelabel2 = wx.StaticText(panel, label=_('time(s) per'))
		self.time = wx.SpinCtrl(panel, min=1, max=100000, initial=1)
		self.timeunit = wx.Choice(panel, choices=self.RepeatOptions.rateUnit, style=wx.CB_READONLY)
		self.timeunit.SetSelection(2)
		
		self.interval.Disable()
		self.unit.Disable()
		self.max.Disable()
		self.amount.Disable()
		self.time.Disable()
		self.timeunit.Disable()

		okBtn = wx.Button(panel, wx.ID_OK)
		okBtn.Bind(wx.EVT_BUTTON, self.OnOk)
		cancelBtn = wx.Button(panel, wx.ID_CANCEL)

		toserver = wx.BoxSizer(wx.HORIZONTAL)
		toserver.Add(tolabel, 0, wx.ALL, 5)
		toserver.Add(self.to, 1, wx.ALL, 5)
		toserver.Add(serverlabel, 0, wx.ALL, 5)
		toserver.Add(self.server, 1, wx.ALL, 5)
		toserver.Add(portlabel, 0, wx.ALL, 5)
		toserver.Add(self.port, 0, wx.ALL, 5)

		userpass = wx.BoxSizer(wx.HORIZONTAL)
		userpass.Add(useridlabel, 0, wx.ALL, 5)
		userpass.Add(self.userid, 1, wx.ALL, 5)
		userpass.Add(passwordlabel, 0, wx.ALL, 5)
		userpass.Add(self.password, 1, wx.ALL, 5)
		userpass.Add(self.secure, 0, wx.ALL, 5)

		subject = wx.BoxSizer(wx.HORIZONTAL)
		subject.Add(subjectlabel, 0, wx.ALL, 5)
		subject.Add(self.subject, 1, wx.ALL, 5)

		body = wx.BoxSizer(wx.HORIZONTAL)
		body.Add(bodylabel, 0, wx.ALL, 5)
		body.Add(self.body, 1, wx.ALL, 5)

		addsk = wx.BoxSizer(wx.HORIZONTAL)
		addsk.Add((0, 0), 1, wx.ALL, 5)
		addsk.Add(self.addsk, 1, wx.ALL, 5)

		repeath = wx.BoxSizer(wx.HORIZONTAL)
		repeath.Add(intervallabel, 0, wx.ALL, 5)
		repeath.Add(self.interval, 0, wx.ALL, 5)
		repeath.Add(self.unit, 0, wx.ALL, 5)
		repeath.Add(maxlabel, 0, wx.ALL, 5)
		repeath.Add(self.max, 0, wx.ALL, 5)

		rate = wx.BoxSizer(wx.HORIZONTAL)
		rate.Add(ratelabel, 0, wx.ALL, 5)
		rate.Add(self.amount, 0, wx.ALL, 5)
		rate.Add(ratelabel2, 0, wx.ALL, 5)
		rate.Add(self.time, 0, wx.ALL, 5)
		rate.Add(self.timeunit, 0, wx.ALL, 5)

		ok_cancel = wx.BoxSizer(wx.HORIZONTAL)
		ok_cancel.Add((0, 0), 1, wx.ALL, 0)
		ok_cancel.Add(okBtn, 0, wx.RIGHT | wx.LEFT, 10)
		ok_cancel.Add(cancelBtn, 0, wx.RIGHT | wx.LEFT, 10)
		ok_cancel.Add((0, 0), 1, wx.ALL, 0)

		main = wx.BoxSizer(wx.VERTICAL)
		main.Add(toserver, 1, wx.ALL | wx.EXPAND, 0)
		main.Add(userpass, 1, wx.ALL | wx.EXPAND, 0)
		main.Add(subject, 1, wx.ALL | wx.EXPAND, 0)
		main.Add(body, 1, wx.ALL | wx.EXPAND, 0)
		main.Add(addsk, 1, wx.ALL | wx.EXPAND, 0)
		main.AddSpacer(10)
		main.Add(self.repeat, 1, wx.RIGHT | wx.LEFT, 5)
		main.Add(repeath, 1, wx.RIGHT | wx.LEFT, 5)
		main.AddSpacer(10)
		main.Add(self.rate, 1, wx.RIGHT | wx.LEFT, 5)
		main.Add(rate, 1, wx.RIGHT | wx.LEFT, 5)
		main.Add((0, 0), 1, wx.ALL, 0)
		main.Add(ok_cancel, 0, wx.ALL | wx.EXPAND, 10)

		panel.SetSizer(main)
		self.Centre()

		self.server.SetValue('smtp.gmail.com')
		self.secure.SetValue(True)

	def on_addsk(self, e):
		oldkey = False
		dlg = selectKey(oldkey,1)
		res = dlg.ShowModal()
		if res == wx.OK:
			self.body.AppendText('{{flow.'+dlg.selected_vessel+'.'+dlg.selected_key+'}}')
		dlg.Destroy()

	def on_repeat(self, e):
		if self.repeat.GetValue():
			self.interval.Enable()
			self.unit.Enable()
			self.max.Enable()
			self.rate.SetValue(False)
			self.amount.Disable()
			self.time.Disable()
			self.timeunit.Disable()
		else:
			self.interval.Disable()
			self.unit.Disable()
			self.max.Disable()

	def on_rate(self, e):
		if self.rate.GetValue():
			self.amount.Enable()
			self.time.Enable()
			self.timeunit.Enable()
			self.repeat.SetValue(False)
			self.interval.Disable()
			self.unit.Disable()
			self.max.Disable()

		else:
			self.amount.Disable()
			self.time.Disable()
			self.timeunit.Disable()

	def OnOk(self,e):
		to = self.to.GetValue()
		if not to:
			wx.MessageBox(_('You must provide an email address to send your message to.'), 'Info', wx.OK | wx.ICON_INFORMATION)
			return
		server = self.server.GetValue()
		if not server:
			wx.MessageBox(_('You must provide a SMTP server.'), 'Info', wx.OK | wx.ICON_INFORMATION)
			return
		userid = self.userid.GetValue()
		password = self.password.GetValue()
		if not userid or not password:
			wx.MessageBox(_('You must provide user ID and password for your server.'), 'Info', wx.OK | wx.ICON_INFORMATION)
			return
		subject = self.subject.GetValue()
		body = self.body.GetValue()
		if not subject or not body:
			wx.MessageBox(_('You must provide subject and body of your email.'), 'Info', wx.OK | wx.ICON_INFORMATION)
			return
		self.ActionNodes = []
		email_node = ujson.loads(self.email_node_template)
		email_node['id'] = self.nodes.get_node_id()
		email_node['z'] = self.actions_flow_id
		email_node['server'] = server
		email_node['port'] = str(self.port.GetValue())
		email_node['secure'] = self.secure.GetValue()
		email_node['name'] = to
		email_node['dname'] = 'a|'+email_node['id']+'|'+str(self.action_id)
		self.ActionNodes.append(email_node)
		payload_node = ujson.loads(self.payload_node_template)
		payload_node['id'] = self.nodes.get_node_id()
		payload_node['z'] = self.actions_flow_id
		payload_node['name'] = email_node['dname']
		payload_node['template'] = body
		payload_node['wires'] = [[email_node['id']]]
		self.ActionNodes.append(payload_node)
		topic_node = ujson.loads(self.topic_node_template)
		topic_node['id'] = self.nodes.get_node_id()
		topic_node['z'] = self.actions_flow_id
		topic_node['name'] = email_node['dname']
		topic_node['template'] = subject
		topic_node['wires'] = [[payload_node['id']]]
		self.ActionNodes.append(topic_node)
		if not self.repeat.GetValue() and not self.rate.GetValue():
			self.connector_id = topic_node['id']
		elif self.repeat.GetValue():
			repeat_node = ujson.loads(self.RepeatOptions.repeat_template)
			repeat_node['id'] = self.nodes.get_node_id()
			repeat_node['z'] = self.actions_flow_id
			repeat_node['name'] = email_node['dname']
			repeat_node['interval'] = str(self.interval.GetValue())
			repeat_node['intervalUnit'] = self.RepeatOptions.intervalUnit2[self.unit.GetSelection()]
			repeat_node['maximum'] = str(self.max.GetValue())
			repeat_node['wires'] = [[topic_node['id']]]
			self.connector_id = repeat_node['id']
			self.ActionNodes.append(repeat_node)
		elif self.rate.GetValue():
			rate_node = ujson.loads(self.RepeatOptions.rate_limit_template)
			rate_node['id'] = self.nodes.get_node_id()
			rate_node['z'] = self.actions_flow_id
			rate_node['name'] = email_node['dname']
			rate_node['rate'] = str(self.amount.GetValue())
			rate_node['nbRateUnits'] = str(self.time.GetValue())
			rate_node['rateUnits'] = self.RepeatOptions.rateUnit2[self.timeunit.GetSelection()]
			rate_node['wires'] = [[topic_node['id']]]
			self.connector_id = rate_node['id']
			self.ActionNodes.append(rate_node)
		self.credentials = {email_node['id']:{"userid":userid,"password":password}}
		self.EndModal(wx.OK)

class ActionPlaySound(wx.Dialog):
	def __init__(self, parent, edit):
		self.credentials = ''
		self.currentpath = parent.currentpath
		self.nodes = parent.nodes
		self.actions_flow_id = parent.actions_flow_id
		self.action_id = parent.available_actions_select.GetSelection()
		self.RepeatOptions = RepeatOptions()
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

		wx.Dialog.__init__(self, None, title = title, size=(550, 290))
		self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))

		panel = wx.Panel(self)

		self.path_sound = wx.TextCtrl(panel)
		self.button_select_sound = wx.Button(panel, label=_('File'))
		self.button_select_sound.Bind(wx.EVT_BUTTON, self.on_select_sound)

		self.repeat = wx.CheckBox(panel, label=_('Repeat'))
		self.repeat.Bind(wx.EVT_CHECKBOX, self.on_repeat)
		intervallabel = wx.StaticText(panel, label=_('Interval'))
		self.interval = wx.SpinCtrl(panel, min=1, max=100000, initial=1)
		self.unit = wx.Choice(panel, choices=self.RepeatOptions.intervalUnit, style=wx.CB_READONLY)
		self.unit.SetSelection(1)
		maxlabel = wx.StaticText(panel, label=_('Max.'))
		self.max = wx.SpinCtrl(panel, min=1, max=100000, initial=1)

		self.rate = wx.CheckBox(panel, label=_('Rate limit'))
		self.rate.Bind(wx.EVT_CHECKBOX, self.on_rate)
		ratelabel = wx.StaticText(panel, label=_('Rate'))
		self.amount = wx.SpinCtrl(panel, min=1, max=100000, initial=1)
		ratelabel2 = wx.StaticText(panel, label=_('time(s) per'))
		self.time = wx.SpinCtrl(panel, min=1, max=100000, initial=1)
		self.timeunit = wx.Choice(panel, choices=self.RepeatOptions.rateUnit, style=wx.CB_READONLY)
		self.timeunit.SetSelection(2)
		
		self.interval.Disable()
		self.unit.Disable()
		self.max.Disable()
		self.amount.Disable()
		self.time.Disable()
		self.timeunit.Disable()

		okBtn = wx.Button(panel, wx.ID_OK)
		okBtn.Bind(wx.EVT_BUTTON, self.OnOk)
		cancelBtn = wx.Button(panel, wx.ID_CANCEL)

		file = wx.BoxSizer(wx.HORIZONTAL)
		file.Add(self.path_sound, 1, wx.ALL, 5)
		file.Add(self.button_select_sound, 0, wx.ALL, 5)

		repeath = wx.BoxSizer(wx.HORIZONTAL)
		repeath.Add(intervallabel, 0, wx.ALL, 5)
		repeath.Add(self.interval, 0, wx.ALL, 5)
		repeath.Add(self.unit, 0, wx.ALL, 5)
		repeath.Add(maxlabel, 0, wx.ALL, 5)
		repeath.Add(self.max, 0, wx.ALL, 5)

		rate = wx.BoxSizer(wx.HORIZONTAL)
		rate.Add(ratelabel, 0, wx.ALL, 5)
		rate.Add(self.amount, 0, wx.ALL, 5)
		rate.Add(ratelabel2, 0, wx.ALL, 5)
		rate.Add(self.time, 0, wx.ALL, 5)
		rate.Add(self.timeunit, 0, wx.ALL, 5)

		ok_cancel = wx.BoxSizer(wx.HORIZONTAL)
		ok_cancel.Add((0, 0), 1, wx.ALL, 0)
		ok_cancel.Add(okBtn, 0, wx.RIGHT | wx.LEFT, 10)
		ok_cancel.Add(cancelBtn, 0, wx.RIGHT | wx.LEFT, 10)
		ok_cancel.Add((0, 0), 1, wx.ALL, 0)

		main = wx.BoxSizer(wx.VERTICAL)
		main.Add(file, 1, wx.ALL | wx.EXPAND, 0)
		main.AddSpacer(15)
		main.Add(self.repeat, 1, wx.RIGHT | wx.LEFT, 5)
		main.Add(repeath, 1, wx.RIGHT | wx.LEFT, 5)
		main.AddSpacer(10)
		main.Add(self.rate, 1, wx.RIGHT | wx.LEFT, 5)
		main.Add(rate, 1, wx.RIGHT | wx.LEFT, 5)
		main.Add((0, 0), 1, wx.ALL, 0)
		main.Add(ok_cancel, 0, wx.ALL | wx.EXPAND, 10)

		panel.SetSizer(main)

	def on_repeat(self, e):
		if self.repeat.GetValue():
			self.interval.Enable()
			self.unit.Enable()
			self.max.Enable()
			self.rate.SetValue(False)
			self.amount.Disable()
			self.time.Disable()
			self.timeunit.Disable()
		else:
			self.interval.Disable()
			self.unit.Disable()
			self.max.Disable()

	def on_rate(self, e):
		if self.rate.GetValue():
			self.amount.Enable()
			self.time.Enable()
			self.timeunit.Enable()
			self.repeat.SetValue(False)
			self.interval.Disable()
			self.unit.Disable()
			self.max.Disable()

		else:
			self.amount.Disable()
			self.time.Disable()
			self.timeunit.Disable()

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
		self.ActionNodes = []
		action_node = ujson.loads(self.play_sound_node_template)
		action_node['id'] = self.nodes.get_node_id()
		action_node['z'] = self.actions_flow_id
		action_node['name'] = 'a|'+action_node['id']+'|'+str(self.action_id)
		action_node['append'] = file
		self.ActionNodes.append(action_node)
		if not self.repeat.GetValue() and not self.rate.GetValue():
			self.connector_id = action_node['id']
		elif self.repeat.GetValue():
			repeat_node = ujson.loads(self.RepeatOptions.repeat_template)
			repeat_node['id'] = self.nodes.get_node_id()
			repeat_node['z'] = self.actions_flow_id
			repeat_node['name'] = action_node['name']
			repeat_node['interval'] = str(self.interval.GetValue())
			repeat_node['intervalUnit'] = self.RepeatOptions.intervalUnit2[self.unit.GetSelection()]
			repeat_node['maximum'] = str(self.max.GetValue())
			repeat_node['wires'] = [[action_node['id']]]
			self.connector_id = repeat_node['id']
			self.ActionNodes.append(repeat_node)
		elif self.rate.GetValue():
			rate_node = ujson.loads(self.RepeatOptions.rate_limit_template)
			rate_node['id'] = self.nodes.get_node_id()
			rate_node['z'] = self.actions_flow_id
			rate_node['name'] = action_node['name']
			rate_node['rate'] = str(self.amount.GetValue())
			rate_node['nbRateUnits'] = str(self.time.GetValue())
			rate_node['rateUnits'] = self.RepeatOptions.rateUnit2[self.timeunit.GetSelection()]
			rate_node['wires'] = [[action_node['id']]]
			self.connector_id = rate_node['id']
			self.ActionNodes.append(rate_node)
		self.EndModal(wx.OK)

class ActionRunCommand(wx.Dialog):
	def __init__(self, parent, edit):
		self.credentials = ''
		self.currentpath = parent.currentpath
		self.nodes = parent.nodes
		self.actions_flow_id = parent.actions_flow_id
		self.action_id = parent.available_actions_select.GetSelection()
		self.RepeatOptions = RepeatOptions()
		self.run_command_node_template = '''
		    {
		        "id": "",
		        "type": "exec",
		        "z": "",
		        "command": "",
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

		if edit == 0: title = _('Add command')
		else: title = _('Edit command')

		wx.Dialog.__init__(self, None, title = title, size=(550, 350))
		self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))

		panel = wx.Panel(self)

		commandlabel = wx.StaticText(panel, label=_('Command'))
		self.command = wx.TextCtrl(panel)
		argumentslabel = wx.StaticText(panel, label=_('Arguments'))
		self.arguments = wx.TextCtrl(panel)

		self.repeat = wx.CheckBox(panel, label=_('Repeat'))
		self.repeat.Bind(wx.EVT_CHECKBOX, self.on_repeat)
		intervallabel = wx.StaticText(panel, label=_('Interval'))
		self.interval = wx.SpinCtrl(panel, min=1, max=100000, initial=1)
		self.unit = wx.Choice(panel, choices=self.RepeatOptions.intervalUnit, style=wx.CB_READONLY)
		self.unit.SetSelection(1)
		maxlabel = wx.StaticText(panel, label=_('Max.'))
		self.max = wx.SpinCtrl(panel, min=1, max=100000, initial=1)

		self.rate = wx.CheckBox(panel, label=_('Rate limit'))
		self.rate.Bind(wx.EVT_CHECKBOX, self.on_rate)
		ratelabel = wx.StaticText(panel, label=_('Rate'))
		self.amount = wx.SpinCtrl(panel, min=1, max=100000, initial=1)
		ratelabel2 = wx.StaticText(panel, label=_('time(s) per'))
		self.time = wx.SpinCtrl(panel, min=1, max=100000, initial=1)
		self.timeunit = wx.Choice(panel, choices=self.RepeatOptions.rateUnit, style=wx.CB_READONLY)
		self.timeunit.SetSelection(2)

		okBtn = wx.Button(panel, wx.ID_OK)
		okBtn.Bind(wx.EVT_BUTTON, self.OnOk)
		cancelBtn = wx.Button(panel, wx.ID_CANCEL)

		command = wx.BoxSizer(wx.HORIZONTAL)
		command.Add(commandlabel, 0, wx.ALL, 5)
		command.Add(self.command, 1, wx.ALL, 5)

		arguments = wx.BoxSizer(wx.HORIZONTAL)
		arguments.Add(argumentslabel, 0, wx.ALL, 5)
		arguments.Add(self.arguments, 1, wx.ALL, 5)

		repeath = wx.BoxSizer(wx.HORIZONTAL)
		repeath.Add(intervallabel, 0, wx.ALL, 5)
		repeath.Add(self.interval, 0, wx.ALL, 5)
		repeath.Add(self.unit, 0, wx.ALL, 5)
		repeath.Add(maxlabel, 0, wx.ALL, 5)
		repeath.Add(self.max, 0, wx.ALL, 5)

		rate = wx.BoxSizer(wx.HORIZONTAL)
		rate.Add(ratelabel, 0, wx.ALL, 5)
		rate.Add(self.amount, 0, wx.ALL, 5)
		rate.Add(ratelabel2, 0, wx.ALL, 5)
		rate.Add(self.time, 0, wx.ALL, 5)
		rate.Add(self.timeunit, 0, wx.ALL, 5)

		ok_cancel = wx.BoxSizer(wx.HORIZONTAL)
		ok_cancel.Add((0, 0), 1, wx.ALL, 0)
		ok_cancel.Add(okBtn, 0, wx.RIGHT | wx.LEFT, 10)
		ok_cancel.Add(cancelBtn, 0, wx.RIGHT | wx.LEFT, 10)
		ok_cancel.Add((0, 0), 1, wx.ALL, 0)

		main = wx.BoxSizer(wx.VERTICAL)
		main.Add(command, 1, wx.ALL | wx.EXPAND, 10)
		main.Add(arguments, 1, wx.ALL | wx.EXPAND, 10)
		main.AddSpacer(15)
		main.Add(self.repeat, 1, wx.RIGHT | wx.LEFT, 5)
		main.Add(repeath, 1, wx.RIGHT | wx.LEFT, 5)
		main.AddSpacer(10)
		main.Add(self.rate, 1, wx.RIGHT | wx.LEFT, 5)
		main.Add(rate, 1, wx.RIGHT | wx.LEFT, 5)
		main.Add((0, 0), 1, wx.ALL, 0)
		main.Add(ok_cancel, 0, wx.ALL | wx.EXPAND, 10)

		panel.SetSizer(main)

		if edit != 0:
			self.command.SetValue(edit[0])
			if edit[1] != 0: self.arguments.SetValue(edit[1])

		self.interval.Disable()
		self.unit.Disable()
		self.max.Disable()
		self.amount.Disable()
		self.time.Disable()
		self.timeunit.Disable()

	def on_repeat(self, e):
		if self.repeat.GetValue():
			self.interval.Enable()
			self.unit.Enable()
			self.max.Enable()
			self.rate.SetValue(False)
			self.amount.Disable()
			self.time.Disable()
			self.timeunit.Disable()
		else:
			self.interval.Disable()
			self.unit.Disable()
			self.max.Disable()

	def on_rate(self, e):
		if self.rate.GetValue():
			self.amount.Enable()
			self.time.Enable()
			self.timeunit.Enable()
			self.repeat.SetValue(False)
			self.interval.Disable()
			self.unit.Disable()
			self.max.Disable()
		else:
			self.amount.Disable()
			self.time.Disable()
			self.timeunit.Disable()

	def OnOk(self,e):
		command = self.command.GetValue()
		arguments = self.arguments.GetValue()
		if not command:
			wx.MessageBox(_('You have to provide a command.'), 'Info', wx.OK | wx.ICON_INFORMATION)
			return
		self.ActionNodes = []
		run_command_node = ujson.loads(self.run_command_node_template)
		run_command_node['id'] = self.nodes.get_node_id()
		run_command_node['z'] = self.actions_flow_id
		run_command_node['name'] = 'a|'+run_command_node['id']+'|'+str(self.action_id)
		run_command_node['command'] = command
		run_command_node['append'] = arguments
		self.ActionNodes.append(run_command_node)
		if not self.repeat.GetValue() and not self.rate.GetValue():
			self.connector_id = run_command_node['id']
		elif self.repeat.GetValue():
			repeat_node = ujson.loads(self.RepeatOptions.repeat_template)
			repeat_node['id'] = self.nodes.get_node_id()
			repeat_node['z'] = self.actions_flow_id
			repeat_node['name'] = run_command_node['name']
			repeat_node['interval'] = str(self.interval.GetValue())
			repeat_node['intervalUnit'] = self.RepeatOptions.intervalUnit2[self.unit.GetSelection()]
			repeat_node['maximum'] = str(self.max.GetValue())
			repeat_node['wires'] = [[run_command_node['id']]]
			self.connector_id = repeat_node['id']
			self.ActionNodes.append(repeat_node)
		elif self.rate.GetValue():
			rate_node = ujson.loads(self.RepeatOptions.rate_limit_template)
			rate_node['id'] = self.nodes.get_node_id()
			rate_node['z'] = self.actions_flow_id
			rate_node['name'] = run_command_node['name']
			rate_node['rate'] = str(self.amount.GetValue())
			rate_node['nbRateUnits'] = str(self.time.GetValue())
			rate_node['rateUnits'] = self.RepeatOptions.rateUnit2[self.timeunit.GetSelection()]
			rate_node['wires'] = [[run_command_node['id']]]
			self.connector_id = rate_node['id']
			self.ActionNodes.append(rate_node)
		self.EndModal(wx.OK)

class ActionSendTelegram(wx.Dialog):
	def __init__(self, parent, edit):
		self.credentials = ''
		self.nodes = parent.nodes
		self.actions_flow_id = parent.actions_flow_id
		self.telegramid = parent.telegramid
		self.action_id = parent.available_actions_select.GetSelection()
		self.RepeatOptions = RepeatOptions()
		self.telegram_node_template = '''
		    {
		        "id": "",
		        "type": "chatbot-telegram-send",
		        "z": "",
		        "bot": "",
		        "botProduction": "",
		        "track": false,
		        "passThrough": false,
		        "outputs": 0,
		        "x": 380,
		        "y": 120,
		        "wires": []
		    }'''
		self.text_node_template = '''
		    {
		        "id": "",
		        "type": "chatbot-message",
		        "z": "",
		        "name": "",
		        "message": [
		            {
		                "message": ""
		            }
		        ],
		        "answer": false,
		        "silent": false,
		        "x": 380,
		        "y": 120,
		        "wires": [[]]
		    }'''
		self.conversation_node_template = '''
		    {
		        "id": "",
		        "type": "chatbot-conversation",
		        "z": "",
		        "name": "",
		        "botTelegram": "",
		        "botTelegramProduction": "",
		        "botSlack": "",
		        "botSlackProduction": "",
		        "botFacebook": "",
		        "botFacebookProduction": "",
		        "botViber": "",
		        "botViberProduction": "",
		        "botUniversal": "",
		        "botUniversalProduction": "",
		        "botTwilio": "",
		        "botTwilioProduction": "",
		        "chatId": "",
		        "transport": "telegram",
		        "messageId": "",
		        "contextMessageId": false,
		        "store": "",
		        "x": 380,
		        "y": 120,
		        "wires": [[]]
		    }'''
		self.payload_node_template = '''
		    {
		        "id": "",
		        "type": "template",
		        "z": "",
		        "name": "",
		        "field": "payload",
		        "fieldType": "msg",
		        "format": "handlebars",
		        "syntax": "mustache",
		        "template": "",
		        "output": "str",
		        "x": 380,
		        "y": 120,
		        "wires": [
		            []
		        ]
		    }'''

		if edit == 0: title = _('Add Telegram action')
		else: title = _('Edit Telegram action')

		wx.Dialog.__init__(self, None, title = title, size=(710, 420))
		self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))

		panel = wx.Panel(self)

		chatidlabel = wx.StaticText(panel, label=_('Chat ID'))
		self.chatid = wx.TextCtrl(panel)

		msglabel = wx.StaticText(panel, label=_('Message'))
		self.msg = wx.TextCtrl(panel, style=wx.TE_MULTILINE, size=(-1,60))

		self.addsk = wx.Button(panel, label=_('Add Signal K key value'))
		self.addsk.Bind(wx.EVT_BUTTON, self.on_addsk)

		self.repeat = wx.CheckBox(panel, label=_('Repeat'))
		self.repeat.Bind(wx.EVT_CHECKBOX, self.on_repeat)
		intervallabel = wx.StaticText(panel, label=_('Interval'))
		self.interval = wx.SpinCtrl(panel, min=1, max=100000, initial=1)
		self.unit = wx.Choice(panel, choices=self.RepeatOptions.intervalUnit, style=wx.CB_READONLY)
		self.unit.SetSelection(1)
		maxlabel = wx.StaticText(panel, label=_('Max.'))
		self.max = wx.SpinCtrl(panel, min=1, max=100000, initial=1)

		self.rate = wx.CheckBox(panel, label=_('Rate limit'))
		self.rate.Bind(wx.EVT_CHECKBOX, self.on_rate)
		ratelabel = wx.StaticText(panel, label=_('Rate'))
		self.amount = wx.SpinCtrl(panel, min=1, max=100000, initial=1)
		ratelabel2 = wx.StaticText(panel, label=_('time(s) per'))
		self.time = wx.SpinCtrl(panel, min=1, max=100000, initial=1)
		self.timeunit = wx.Choice(panel, choices=self.RepeatOptions.rateUnit, style=wx.CB_READONLY)
		self.timeunit.SetSelection(2)
		
		self.interval.Disable()
		self.unit.Disable()
		self.max.Disable()
		self.amount.Disable()
		self.time.Disable()
		self.timeunit.Disable()

		okBtn = wx.Button(panel, wx.ID_OK)
		okBtn.Bind(wx.EVT_BUTTON, self.OnOk)
		cancelBtn = wx.Button(panel, wx.ID_CANCEL)

		subject = wx.BoxSizer(wx.HORIZONTAL)
		subject.Add(chatidlabel, 0, wx.ALL, 5)
		subject.Add(self.chatid, 0, wx.ALL, 5)

		body = wx.BoxSizer(wx.HORIZONTAL)
		body.Add(msglabel, 0, wx.ALL, 5)
		body.Add(self.msg, 1, wx.ALL, 5)

		addsk = wx.BoxSizer(wx.HORIZONTAL)
		addsk.Add((0, 0), 1, wx.ALL, 5)
		addsk.Add(self.addsk, 1, wx.ALL, 5)

		repeath = wx.BoxSizer(wx.HORIZONTAL)
		repeath.Add(intervallabel, 0, wx.ALL, 5)
		repeath.Add(self.interval, 0, wx.ALL, 5)
		repeath.Add(self.unit, 0, wx.ALL, 5)
		repeath.Add(maxlabel, 0, wx.ALL, 5)
		repeath.Add(self.max, 0, wx.ALL, 5)

		rate = wx.BoxSizer(wx.HORIZONTAL)
		rate.Add(ratelabel, 0, wx.ALL, 5)
		rate.Add(self.amount, 0, wx.ALL, 5)
		rate.Add(ratelabel2, 0, wx.ALL, 5)
		rate.Add(self.time, 0, wx.ALL, 5)
		rate.Add(self.timeunit, 0, wx.ALL, 5)

		ok_cancel = wx.BoxSizer(wx.HORIZONTAL)
		ok_cancel.Add((0, 0), 1, wx.ALL, 0)
		ok_cancel.Add(okBtn, 0, wx.RIGHT | wx.LEFT, 10)
		ok_cancel.Add(cancelBtn, 0, wx.RIGHT | wx.LEFT, 10)
		ok_cancel.Add((0, 0), 1, wx.ALL, 0)

		main = wx.BoxSizer(wx.VERTICAL)
		main.Add(subject, 1, wx.ALL, 5)
		main.Add(body, 1, wx.ALL | wx.EXPAND, 5)
		main.Add(addsk, 1, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)
		main.AddSpacer(15)
		main.Add(self.repeat, 1, wx.RIGHT | wx.LEFT, 5)
		main.Add(repeath, 1, wx.RIGHT | wx.LEFT, 5)
		main.AddSpacer(10)
		main.Add(self.rate, 1, wx.RIGHT | wx.LEFT, 5)
		main.Add(rate, 1, wx.RIGHT | wx.LEFT, 5)
		main.Add((0, 0), 1, wx.ALL, 0)
		main.Add(ok_cancel, 0, wx.ALL | wx.EXPAND, 10)

		panel.SetSizer(main)
		self.Centre()

	def on_addsk(self, e):
		oldkey = False
		dlg = selectKey(oldkey,1)
		res = dlg.ShowModal()
		if res == wx.OK:
			self.msg.AppendText('{{flow.'+dlg.selected_vessel+'.'+dlg.selected_key+'}}')
		dlg.Destroy()

	def on_repeat(self, e):
		if self.repeat.GetValue():
			self.interval.Enable()
			self.unit.Enable()
			self.max.Enable()
			self.rate.SetValue(False)
			self.amount.Disable()
			self.time.Disable()
			self.timeunit.Disable()
		else:
			self.interval.Disable()
			self.unit.Disable()
			self.max.Disable()

	def on_rate(self, e):
		if self.rate.GetValue():
			self.amount.Enable()
			self.time.Enable()
			self.timeunit.Enable()
			self.repeat.SetValue(False)
			self.interval.Disable()
			self.unit.Disable()
			self.max.Disable()

		else:
			self.amount.Disable()
			self.time.Disable()
			self.timeunit.Disable()

	def OnOk(self,e):
		chatid = self.chatid.GetValue()
		if not chatid:
			wx.MessageBox(_('Send "/start" from your bot and you will get your chat ID.'), 'Info', wx.OK | wx.ICON_INFORMATION)
			return
		msg = self.msg.GetValue()
		if not msg:
			wx.MessageBox(_('Write a message to send.'), 'Info', wx.OK | wx.ICON_INFORMATION)
			return
		self.ActionNodes = []
		telegram_node = ujson.loads(self.telegram_node_template)
		telegram_node['z'] = self.actions_flow_id
		telegram_node['bot'] = self.telegramid
		text_node = ujson.loads(self.text_node_template)
		text_node['z'] = self.actions_flow_id
		text_node['id'] = self.nodes.get_node_id()
		subid0 = text_node['id'].split('.')
		subid = subid0[0]
		telegram_node['id'] = self.nodes.get_node_id(subid)
		text_node['name'] = 'a|'+telegram_node['id']+'|'+str(self.action_id)
		text_node['wires'] = [[telegram_node['id']]]
		self.ActionNodes.append(telegram_node)
		self.ActionNodes.append(text_node)
		conversation_node = ujson.loads(self.conversation_node_template)
		conversation_node['id'] = self.nodes.get_node_id()
		conversation_node['z'] = self.actions_flow_id
		conversation_node['name'] = text_node['name']
		conversation_node['botTelegram'] = self.telegramid
		conversation_node['chatId'] = chatid
		conversation_node['wires'] = [[text_node['id']]]
		self.ActionNodes.append(conversation_node)
		payload_node = ujson.loads(self.payload_node_template)
		payload_node['id'] = self.nodes.get_node_id()
		payload_node['z'] = self.actions_flow_id
		payload_node['name'] = text_node['name']
		payload_node['template'] = msg
		payload_node['wires'] = [[conversation_node['id']]]
		self.ActionNodes.append(payload_node)
		if not self.repeat.GetValue() and not self.rate.GetValue():
			self.connector_id = payload_node['id']
		elif self.repeat.GetValue():
			repeat_node = ujson.loads(self.RepeatOptions.repeat_template)
			repeat_node['id'] = self.nodes.get_node_id()
			repeat_node['z'] = self.actions_flow_id
			repeat_node['name'] = text_node['name']
			repeat_node['interval'] = str(self.interval.GetValue())
			repeat_node['intervalUnit'] = self.RepeatOptions.intervalUnit2[self.unit.GetSelection()]
			repeat_node['maximum'] = str(self.max.GetValue())
			repeat_node['wires'] = [[payload_node['id']]]
			self.connector_id = repeat_node['id']
			self.ActionNodes.append(repeat_node)
		elif self.rate.GetValue():
			rate_node = ujson.loads(self.RepeatOptions.rate_limit_template)
			rate_node['id'] = self.nodes.get_node_id()
			rate_node['z'] = self.actions_flow_id
			rate_node['name'] = text_node['name']
			rate_node['rate'] = str(self.amount.GetValue())
			rate_node['nbRateUnits'] = str(self.time.GetValue())
			rate_node['rateUnits'] = self.RepeatOptions.rateUnit2[self.timeunit.GetSelection()]
			rate_node['wires'] = [[payload_node['id']]]
			self.connector_id = rate_node['id']
			self.ActionNodes.append(rate_node)
		self.EndModal(wx.OK)