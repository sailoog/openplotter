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

import wx, subprocess
from classes.paths import Paths
from classes.op_conf import Conf
from classes.language import Language

class MyFrame(wx.Frame):
		
		def __init__(self):

			self.paths=Paths()

			self.conf=Conf()

			Language(self.conf.get('GENERAL','lang'))

			wx.Frame.__init__(self, None, title=_('Calculate'), size=(690,320))
			
			self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
			
			self.icon = wx.Icon(self.paths.op_path+'/openplotter.ico', wx.BITMAP_TYPE_ICO)
			self.SetIcon(self.icon)

			wx.StaticBox(self, size=(330, 50), pos=(10, 10))
			wx.StaticText(self, label=_('Rate (sec)'), pos=(20, 30))
			self.rate_list = ['0.1', '0.25', '0.5', '0.75', '1', '1.5', '2']
			self.rate2= wx.ComboBox(self, choices=self.rate_list, style=wx.CB_READONLY, size=(80, 32), pos=(150, 23))
			self.button_ok_rate2 =wx.Button(self, label=_('Ok'),size=(70, 32), pos=(250, 23))
			self.Bind(wx.EVT_BUTTON, self.ok_rate2, self.button_ok_rate2)

			wx.StaticBox(self, size=(330, 50), pos=(350, 10))
			wx.StaticText(self, label=_('Accuracy (sec)'), pos=(360, 30))
			self.accuracy= wx.ComboBox(self, choices=self.rate_list, style=wx.CB_READONLY, size=(80, 32), pos=(500, 23))
			self.button_ok_accuracy =wx.Button(self, label=_('Ok'),size=(70, 32), pos=(600, 23))
			self.Bind(wx.EVT_BUTTON, self.ok_accuracy, self.button_ok_accuracy)

			wx.StaticBox(self, size=(330, 65), pos=(10, 65))
			self.mag_var = wx.CheckBox(self, label=_('Magnetic variation'), pos=(20, 80))
			self.mag_var.Bind(wx.EVT_CHECKBOX, self.nmea_mag_var)
			wx.StaticText(self, label=_('Generated NMEA: $OCHDG'), pos=(20, 105))

			wx.StaticBox(self, size=(330, 65), pos=(10, 130))
			self.heading_t = wx.CheckBox(self, label=_('True heading'), pos=(20, 145))
			self.heading_t.Bind(wx.EVT_CHECKBOX, self.nmea_hdt)
			wx.StaticText(self, label=_('Generated NMEA: $OCHDT'), pos=(20, 170))

			wx.StaticBox(self, size=(330, 65), pos=(10, 195))
			self.rot = wx.CheckBox(self, label=_('Rate of turn'), pos=(20, 210))
			self.rot.Bind(wx.EVT_CHECKBOX, self.nmea_rot)
			wx.StaticText(self, label=_('Generated NMEA: $OCROT'), pos=(20, 235))

			wx.StaticBox(self, label=_(' True wind '), size=(330, 90), pos=(350, 65))
			self.TW_STW = wx.CheckBox(self, label=_('Use speed log'), pos=(360, 80))
			self.TW_STW.Bind(wx.EVT_CHECKBOX, self.TW)
			self.TW_SOG = wx.CheckBox(self, label=_('Use GPS'), pos=(360, 105))
			self.TW_SOG.Bind(wx.EVT_CHECKBOX, self.TW)
			wx.StaticText(self, label=_('Generated NMEA: $OCMWV, $OCMWD'), pos=(360, 130))

			self.CreateStatusBar()

			self.Centre()

			self.Show(True)

			self.rate2.SetValue(self.conf.get('CALCULATE', 'nmea_rate_cal'))
			self.accuracy.SetValue(self.conf.get('CALCULATE', 'cal_accuracy'))
			if self.conf.get('CALCULATE', 'nmea_mag_var')=='1': self.mag_var.SetValue(True)
			if self.conf.get('CALCULATE', 'nmea_hdt')=='1': self.heading_t.SetValue(True)
			if self.conf.get('CALCULATE', 'nmea_rot')=='1': self.rot.SetValue(True)
			if self.conf.get('CALCULATE', 'tw_stw')=='1': self.TW_STW.SetValue(True)
			if self.conf.get('CALCULATE', 'tw_sog')=='1': self.TW_SOG.SetValue(True)

		def start_calculate(self):
			subprocess.call(['pkill', '-f', 'calculate_d.py'])
			if self.mag_var.GetValue() or self.heading_t.GetValue() or self.rot.GetValue() or self.TW_STW.GetValue() or self.TW_SOG.GetValue():
				subprocess.Popen(['python', self.paths.currentpath+'/calculate_d.py'])

		def ok_rate2(self, e):
			rate=self.rate2.GetValue()
			self.conf.set('CALCULATE', 'nmea_rate_cal', rate)
			self.start_calculate()
			self.ShowMessage(_('Generation rate set to ')+rate+_(' seconds'))

		def ok_accuracy(self,e):
			accuracy=self.accuracy.GetValue()
			self.conf.set('CALCULATE', 'cal_accuracy', accuracy)
			self.start_calculate()
			self.ShowMessage(_('Calculation accuracy set to ')+accuracy+_(' seconds'))

		def nmea_mag_var(self, e):
			sender = e.GetEventObject()
			if sender.GetValue(): self.conf.set('CALCULATE', 'nmea_mag_var', '1')
			else: self.conf.set('CALCULATE', 'nmea_mag_var', '0')
			self.start_calculate()

		def nmea_hdt(self, e):
			sender = e.GetEventObject()
			if sender.GetValue(): self.conf.set('CALCULATE', 'nmea_hdt', '1')
			else: self.conf.set('CALCULATE', 'nmea_hdt', '0')
			self.start_calculate()

		def nmea_rot(self, e):
			sender = e.GetEventObject()
			if sender.GetValue(): self.conf.set('CALCULATE', 'nmea_rot', '1')
			else: self.conf.set('CALCULATE', 'nmea_rot', '0')
			self.start_calculate()

		def	TW(self, e):
			sender = e.GetEventObject()
			state=sender.GetValue()
			self.TW_STW.SetValue(False)
			self.TW_SOG.SetValue(False)
			self.conf.set('CALCULATE', 'tw_stw', '0')
			self.conf.set('CALCULATE', 'tw_sog', '0')
			if state: sender.SetValue(True)
			if self.TW_STW.GetValue(): self.conf.set('CALCULATE', 'tw_stw', '1')
			if self.TW_SOG.GetValue(): self.conf.set('CALCULATE', 'tw_sog', '1')
			self.start_calculate()

app = wx.App()
MyFrame().Show()
app.MainLoop()