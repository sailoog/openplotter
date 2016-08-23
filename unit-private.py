#!/usr/bin/env python

# This file is part of Openplotter.
# Copyright (C) 2015 by sailoog <https://github.com/sailoog/openplotter>
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

import wx, sys, socket, time, webbrowser, serial, requests, json,websocket,threading,logging
from classes.paths import Paths
from classes.conf import Conf
from classes.language import Language

class MyFrame(wx.Frame):
		
	def __init__(self):
		

		logging.basicConfig()
		self.buffer=[]
		self.sortCol=0
	
		self.home=Paths().home
		self.currentpath=Paths().currentpath
		self.conf=Conf()

		Language(self.conf.get('GENERAL','lang'))

		self.data_SK_unit=''
		with open(self.home+'/.config/openplotter/classes/keyswithmetadata.json') as data_file:
			self.data_SK_unit = json.load(data_file)

		self.data_SK_unit_private=''
		with open(self.home+'/.config/openplotter/classes/privatekeyswithmetadata.json') as data_file:
			self.data_SK_unit_private = json.load(data_file)
		
		wx.Frame.__init__(self, None, title='diagnostic SignalK input', size=(650,435))
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		panel = wx.Panel(self, wx.ID_ANY)

		self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
		
		self.icon = wx.Icon(self.currentpath+'/openplotter.ico', wx.BITMAP_TYPE_ICO)
		self.SetIcon(self.icon)

		self.list = wx.ListCtrl(panel, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
		self.list.InsertColumn(0, _('SignalK'), width=400)
		self.list.InsertColumn(1, _('SK_Unit'), width=80)
		self.list.InsertColumn(2, _('Unit'), width=80)
		self.list.InsertColumn(3, _('Description'), width=500)

		self.sort_UnitSK =wx.Button(panel, label=_('Unit SK'))
		self.sort_UnitSK.Bind(wx.EVT_BUTTON, self.on_sort_UnitSK)

		self.sort_Unit =wx.Button(panel, label=_('Unit'))
		self.Bind(wx.EVT_BUTTON, self.on_sort_Unit, self.sort_Unit)

		self.sort_SK =wx.Button(panel, label=_('Sort SK'))
		self.sort_SK.Bind(wx.EVT_BUTTON, self.on_sort_SK)

		self.change_selected =wx.Button(panel, label=_('change selected'))
		self.change_selected.Bind(wx.EVT_BUTTON, self.on_change_selected)
		
		list_convert=['m m','m ft','m nm','m km','Pa Pa','Pa hPa','Pa Bar','rad rad','rad deg','m/s kn','m/s m/s','m/s kmh','m/s mph','m3 dm3','m3 gal','s h','s d','s y','K K','K C','K F']
		self.select_Unit_t=wx.StaticText(panel, label=_('convert'), pos=(190, 125))
		self.select_Unit= wx.ComboBox(panel, choices=list_convert, style=wx.CB_READONLY, size=(150, 32), pos=(190, 150))
		
		
		vbox = wx.BoxSizer(wx.VERTICAL)
		hlistbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hlistbox.Add(self.list, 1, wx.ALL|wx.EXPAND, 5)
		hbox.Add(self.sort_SK, 0, wx.RIGHT|wx.LEFT, 5)
		hbox.Add(self.sort_UnitSK, 0, wx.RIGHT|wx.LEFT, 5)
		hbox.Add(self.sort_Unit, 0, wx.RIGHT|wx.LEFT, 5)
		hbox.Add(self.change_selected, 0, wx.RIGHT|wx.LEFT, 5)
		hbox.Add(self.select_Unit_t, 0, wx.LEFT|wx.TOP, 5)
		hbox.Add(self.select_Unit, 0, wx.RIGHT|wx.LEFT, 5)
		vbox.Add(hlistbox, 1, wx.ALL|wx.EXPAND, 0)
		vbox.Add(hbox, 0, wx.ALL|wx.EXPAND, 0)
		panel.SetSizer(vbox)
		
		self.CreateStatusBar()

		self.read()

		self.Show(True)

		self.status=''
		self.data=[]
		self.baudc=0
		self.baud=0

	def read(self):
		index=0
		self.list_SK=[]
		for i in self.data_SK_unit_private:
			if 'units' in self.data_SK_unit_private[i]:
				if 'description' in self.data_SK_unit_private[i]:
					self.list_SK.append([str(i),str(self.data_SK_unit[i]['units']),str(self.data_SK_unit_private[i]['units']),str(self.data_SK_unit_private[i]['description'])])
				else:
					self.list_SK.append([str(i),str(self.data_SK_unit[i]['units']),str(self.data_SK_unit_private[i]['units']),''])

		self.sorting()			
		
	def lookup_star(self,name):			
		skip=-1
		index=0
		st=''
		for i in name.split('.'):
			if index>-1:
				if skip==0: 
					st+='.*'
				else:
					if i in ['propulsion','inventory']: skip=1
					elif i == 'resources':skip=2
					st+='.'+i
			index+=1
			skip-=1
					
		st=st[1:]	
		self.SK_unit=''
		self.SK_description=''
		try:
			self.SK_unit=self.data_SK_unit[st]['units']
			self.SK_description=self.data_SK_unit[st]['description']
		except:
			print 'no unit for ',st
			
	def on_sort_Unit(self, e):
		self.sortCol=2
		self.sorting()			

	def on_sort_UnitSK(self, e):
		self.sortCol=1
		self.sorting()			

	def on_sort_SK(self, e):
		self.sortCol=0
		self.sorting()

	def on_change_selected(self, e):
		list_select=[]
		item = self.list.GetFirstSelected()
		while item != -1:
			# do something with the item
			list_select.append(self.get_by_index(item))
			item = self.list.GetNextSelected(item)

		orig_unit_t=self.select_Unit.GetValue()
		if len(orig_unit_t)>2:
			orig_unit=orig_unit_t.split(' ')
			OK=True
			for i in list_select:
				if orig_unit[0]!=i[1]: OK=False
			
			if OK:
				for i in list_select:
					self.data_SK_unit_private[i[0]]['units']=orig_unit[1]
					#print self.data_SK_unit_private[i[0]]
				with open(self.home+'/.config/openplotter/classes/privatekeyswithmetadata.json','w') as data_file:
					json.dump(self.data_SK_unit_private, data_file)

				self.data_SK_unit_private=[]
				with open(self.home+'/.config/openplotter/classes/privatekeyswithmetadata.json') as data_file:
					self.data_SK_unit_private = json.load(data_file)
				self.read()			
			
	def get_by_index(self,item):
		index=0
		for i in self.list_SK:
			if index==item:
				return i
			index += 1
		return False
	
				
	def sorting(self):
		self.list.DeleteAllItems()
		list_new=[]
		for i in sorted(self.list_SK, key=lambda item: (item[self.sortCol])):
			list_new.append(i)
		self.list_SK=list_new
		self.init2()			

	def init2(self):
		index=0
		for i in self.list_SK:
			self.list.InsertStringItem(index, i[0])	
			self.list.SetStringItem(index, 1, i[1])
			self.list.SetStringItem(index, 2, i[2])
			self.list.SetStringItem(index, 3, i[3])
			index+=1

	def OnClose(self, event):
		self.Destroy()

	def on_message(self,ws, message):
		try:
			js_up=json.loads(message)['updates'][0]
		except:
			return
		label=js_up['source']['label']
		
		srcExist=False
		try:
			src=js_up['source']['src']
			srcExist=True
		except:	pass
		if not srcExist:
			try:
				src=js_up['source']['talker']
				srcExist=True
			except:
				src='xx'
		try:
			timestamp=js_up['timestamp']
		except:
			timestamp='2000-01-01T00:00:00.000Z'
					
		values_=js_up['values']
		srclabel2=''
		
		for values in values_:
			path=values['path']
			value=values['value']
			
			if type(value) is dict:
				if 'timestamp' in value:timestamp=value['timestamp']
				if 'source' in value:
					try:
						src2=value['source']['talker']
					except:
						src2='xx'
					srclabel2=label +'.'+ src2
					
				for lvalue in value:
					if lvalue in ['timestamp','source']:pass
					else:
						path2=path+'.'+lvalue
						value2=value[lvalue]
						self.update_add(value2, path2, srclabel2, timestamp)
			else:
				srclabel=label +'.'+ src
				self.update_add(value, path, srclabel, timestamp)
			

	def update_add(self,value, path, src, timestamp):
		# SRC SignalK Value Unit Interval Status Description timestamp
		#  0    1      2     3      4        5        6          7
		if type(value) is float: pass
		elif type(value) is int: value=1.0*value
		else: value=0.0

		index=0
		exists=False
		for i in self.list_SK:
			if path==i[1]:
				if src==i[0]:
					exists=True
					i[2]=value
					if type(i[2]) is float: pass
					else:	i[2]=0.0
					if i[4]==0.0: i[4]=self.json_interval(i[7],timestamp)
					else:         i[4]=i[4]*.8+0.2*self.json_interval(i[7],timestamp)
					i[7]=timestamp
					self.buffer.append([index, 2, str('%.3f' % i[2])])
					self.buffer.append([index, 4, str('%.2f' % i[4])])
			if exists:
				i=self.list_SK[-1]
			index+=1
		if not exists:
			self.lookup_star(path)
			self.list_SK.append([src,path,value,self.SK_unit,0.0,1,self.SK_description,timestamp])
			self.buffer.append([-1, 0,''])

app = wx.App()
MyFrame().Show()
app.MainLoop()