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

import wx, wx.lib.scrolledpanel, sys, os, ConfigParser, re, subprocess, time
import xml.etree.ElementTree as ET

op_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../..')
sys.path.append(op_folder+'/classes')
from conf import Conf
from language import Language

class MyFrame(wx.Frame):
		
		def __init__(self):

			self.conf = Conf()
			self.home = self.conf.home
			self.op_folder = self.conf.op_folder

			Language(self.conf)
			
			title = _('Moitessier HAT Settings')

			wx.Frame.__init__(self, None, title=title, size=(710,460))
			
			self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
			
			self.icon = wx.Icon(op_folder+'/openplotter.ico', wx.BITMAP_TYPE_ICO)
			self.SetIcon(self.icon)

			self.p = wx.lib.scrolledpanel.ScrolledPanel(self, -1, style=wx.TAB_TRAVERSAL | wx.SUNKEN_BORDER)
			self.p.SetAutoLayout(1)
			self.p.SetupScrolling()
			self.nb = wx.Notebook(self.p)
			self.p_info = wx.Panel(self.nb)
			self.p_settings = wx.Panel(self.nb)
			self.p_update = wx.Panel(self.nb)
			self.nb.AddPage(self.p_info, _('Info'))
			self.nb.AddPage(self.p_settings, _('Settings'))
			self.nb.AddPage(self.p_update, _('Install'))
			sizer = wx.BoxSizer()
			sizer.Add(self.nb, 1, wx.EXPAND)
			self.p.SetSizer(sizer)

##################################################################### info

			info_box = wx.StaticBox(self.p_info, -1, _(' Info '))

			self.button_get_info =wx.Button(self.p_info, label= _('HAT info'))
			self.Bind(wx.EVT_BUTTON, self.on_get_info, self.button_get_info)

			self.button_statistics =wx.Button(self.p_info, label= _('Statistics'))
			self.Bind(wx.EVT_BUTTON, self.on_statistics, self.button_statistics)

			self.button_reset_statistics =wx.Button(self.p_info, label= _('Reset statistics'))
			self.Bind(wx.EVT_BUTTON, self.on_reset_statistics, self.button_reset_statistics)

			sensors_box = wx.StaticBox(self.p_info, -1, _(' Sensors '))

			self.button_MPU9250 =wx.Button(self.p_info, label= _('MPU-9250'))
			self.Bind(wx.EVT_BUTTON, self.on_MPU9250, self.button_MPU9250)

			self.button_MS560702BA03 =wx.Button(self.p_info, label= _('MS5607-02BA03'))
			self.Bind(wx.EVT_BUTTON, self.on_MS560702BA03, self.button_MS560702BA03)

			self.button_Si7020A20 =wx.Button(self.p_info, label= _('Si7020-A20'))
			self.Bind(wx.EVT_BUTTON, self.on_Si7020A20, self.button_Si7020A20)

			self.logger = wx.TextCtrl(self.p_info, style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_DONTWRAP|wx.LC_SORT_ASCENDING)

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

			buttons_up = wx.BoxSizer(wx.HORIZONTAL)
			buttons_up.Add(h_boxSizer1, 1, wx.ALL | wx.EXPAND, 0)
			buttons_up.Add(h_boxSizer3, 1, wx.LEFT | wx.EXPAND, 10)

			buttons = wx.BoxSizer(wx.HORIZONTAL)
			buttons.Add((0,0), 1, wx.ALL | wx.EXPAND, 0)
			buttons.Add(button_ok, 0, wx.ALL | wx.EXPAND, 0)

			vbox3 = wx.BoxSizer(wx.VERTICAL)
			vbox3.Add(buttons_up, 0, wx.ALL | wx.EXPAND, 5)
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
			self.mmsi1 = wx.SpinCtrl(self.p_settings, min=111111, max=999999999, initial=222222222)

			mmsi2_label = wx.StaticText(self.p_settings, -1, _('MMSI boat 2'))
			self.mmsi2 = wx.SpinCtrl(self.p_settings, min=111111, max=999999999, initial=333333333)

			receiver1_label = wx.StaticText(self.p_settings, -1, '1')
			receiver2_label = wx.StaticText(self.p_settings, -1, '2')
			empty_label = wx.StaticText(self.p_settings, -1, ' ')

			freq1_label = wx.StaticText(self.p_settings, -1, _('frequency 1'))
			freq2_label = wx.StaticText(self.p_settings, -1, _('frequency 2'))
			metamask_label = wx.StaticText(self.p_settings, -1, 'metamask')
			afcRange_label = wx.StaticText(self.p_settings, -1, 'afcRange')
			tcxoFreq_label = wx.StaticText(self.p_settings, -1, 'tcxoFreq')

			self.rec1_freq1 = wx.SpinCtrl(self.p_settings, min=159000000, max=162025000, initial=161975000)
			self.rec1_freq2 = wx.SpinCtrl(self.p_settings, min=159000000, max=162025000, initial=162025000)
			self.rec1_metamask = wx.SpinCtrl(self.p_settings, min=0, max=99, initial=0)
			self.rec1_afcRange = wx.SpinCtrl(self.p_settings, min=500, max=2000, initial=1000)
			self.rec1_tcxoFreq = wx.SpinCtrl(self.p_settings, min=10000000, max=20000000, initial=13000000)

			self.rec2_freq1 = wx.SpinCtrl(self.p_settings, min=159000000, max=162025000, initial=161975000)
			self.rec2_freq2 = wx.SpinCtrl(self.p_settings, min=159000000, max=162025000, initial=162025000)
			self.rec2_metamask = wx.SpinCtrl(self.p_settings, min=0, max=99, initial=0)
			self.rec2_afcRange = wx.SpinCtrl(self.p_settings, min=500, max=2000, initial=1000)
			self.rec2_tcxoFreq = wx.SpinCtrl(self.p_settings, min=10000000, max=20000000, initial=13000000)

			self.logger2 = wx.TextCtrl(self.p_settings, style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_DONTWRAP|wx.LC_SORT_ASCENDING)

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
			rec1_labels.Add(empty_label, 0, wx.LEFT | wx.EXPAND, 15)
			rec1_labels.Add(freq1_label, 1, wx.LEFT | wx.EXPAND, 5)
			rec1_labels.Add(freq2_label, 1, wx.LEFT | wx.EXPAND, 5)
			rec1_labels.Add(metamask_label, 1, wx.LEFT | wx.EXPAND, 5)
			rec1_labels.Add(afcRange_label, 1, wx.LEFT | wx.EXPAND, 5)
			rec1_labels.Add(tcxoFreq_label, 1, wx.LEFT | wx.EXPAND, 5)

			receiver1 = wx.BoxSizer(wx.HORIZONTAL)
			receiver1.Add(receiver1_label, 0, wx.UP | wx.LEFT | wx.EXPAND, 10)
			receiver1.Add(self.rec1_freq1, 1, wx.ALL | wx.EXPAND, 5)
			receiver1.Add(self.rec1_freq2, 1, wx.ALL | wx.EXPAND, 5)
			receiver1.Add(self.rec1_metamask, 1, wx.ALL | wx.EXPAND, 5)
			receiver1.Add(self.rec1_afcRange, 1, wx.ALL | wx.EXPAND, 5)
			receiver1.Add(self.rec1_tcxoFreq, 1, wx.ALL | wx.EXPAND, 5)

			receiver2 = wx.BoxSizer(wx.HORIZONTAL)
			receiver2.Add(receiver2_label, 0, wx.UP | wx.LEFT | wx.EXPAND, 10)
			receiver2.Add(self.rec2_freq1, 1, wx.ALL | wx.EXPAND, 5)
			receiver2.Add(self.rec2_freq2, 1, wx.ALL | wx.EXPAND, 5)
			receiver2.Add(self.rec2_metamask, 1, wx.ALL | wx.EXPAND, 5)
			receiver2.Add(self.rec2_afcRange, 1, wx.ALL | wx.EXPAND, 5)
			receiver2.Add(self.rec2_tcxoFreq, 1, wx.ALL | wx.EXPAND, 5)

			v_boxSizer8 = wx.StaticBoxSizer(ais_box, wx.VERTICAL)
			v_boxSizer8.Add(h_boxSizer6, 0, wx.ALL | wx.EXPAND, 0)
			v_boxSizer8.Add(h_boxSizer7, 0, wx.ALL | wx.EXPAND, 0)
			v_boxSizer8.AddSpacer(15)
			v_boxSizer8.Add(rec1_labels, 0, wx.ALL | wx.EXPAND, 0)
			v_boxSizer8.Add(receiver1, 0, wx.ALL | wx.EXPAND, 0)
			v_boxSizer8.Add(receiver2, 0, wx.ALL | wx.EXPAND, 0)

			buttons2 = wx.BoxSizer(wx.HORIZONTAL)
			buttons2.Add((0,0), 1, wx.ALL | wx.EXPAND, 0)
			buttons2.Add(self.button_apply, 0, wx.RIGHT | wx.EXPAND, 10)
			buttons2.Add(button_ok2, 0, wx.ALL | wx.EXPAND, 0)

			vbox4 = wx.BoxSizer(wx.VERTICAL)
			vbox4.Add(h_boxSizer5, 0, wx.ALL | wx.EXPAND, 5)
			vbox4.Add(v_boxSizer8, 0, wx.ALL | wx.EXPAND, 5)
			vbox4.Add(self.logger2, 1, wx.ALL | wx.EXPAND, 5)
			vbox4.Add(buttons2, 0, wx.ALL | wx.EXPAND, 5)

			self.p_settings.SetSizer(vbox4)

##################################################################### settings

			kernel_box = wx.StaticBox(self.p_update, -1, _(' Current Kernel version '))

			self.kernel_label = wx.StaticText(self.p_update, -1)

			packages_box = wx.StaticBox(self.p_update, -1, _(' Available packages '))

			self.packages_list = os.listdir(self.op_folder+'/tools/moitessier_hat/packages')
			self.packages_select = wx.Choice(self.p_update, choices=self.packages_list, style=wx.CB_READONLY)
			self.packages_select.SetSelection(0)

			self.button_install =wx.Button(self.p_update, label=_('Install'))
			self.Bind(wx.EVT_BUTTON, self.on_install, self.button_install)

			self.logger3 = wx.TextCtrl(self.p_update, style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_DONTWRAP|wx.LC_SORT_ASCENDING)

			button_ok3 =wx.Button(self.p_update, label=_('Close'))
			self.Bind(wx.EVT_BUTTON, self.on_ok, button_ok3)

			v_kernel_box = wx.StaticBoxSizer(kernel_box, wx.VERTICAL)
			v_kernel_box.AddSpacer(5)
			v_kernel_box.Add(self.kernel_label, 0, wx.ALL | wx.EXPAND, 5)

			h_packages_box = wx.StaticBoxSizer(packages_box, wx.HORIZONTAL)
			h_packages_box.Add(self.packages_select, 1, wx.ALL | wx.EXPAND, 5)
			h_packages_box.Add(self.button_install, 0, wx.ALL | wx.EXPAND, 5)

			buttons3 = wx.BoxSizer(wx.HORIZONTAL)
			buttons3.Add((0,0), 1, wx.ALL | wx.EXPAND, 0)
			buttons3.Add(button_ok3, 0, wx.ALL | wx.EXPAND, 0)

			update_final = wx.BoxSizer(wx.VERTICAL)
			update_final.Add(v_kernel_box, 0, wx.ALL | wx.EXPAND, 5)
			update_final.Add(h_packages_box, 0, wx.ALL | wx.EXPAND, 5)
			update_final.Add(self.logger3, 1, wx.ALL | wx.EXPAND, 5)
			update_final.Add(buttons3, 0, wx.ALL | wx.EXPAND, 5)

			self.p_update.SetSizer(update_final)

#####################################################################

			self.Centre()

			self.read()


		def read(self):
			self.current_kernel = subprocess.check_output(['uname','-r','-v'])
			self.kernel_label.SetLabel(self.current_kernel)
			try:
				out = subprocess.check_output(['more','product'],cwd='/proc/device-tree/hat')
			except:
				self.logger.SetValue(_('Moitessier HAT is not attached!'))
				self.disable_all_buttons()
				return
			else:
				if not 'Moitessier' in out: 
					self.logger.SetValue(_('Moitessier HAT is not attached!'))
					self.disable_all_buttons()
					return
				else: self.logger.SetValue(_('Moitessier HAT is attached.\n'))

			if not os.path.isfile(self.home+'/moitessier/app/moitessier_ctrl/moitessier_ctrl'):
				self.logger.AppendText(_('Moitessier HAT package is not installed!'))
				self.disable_info_settings_buttons()
				return
			else:
				self.logger.AppendText(_('Moitessier HAT package is installed.\n'))
				self.logger2.SetValue(_('All changes will be temporal.\nDefault settings will be loaded after rebooting.\n'))
				self.logger3.SetValue(_('Select the package that matches the current Kernel version.\nBefore installing, be sure the HAT is not being used by any service (kplex, GPSD, OpenCPN ...).\nIf installation fails, you may have to try to install the package several times.'))

			try:
				tree = ET.parse(self.home+'/moitessier/app/moitessier_ctrl/config.xml')
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
						self.rec1_metamask.SetValue(int(subitem.text))
					for subitem in item.iter("afcRange"):
						self.rec1_afcRange.SetValue(int(subitem.text))
					for subitem in item.iter("tcxoFreq"):
						self.rec1_tcxoFreq.SetValue(int(subitem.text))
				for item in root.iterfind('receiver[@name="receiver2"]'):
					for subitem in item.iter("channelFreq"):
						self.rec2_freq1.SetValue(int(subitem[0].text)) 
						self.rec2_freq2.SetValue(int(subitem[1].text))
					for subitem in item.iter("metamask"):
						self.rec2_metamask.SetValue(int(subitem.text))
					for subitem in item.iter("afcRange"):
						self.rec2_afcRange.SetValue(int(subitem.text))
					for subitem in item.iter("tcxoFreq"):
						self.rec2_tcxoFreq.SetValue(int(subitem.text))
			except: 
				self.logger2.AppendText(_('Failure reading config.xml file!'))
				self.disable_all_buttons()

		def on_install(self,e):
			if self.packages_select.GetStringSelection() == '':
				self.logger3.SetValue(_('Select a package to install.'))
			else:
				subprocess.Popen(['lxterminal', '-e', 'bash', self.op_folder+'/tools/moitessier_hat/install.sh', self.op_folder+'/tools/moitessier_hat/packages/'+self.packages_select.GetStringSelection()])
				self.logger3.SetValue(_('Updating Moitessier Hat modules and firmware...'))

		def disable_all_buttons(self):
			self.disable_info_settings_buttons()
			self.packages_select.Disable()
			self.button_install.Disable()

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
			self.rec1_tcxoFreq.Disable()
			self.rec2_freq1.Disable()
			self.rec2_freq2.Disable()
			self.rec2_metamask.Disable()
			self.rec2_afcRange.Disable()
			self.rec2_tcxoFreq.Disable()
			self.button_apply.Disable()

		def on_defaults(self,e):
			subprocess.call([self.home+'/moitessier/app/moitessier_ctrl/moitessier_ctrl','/dev/moitessier.ctrl','4','1'])
			self.simulator.SetValue(False)
			self.interval.SetValue(1000)
			self.mmsi1.SetValue(222222222) 
			self.mmsi2.SetValue(333333333)
			self.rec1_freq1.SetValue(161975000) 
			self.rec1_freq2.SetValue(162025000)
			self.rec1_metamask.SetValue(0)
			self.rec1_afcRange.SetValue(1000)
			self.rec1_tcxoFreq.SetValue(13000000)
			self.rec2_freq1.SetValue(161975000) 
			self.rec2_freq2.SetValue(162025000)
			self.rec2_metamask.SetValue(0)
			self.rec2_afcRange.SetValue(1000)
			self.rec2_tcxoFreq.SetValue(13000000)
			self.on_apply()
			self.logger2.AppendText(_('Defaults loaded.\n'))

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
						subitem.text = str(self.rec1_metamask.GetValue())
					for subitem in item.iter("afcRange"):
						subitem.text = str(self.rec1_afcRange.GetValue())
					for subitem in item.iter("tcxoFreq"):
						subitem.text = str(self.rec1_tcxoFreq.GetValue())
				for item in root.iterfind('receiver[@name="receiver2"]'):
					for subitem in item.iter("channelFreq"):
						subitem[0].text = str(self.rec2_freq1.GetValue())
						subitem[1].text = str(self.rec2_freq2.GetValue())
					for subitem in item.iter("metamask"):
						subitem.text = str(self.rec2_metamask.GetValue())
					for subitem in item.iter("afcRange"):
						subitem.text = str(self.rec2_afcRange.GetValue())
					for subitem in item.iter("tcxoFreq"):
						subitem.text = str(self.rec2_tcxoFreq.GetValue())
				tree.write(self.home+'/moitessier/app/moitessier_ctrl/config.xml',encoding='utf-8', xml_declaration=True)
				subprocess.call([self.home+'/moitessier/app/moitessier_ctrl/moitessier_ctrl','/dev/moitessier.ctrl','5',self.home+'/moitessier/app/moitessier_ctrl/config.xml'])
				self.logger2.SetValue(_('Changes applied.\n'))
			except: self.logger2.SetValue(_('Apply changes failed!\n'))

		def on_get_info(self, e):
			output = subprocess.check_output([self.home+'/moitessier/app/moitessier_ctrl/moitessier_ctrl','/dev/moitessier.ctrl','1'])
			self.logger.SetValue(output)

		def on_statistics(self, e):
			output = subprocess.check_output([self.home+'/moitessier/app/moitessier_ctrl/moitessier_ctrl','/dev/moitessier.ctrl','0'])
			self.logger.SetValue(output)

		def on_reset_statistics(self, e):
			output = subprocess.check_output([self.home+'/moitessier/app/moitessier_ctrl/moitessier_ctrl','/dev/moitessier.ctrl','3'])
			self.logger.SetValue(output)

		def on_enable_gnss(self, e):
			output = subprocess.check_output([self.home+'/moitessier/app/moitessier_ctrl/moitessier_ctrl','/dev/moitessier.ctrl','4','1'])
			self.logger2.SetValue(output)

		def on_disable_gnss(self, e):
			output = subprocess.check_output([self.home+'/moitessier/app/moitessier_ctrl/moitessier_ctrl','/dev/moitessier.ctrl','4','0'])
			self.logger2.SetValue(output)

		def on_MPU9250(self, e):
			output = subprocess.check_output([self.home+'/moitessier/app/sensors/MPU-9250', '/dev/i2c-1'])
			self.logger.SetValue(output)

		def on_MS560702BA03(self, e):
			output = subprocess.check_output([self.home+'/moitessier/app/sensors/MS5607-02BA03', '/dev/i2c-1'])
			self.logger.SetValue(output)

		def on_Si7020A20(self, e):
			output = subprocess.check_output([self.home+'/moitessier/app/sensors/Si7020-A20', '/dev/i2c-1'])
			self.logger.SetValue(output)
			
		def on_reset(self, e):
			output = subprocess.check_output([self.home+'/moitessier/app/moitessier_ctrl/moitessier_ctrl','/dev/moitessier.ctrl','2'])
			self.logger2.SetValue(output)

		def on_ok(self, e):
			self.Close()

app = wx.App()
MyFrame().Show()
app.MainLoop()
