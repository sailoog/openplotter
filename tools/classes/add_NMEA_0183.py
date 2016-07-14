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
import wx, pynmea2, inspect, webbrowser, json, subprocess, requests
from classes.paths import Paths

class addNMEA_0183(wx.Dialog):

	def __init__(self,edit):

		wx.Dialog.__init__(self, None, title=_('add NMEA 0183 sentence'), size=(670,440))

		self.paths=Paths()

		panel = wx.Panel(self)

		self.list_sentences=[]
		self.sentences=[]
		self.fields=[]

		for name, obj in inspect.getmembers(pynmea2):
			if inspect.isclass(obj):
				if 'pynmea2.types.talker.' in str(obj) and 'pynmea2.types.talker.Transducer' not in str(obj):
					self.list_sentences.append('$--'+obj.__name__)
					self.sentences.append(obj.__name__)
					self.fields.append(obj.fields)

		wx.StaticText(panel, label=_('Sentence'), pos=(10, 10))
		self.sentence= wx.ComboBox(panel, choices=self.list_sentences, style=wx.CB_READONLY, size=(120, 30), pos=(10, 35))
 		self.sentence.Bind(wx.EVT_COMBOBOX, self.onSelect)

		self.rate_list = ['0.1', '0.25', '0.5', '0.75', '1', '5', '30', '60', '300']
		wx.StaticText(panel, label=_('Rate (sec)'), pos=(150, 10))
		self.rate= wx.ComboBox(panel, choices=self.rate_list, style=wx.CB_READONLY, size=(80, 30), pos=(150, 35))
		self.rate.Bind(wx.EVT_COMBOBOX, self.onSelect_rate)

 		self.button_nmea_info =wx.Button(panel, label=_('NMEA info'), pos=(250, 33))
		self.Bind(wx.EVT_BUTTON, self.nmea_info, self.button_nmea_info)

		cancelBtn = wx.Button(panel, wx.ID_CANCEL, pos=(465, 33))
		okBtn = wx.Button(panel, wx.ID_OK, pos=(575, 33))

		self.list_fields = wx.ListCtrl(panel, style=wx.LC_REPORT, size=(650, 170), pos=(10, 70))
		self.list_fields.InsertColumn(0, _('Field'), width=290)
		self.list_fields.InsertColumn(1, _('Value'), width=580)
		self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSelect_field, self.list_fields)

		self.list_value_type=[_('--Select type'),_('Expression'),'Signal K value',_('Number'),_('String')]
		self.value_type= wx.ComboBox(panel, choices=self.list_value_type, style=wx.CB_READONLY, size=(180, 30), pos=(10, 250))
 		self.value_type.Bind(wx.EVT_COMBOBOX, self.check_value_type)
 		self.value_type.SetSelection(0)

		self.list_vessels=[_('--vessel'),'self']
		try:
			response = requests.get('http://localhost:3000/signalk/v1/api/vessels')
			data = response.json()
		except:data=None
		if data:
			for i in data:
				self.list_vessels.append(i)
		self.skvessels= wx.ComboBox(panel, choices=self.list_vessels, style=wx.CB_READONLY, size=(180, 30), pos=(10, 290))
		self.skvessels.Bind(wx.EVT_COMBOBOX, self.reset_group_key)

		self.list_skgroups=[]
		try:
			response = subprocess.check_output(self.paths.home+'/.config/signalk-server-node/node_modules/signalk-schema/scripts/extractKeysAndMeta.js')
			self.data = json.loads(response)
		except:self.data=None
		list_temp=[_('--group')]
		if self.data:
			for i in self.data:
				temp=i.split('.')
				if temp[0] not in list_temp: list_temp.append(temp[0])
		self.list_skgroups=sorted(list_temp)
		self.skgroups= wx.ComboBox(panel, choices=self.list_skgroups, style=wx.CB_READONLY, size=(135, 30), pos=(200, 290))
		self.skgroups.Bind(wx.EVT_COMBOBOX, self.skpaths)

		self.list_signalk=[_('--key')]
		self.signalk= wx.ComboBox(panel, choices=self.list_signalk, style=wx.CB_READONLY, size=(315, 30), pos=(345, 290))
		self.signalk.Bind(wx.EVT_COMBOBOX, self.onSelect_key)

 		self.description = wx.TextCtrl(panel, style=wx.TE_MULTILINE|wx.TE_READONLY, size=(650, 23), pos=(10, 325))
		self.description.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_INACTIVECAPTION))

		self.list_operators=[_('--operator'),'/','*','+','-']
		self.operator= wx.ComboBox(panel, choices=self.list_operators, style=wx.CB_READONLY, size=(120, 30), pos=(10, 362))

		self.string_number = wx.TextCtrl(panel, size=(80, 30), pos=(140, 362))

		self.equal=wx.StaticText(panel, label=_('='), pos=(225, 365))

		self.list_formats=[_('--format'),_('decimals: x.x'),_('decimals: x.xx'),_('time: hhmmss.ss'),_('date: ddmmyy'),_('lat: ddmm.mm'),_('lon: dddmm.mm'),_('lat: N/S'),_('lon: E/W')]
		self.formats= wx.ComboBox(panel, choices=self.list_formats, style=wx.CB_READONLY, size=(150, 30), pos=(240, 362))

 		self.button_add_value =wx.Button(panel, label=_('Add value'), pos=(460, 360))
		self.Bind(wx.EVT_BUTTON, self.add_value, self.button_add_value)

 		self.button_del_value =wx.Button(panel, label=_('Delete value'), pos=(560, 360))
		self.Bind(wx.EVT_BUTTON, self.del_value, self.button_del_value)

		if edit == 0:
			self.rate.SetValue('1')
			self.nmea=['',[],self.rate.GetValue()]

		else:
			self.rate.SetValue(edit[1][2])
			self.sentence.SetValue('$--'+edit[1][0])
			self.nmea=edit[1]
			for index,item in enumerate(self.sentences):
				if edit[1][0] in item: sent=index
			for index, item in enumerate(self.fields[sent]):
				self.list_fields.InsertStringItem(index,item[0])
				self.list_fields.SetStringItem(index,1,self.nmea[1][index])

		self.disable_all()

		self.reset_fields()

		self.Centre()

	def onSelect_rate(self,e):
		tmp=self.rate.GetValue()
		self.nmea[2]=tmp.encode('utf8')

	def onSelect_key(self,e):
		selected_group=self.skgroups.GetValue()+'.'
		selected_key=self.signalk.GetValue()
		exist=None
		for i in self.data:
			if selected_group in i:
				if selected_key in i:
					exist=1
					txt=' '
					desc=self.data[i].get('description')
					if desc: txt+=desc+'.'
					units=self.data[i].get('units')
					if units: txt+=' '+_('Units:')+' '+units+'.'
					values=self.data[i].get('enum')
					if values: txt+=' '+_('Values:')+' '+values+'.'
					self.description.SetValue(txt)
		if not exist: self.description.SetValue(_('Select the general key to see description for this key'))

	def onSelect(self,e):
		selected=self.sentence.GetCurrentSelection()
		self.nmea[0]=self.sentences[selected]
		self.list_fields.DeleteAllItems()
		list_tmp=[]
		for index, item in enumerate(self.fields[selected]):
			self.list_fields.InsertStringItem(index,item[0])
			list_tmp.append('')
		self.nmea[1]=list_tmp
		self.disable_all()
		self.reset_fields()
		self.value_type.SetSelection(0)

	def onSelect_field(self,e):
		self.value_type.SetSelection(0)
		self.button_del_value.Enable()
		self.check_value_type(0)

	def add_value(self,e):
		selected_field=self.list_fields.GetFirstSelected()
		selected_type=self.value_type.GetValue()
		vessel=self.skvessels.GetValue()
		group=self.skgroups.GetValue()
		key=self.signalk.GetValue()
		operator=self.operator.GetValue()
		str_num=self.string_number.GetValue()
		formats=self.formats.GetValue()
		if not '--' in formats:
			formats2=formats.split(':')
			formats2=formats2[1].strip()
		#expression
		if selected_type==self.list_value_type[1]:
			if '--' in vessel or '--' in group or '--' in key or '--' in operator or not str_num or '--' in formats:
				self.list_fields.SetStringItem(selected_field,1,_('FAILED. Fill in all the available fields.'))
				self.nmea[1][selected_field]=''
				return
			try:
				number=eval('10'+operator+str_num)
				number=float(number)
			except:
				self.list_fields.SetStringItem(selected_field,1,_('FAILED. This is not a valid expression.'))
				self.nmea[1][selected_field]=''
				return
			txt='['+vessel+'.'+group+'.'+key+']'+operator+str_num+'='+formats2
			self.list_fields.SetStringItem(selected_field,1,_(txt))
			self.nmea[1][selected_field]=txt.encode('utf8')
		#signal k
		if selected_type==self.list_value_type[2]:
			if '--' in vessel or '--' in group or '--' in key or '--' in formats:
				self.list_fields.SetStringItem(selected_field,1,_('FAILED. Fill in all the available fields.'))
				self.nmea[1][selected_field]=''
				return
			txt='['+vessel+'.'+group+'.'+key+']'+'='+formats2
			self.list_fields.SetStringItem(selected_field,1,_(txt))
			self.nmea[1][selected_field]=txt.encode('utf8')
		#number
		if selected_type==self.list_value_type[3]:
			if not str_num:
				self.list_fields.SetStringItem(selected_field,1,_('FAILED. Fill in all the available fields.'))
				self.nmea[1][selected_field]=''
				return
			try:number=float(str_num)
			except:
				self.list_fields.SetStringItem(selected_field,1,_('FAILED. This field must be a number.'))
				self.nmea[1][selected_field]=''
				return
			self.list_fields.SetStringItem(selected_field,1,_(str_num))
			self.nmea[1][selected_field]=str_num.encode('utf8')
		#string
		if selected_type==self.list_value_type[4]:
			if not str_num:
				self.list_fields.SetStringItem(selected_field,1,_('FAILED. Fill in all the available fields.'))
				self.nmea[1][selected_field]=''
				return
			self.list_fields.SetStringItem(selected_field,1,_(str_num))
			self.nmea[1][selected_field]=str_num.encode('utf8')

	def del_value(self,e):
		selected_field=self.list_fields.GetFirstSelected()
		self.list_fields.SetStringItem(selected_field,1,'')
		self.nmea[1][selected_field]=''

	def nmea_info(self, e):
		url = self.paths.op_path+'/docs/NMEA.html'
		webbrowser.open(url,new=2)

	def skpaths(self, e):
		vessel=self.skvessels.GetValue()
		group=self.skgroups.GetValue()
		if '--' in vessel or '--' in group:
			self.reset_group_key(0)
			return
		group=group+'.'
		self.signalk.Clear()
		self.list_signalk=[_('--key')]
		list_tmp=[]
		for i in self.data:
			if group in i:
				list_tmp.append(i.replace(group,'',1))
				if '*' in i:
					skpath=i.replace('.','/')
					skpath=skpath.replace('*','?',1)
					try:
						response2 = requests.get('http://localhost:3000/signalk/v1/api/vessels/'+vessel+'/'+skpath)
					 	data2 = response2.json()
					except:data2=None
					if data2:
						for ii in data2:
							iii=i.replace('*',ii,1)
							list_tmp.append(iii.replace(group,'',1))
		list_tmp2=sorted(list_tmp)
		for i in list_tmp2:
			self.list_signalk.append(i)
		self.signalk.AppendItems(self.list_signalk)
		self.signalk.SetSelection(0)
		self.description.SetValue('')

	def check_value_type(self, e):
		self.reset_fields()
		selected=self.value_type.GetValue()
		#none
		if not selected or selected==self.list_value_type[0]:
			self.skvessels.Disable()
			self.skgroups.Disable()
			self.signalk.Disable()
			self.operator.Disable()
			self.string_number.Disable()
			self.formats.Disable()
			self.value_type.Enable()
			self.button_add_value.Disable()
		#expression
		if selected==self.list_value_type[1]:
			self.skvessels.Enable()
			self.skgroups.Enable()
			self.signalk.Enable()
			self.operator.Enable()
			self.string_number.Enable()
			self.formats.Enable()
			self.value_type.Enable()
			self.button_add_value.Enable()
		#signal k
		if selected==self.list_value_type[2]:
			self.skvessels.Enable()
			self.skgroups.Enable()
			self.signalk.Enable()
			self.operator.Disable()
			self.string_number.Disable()
			self.formats.Enable()
			self.value_type.Enable()
			self.button_add_value.Enable()
		#number
		if selected==self.list_value_type[3] or selected==self.list_value_type[4]:
			self.skvessels.Disable()
			self.skgroups.Disable()
			self.signalk.Disable()
			self.operator.Disable()
			self.string_number.Enable()
			self.formats.Disable()
			self.value_type.Enable()
			self.button_add_value.Enable()

	def reset_fields(self):
		self.skvessels.SetSelection(0)
		self.reset_group_key(0)
		self.operator.SetSelection(0)
		self.string_number.SetValue('')
		self.formats.SetSelection(0)

	def reset_group_key(self,e):
		self.skgroups.SetSelection(0)
		self.signalk.Clear()
		self.list_signalk=[_('--key')]
		self.signalk.AppendItems(self.list_signalk)
		self.signalk.SetSelection(0)
		self.description.SetValue('')

	def disable_all(self):
		self.skvessels.Disable()
		self.skgroups.Disable()
		self.signalk.Disable()
		self.operator.Disable()
		self.string_number.Disable()
		self.formats.Disable()
		self.value_type.Disable()
		self.button_add_value.Disable()
		self.button_del_value.Disable()
