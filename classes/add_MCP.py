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
import wx, subprocess, json
from w1thermsensor import W1ThermSensor
from classes.paths import Paths
from classes.conf import Conf

paths=Paths()
home=paths.home

class addMCP(wx.Dialog):

	def __init__(self,edit):
		self.conf=Conf()
		self.edit = edit

		wx.Dialog.__init__(self, None, title=_('Edit MCP analog input ')+str(edit[2]), size=(430,350))

		panel = wx.Panel(self)

		list_tmp=[]
		response = subprocess.check_output(home+'/.config/signalk-server-node/node_modules/signalk-schema/scripts/extractKeysAndMeta.js')
		self.data = json.loads(response)
		for i in self.data:
			list_tmp.append(i)
		list_sk_path=sorted(list_tmp)

		titl = wx.StaticText(panel, label='Signal K')
		self.SKkey= wx.ComboBox(panel, choices=list_sk_path, style=wx.CB_READONLY, size=(410, 30))
 		self.SKkey.Bind(wx.EVT_COMBOBOX, self.onSelect)
 		self.description = wx.TextCtrl(panel, -1, style=wx.TE_MULTILINE|wx.TE_READONLY, size=(410, -1))
		self.description.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_INACTIVECAPTION))

		asterix_t = wx.StaticText(panel, label=_('*'))
		self.asterix = wx.TextCtrl(panel, size=(150, 30))
		asterix_t2 = wx.StaticText(panel, label=_('allowed characters: 0-9, a-z, A-Z.'))

		self.aktiv = wx.CheckBox(panel, label=_('aktiv'))
		self.convert = wx.CheckBox(panel, label=_('convert'))
		self.convert.Bind(wx.EVT_CHECKBOX, self.on_convert)

		cancelBtn = wx.Button(panel, wx.ID_CANCEL)
		okBtn = wx.Button(panel, wx.ID_OK)

		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add((0,0), 1, wx.ALL|wx.EXPAND, 5)
		hbox.Add(cancelBtn, 0, wx.ALL|wx.EXPAND, 5)
		hbox.Add(okBtn, 0, wx.ALL|wx.EXPAND, 5)
		
		
		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.Add(self.aktiv, 0, wx.ALL|wx.EXPAND, 5)
		vbox.AddSpacer(5)
		vbox.Add(titl, 0, wx.RIGHT|wx.LEFT|wx.EXPAND, 5)
		vbox.Add(self.SKkey, 0, wx.RIGHT|wx.LEFT|wx.EXPAND, 5)
		vbox.Add(self.description, 0, wx.RIGHT|wx.LEFT|wx.EXPAND, 5)
		vbox.AddSpacer(5)
		vbox.Add(asterix_t, 0, wx.RIGHT|wx.LEFT|wx.EXPAND, 5)
		vbox.Add(self.asterix, 0, wx.RIGHT|wx.LEFT, 5)
		vbox.Add(asterix_t2, 0, wx.RIGHT|wx.LEFT|wx.EXPAND, 5)
		vbox.Add((0,0), 1, wx.ALL|wx.EXPAND, 0)
		vbox.Add(self.convert, 0, wx.ALL|wx.EXPAND, 5)		
		vbox.Add(hbox, 1, wx.RIGHT|wx.LEFT|wx.EXPAND, 5)

		panel.SetSizer(vbox)		

		
		self.asterix.SetValue(edit[4])
		self.SKkey.SetValue(edit[3])
		for i in self.data:
			if edit[4]==i:
				try: self.description.SetValue(self.data[i]['description'])
				except: self.description.SetValue('')
		state=False
		if edit[1]==1: state=True
		self.aktiv.SetValue(state)
		state=False
		if edit[5]==1: state=True
		self.convert.SetValue(state)			

	def onSelect(self,e):
		selected= self.SKkey.GetValue()
		for i in self.data:
			if selected==i:
				try: self.description.SetValue(self.data[i]['description'])
				except: self.description.SetValue('')

	def on_convert(self,e):
		convert=0
		if self.convert.GetValue(): 
			convert=1
			if self.conf.has_option('SPI', 'value_'+str(self.edit[2])):
				data=self.conf.get('SPI', 'value_'+str(self.edit[2]))
				try:
					temp_list=eval(data)
				except:temp_list = []
				min=1023
				max=0
				for ii in temp_list:
					if ii[0]>max: max=ii[0]
					if ii[0]<min: min=ii[0]
				if min>0:
					wx.MessageBox(_('minimum raw value in setting table > 0'),'info', wx.OK | wx.ICON_INFORMATION)
					convert=0
				if max<1023:
					wx.MessageBox(_('maximum raw value in setting table < 1023'),'info', wx.OK | wx.ICON_INFORMATION)
					convert=0
			else:
				wx.MessageBox(_('no option value_'+str(self.edit[2])+' in openplotter.conf'),'info', wx.OK | wx.ICON_INFORMATION)
				convert=0
				
		self.convert.SetValue(convert)