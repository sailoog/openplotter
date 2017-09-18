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
import wx, pynmea2, inspect, webbrowser, json, subprocess, requests, re

class addNMEA_0183(wx.Dialog):

	def __init__(self,edit,conf):

		self.conf = conf
		self.home = self.conf.home
		self.currentpath = self.home+self.conf.get('GENERAL', 'op_folder')+'/openplotter'

		wx.Dialog.__init__(self, None, title=_('add NMEA 0183 sentence'), size=(670,410))

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
		wx.StaticText(panel, label=_('Rate (sec)'), pos=(135, 10))
		self.rate= wx.ComboBox(panel, choices=self.rate_list, style=wx.CB_READONLY, size=(80, 30), pos=(135, 35))
		self.rate.Bind(wx.EVT_COMBOBOX, self.onSelect_rate)

 		self.button_nmea_info =wx.Button(panel, label=_('NMEA info'), pos=(220, 33))
		self.Bind(wx.EVT_BUTTON, self.nmea_info, self.button_nmea_info)

 		self.button_rmc_examp =wx.Button(panel, label=_('RMC examp'), pos=(315, 33))
		self.Bind(wx.EVT_BUTTON, self.rmc_examp, self.button_rmc_examp)

		cancelBtn = wx.Button(panel, label=_('cancel'), pos=(475, 33))
		cancelBtn.Bind(wx.EVT_BUTTON, self.on_cancel)
		okBtn = wx.Button(panel, wx.ID_OK, pos=(575, 33))

		self.list_fields = wx.ListCtrl(panel, style=wx.LC_REPORT, size=(650, 170), pos=(10, 70))
		self.list_fields.InsertColumn(0, _('Field'), width=290)
		self.list_fields.InsertColumn(1, _('Value'), width=580)
		self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSelect_field, self.list_fields)
		self.list_fields.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onEdit_fields)

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
		self.skvessels.Bind(wx.EVT_COMBOBOX, self.onSelect_vessel)

		self.list_skgroups=[_('--group')]
		self.skgroups= wx.ComboBox(panel, choices=self.list_skgroups, style=wx.CB_READONLY, size=(135, 30), pos=(200, 290))
		self.skgroups.Bind(wx.EVT_COMBOBOX, self.onSelect_group)

		self.list_signalk=[_('--key')]
		self.signalk= wx.ComboBox(panel, choices=self.list_signalk, style=wx.CB_READONLY, size=(315, 30), pos=(345, 290))

		self.list_operators=[_('--operator'),'/','*','+','-']
		self.operator= wx.ComboBox(panel, choices=self.list_operators, style=wx.CB_READONLY, size=(120, 30), pos=(10, 332))

		self.string_number = wx.TextCtrl(panel, size=(80, 30), pos=(140, 332))

		self.equal=wx.StaticText(panel, label=_('='), pos=(225, 335))

		self.list_formats=['--format','decimals: x.x','decimals: x.x|deg','decimals: x.x|kn','decimals: x.x|C','decimals: x.x|F','decimals: x.xx','decimals: x.xxx','decimals: x.xxxx','time: hhmmss.ss','date: ddmmyy','lat: ddmm.mm','lon: dddmm.mm','lat: N/S','lon: E/W']
		self.formats= wx.ComboBox(panel, choices=self.list_formats, style=wx.CB_READONLY, size=(170, 30), pos=(240, 332))

 		self.button_add_value =wx.Button(panel, label=_('Add value'), pos=(460, 330))
		self.Bind(wx.EVT_BUTTON, self.add_value, self.button_add_value)

 		self.button_del_value =wx.Button(panel, label=_('Delete value'), pos=(560, 330))
		self.Bind(wx.EVT_BUTTON, self.del_value, self.button_del_value)

		self.list_fiel = []
		if edit == 0:
			self.rate.SetValue('1')
			self.nmea=['',[],float(self.rate.GetValue())]

		else:
			self.button_rmc_examp.Disable()
			for rateI in self.rate_list:
				if float(rateI) == edit[1][2]:		
					self.rate.SetValue(rateI)
			self.sentence.SetValue('$--'+edit[1][0])
			self.nmea=edit[1]
			for index,item in enumerate(self.sentences):
				if edit[1][0] in item: sent=index
			for index, item in enumerate(self.fields[sent]):
				self.list_fiel.append([index,item[0],self.nmea[1][index]])
				self.list_fields.InsertStringItem(index,item[0])
				self.list_fields.SetStringItem(index,1,str(self.nmea[1][index]))

		self.disable_all()

		self.reset_fields()

		self.Centre()

	def is_number(self, s):
		try:
			float(s)
			return True
		except ValueError:
			return False		
		
	def onEdit_fields(self,e):
		selected_field=self.list_fields.GetFirstSelected()
		if len(self.list_fiel) != 0:
			if type(self.list_fiel[selected_field][2]) is list:
				if (self.list_fiel[selected_field][2][2] == '+') == True and self.list_fiel[selected_field][2][3] == 0:
					self.check_value_type_(self.list_value_type[2])
					self.skvessels.SetValue(self.list_vessels[1])
					self.onSelect_vessel_(self.list_vessels[1])
					sk = self.list_fiel[selected_field][2][0]
					sk0 = sk.split('.')[0]
					skr = sk[len(sk0)+1:]
					self.skgroups.SetValue(sk0)
					self.onSelect_group_(sk0)
					self.signalk.SetValue(skr)
					format = self.list_formats[0]
					formats = self.list_fiel[selected_field][2][1]
					for value_ in self.list_formats:
						if formats in value_:
							format = value_
							break						
					self.formats.SetValue(format)
				else:
					self.check_value_type_(self.list_value_type[1])
					self.skvessels.SetValue(self.list_vessels[1])
					self.onSelect_vessel_(self.list_vessels[1])
					sk = self.list_fiel[selected_field][2][0]
					sk0 = sk.split('.')[0]
					skr = sk[len(sk0)+1:]
					self.skgroups.SetValue(sk0)
					self.onSelect_group_(sk0)
					self.signalk.SetValue(skr)
					opera = self.list_operators[0]
					for value_ in self.list_operators:
						if self.list_fiel[selected_field][2][2] in value_:
							opera = value_
							break						
					self.operator.SetValue(opera)
					format = self.list_formats[0]
					formats = self.list_fiel[selected_field][2][1]
					for value_ in self.list_formats:
						if formats in value_:
							format = value_
							break						
					self.formats.SetValue(format)
					self.string_number.SetValue(str(self.list_fiel[selected_field][2][3]))
			else:
				if self.is_number(self.list_fiel[selected_field][2]):
					self.check_value_type_(self.list_value_type[3])
					self.string_number.SetValue(self.list_fiel[selected_field][2])
				else:
					if len(self.list_fiel[selected_field][2])>0:
						self.check_value_type_(self.list_value_type[4])
						self.string_number.SetValue(self.list_fiel[selected_field][2])
			

	def onSelect_vessel(self,e):
		vessel=self.skvessels.GetValue()
		if '--' in vessel:
			self.reset_group_key()
			return
		self.onSelect_vessel_(vessel)

	def onSelect_vessel_(self,vessel):
		self.list_skgroups=[]
		try:
			response = requests.get('http://localhost:3000/signalk/v1/api/vessels/'+vessel)
			self.data = response.json()
		except:self.data=None
		list_temp=[_('--group')]
		self.skgroups.Clear()
		if self.data:
			for k,v in self.data.items():
				if isinstance(v, dict):
					if k not in list_temp: list_temp.append(k)
		self.list_skgroups=sorted(list_temp)
		self.skgroups.AppendItems(self.list_skgroups)
		self.reset_group_key()

	def onSelect_group(self, e):
		vessel=self.skvessels.GetValue()
		group=self.skgroups.GetValue()
		if '--' in vessel or '--' in group:
			self.reset_group_key()
			return
		self.onSelect_group_(group)
		
	def onSelect_group_(self, group):
		group=group+'.'
		self.signalk.Clear()
		self.list_signalk=[_('--key')]
		self.path = []
		self.data_keys=[]
		self.keys(self.data)
		list_tmp2=sorted(self.data_keys)
		for i in list_tmp2:
			if group == i[:len(group)]:
				self.list_signalk.append(i.replace(group,'',1))
		self.signalk.AppendItems(self.list_signalk)
		self.signalk.SetSelection(0)

	def keys(self,d):
		for k,v in d.items():
			if isinstance(v, dict):
				self.path.append(k)
				self.keys(v)
				self.path.pop()
			else:
				if k != 'value':
					self.path.append(k)
					self.data_keys.append(".".join(self.path))
					self.path.pop()
				else:
					self.data_keys.append(".".join(self.path))

	def onSelect_rate(self,e):
		tmp=self.rate.GetValue()
		self.nmea[2]=float(tmp)

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
		if selected_type == _('String'):
			if not re.match('^[0-9a-zA-Z/_]+$', str_num) and len(str_num) > 0 :
				self.list_fields.SetStringItem(selected_field,1,_('Failed. String must contain only allowed characters.'))
				str_num=''
				self.string_number.SetValue('')
				return		
		else:
			if not re.match('^[0-9./]+$', str_num) and len(str_num) > 0 :
				self.list_fields.SetStringItem(selected_field,1,_('Failed. String must contain only allowed characters.'))
				str_num=''
				self.string_number.SetValue('')
				return
			
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
			#txt='['+vessel+'.'+group+'.'+key+']'+operator+str_num+'='+formats2
			#if '.value' in key: key=key[:-6]
			txt=[(group+'.'+key).encode('utf8'),formats2.encode('utf8'),operator.encode('utf8'),float(str_num)]
			self.list_fields.SetStringItem(selected_field,1,str(txt))
			self.nmea[1][selected_field]=txt
		#signal k
		if selected_type==self.list_value_type[2]:
			if '--' in vessel or '--' in group or '--' in key or '--' in formats:
				self.list_fields.SetStringItem(selected_field,1,_('FAILED. Fill in all the available fields.'))
				self.nmea[1][selected_field]=''
				return
			#txt='[\''+group+'.'+key+'\',\''+formats2+'\']'
			#if '.value' in key: key=key[:-6]
			txt=[(group+'.'+key).encode('utf8'),formats2.encode('utf8'),'+',0.0]
			self.list_fields.SetStringItem(selected_field,1,str(txt))
			self.nmea[1][selected_field]=txt
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
		url = self.currentpath+'/docs/NMEA.html'
		webbrowser.open(url,new=2)
		
	def rmc_examp(self, e):
		edit = ['', ['RMC', [['navigation.datetime', 'hhmmss.ss', '+', 0.0], 'P', ['navigation.position.latitude', 'ddmm.mm', '+', 0.0], ['navigation.position.latitude', 'N/S', '+', 0.0], ['navigation.position.longitude', 'dddmm.mm', '+', 0.0], ['navigation.position.longitude', 'E/W', '+', 0.0], ['navigation.speedOverGround', 'x.x|kn', '+', 0.0], ['navigation.courseOverGroundTrue', 'x.x|deg', '+', 0.0], ['navigation.datetime', 'ddmmyy', '+', 0.0], '', 'A'], 1.0]]
		self.rate.SetValue(str(edit[1][2]))
		self.sentence.SetValue('$--'+edit[1][0])
		self.nmea=edit[1]
		for index,item in enumerate(self.sentences):
			if edit[1][0] in item: sent=index
		for index, item in enumerate(self.fields[sent]):
			self.list_fiel.append([index,item[0],self.nmea[1][index]])
			self.list_fields.InsertStringItem(index,item[0])
			self.list_fields.SetStringItem(index,1,str(self.nmea[1][index]))
		
	def check_value_type(self, e):
		self.reset_fields()
		selected=self.value_type.GetValue()
		self.check_value_type_(selected)

	def check_value_type_(self, selected):
		self.value_type.SetValue(selected)
		#none
		if not selected or selected.encode('utf-8')==self.list_value_type[0]:
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
		self.reset_group_key()
		self.operator.SetSelection(0)
		self.string_number.SetValue('')
		self.formats.SetSelection(0)

	def reset_group_key(self):
		self.skgroups.SetSelection(0)
		self.signalk.Clear()
		self.list_signalk=[_('--key')]
		self.signalk.AppendItems(self.list_signalk)
		self.signalk.SetSelection(0)

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

	def on_cancel(self, event):
		self.Close()
