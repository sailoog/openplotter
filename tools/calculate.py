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

import wx, sys, os, subprocess

op_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')
sys.path.append(op_folder+'/classes')
from conf import Conf
from language import Language

class MyFrame(wx.Frame):
		
		def __init__(self):

			self.conf = Conf()
			self.home = self.conf.home
			self.currentpath = self.home+self.conf.get('GENERAL', 'op_folder')+'/openplotter'

			Language(self.conf)

			title = _('Calculate')

			wx.Frame.__init__(self, None, title=title, size=(690,400))
			
			self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
			
			self.icon = wx.Icon(self.currentpath+'/openplotter.ico', wx.BITMAP_TYPE_ICO)
			self.SetIcon(self.icon)

			rate_list = ['0.1', '0.25', '0.5', '0.75', '1', '1.5', '2', '5', '30', '60', '300']

			panel = wx.Panel(self)

			mg_box = wx.StaticBox(panel, -1, _(' Magnetic variation '))
			self.mag_var = wx.CheckBox(panel, -1, label=_('Enable'))
			mg_requires = wx.StaticText(panel, label=_('Requires: position, date.'))
			mg_accu_label = wx.StaticText(panel, label=_('Accuracy (sec)'))
			self.mg_accu= wx.ComboBox(panel, choices=rate_list, style=wx.CB_READONLY)
			mg_rate_label = wx.StaticText(panel, label=_('Rate (sec)'))
			self.mg_rate= wx.ComboBox(panel, choices=rate_list, style=wx.CB_READONLY)

			rt_box = wx.StaticBox(panel, -1, _(' Rate of turn '))
			self.rate_turn = wx.CheckBox(panel, -1, label=_('Enable'))
			rt_requires = wx.StaticText(panel, label=_('Requires: magnetic heading.'))
			rt_accu_label = wx.StaticText(panel, label=_('Accuracy (sec)'))
			self.rt_accu= wx.ComboBox(panel, choices=rate_list, style=wx.CB_READONLY)
			rt_rate_label = wx.StaticText(panel, label=_('Rate (sec)'))
			self.rt_rate= wx.ComboBox(panel, choices=rate_list, style=wx.CB_READONLY)

			th_box = wx.StaticBox(panel, -1, _(' True heading '))
			self.heading_t = wx.CheckBox(panel, -1, label=_('Deviation is included'))
			self.heading_t.Bind(wx.EVT_CHECKBOX, self.on_select_th)
			th_requires = wx.StaticText(panel, label=_('Requires: magnetic heading, variation.'))
			self.add_deviation = wx.CheckBox(panel, -1, label=_('Add deviation table'))
			self.add_deviation.Bind(wx.EVT_CHECKBOX, self.on_select_th)
			th_requires2 = wx.StaticText(panel, label=_('Requires: magnetic heading, variation, deviation.'))
			th_accu_label = wx.StaticText(panel, label=_('Accuracy (sec)'))
			self.th_accu= wx.ComboBox(panel, choices=rate_list, style=wx.CB_READONLY)
			th_rate_label = wx.StaticText(panel, label=_('Rate (sec)'))
			self.th_rate= wx.ComboBox(panel, choices=rate_list, style=wx.CB_READONLY)

			tw_box = wx.StaticBox(panel, -1, _(' True wind speed and direction '))
			self.true_wind = wx.CheckBox(panel, -1, label=_('Use Speed Through Water'))
			self.true_wind.Bind(wx.EVT_CHECKBOX, self.on_select_tw)
			tw_requires = wx.StaticText(panel, label=_('Requires: STW, AWS, AWA.'))
			self.true_wind2 = wx.CheckBox(panel, -1, label=_('Use Speed Over Ground'))
			self.true_wind2.Bind(wx.EVT_CHECKBOX, self.on_select_tw)
			tw_requires2 = wx.StaticText(panel, label=_('Requires: SOG, COG, HDT, AWS, AWA.'))
			tw_accu_label = wx.StaticText(panel, label=_('Accuracy (sec)'))
			self.tw_accu= wx.ComboBox(panel, choices=rate_list, style=wx.CB_READONLY)
			tw_rate_label = wx.StaticText(panel, label=_('Rate (sec)'))
			self.tw_rate= wx.ComboBox(panel, choices=rate_list, style=wx.CB_READONLY)

			button_cancel =wx.Button(panel, label=_('Cancel'))
			self.Bind(wx.EVT_BUTTON, self.on_cancel, button_cancel)

			button_ok =wx.Button(panel, label=_('OK'))
			self.Bind(wx.EVT_BUTTON, self.on_ok, button_ok)

			self.true_wind.Disable()
			self.true_wind2.Disable()

			mg_boxSizer = wx.StaticBoxSizer(mg_box, wx.VERTICAL)
			mg_boxSizer.Add(self.mag_var, 0, wx.ALL | wx.EXPAND, 5)
			mg_boxSizer.Add(mg_requires, 0, wx.LEFT | wx.EXPAND, 5)
			mg_h = wx.BoxSizer(wx.HORIZONTAL)
			mg_h.Add(mg_rate_label, 0, wx.UP | wx.EXPAND, 10)
			mg_h.Add(self.mg_rate, 0, wx.ALL | wx.EXPAND, 5)
			mg_h.Add(mg_accu_label, 0, wx.UP | wx.EXPAND, 10)
			mg_h.Add(self.mg_accu, 0, wx.ALL | wx.EXPAND, 5)
			mg_boxSizer.Add(mg_h, 0, wx.ALL | wx.EXPAND, 5)

			rt_boxSizer = wx.StaticBoxSizer(rt_box, wx.VERTICAL)
			rt_boxSizer.Add(self.rate_turn, 0, wx.ALL | wx.EXPAND, 5)
			rt_boxSizer.Add(rt_requires, 0, wx.LEFT | wx.EXPAND, 5)
			rt_h = wx.BoxSizer(wx.HORIZONTAL)
			rt_h.Add(rt_rate_label, 0, wx.UP | wx.EXPAND, 10)
			rt_h.Add(self.rt_rate, 0, wx.ALL | wx.EXPAND, 5)
			rt_h.Add(rt_accu_label, 0, wx.UP | wx.EXPAND, 10)
			rt_h.Add(self.rt_accu, 0, wx.ALL | wx.EXPAND, 5)
			rt_boxSizer.Add(rt_h, 0, wx.ALL | wx.EXPAND, 5)

			th_boxSizer = wx.StaticBoxSizer(th_box, wx.VERTICAL)
			th_boxSizer.Add(self.heading_t, 0, wx.ALL | wx.EXPAND, 5)
			th_boxSizer.Add(th_requires, 0, wx.LEFT | wx.EXPAND, 5)
			th_boxSizer.Add(self.add_deviation, 0, wx.ALL | wx.EXPAND, 5)
			th_boxSizer.Add(th_requires2, 0, wx.LEFT | wx.EXPAND, 5)
			th_h = wx.BoxSizer(wx.HORIZONTAL)
			th_h.Add(th_rate_label, 0, wx.UP | wx.EXPAND, 10)
			th_h.Add(self.th_rate, 0, wx.ALL | wx.EXPAND, 5)
			th_h.Add(th_accu_label, 0, wx.UP | wx.EXPAND, 10)
			th_h.Add(self.th_accu, 0, wx.ALL | wx.EXPAND, 5)
			th_boxSizer.Add(th_h, 0, wx.ALL | wx.EXPAND, 5)

			tw_boxSizer = wx.StaticBoxSizer(tw_box, wx.VERTICAL)
			tw_boxSizer.Add(self.true_wind, 0, wx.ALL | wx.EXPAND, 5)
			tw_boxSizer.Add(tw_requires, 0, wx.LEFT | wx.EXPAND, 5)
			tw_boxSizer.Add(self.true_wind2, 0, wx.ALL | wx.EXPAND, 5)
			tw_boxSizer.Add(tw_requires2, 0, wx.LEFT | wx.EXPAND, 5)
			tw_h = wx.BoxSizer(wx.HORIZONTAL)
			tw_h.Add(tw_rate_label, 0, wx.UP | wx.EXPAND, 10)
			tw_h.Add(self.tw_rate, 0, wx.ALL | wx.EXPAND, 5)
			tw_h.Add(tw_accu_label, 0, wx.UP | wx.EXPAND, 10)
			tw_h.Add(self.tw_accu, 0, wx.ALL | wx.EXPAND, 5)
			tw_boxSizer.Add(tw_h, 0, wx.ALL | wx.EXPAND, 5)

			vbox = wx.BoxSizer(wx.VERTICAL)
			vbox.Add(mg_boxSizer, 0, wx.ALL | wx.EXPAND, 5)
			vbox.Add(tw_boxSizer, 0, wx.ALL | wx.EXPAND, 5)

			vbox2 = wx.BoxSizer(wx.VERTICAL)
			vbox2.Add(th_boxSizer, 0, wx.ALL | wx.EXPAND, 5)
			vbox2.Add(rt_boxSizer, 0, wx.ALL | wx.EXPAND, 5)

			hbox = wx.BoxSizer(wx.HORIZONTAL)
			hbox.Add(vbox, 0, wx.ALL | wx.EXPAND, 0)
			hbox.Add(vbox2, 0, wx.ALL | wx.EXPAND, 0)

			hbox2 = wx.BoxSizer(wx.HORIZONTAL)
			hbox2.Add((0,0), 1, wx.ALL | wx.EXPAND, 0)
			hbox2.Add(button_cancel, 0, wx.ALL | wx.EXPAND, 10)
			hbox2.Add(button_ok, 0, wx.ALL | wx.EXPAND, 10)

			vbox3 = wx.BoxSizer(wx.VERTICAL)
			vbox3.Add(hbox, 0, wx.ALL | wx.EXPAND, 0)
			vbox3.Add(hbox2, 0, wx.ALL | wx.EXPAND, 0)

			panel.SetSizer(vbox3)

			self.Centre()

			if self.conf.get('CALCULATE', 'mag_var')=='1': self.mag_var.SetValue(True)
			self.mg_rate.SetValue(self.conf.get('CALCULATE', 'mag_var_rate'))
			self.mg_accu.SetValue(self.conf.get('CALCULATE', 'mag_var_accuracy'))

			if self.conf.get('CALCULATE', 'hdt')=='1': self.heading_t.SetValue(True)
			if self.conf.get('CALCULATE', 'hdt_dev')=='1': self.add_deviation.SetValue(True)
			if self.conf.get('COMPASS', 'magnetic_h')=='1': self.add_deviation.Disable()

			self.th_rate.SetValue(self.conf.get('CALCULATE', 'hdt_rate'))
			self.th_accu.SetValue(self.conf.get('CALCULATE', 'hdt_accuracy'))

			if self.conf.get('CALCULATE', 'rot')=='1': self.rate_turn.SetValue(True)
			self.rt_rate.SetValue(self.conf.get('CALCULATE', 'rot_rate'))
			self.rt_accu.SetValue(self.conf.get('CALCULATE', 'rot_accuracy'))

			if self.conf.get('CALCULATE', 'tw_stw')=='1': self.true_wind.SetValue(True)
			if self.conf.get('CALCULATE', 'tw_sog')=='1': self.true_wind2.SetValue(True)
			self.tw_rate.SetValue(self.conf.get('CALCULATE', 'tw_rate'))
			self.tw_accu.SetValue(self.conf.get('CALCULATE', 'tw_accuracy'))

		def on_ok(self, e):
			if self.mag_var.GetValue():
				if self.mg_rate.GetValue() and self.mg_accu.GetValue():
					self.conf.set('CALCULATE', 'mag_var', '1')
					self.conf.set('CALCULATE', 'mag_var_rate', self.mg_rate.GetValue())
					self.conf.set('CALCULATE', 'mag_var_accuracy', self.mg_accu.GetValue())
				else:
					self.ShowMessage(_('You have to provide rate and accuracy values for magnetic variation'))
					return
			else: self.conf.set('CALCULATE', 'mag_var', '0')

			if self.conf.get('COMPASS', 'magnetic_h')=='1': self.add_deviation.SetValue(False)
			if self.heading_t.GetValue() or self.add_deviation.GetValue():
				if self.th_rate.GetValue() and self.th_accu.GetValue():
					if self.heading_t.GetValue(): self.conf.set('CALCULATE', 'hdt', '1')
					else: self.conf.set('CALCULATE', 'hdt', '0')
					if self.add_deviation.GetValue(): self.conf.set('CALCULATE', 'hdt_dev', '1')
					else: self.conf.set('CALCULATE', 'hdt_dev', '0')
					self.conf.set('CALCULATE', 'hdt_rate', self.th_rate.GetValue())
					self.conf.set('CALCULATE', 'hdt_accuracy', self.th_accu.GetValue())
				else:
					self.ShowMessage(_('You have to provide rate and accuracy values for true heading'))
					return
			else: 
				self.conf.set('CALCULATE', 'hdt', '0')
				self.conf.set('CALCULATE', 'hdt_dev', '0')

			if self.rate_turn.GetValue():
				if self.rt_rate.GetValue() and self.rt_accu.GetValue():
					self.conf.set('CALCULATE', 'rot', '1')
					self.conf.set('CALCULATE', 'rot_rate', self.rt_rate.GetValue())
					self.conf.set('CALCULATE', 'rot_accuracy', self.rt_accu.GetValue())
				else:
					self.ShowMessage(_('You have to provide rate and accuracy values for rate of turn'))
					return
			else: self.conf.set('CALCULATE', 'rot', '0')

			if self.true_wind.GetValue() or self.true_wind2.GetValue():
				if self.tw_rate.GetValue() and self.tw_accu.GetValue():
					if self.true_wind.GetValue(): self.conf.set('CALCULATE', 'tw_stw', '1')
					else: self.conf.set('CALCULATE', 'tw_stw', '0')
					if self.true_wind2.GetValue(): self.conf.set('CALCULATE', 'tw_sog', '1')
					else: self.conf.set('CALCULATE', 'tw_sog', '0')
					self.conf.set('CALCULATE', 'tw_rate', self.tw_rate.GetValue())
					self.conf.set('CALCULATE', 'tw_accuracy', self.tw_accu.GetValue())
				else:
					self.ShowMessage(_('You have to provide rate and accuracy values for true wind speed and direction'))
					return
			else:
				self.conf.set('CALCULATE', 'tw_stw', '0')
				self.conf.set('CALCULATE', 'tw_sog', '0')

			subprocess.call(['pkill', '-f', 'SK-base_d.py'])
			subprocess.Popen(['python', self.currentpath + '/SK-base_d.py'])
			self.Close()

		def on_cancel(self, e):
			self.Close()

		def ShowMessage(self, w_msg):
			wx.MessageBox(w_msg, 'Info', wx.OK | wx.ICON_INFORMATION)

		def on_select_tw(self,e):
			sender = e.GetEventObject()
			if sender.GetValue():
				self.true_wind2.SetValue(False)
				self.true_wind.SetValue(False)
				sender.SetValue(True)

		def on_select_th(self,e):
			sender = e.GetEventObject()
			if sender.GetValue():
				self.heading_t.SetValue(False)
				self.add_deviation.SetValue(False)
				sender.SetValue(True)

app = wx.App()
MyFrame().Show()
app.MainLoop()