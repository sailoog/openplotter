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
import wx

class addTrigger(wx.Dialog):

	def __init__(self,datastream_list,a):

		wx.Dialog.__init__(self, None, title=_('Add trigger'), size=(330,290))

		panel = wx.Panel(self)

		self.a=a

		self.datastream_list2=[]
		for i in datastream_list:
			self.datastream_list2.append(i)
		self.datastream_list2.append(_('None (always true)'))

		wx.StaticText(panel, label=_('trigger'), pos=(10, 10))
		self.trigger_select= wx.ComboBox(panel, choices=self.datastream_list2, style=wx.CB_READONLY, size=(310, 32), pos=(10, 35))
		self.trigger_select.Bind(wx.EVT_COMBOBOX, self.onSelect)
		wx.StaticText(panel, label=_('operator'), pos=(10, 70))
		self.operator_select= wx.ComboBox(panel, choices=self.a.operators_list, style=wx.CB_READONLY, size=(310, 32), pos=(10, 95))
		wx.StaticText(panel, label=_('value'), pos=(10, 130))
		self.value = wx.TextCtrl(panel, size=(310, 32), pos=(10, 155))

		self.value.Disable()
		
		cancelBtn = wx.Button(panel, wx.ID_CANCEL, pos=(70, 205))
		okBtn = wx.Button(panel, wx.ID_OK, pos=(180, 205))

	def onSelect(self,e):
		if (self.trigger_select.GetCurrentSelection())+1==len(self.datastream_list2):
			self.operator_select.Disable()
			self.value.Disable()
			wx.MessageBox(_('The actions of this trigger will always be executed.'), 'Info', wx.OK | wx.ICON_INFORMATION)
		else:
			trigger=self.a.DataList[self.trigger_select.GetCurrentSelection()]
			operators_valid_list=trigger[7]
			new_list=[]
			for i in operators_valid_list:
				new_list.append(self.a.operators_list[i])
			self.operator_select.Enable()
			self.operator_select.Clear()
			self.operator_select.AppendItems(new_list)
			self.operator_select.SetSelection(0)
			disable_field=trigger[8]
			self.value.SetValue('')
			if disable_field==1: self.value.Enable()
			if disable_field==0: self.value.Disable()
			if trigger[1]==_('SW1') or trigger==_('SW2') or trigger==_('SW3') or trigger==_('SW4') or trigger==_('SW5') or trigger==_('SW6'):
				wx.MessageBox(_('Be sure you have filled in GPIO and Pull Down/Up fields in "Switches" tab and enabled the desired switch.'), 'Info', wx.OK | wx.ICON_INFORMATION)
