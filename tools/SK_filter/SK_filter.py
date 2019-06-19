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
import wx, os, sys, subprocess, ConfigParser, webbrowser, time, ujson

op_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../..')
sys.path.append(op_folder+'/classes')
from conf import Conf
from language import Language
from SK_settings import SK_settings
from nodes_SK_filter import Nodes, TriggerFilterSK, ActionEndFilterSignalk

class MyFrame(wx.Frame):
	def __init__(self):
		self.conf = Conf()
		self.home = self.conf.home
		self.op_folder = self.conf.get('GENERAL', 'op_folder')
		self.currentpath = self.op_folder
		self.help_bmp = wx.Bitmap(self.op_folder + "/static/icons/help-browser.png", wx.BITMAP_TYPE_ANY)
		Language(self.conf)
		self.SK_settings = SK_settings(self.conf)	
		
		self.available_operators = ['eq', 'neq', 'lt', 'lte', 'gt', 'gte','btwn', 'cont', 'true', 'false', 'null', 'nnull', 'empty', 'nempty']
		self.available_conditions = ['=', '!=', '<', '<=', '>', '>=', _('is between'), _('contains'), _('is true'), ('is false'), _('is null'), _('is not null'), _('is empty'), _('is not empty')]		

		self.available_source = [_('label'),_('type'),_('pgn'),_('src'),_('sentence'),_('talker')]
		self.available_source_nr = ['label','type','pgn','src','sentence','talker']

		wx.Frame.__init__(self, None, title=_('SignalK input filter (uses node-red)'), size=(710,460))
		
		self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
		
		self.icon = wx.Icon(self.op_folder+'/static/icons/openplotter.ico', wx.BITMAP_TYPE_ICO)
		self.SetIcon(self.icon)

		self.list_triggers = wx.ListCtrl(self, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
		self.list_triggers.InsertColumn(0, _('Signal K key'), width=240)
		self.list_triggers.InsertColumn(1, _('Source Type'), width=120)
		self.list_triggers.InsertColumn(2, _('Condition'), width=70)
		self.list_triggers.InsertColumn(3, _('Value'), width=90)
		self.list_triggers.InsertColumn(4, _('Value2'), width=60)

		self.list_triggers.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_select_triggers)
		self.list_triggers.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.on_deselected_triggers)
		self.list_triggers.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_edit_triggers)

		add_trigger = wx.Button(self, label=_('add'))
		add_trigger.Bind(wx.EVT_BUTTON, self.on_add_trigger)

		delete_trigger = wx.Button(self, label=_('delete'))
		delete_trigger.Bind(wx.EVT_BUTTON, self.on_delete_trigger)

		diagnostic = wx.Button(self, label=_('SK Diagnostic'))
		diagnostic.Bind(wx.EVT_BUTTON, self.on_diagnostic_SK)

		reset_skf = wx.Button(self, label=_('Restart'))
		reset_skf.Bind(wx.EVT_BUTTON, self.reset_sensors)

		help_button = wx.BitmapButton(self, bitmap=self.help_bmp, size=(self.help_bmp.GetWidth()+40, self.help_bmp.GetHeight()+10))
		help_button.Bind(wx.EVT_BUTTON, self.on_help_filter)

		apply_changes = wx.Button(self, label=_('Apply changes'))
		apply_changes.Bind(wx.EVT_BUTTON, self.on_apply_changes_triggers)
		cancel_changes = wx.Button(self, label=_('Cancel changes'))
		cancel_changes.Bind(wx.EVT_BUTTON, self.on_cancel_changes_triggers)

		hlistbox_but = wx.BoxSizer(wx.VERTICAL)
		hlistbox_but.Add(add_trigger, 0, wx.ALL, 5)
		hlistbox_but.Add(delete_trigger, 0, wx.ALL, 5)

		hlistbox = wx.BoxSizer(wx.HORIZONTAL)
		hlistbox.Add(self.list_triggers, 1, wx.ALL | wx.EXPAND, 5)
		hlistbox.Add(hlistbox_but, 0, wx.RIGHT | wx.LEFT, 0)

		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(help_button, 0, wx.ALL, 0)
		hbox.Add(diagnostic, 0, wx.RIGHT | wx.LEFT, 5)
		hbox.Add(reset_skf, 0, wx.RIGHT | wx.LEFT, 5)
		hbox.AddStretchSpacer(1)
		hbox.Add(apply_changes, 0, wx.RIGHT | wx.LEFT, 5)
		hbox.Add(cancel_changes, 0, wx.RIGHT | wx.LEFT, 5)

		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.Add(hlistbox, 1, wx.ALL | wx.EXPAND, 0)
		vbox.Add(hbox, 0, wx.ALL | wx.EXPAND, 5)

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
		self.remove_credentials = []
		self.on_print_triggers()

	def on_print_triggers(self):
		self.list_triggers.DeleteAllItems()
		self.selected_trigger = -1
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
						if node['type'] == 'signalk-subscribe' or 'signalk-input-handler': 
							path = node['path']
							field2 = node['context']
							nsrc = node['source']
				if node['id'] == trigger["trigger_node_out_id"]:
					if 'func' in node:
						if 	node['func'] == 'return msg;': enabled = True
					else:
						enabled = True
				self.nodeid = node['id']
			self.list_triggers.Append([path.decode('utf8'), '', '', '', ''])
			self.last = self.list_triggers.GetItemCount()-1
			self.selected_trigger = self.list_triggers.GetItemCount()-1
			self.on_print_conditions()

	def on_print_conditions(self):
		if self.selected_trigger == -1: return
		conditions = self.actions_flow_tree[self.selected_trigger]["conditions"]
		triggertype = self.actions_flow_tree[self.selected_trigger]["type"]
		for condition in conditions:
			name = "c|"+condition["condition_node_out_id"]+"|"+condition["operator"]
			field2 = ''
			field3 = ''
			value2 = ''
			for node in self.conditions_flow_nodes:
				if 'name' in node and name == node['name']:
					if node['type'] == 'switch':
						if 'property' in node:
							property = node['property']
						else:
							property =''
						if 'v' in node['rules'][0]:
							if triggertype == '5':
								try:
									seconds = float(node['rules'][0]['v'])/1000
									local_time = datetime.fromtimestamp(seconds)
									field2 = local_time.strftime("%Y-%m-%d %H:%M:%S")
								except: pass
							else: value = node['rules'][0]['v']
						if 't' in node['rules'][0] and node['rules'][0]['t'] == 'btwn':
							if 'v2' in node['rules'][0]:
								if triggertype == '5':
									try:
										seconds = float(node['rules'][0]['v2'])/1000
										local_time = datetime.fromtimestamp(seconds)
										field3 = local_time.strftime("%Y-%m-%d %H:%M:%S")
									except: pass
								else: value2 = node['rules'][0]['v2']
			self.list_triggers.SetStringItem(self.last,1,property.decode('utf8'))
			self.list_triggers.SetStringItem(self.last,2,self.available_conditions[int(condition["operator"])].decode('utf8'))
			self.list_triggers.SetStringItem(self.last,3,value.decode('utf8'))
			self.list_triggers.SetStringItem(self.last,4,value2.decode('utf8'))
			self.last = self.list_triggers.GetItemCount()-1

	def on_select_triggers(self, e):
		self.selected_trigger = self.list_triggers.GetFirstSelected()
	
	def on_deselected_triggers(self, e):
		self.on_print_triggers()

	def on_edit_triggers(self, e):
		if self.selected_trigger == -1: return
		node = self.actions_flow_tree[self.selected_trigger]['trigger_node_out_id']
		self.nodetrigger = node
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

		#find connected condition
		nodec = self.actions_flow_tree[self.selected_trigger]['conditions'][self.selected_condition]['condition_node_out_id']
		typec = self.actions_flow_tree[self.selected_trigger]['conditions'][self.selected_condition]['operator']
		name = 'c|'+nodec+'|'+typec
		edit2 = ''
		for i in self.conditions_flow_nodes:
			if 'name' in i:
				if i['name'] == name: 
					edit2 = i['rules'][0]
					src_property = (i['property'].split('.'))[1]
					self.edit_cond = i

		self.edit_add_trigger(edit,edit2,src_property)

	def on_add_trigger(self, e):
		self.edit_add_trigger(0,0,0)

	def edit_add_trigger(self, edit, edit2, src_property):
		trigger = 0
		dlg = TriggerFilterSK(self,edit,edit2,trigger,src_property)
		res = dlg.ShowModal()
		if res == wx.OK:
			if not edit:
				for i in dlg.TriggerNodes:
					self.triggers_flow_nodes.append(i)
					if 'name' in i: items = i['name'].split('|')
					self.actions_flow_tree.append({"trigger_node_out_id": items[1],"type": items[2],"conditions": []})					
				j=0
				for i in self.actions_flow_tree:
					if i["trigger_node_out_id"] == items[1]:
						self.act_action_flow_tree = j
					j += 1
				trigger_id = items[1]
				self.conditions_flow_nodes.append(dlg.ConditionNode)
				items = dlg.ConditionNode['name'].split('|')
				self.actions_flow_tree[self.act_action_flow_tree]['conditions'].append({"condition_node_out_id": items[1],"operator": items[2],"actions": []})
				self.condition_id = items[1]
				for i in self.triggers_flow_nodes:
					if i['id'] == trigger_id: i['wires'][0].append(dlg.condition_connector_id)				
				self.add_action()								
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
				#condition
				self.edit_cond['rules'] = dlg.ConditionNode['rules']
				self.edit_cond['property'] = dlg.ConditionNode['property']
				namesplit = self.edit_cond['name'].split('|')
				operator = self.available_operators.index(self.edit_cond['rules'][0]['t'])
				self.edit_cond['name'] = namesplit[0]+'|'+namesplit[1]+'|'+str(operator)

				for i in self.actions_flow_tree[self.selected_trigger]['conditions']:
					if 'condition_node_out_id' in i:
						if i['condition_node_out_id'] == namesplit[1]:
							i['operator'] = str(operator)
				
			self.on_print_triggers()
			last = self.list_triggers.GetItemCount()-1
				
		dlg.Destroy()

	def add_action(self):
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
		
		ActionNodes = []
		sk_node = ujson.loads(self.sk_node_template)
		sk_node['id'] = self.nodes.get_node_id()
		sk_node['z'] = self.actions_flow_id
		sk_node['name'] = 'a|'+sk_node['id']+'|0'
		ActionNodes.append(sk_node)
		action_connector_id = sk_node['id']
							
		for i in ActionNodes:
			self.actions_flow_nodes.append(i)
			if 'dname' in i: items = i['dname'].split('|')
			elif 'name' in i: items = i['name'].split('|')
		self.actions_flow_tree[self.act_action_flow_tree]['conditions'][0]['actions'].append({"action_node_out_id": items[1],"type": items[2]})
		for i in self.conditions_flow_nodes:
			if i['id'] == self.condition_id: i['wires'][0].append(action_connector_id)

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

	def on_apply_changes_triggers(self, e):
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

	def on_cancel_changes_triggers(self, e):
		self.read_triggers()

	def on_help_filter(self, e):
		url = self.currentpath+"/docs/html/tools/filter_signalk_inputs.html"
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

	def ShowStatusBar(self, w_msg, colour):
		#self.GetStatusBar().SetForegroundColour(colour)
		#self.SetStatusText.value = w_msg
		pass

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
		
	def on_diagnostic_SK(self, e):
		subprocess.call(['pkill', '-f', 'diagnostic-SK-input.py'])
		subprocess.Popen(['python', self.op_folder + '/diagnostic-SK-input.py'])

	def reset_sensors(self,event):
		pass

app = wx.App()
MyFrame().Show()
app.MainLoop()
