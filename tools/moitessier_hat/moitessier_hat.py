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

import wx, wx.lib.scrolledpanel, sys, os, re, subprocess, time, ujson, webbrowser
import wx.richtext as rt
import xml.etree.ElementTree as ET

op_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../..')
sys.path.append(op_folder+'/classes')
from conf import Conf
from language import Language
from SK_settings import SK_settings
from opencpnSettings import opencpnSettings

class MyFrame(wx.Frame):
		
		def __init__(self):

			self.conf = Conf()
			self.home = self.conf.home
			self.op_folder = self.conf.op_folder

			Language(self.conf)
			
			title = _('Moitessier HAT Setup')

			wx.Frame.__init__(self, None, title=title, size=(710,460))
			
			self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
			
			self.icon = wx.Icon(op_folder+'/static/icons/moitessier_hat.ico', wx.BITMAP_TYPE_ICO)
			self.SetIcon(self.icon)
			self.help_bmp = wx.Bitmap(self.op_folder + "/static/icons/help-browser.png", wx.BITMAP_TYPE_ANY)

			self.p = wx.lib.scrolledpanel.ScrolledPanel(self, -1, style=wx.TAB_TRAVERSAL | wx.SUNKEN_BORDER)
			self.p.SetAutoLayout(1)
			self.p.SetupScrolling()
			self.nb = wx.Notebook(self.p)
			self.p_info = wx.Panel(self.nb)
			self.p_settings = wx.Panel(self.nb)
			self.p_update = wx.Panel(self.nb)
			self.p_configure = wx.Panel(self.nb)
			self.nb.AddPage(self.p_info, _('HAT info'))
			self.nb.AddPage(self.p_update, _('Install drivers'))
			self.nb.AddPage(self.p_configure, _('OpenPlotter configuration'))
			self.nb.AddPage(self.p_settings, _('Play with settings'))
			sizer = wx.BoxSizer()
			sizer.Add(self.nb, 1, wx.EXPAND)
			self.p.SetSizer(sizer)

##################################################################### info

			info_box = wx.StaticBox(self.p_info, -1, _(' Info '))

			self.button_get_info =wx.Button(self.p_info, label= _('Settings'))
			self.Bind(wx.EVT_BUTTON, self.on_get_info, self.button_get_info)

			self.button_statistics =wx.Button(self.p_info, label= _('Statistics'))
			self.Bind(wx.EVT_BUTTON, self.on_statistics, self.button_statistics)

			self.button_reset_statistics =wx.Button(self.p_info, label= _('Reset statistics'))
			self.Bind(wx.EVT_BUTTON, self.on_reset_statistics, self.button_reset_statistics)

			sensors_box = wx.StaticBox(self.p_info, -1, _(' Test sensors '))

			self.button_MPU9250 =wx.Button(self.p_info, label= _('MPU-9250'))
			self.Bind(wx.EVT_BUTTON, self.on_MPU9250, self.button_MPU9250)

			self.button_MS560702BA03 =wx.Button(self.p_info, label= _('MS5607-02BA03'))
			self.Bind(wx.EVT_BUTTON, self.on_MS560702BA03, self.button_MS560702BA03)

			self.button_Si7020A20 =wx.Button(self.p_info, label= _('Si7020-A20'))
			self.Bind(wx.EVT_BUTTON, self.on_Si7020A20, self.button_Si7020A20)

			self.logger = rt.RichTextCtrl(self.p_info, style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_DONTWRAP|wx.LC_SORT_ASCENDING)
			self.logger.SetMargins((10,10))

			help_button = wx.BitmapButton(self.p_info, bitmap=self.help_bmp, size=(self.help_bmp.GetWidth()+40, self.help_bmp.GetHeight()+10))
			help_button.Bind(wx.EVT_BUTTON, self.on_help)

			shop =wx.Button(self.p_info, label=_('Shop'))
			self.Bind(wx.EVT_BUTTON, self.onShop, shop)

			checkB =wx.Button(self.p_info, label=_('Check'))
			self.Bind(wx.EVT_BUTTON, self.onCheck, checkB)

			button_ok =wx.Button(self.p_info, label=_('Close'))
			self.Bind(wx.EVT_BUTTON, self.on_ok, button_ok)

			h_boxSizer1 = wx.StaticBoxSizer(info_box, wx.HORIZONTAL)
			h_boxSizer1.AddSpacer(5)
			h_boxSizer1.Add(self.button_get_info, 0, wx.ALL | wx.EXPAND, 5)
			h_boxSizer1.Add(self.button_statistics, 0, wx.ALL | wx.EXPAND, 5)
			h_boxSizer1.Add(self.button_reset_statistics, 0, wx.ALL | wx.EXPAND, 5)

			h_boxSizer3 = wx.StaticBoxSizer(sensors_box, wx.HORIZONTAL)
			h_boxSizer3.AddSpacer(5)
			h_boxSizer3.Add(self.button_MPU9250, 0, wx.ALL | wx.EXPAND, 5)
			h_boxSizer3.Add(self.button_MS560702BA03, 0, wx.ALL | wx.EXPAND, 5)
			h_boxSizer3.Add(self.button_Si7020A20, 0, wx.ALL | wx.EXPAND, 5)

			buttons = wx.BoxSizer(wx.HORIZONTAL)
			buttons.Add(help_button, 0, wx.ALL | wx.EXPAND, 0)
			buttons.Add(shop, 0, wx.LEFT | wx.EXPAND, 10)
			buttons.AddStretchSpacer(1)
			buttons.Add(checkB, 0, wx.ALL | wx.EXPAND, 0)
			buttons.Add(button_ok, 0, wx.LEFT | wx.EXPAND, 10)

			vbox3 = wx.BoxSizer(wx.VERTICAL)
			vbox3.Add(h_boxSizer1, 0, wx.ALL | wx.EXPAND, 5)
			vbox3.Add(h_boxSizer3, 0, wx.ALL | wx.EXPAND, 5)
			vbox3.Add(self.logger, 1, wx.ALL | wx.EXPAND, 5)
			vbox3.Add(buttons, 0, wx.ALL | wx.EXPAND, 5)

			self.p_info.SetSizer(vbox3)

##################################################################### settings

			gnss_box = wx.StaticBox(self.p_settings, -1, ' GNSS ')

			self.button_enable_gnss =wx.Button(self.p_settings, label= _('Enable'))
			self.Bind(wx.EVT_BUTTON, self.on_enable_gnss, self.button_enable_gnss)

			self.button_disable_gnss =wx.Button(self.p_settings, label= _('Disable'))
			self.Bind(wx.EVT_BUTTON, self.on_disable_gnss, self.button_disable_gnss)

			general_box = wx.StaticBox(self.p_settings, -1, _(' General '))

			self.button_reset =wx.Button(self.p_settings, label= _('Reset HAT'))
			self.Bind(wx.EVT_BUTTON, self.on_reset, self.button_reset)

			self.button_defaults =wx.Button(self.p_settings, label= _('Load defaults'))
			self.Bind(wx.EVT_BUTTON, self.on_defaults, self.button_defaults)

			ais_box = wx.StaticBox(self.p_settings, -1, ' AIS ')

			self.simulator = wx.CheckBox(self.p_settings, label=_('enable simulator'))

			interval_label = wx.StaticText(self.p_settings, -1, _('interval (ms)'))
			self.interval = wx.SpinCtrl(self.p_settings, min=1, max=9999, initial=1000)

			mmsi1_label = wx.StaticText(self.p_settings, -1, _('MMSI boat 1'))
			self.mmsi1 = wx.SpinCtrl(self.p_settings, min=111111, max=999999999, initial=5551122)

			mmsi2_label = wx.StaticText(self.p_settings, -1, _('MMSI boat 2'))
			self.mmsi2 = wx.SpinCtrl(self.p_settings, min=111111, max=999999999, initial=6884120)

			freq1_label = wx.StaticText(self.p_settings, -1, _('channel A [Hz]'))
			freq2_label = wx.StaticText(self.p_settings, -1, _('channel B [Hz]'))
			metamask_label = wx.StaticText(self.p_settings, -1, 'meta data')
			afcRange_label = wx.StaticText(self.p_settings, -1, 'AFC range [Hz]')

			self.rec1_freq1 = wx.SpinCtrl(self.p_settings, min=159000000, max=162025000, initial=161975000)
			self.rec1_freq2 = wx.SpinCtrl(self.p_settings, min=159000000, max=162025000, initial=162025000)
			self.rec1_metamask = wx.Choice(self.p_settings, choices=(_('none'),'RSSI'), style=wx.CB_READONLY)
			self.rec1_metamask.SetSelection(0)
			self.rec1_afcRange = wx.SpinCtrl(self.p_settings, min=500, max=2000, initial=1500)

			self.logger2 = rt.RichTextCtrl(self.p_settings, style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_DONTWRAP|wx.LC_SORT_ASCENDING)
			self.logger2.SetMargins((10,10))

			help_button = wx.BitmapButton(self.p_settings, bitmap=self.help_bmp, size=(self.help_bmp.GetWidth()+40, self.help_bmp.GetHeight()+10))
			help_button.Bind(wx.EVT_BUTTON, self.on_help)

			self.button_apply =wx.Button(self.p_settings, label=_('Apply changes'))
			self.Bind(wx.EVT_BUTTON, self.on_apply, self.button_apply)

			button_ok2 =wx.Button(self.p_settings, label=_('Close'))
			self.Bind(wx.EVT_BUTTON, self.on_ok, button_ok2)

			h_boxSizer2 = wx.StaticBoxSizer(gnss_box, wx.HORIZONTAL)
			h_boxSizer2.AddSpacer(5)
			h_boxSizer2.Add(self.button_enable_gnss, 1, wx.ALL | wx.EXPAND, 5)
			h_boxSizer2.Add(self.button_disable_gnss, 1, wx.ALL | wx.EXPAND, 5)

			h_boxSizer4 = wx.StaticBoxSizer(general_box, wx.HORIZONTAL)
			h_boxSizer4.AddSpacer(5)
			h_boxSizer4.Add(self.button_reset, 1, wx.ALL | wx.EXPAND, 5)
			h_boxSizer4.Add(self.button_defaults, 1, wx.ALL | wx.EXPAND, 5)

			h_boxSizer5 = wx.BoxSizer(wx.HORIZONTAL)
			h_boxSizer5.Add(h_boxSizer2, 1, wx.RIGHT | wx.EXPAND, 10)
			h_boxSizer5.Add(h_boxSizer4, 1, wx.ALL | wx.EXPAND, 0)

			h_boxSizer6 = wx.BoxSizer(wx.HORIZONTAL)
			h_boxSizer6.Add((0,0), 1, wx.LEFT | wx.EXPAND, 5)
			h_boxSizer6.Add(interval_label, 1, wx.LEFT | wx.EXPAND, 5)
			h_boxSizer6.Add(mmsi1_label, 1, wx.LEFT | wx.EXPAND, 5)
			h_boxSizer6.Add(mmsi2_label, 1, wx.LEFT | wx.EXPAND, 5)

			h_boxSizer7 = wx.BoxSizer(wx.HORIZONTAL)
			h_boxSizer7.Add(self.simulator, 1, wx.ALL | wx.EXPAND, 5)
			h_boxSizer7.Add(self.interval, 1, wx.ALL | wx.EXPAND, 5)
			h_boxSizer7.Add(self.mmsi1, 1, wx.ALL | wx.EXPAND, 5)
			h_boxSizer7.Add(self.mmsi2, 1, wx.ALL | wx.EXPAND, 5)

			rec1_labels = wx.BoxSizer(wx.HORIZONTAL)
			rec1_labels.Add(freq1_label, 1, wx.LEFT | wx.EXPAND, 5)
			rec1_labels.Add(freq2_label, 1, wx.LEFT | wx.EXPAND, 5)
			rec1_labels.Add(metamask_label, 1, wx.LEFT | wx.EXPAND, 5)
			rec1_labels.Add(afcRange_label, 1, wx.LEFT | wx.EXPAND, 5)

			receiver1 = wx.BoxSizer(wx.HORIZONTAL)
			receiver1.Add(self.rec1_freq1, 1, wx.ALL | wx.EXPAND, 5)
			receiver1.Add(self.rec1_freq2, 1, wx.ALL | wx.EXPAND, 5)
			receiver1.Add(self.rec1_metamask, 1, wx.ALL | wx.EXPAND, 5)
			receiver1.Add(self.rec1_afcRange, 1, wx.ALL | wx.EXPAND, 5)

			v_boxSizer8 = wx.StaticBoxSizer(ais_box, wx.VERTICAL)
			v_boxSizer8.Add(h_boxSizer6, 0, wx.ALL | wx.EXPAND, 0)
			v_boxSizer8.Add(h_boxSizer7, 0, wx.ALL | wx.EXPAND, 0)
			v_boxSizer8.AddSpacer(15)
			v_boxSizer8.Add(rec1_labels, 0, wx.ALL | wx.EXPAND, 0)
			v_boxSizer8.Add(receiver1, 0, wx.ALL | wx.EXPAND, 0)
	

			buttons2 = wx.BoxSizer(wx.HORIZONTAL)
			buttons2.Add(help_button, 0, wx.ALL | wx.EXPAND, 0)
			buttons2.AddStretchSpacer(1)
			buttons2.Add(self.button_apply, 0, wx.RIGHT | wx.EXPAND, 10)
			buttons2.Add(button_ok2, 0, wx.ALL | wx.EXPAND, 0)

			vbox4 = wx.BoxSizer(wx.VERTICAL)
			vbox4.Add(h_boxSizer5, 0, wx.ALL | wx.EXPAND, 5)
			vbox4.Add(v_boxSizer8, 0, wx.ALL | wx.EXPAND, 5)
			vbox4.Add(self.logger2, 1, wx.ALL | wx.EXPAND, 5)
			vbox4.Add(buttons2, 0, wx.ALL | wx.EXPAND, 5)

			self.p_settings.SetSizer(vbox4)

##################################################################### install

			kernel_box = wx.StaticBox(self.p_update, -1, _(' Current kernel version '))

			self.kernel_label = wx.StaticText(self.p_update, -1)

			packages_box = wx.StaticBox(self.p_update, -1, _(' Available packages '))

			self.packages_list = []
			self.packages_select = wx.Choice(self.p_update, choices=self.packages_list, style=wx.CB_READONLY)
			self.readAvailable()

			self.button_install =wx.Button(self.p_update, label=_('Install'))
			self.Bind(wx.EVT_BUTTON, self.on_install, self.button_install)

			downloadB =wx.Button(self.p_update, label=_('Download'))
			self.Bind(wx.EVT_BUTTON, self.onDownload, downloadB)

			drivers =wx.Button(self.p_update, label=_('All drivers'))
			self.Bind(wx.EVT_BUTTON, self.onDrivers, drivers)

			self.logger3 = rt.RichTextCtrl(self.p_update, style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_DONTWRAP|wx.LC_SORT_ASCENDING)
			self.logger3.SetMargins((10,10))

			help_button = wx.BitmapButton(self.p_update, bitmap=self.help_bmp, size=(self.help_bmp.GetWidth()+40, self.help_bmp.GetHeight()+10))
			help_button.Bind(wx.EVT_BUTTON, self.on_help)

			button_ok3 =wx.Button(self.p_update, label=_('Close'))
			self.Bind(wx.EVT_BUTTON, self.on_ok, button_ok3)

			v_kernel_box = wx.StaticBoxSizer(kernel_box, wx.VERTICAL)
			v_kernel_box.AddSpacer(5)
			v_kernel_box.Add(self.kernel_label, 0, wx.ALL | wx.EXPAND, 5)

			h_packages_box = wx.StaticBoxSizer(packages_box, wx.HORIZONTAL)
			h_packages_box.Add(self.packages_select, 1, wx.ALL | wx.EXPAND, 5)
			h_packages_box.Add(self.button_install, 0, wx.ALL | wx.EXPAND, 5)
			h_packages_box.Add(downloadB, 0, wx.ALL | wx.EXPAND, 5)
			h_packages_box.Add(drivers, 0, wx.ALL | wx.EXPAND, 5)

			buttons3 = wx.BoxSizer(wx.HORIZONTAL)
			buttons3.Add(help_button, 0, wx.ALL | wx.EXPAND, 0)
			buttons3.AddStretchSpacer(1)
			buttons3.Add(button_ok3, 0, wx.ALL | wx.EXPAND, 0)

			update_final = wx.BoxSizer(wx.VERTICAL)
			update_final.Add(v_kernel_box, 0, wx.ALL | wx.EXPAND, 5)
			update_final.Add(h_packages_box, 0, wx.ALL | wx.EXPAND, 5)
			update_final.Add(self.logger3, 1, wx.ALL | wx.EXPAND, 5)
			update_final.Add(buttons3, 0, wx.ALL | wx.EXPAND, 5)

			self.p_update.SetSizer(update_final)

##################################################################### configure

			checkConfB =wx.Button(self.p_configure, label= _('Check'))
			self.Bind(wx.EVT_BUTTON, self.onCheckConfB, checkConfB)

			self.logger4 = rt.RichTextCtrl(self.p_configure, style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_DONTWRAP|wx.LC_SORT_ASCENDING)
			self.logger4.SetMargins((10,10))

			help_button = wx.BitmapButton(self.p_configure, bitmap=self.help_bmp, size=(self.help_bmp.GetWidth()+40, self.help_bmp.GetHeight()+10))
			help_button.Bind(wx.EVT_BUTTON, self.on_help)

			button_ok4 =wx.Button(self.p_configure, label=_('Close'))
			self.Bind(wx.EVT_BUTTON, self.on_ok, button_ok4)

			buttons4 = wx.BoxSizer(wx.HORIZONTAL)
			buttons4.Add(help_button, 0, wx.ALL | wx.EXPAND, 0)
			buttons4.AddStretchSpacer(1)
			buttons4.Add(checkConfB, 0, wx.ALL | wx.EXPAND, 0)
			buttons4.Add(button_ok4, 0, wx.LEFT | wx.EXPAND, 10)

			vbox5 = wx.BoxSizer(wx.VERTICAL)
			vbox5.Add(self.logger4, 1, wx.ALL | wx.EXPAND, 5)
			vbox5.Add(buttons4, 0, wx.ALL | wx.EXPAND, 5)

			self.p_configure.SetSizer(vbox5)

#####################################################################

			self.Centre()
			self.read()

		def onCheckConfB(self,e=0):
			self.conf = Conf()
			self.SK_settings = SK_settings(self.conf)
			self.opencpnSettings = opencpnSettings()
			self.logger4.Clear()

			serialInst = self.conf.get('UDEV', 'Serialinst')
			try: serialInst = eval(serialInst)
			except: serialInst = {}
			serialalias = ''
			assignment = ''
			device = ''
			for alias in serialInst:
				if serialInst[alias]['device'] == '/dev/moitessier.tty' and serialInst[alias]['data'] == 'NMEA 0183': 
					serialalias = alias
					assignment = serialInst[alias]['assignment']
					device = self.SK_settings.check_device(alias)

			pypilot = self.conf.get('PYPILOT', 'mode')
			heading = self.conf.get('PYPILOT', 'translation_magnetic_h')
			attitude = self.conf.get('PYPILOT', 'translation_attitude')

			i2c = self.conf.get('I2C', 'sensors')
			try: i2c = eval(i2c)
			except: i2c = {}
			pressure = ''
			temperature = ''
			for sensor in i2c:
				if sensor[0] == 'MS5607-02BA03' and sensor[1] == '0x77':
					pressure = sensor[2][0][0]
					temperature = sensor[2][1][0]

			XDRBaro = False
			SKplugin = False
			setting_file = self.home+'/.signalk/plugin-config-data/sk-to-nmea0183.json'
			if os.path.isfile(setting_file):
				with open(setting_file) as data_file:
					data = ujson.load(data_file)
				if 'enabled' in data: SKplugin = data['enabled']
				if 'configuration' in data:
					if 'XDRBaro' in data['configuration']: XDRBaro = data['configuration']['XDRBaro']

			opencpnConnection = self.opencpnSettings.getConnectionState()

			self.logger4.BeginTextColour((55, 55, 55))
			self.logger4.BeginBold()
			self.logger4.WriteText('AIS - GNSS')
			self.logger4.EndBold()
			self.logger4.Newline()
			self.logger4.WriteText(_('Serial alias: '))
			self.logger4.EndTextColour()
			if serialalias:
				self.logger4.BeginTextColour((0, 255, 0))
				self.logger4.WriteText(serialalias)
			else:
				self.logger4.BeginTextColour((255, 0, 0))
				self.logger4.WriteText(_('none'))
			self.logger4.EndTextColour()
			self.logger4.Newline()
			self.logger4.BeginTextColour((55, 55, 55))
			self.logger4.WriteText(_('Assignment: '))
			self.logger4.EndTextColour()
			if not assignment:
				self.logger4.BeginTextColour((255, 0, 0))
				self.logger4.WriteText(_('none'))
			elif assignment != 'GPSD':
				if assignment == '0': x = _('manual')
				else: x = assignment
				self.logger4.BeginTextColour((0, 255, 0))
				self.logger4.WriteText(x)
			else:
				self.logger4.BeginTextColour((255, 0, 0))
				self.logger4.WriteText(assignment)
			self.logger4.EndTextColour()
			self.logger4.Newline()
			self.logger4.BeginTextColour((55, 55, 55))
			self.logger4.WriteText(_('Signal K connection status: '))
			self.logger4.EndTextColour()
			if not assignment:
				self.logger4.BeginTextColour((255, 0, 0))
				self.logger4.WriteText(_('none'))
			elif assignment == '0' or assignment == 'GPSD' or assignment == 'Signal K > OpenCPN':
				if device == 'enabled':
					self.logger4.BeginTextColour((0, 255, 0))
					self.logger4.WriteText(_('enabled'))
				elif device == 'disabled':
					self.logger4.BeginTextColour((255, 0, 0))
					self.logger4.WriteText(_('disabled'))
				else:
					self.logger4.BeginTextColour((255, 0, 0))
					self.logger4.WriteText(_('connection does not exist'))
			elif 'pypilot' in assignment:
				if self.SK_settings.pypilot_enabled == True:
					self.logger4.BeginTextColour((0, 255, 0))
					self.logger4.WriteText(_('enabled'))
				else:
					self.logger4.BeginTextColour((255, 0, 0))
					self.logger4.WriteText(_('disabled'))
			else:
				self.logger4.BeginTextColour((255, 0, 0))
				self.logger4.WriteText(_('none'))
			self.logger4.EndTextColour()

			self.logger4.BeginTextColour((55, 55, 55))
			self.logger4.Newline()
			self.logger4.BeginBold()
			self.logger4.WriteText(_('Compass - Heel - Trim'))
			self.logger4.EndBold()
			self.logger4.Newline()
			self.logger4.WriteText(_('Pypilot status: '))
			self.logger4.EndTextColour()
			if pypilot == 'basic autopilot' or pypilot == 'imu':
				self.logger4.BeginTextColour((0, 255, 0))
				self.logger4.WriteText(_('enabled'))
			else:
				self.logger4.BeginTextColour((255, 0, 0))
				self.logger4.WriteText(_('disabled'))
			self.logger4.EndTextColour()
			self.logger4.Newline()
			self.logger4.BeginTextColour((55, 55, 55))
			self.logger4.WriteText(_('Heading: '))
			self.logger4.EndTextColour()
			if pypilot != 'disabled' and heading == '1':
				self.logger4.BeginTextColour((0, 255, 0))
				self.logger4.WriteText(_('enabled'))
			else:
				self.logger4.BeginTextColour((255, 0, 0))
				self.logger4.WriteText(_('disabled'))
			self.logger4.EndTextColour()
			self.logger4.Newline()
			self.logger4.BeginTextColour((55, 55, 55))
			self.logger4.WriteText(_('Pitch, Roll: '))
			self.logger4.EndTextColour()
			if pypilot != 'disabled' and attitude == '1':
				self.logger4.BeginTextColour((0, 255, 0))
				self.logger4.WriteText(_('enabled'))
			else:
				self.logger4.BeginTextColour((255, 0, 0))
				self.logger4.WriteText(_('disabled'))
			self.logger4.EndTextColour()

			self.logger4.Newline()
			self.logger4.BeginTextColour((55, 55, 55))
			self.logger4.BeginBold()
			self.logger4.WriteText(_('Pressure - Temperature'))
			self.logger4.EndBold()
			self.logger4.Newline()
			self.logger4.WriteText(_('I2C - Signal K key for pressure: '))
			self.logger4.EndTextColour()
			if pressure:
				self.logger4.BeginTextColour((0, 255, 0))
				self.logger4.WriteText(pressure)
			else:
				self.logger4.BeginTextColour((255, 0, 0))
				self.logger4.WriteText(_('none'))
			self.logger4.EndTextColour()
			self.logger4.Newline()
			self.logger4.BeginTextColour((55, 55, 55))
			self.logger4.WriteText(_('I2C - Signal K key for temperature: '))
			self.logger4.EndTextColour()
			if temperature:
				self.logger4.BeginTextColour((0, 255, 0))
				self.logger4.WriteText(temperature)
			else:
				self.logger4.BeginTextColour((255, 0, 0))
				self.logger4.WriteText(_('none'))
			self.logger4.EndTextColour()
			self.logger4.Newline()
			self.logger4.BeginTextColour((55, 55, 55))
			self.logger4.WriteText(_('Signal K to NMEA 0183 plugin: '))
			self.logger4.EndTextColour()
			if SKplugin:
				self.logger4.BeginTextColour((0, 255, 0))
				self.logger4.WriteText(_('enabled'))
			else:
				self.logger4.BeginTextColour((255, 0, 0))
				self.logger4.WriteText(_('disabled'))
			self.logger4.EndTextColour()
			self.logger4.Newline()
			self.logger4.BeginTextColour((55, 55, 55))
			self.logger4.WriteText(_('XDR (Barometer) conversion: '))
			self.logger4.EndTextColour()
			if SKplugin and XDRBaro:
				self.logger4.BeginTextColour((0, 255, 0))
				self.logger4.WriteText(_('enabled'))
			else:
				self.logger4.BeginTextColour((255, 0, 0))
				self.logger4.WriteText(_('disabled'))
			self.logger4.EndTextColour()

			self.logger4.Newline()
			self.logger4.BeginTextColour((55, 55, 55))
			self.logger4.BeginBold()
			self.logger4.WriteText(_('OpenCPN'))
			self.logger4.EndBold()
			self.logger4.Newline()
			self.logger4.WriteText(_('Signal K connection: '))
			self.logger4.EndTextColour()
			if opencpnConnection:
				self.logger4.BeginTextColour((0, 255, 0))
				self.logger4.WriteText(_('TCP localhost 10110 input'))
			else:
				self.logger4.BeginTextColour((255, 0, 0))
				self.logger4.WriteText(_('missing TCP localhost 10110 input'))
			self.logger4.EndTextColour()
			self.logger4.Newline()
			self.logger4.BeginTextColour((55, 55, 55))
			self.logger4.WriteText(_('Status: '))
			self.logger4.EndTextColour()
			if not opencpnConnection or opencpnConnection == 'disabled':
				self.logger4.BeginTextColour((255, 0, 0))
				self.logger4.WriteText(_('disabled'))
			if opencpnConnection == 'enabled':
				self.logger4.BeginTextColour((0, 255, 0))
				self.logger4.WriteText(_('enabled'))


		def onDownload(self,e):
			self.logger3.Clear()
			self.logger3.BeginTextColour((55, 55, 55))
			kernel = subprocess.check_output(['uname','-r'])
			kernel = kernel.split('-')
			kernel = kernel[0]
			file = 'moitessier_'+kernel+'_armhf.deb'
			self.logger3.WriteText(_('Searching file '))
			self.logger3.BeginBold()
			self.logger3.WriteText(file)
			self.logger3.EndBold()
			self.logger3.WriteText(' ...')
			self.logger3.Newline()
			if os.path.isfile(self.op_folder+'/tools/moitessier_hat/packages/'+file):
				self.logger3.WriteText(_('This file already exists!'))
			else:
				try:
					out = subprocess.check_output(['wget','https://get.rooco.tech/moitessier/release/'+kernel+'/latest/'+file, '-P', self.op_folder+'/tools/moitessier_hat/packages'])
					self.logger3.WriteText(_('File downloaded!'))
				except:
					self.logger3.WriteText(_('File not found!'))
			self.logger3.EndTextColour()
			self.readAvailable()

		def readAvailable(self):
			self.packages_select.Clear()
			self.packages_list = []
			kernel = subprocess.check_output(['uname','-r'])
			kernel = kernel.split('.')
			kernelA = int(kernel[0])
			kernelB = int(kernel[1])
			kernelC = kernel[2].split('-')
			kernelC = int(kernelC[0])
			tmp = os.listdir(self.op_folder+'/tools/moitessier_hat/packages')
			for i in tmp:
				package = i.split('_')
				package = package[1]
				package = package.split('.')
				packageA = int(package[0])
				packageB = int(package[1])
				packageC = int(package[2])
				if packageA >= kernelA:
					if packageB >= kernelB:
						if packageC >= kernelC: self.packages_list.append(i)
			self.packages_select.AppendItems(self.packages_list)
			if len(self.packages_list)>0: self.packages_select.SetSelection(0)

		def onCheck(self,e=0):
			self.logger.Clear()
			self.logger.BeginBold()
			try:
				out = subprocess.check_output(['more','product'],cwd='/proc/device-tree/hat')
			except:
				self.logger.BeginTextColour((255, 0, 0))
				self.logger.WriteText(_('Moitessier HAT is not attached!\n'))
				self.logger.EndTextColour()
				self.disable_info_settings_buttons()
			else:
				if not 'Moitessier' in out: 
					self.logger.BeginTextColour((255, 0, 0))
					self.logger.WriteText(_('Moitessier HAT is not attached!\n'))
					self.logger.EndTextColour()
					self.disable_info_settings_buttons()
				else: 
					self.logger.BeginTextColour((0, 255, 0))
					self.logger.WriteText(_('Moitessier HAT is attached.\n'))
					self.logger.EndTextColour()

			if not os.path.isfile(self.home+'/moitessier/app/moitessier_ctrl/moitessier_ctrl'):
				self.logger.BeginTextColour((255, 0, 0))
				self.logger.WriteText(_('Moitessier HAT package is not installed!\n'))
				self.logger.EndTextColour()
				self.disable_info_settings_buttons()
			else:
				self.logger.BeginTextColour((0, 255, 0))
				self.logger.WriteText(_('Moitessier HAT package is installed.\n'))
				self.logger.EndTextColour()
				self.logger.EndBold()
				self.logger.BeginTextColour((55, 55, 55))
				package = subprocess.check_output(['dpkg','-s','moitessier'])
				self.logger.WriteText(package)
				self.logger.EndTextColour()

				kernel = subprocess.check_output(['uname','-r'])
				kernel = kernel.split('-')
				kernel = kernel[0]
				package = package.split('\n')
				for i in package:
					if 'Version:' in i:
						version = self.extract_value(i)
						version = version.split('-')
						version = version[2]
				if kernel != version:
					self.logger.BeginBold()
					self.logger.BeginTextColour((255, 0, 0))
					self.logger.WriteText(_('The installed package does not match the kernel version. Go to "install" tab to update the package.'))
					self.logger.EndTextColour()
					self.logger.EndBold()

		def extract_value(self, data):
			option, value = data.split(':')
			value = value.strip()
			return value

		def read(self):
			self.onCheck()
			try:
				settings = subprocess.check_output([self.home+'/moitessier/app/moitessier_ctrl/moitessier_ctrl','/dev/moitessier.ctrl','1'])
				settings = settings.replace('\t','')
				settings = settings.split('\n')
				for i in settings:
					if 'enabled:' in i:
						if self.extract_value(i) == '1': self.simulator.SetValue(True)
						else: self.simulator.SetValue(False)
					if 'interval:' in i:
						self.interval.SetValue(int(self.extract_value(i)))
					if 'mmsi:' in i:
						data = self.extract_value(i)
						data = data.split(' ')
						self.mmsi1.SetValue(int(data[0])) 
						self.mmsi2.SetValue(int(data[1]))
					if 'channel frequency 1 [Hz]:' in i:
						self.rec1_freq1.SetValue(int(self.extract_value(i)))
					if 'channel frequency 2 [Hz]:' in i:
						self.rec1_freq2.SetValue(int(self.extract_value(i)))
					if 'meta data mask:' in i:
						if self.extract_value(i) == '0x00': self.rec1_metamask.SetSelection(0)
						else: self.rec1_metamask.SetSelection(1)
					if 'afc range [Hz]:' in i and not 'default' in i:
						self.rec1_afcRange.SetValue(int(self.extract_value(i)))
			except:
				self.logger2.BeginTextColour((255, 0, 0))
				self.logger2.WriteText(_('Failure reading HAT settings!'))
				self.logger2.EndTextColour()
				self.disable_info_settings_buttons()
			else:
				self.logger2.BeginTextColour((55, 55, 55))
				self.logger2.WriteText(_('All changes will be temporal.\nDefault settings will be loaded after rebooting.\n'))
				self.logger2.EndTextColour()

			self.current_kernel = subprocess.check_output(['uname','-r','-v'])
			self.kernel_label.SetLabel(self.current_kernel)
			self.logger3.BeginTextColour((55, 55, 55))
			self.logger3.WriteText(_('Select the package that fits to the current kernel version.'))
			self.logger3.Newline()
			self.logger3.WriteText(_('If there is no matching package, connect to internet and try to download it.'))
			self.logger3.Newline()
			self.logger3.WriteText(_('Before installing, be sure the HAT is not being used by any service (Signal K, Kplex, GPSD, OpenCPN ...).'))
			self.logger3.Newline()
			self.logger3.WriteText(_('If installation fails, you may have to try to reboot and install the package again.'))
			self.logger3.EndTextColour()
			self.onCheckConfB()

		def on_install(self,e):
			if self.packages_select.GetStringSelection() == '':
				self.logger3.SetValue(_('Select a package to install.'))
			else:
				subprocess.Popen(['lxterminal', '-e', 'bash', self.op_folder+'/tools/moitessier_hat/install.sh', self.op_folder+'/tools/moitessier_hat/packages/'+self.packages_select.GetStringSelection()])
				self.logger3.SetValue(_('Updating Moitessier Hat modules and firmware...'))

		def disable_info_settings_buttons(self):
			self.button_get_info.Disable()
			self.button_statistics.Disable()
			self.button_reset_statistics.Disable()
			self.button_MPU9250.Disable()
			self.button_MS560702BA03.Disable()
			self.button_Si7020A20.Disable()
			self.button_enable_gnss.Disable()
			self.button_disable_gnss.Disable()
			self.button_reset.Disable()
			self.button_defaults.Disable()
			self.simulator.Disable()
			self.interval.Disable()
			self.mmsi1.Disable()
			self.mmsi2.Disable()
			self.rec1_freq1.Disable()
			self.rec1_freq2.Disable()
			self.rec1_metamask.Disable()
			self.rec1_afcRange.Disable()
			self.button_apply.Disable()

		def on_defaults(self,e):
			try:
				tree = ET.parse(self.home+'/moitessier/app/moitessier_ctrl/default_config.xml')
				root = tree.getroot()
				for item in root.iter("simulator"):
					for subitem in item.iter("enabled"):
						if subitem.text == '1': self.simulator.SetValue(True)
						else: self.simulator.SetValue(False)
					for subitem in item.iter("interval"):
						self.interval.SetValue(int(subitem.text))
					for subitem in item.iter("mmsi"):
						self.mmsi1.SetValue(int(subitem[0].text)) 
						self.mmsi2.SetValue(int(subitem[1].text))
				for item in root.iterfind('receiver[@name="receiver1"]'):
					for subitem in item.iter("channelFreq"):
						self.rec1_freq1.SetValue(int(subitem[0].text)) 
						self.rec1_freq2.SetValue(int(subitem[1].text))
					for subitem in item.iter("metamask"):
						if subitem.text == '0': self.rec1_metamask.SetSelection(0)
						else: self.rec1_metamask.SetSelection(1)
					for subitem in item.iter("afcRange"):
						self.rec1_afcRange.SetValue(int(subitem.text)) 
			except:
				self.logger2.Clear()
				self.logger2.BeginTextColour((255, 0, 0))
				self.logger2.WriteText(_('Failure reading default_config.xml file!'))
				self.logger2.EndTextColour()
			else:
				self.logger2.Clear()
				self.logger2.BeginTextColour((55, 55, 55))
				self.logger2.WriteText(_('Defaults loaded. Apply changes.'))
				self.logger2.EndTextColour()

		def on_apply(self,e=0):
			try: 
				tree = ET.parse(self.home+'/moitessier/app/moitessier_ctrl/config.xml')
				root = tree.getroot()
				for item in root.iter("simulator"):
					for subitem in item.iter("enabled"):
						if self.simulator.GetValue(): subitem.text = '1'
						else: subitem.text = '0'
					for subitem in item.iter("interval"):
						subitem.text = str(self.interval.GetValue())
					for subitem in item.iter("mmsi"):
						subitem[0].text = str(self.mmsi1.GetValue())
						subitem[1].text = str(self.mmsi2.GetValue())
				for item in root.iterfind('receiver[@name="receiver1"]'):
					for subitem in item.iter("channelFreq"):
						subitem[0].text = str(self.rec1_freq1.GetValue())
						subitem[1].text = str(self.rec1_freq2.GetValue())
					for subitem in item.iter("metamask"):
						if self.rec1_metamask.GetSelection() == 0: subitem.text = '0'
						else: subitem.text = '16'
					for subitem in item.iter("afcRange"):
						subitem.text = str(self.rec1_afcRange.GetValue())
				for item in root.iterfind('receiver[@name="receiver2"]'):
					for subitem in item.iter("channelFreq"):
						subitem[0].text = str(self.rec1_freq1.GetValue())
						subitem[1].text = str(self.rec1_freq2.GetValue())
					for subitem in item.iter("metamask"):
						if self.rec1_metamask.GetSelection() == 0: subitem.text = '0'
						else: subitem.text = '16'
					for subitem in item.iter("afcRange"):
						subitem.text = str(self.rec1_afcRange.GetValue())
				tree.write(self.home+'/moitessier/app/moitessier_ctrl/config.xml',encoding='utf-8', xml_declaration=True)
				subprocess.call([self.home+'/moitessier/app/moitessier_ctrl/moitessier_ctrl','/dev/moitessier.ctrl','5',self.home+'/moitessier/app/moitessier_ctrl/config.xml'])
				self.logger2.Clear()
				self.logger2.BeginTextColour((55, 55, 55))
				self.logger2.WriteText(_('Changes applied.'))
				self.logger2.EndTextColour()
			except: 
				self.logger2.Clear()
				self.logger2.BeginTextColour((255, 0, 0))
				self.logger2.WriteText(_('Apply changes failed!'))
				self.logger2.EndTextColour()

		def on_get_info(self, e):
			self.logger.Clear()
			self.logger.BeginTextColour((55, 55, 55))
			output = subprocess.check_output([self.home+'/moitessier/app/moitessier_ctrl/moitessier_ctrl','/dev/moitessier.ctrl','1'])
			self.logger.WriteText(output)
			self.logger.EndTextColour()

		def on_statistics(self, e):
			self.logger.Clear()
			self.logger.BeginTextColour((55, 55, 55))
			output = subprocess.check_output([self.home+'/moitessier/app/moitessier_ctrl/moitessier_ctrl','/dev/moitessier.ctrl','0'])
			self.logger.WriteText(output)
			self.logger.EndTextColour()

		def on_reset_statistics(self, e):
			self.logger.Clear()
			self.logger.BeginTextColour((55, 55, 55))
			output = subprocess.check_output([self.home+'/moitessier/app/moitessier_ctrl/moitessier_ctrl','/dev/moitessier.ctrl','3'])
			self.logger.WriteText(output)
			self.logger.EndTextColour()

		def on_enable_gnss(self, e):
			self.logger2.Clear()
			self.logger2.BeginTextColour((55, 55, 55))
			output = subprocess.check_output([self.home+'/moitessier/app/moitessier_ctrl/moitessier_ctrl','/dev/moitessier.ctrl','4','1'])
			self.logger2.WriteText(output)
			self.logger2.EndTextColour()

		def on_disable_gnss(self, e):
			self.logger2.Clear()
			self.logger2.BeginTextColour((55, 55, 55))
			output = subprocess.check_output([self.home+'/moitessier/app/moitessier_ctrl/moitessier_ctrl','/dev/moitessier.ctrl','4','0'])
			self.logger2.WriteText(output)
			self.logger2.EndTextColour()

		def on_MPU9250(self, e):
			self.logger.Clear()
			self.logger.BeginTextColour((55, 55, 55))
			output = subprocess.check_output([self.home+'/moitessier/app/sensors/MPU-9250', '/dev/i2c-1'])
			self.logger.WriteText(_('MPU-9250 temperature: ')+output)
			self.logger.WriteText(_('To get accurate readings, make sure the sensor is not being read by another application.'))
			self.logger.EndTextColour()

		def on_MS560702BA03(self, e):
			self.logger.Clear()
			self.logger.BeginTextColour((55, 55, 55))
			output = subprocess.check_output([self.home+'/moitessier/app/sensors/MS5607-02BA03', '/dev/i2c-1'])
			self.logger.WriteText(_('MS5607-02BA03 pressure: ')+output)
			self.logger.WriteText(_('To get accurate readings, make sure the sensor is not being read by another application.'))
			self.logger.EndTextColour()

		def on_Si7020A20(self, e):
			self.logger.Clear()
			self.logger.BeginTextColour((55, 55, 55))
			output = subprocess.check_output([self.home+'/moitessier/app/sensors/Si7020-A20', '/dev/i2c-1'])
			if 'Firmware' in output: output = _('This sensor is not mounted on this HAT\n')
			self.logger.WriteText(_('Si7020-A20 humidity: ')+output)
			self.logger.WriteText(_('To get accurate readings, make sure the sensor is not being read by another application.'))
			self.logger.EndTextColour()
			
		def on_reset(self, e):
			self.logger2.Clear()
			self.logger2.BeginTextColour((55, 55, 55))
			output = subprocess.check_output([self.home+'/moitessier/app/moitessier_ctrl/moitessier_ctrl','/dev/moitessier.ctrl','2'])
			self.logger2.WriteText(output)
			self.logger2.EndTextColour()

		def on_help(self, e):
			url = self.op_folder+"/docs/html/tools/moitessier_hat.html"
			webbrowser.open(url, new=2)

		def onShop(self, e):
			url = "https://shop.sailoog.com/openplotter/4-moitessier-hat.html"
			webbrowser.open(url, new=2)

		def onDrivers(self, e):
			url = "https://www.rooco.eu/2018/06/13/firmware-and-drivers-for-raspberry-pi-moitessier-hat/"
			webbrowser.open(url, new=2)

		def on_ok(self, e):
			self.Close()

app = wx.App()
MyFrame().Show()
app.MainLoop()
