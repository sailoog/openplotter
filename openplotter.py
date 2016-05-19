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

import wx, sys, os, subprocess, webbrowser, re, json, pyudev, time, ConfigParser
import wx.lib.scrolledpanel as scrolled
from wx.lib.mixins.listctrl import CheckListCtrlMixin, ListCtrlAutoWidthMixin
from classes.datastream import DataStream
from classes.actions import Actions
from classes.paths import Paths
from classes.conf import Conf
from classes.language import Language
from classes.add_trigger import addTrigger
from classes.add_action import addAction
from classes.add_DS18B20 import addDS18B20
from classes.add_switch import addSwitch
from classes.add_output import addOutput
from classes.add_USBinst import addUSBinst
from classes.add_topic import addTopic

paths=Paths()
home=paths.home
currentpath=paths.currentpath

class CheckListCtrl(wx.ListCtrl, CheckListCtrlMixin, ListCtrlAutoWidthMixin):
	def __init__(self, parent, height):
		wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER, size=(565, height))
		CheckListCtrlMixin.__init__(self)
		ListCtrlAutoWidthMixin.__init__(self)

class MainFrame(wx.Frame):

	def __init__(self):
		wx.Frame.__init__(self, None, title="OpenPlotter", size=(700,450))
		self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
		self.conf=Conf()
		self.language=self.conf.get('GENERAL','lang')
		Language(self.language)
		self.p = scrolled.ScrolledPanel(self, -1, style = wx.TAB_TRAVERSAL|wx.SUNKEN_BORDER)
		self.p.SetAutoLayout(1)
		self.p.SetupScrolling()
		self.nb = wx.Notebook(self.p)
		self.page1 = wx.Panel(self.nb)
		self.page2 = wx.Panel(self.nb)
		self.page3 = wx.Panel(self.nb)
		self.page4 = wx.Panel(self.nb)
		self.page5 = wx.Panel(self.nb)
		self.page6 = wx.Panel(self.nb)
		self.page7 = wx.Panel(self.nb)
		self.page8 = wx.Panel(self.nb)
		self.page9 = wx.Panel(self.nb)
		self.page10 = wx.Panel(self.nb)
		self.page11 = wx.Panel(self.nb)
		self.page12 = wx.Panel(self.nb)
		self.page13 = wx.Panel(self.nb)
		self.page14 = wx.Panel(self.nb)
		self.page15 = wx.Panel(self.nb)
		self.page16 = wx.Panel(self.nb)
		self.nb.AddPage(self.page14, _('USB manager'))
		self.nb.AddPage(self.page5, _('NMEA 0183'))
		self.nb.AddPage(self.page7, _('Signal K'))
		self.nb.AddPage(self.page3, _('WiFi AP'))
		self.nb.AddPage(self.page10, _('Actions'))
		self.nb.AddPage(self.page8, _('Switches'))
		self.nb.AddPage(self.page13, _('Outputs'))
		self.nb.AddPage(self.page6, _('I2C sensors'))
		self.nb.AddPage(self.page11, _('1W sensors'))
		self.nb.AddPage(self.page12, _('SPI sensors'))
		self.nb.AddPage(self.page4, _('SDR-AIS'))
		self.nb.AddPage(self.page2, _('Calculate'))
		self.nb.AddPage(self.page9, _('Accounts'))
		self.nb.AddPage(self.page16, _('MQTT'))
		self.nb.AddPage(self.page15, _('SMS'))
		self.nb.AddPage(self.page1, _('Startup'))
		sizer = wx.BoxSizer()
		sizer.Add(self.nb, 1, wx.EXPAND)
		self.p.SetSizer(sizer)
		self.icon = wx.Icon(currentpath+'/openplotter.ico', wx.BITMAP_TYPE_ICO)
		self.SetIcon(self.icon)
		self.CreateStatusBar()
		self.Centre()

########################### menu

		self.menubar = wx.MenuBar()
		self.settings = wx.Menu()
		self.time_item1 = self.settings.Append(wx.ID_ANY, _('Set time zone'), _('Set time zone in the new window'))
		self.Bind(wx.EVT_MENU, self.time_zone, self.time_item1)
		self.time_item2 = self.settings.Append(wx.ID_ANY, _('Set time from NMEA'), _('Set system time from NMEA data'))
		self.Bind(wx.EVT_MENU, self.time_gps, self.time_item2)
		self.settings.AppendSeparator()
		self.gpsd_item1 = self.settings.Append(wx.ID_ANY, _('Set GPSD'), _('Set GPSD in the new window'))
		self.Bind(wx.EVT_MENU, self.reconfigure_gpsd, self.gpsd_item1)
		self.menubar.Append(self.settings, _('Settings'))

		self.lang = wx.Menu()
		self.lang_item1 = self.lang.Append(wx.ID_ANY, _('English'), _('Set English language'), kind=wx.ITEM_CHECK)
		self.Bind(wx.EVT_MENU, self.lang_en, self.lang_item1)
		self.lang_item2 = self.lang.Append(wx.ID_ANY, _('Catalan'), _('Set Catalan language'), kind=wx.ITEM_CHECK)
		self.Bind(wx.EVT_MENU, self.lang_ca, self.lang_item2)
		self.lang_item3 = self.lang.Append(wx.ID_ANY, _('Spanish'), _('Set Spanish language'), kind=wx.ITEM_CHECK)
		self.Bind(wx.EVT_MENU, self.lang_es, self.lang_item3)
		self.lang_item4 = self.lang.Append(wx.ID_ANY, _('French'), _('Set French language'), kind=wx.ITEM_CHECK)
		self.Bind(wx.EVT_MENU, self.lang_fr, self.lang_item4)
		self.lang_item5 = self.lang.Append(wx.ID_ANY, _('Dutch'), _('Set Dutch language'), kind=wx.ITEM_CHECK)
		self.Bind(wx.EVT_MENU, self.lang_nl, self.lang_item5)
		self.lang_item6 = self.lang.Append(wx.ID_ANY, _('German'), _('Set German language'), kind=wx.ITEM_CHECK)
		self.Bind(wx.EVT_MENU, self.lang_de, self.lang_item6)		
		self.menubar.Append(self.lang, _('Language'))

		self.helpm = wx.Menu()
		self.helpm_item1=self.helpm.Append(wx.ID_ANY, _('&About'), _('About OpenPlotter'))
		self.Bind(wx.EVT_MENU, self.OnAboutBox, self.helpm_item1)
		self.helpm_item2=self.helpm.Append(wx.ID_ANY, _('OpenPlotter online documentation'), _('OpenPlotter online documentation'))
		self.Bind(wx.EVT_MENU, self.op_doc, self.helpm_item2)
		self.menubar.Append(self.helpm, _('&Help'))

		self.SetMenuBar(self.menubar)
###########################menu
########page1###################
		wx.StaticBox(self.page1, size=(330, 50), pos=(10, 10))
		wx.StaticText(self.page1, label=_('Delay (seconds)'), pos=(20, 30))
		self.delay = wx.TextCtrl(self.page1, -1, size=(55, 32), pos=(170, 23))
		self.button_ok_delay =wx.Button(self.page1, label=_('Ok'),size=(70, 32), pos=(250, 23))
		self.Bind(wx.EVT_BUTTON, self.ok_delay, self.button_ok_delay)

		wx.StaticBox(self.page1, size=(330, 230), pos=(10, 65))
		self.startup_opencpn = wx.CheckBox(self.page1, label=_('OpenCPN'), pos=(20, 80))
		self.startup_opencpn.Bind(wx.EVT_CHECKBOX, self.startup)
		self.startup_opencpn_nopengl = wx.CheckBox(self.page1, label=_('no OpenGL'), pos=(40, 105))
		self.startup_opencpn_nopengl.Bind(wx.EVT_CHECKBOX, self.startup)
		self.startup_opencpn_fullscreen = wx.CheckBox(self.page1, label=_('fullscreen'), pos=(40, 130))
		self.startup_opencpn_fullscreen.Bind(wx.EVT_CHECKBOX, self.startup)

		self.startup_multiplexer = wx.CheckBox(self.page1, label=_('NMEA 0183 multiplexer'), pos=(20, 165))
		self.startup_multiplexer.Bind(wx.EVT_CHECKBOX, self.startup)
		self.startup_nmea_time = wx.CheckBox(self.page1, label=_('Set time from NMEA'), pos=(40, 190))
		self.startup_nmea_time.Bind(wx.EVT_CHECKBOX, self.startup)

		self.startup_remote_desktop = wx.CheckBox(self.page1, label=_('VNC remote desktop'), pos=(20, 225))
		self.startup_remote_desktop.Bind(wx.EVT_CHECKBOX, self.startup)
		self.startup_vnc_pass = wx.CheckBox(self.page1, label=_('use password'), pos=(40, 250))
		self.startup_vnc_pass.Bind(wx.EVT_CHECKBOX, self.startup)

		wx.StaticBox(self.page1, size=(330, 230), pos=(350, 65))

		self.startup_play_sound = wx.CheckBox(self.page1, label=_('Play sound'), pos=(360, 80))
		self.startup_play_sound.Bind(wx.EVT_CHECKBOX, self.startup)
		self.startup_path_sound = wx.TextCtrl(self.page1, -1, size=(200, 32), pos=(360, 110))
		self.button_select_sound =wx.Button(self.page1, label=_('Select'), pos=(570, 110))
		self.Bind(wx.EVT_BUTTON, self.select_sound, self.button_select_sound)

		self.op_maximize = wx.CheckBox(self.page1, label=_('Maximize OpenPlotter'), pos=(360, 150))
		self.op_maximize.Bind(wx.EVT_CHECKBOX, self.startup)
###########################page1
########page2###################
		wx.StaticBox(self.page2, size=(330, 50), pos=(10, 10))
		wx.StaticText(self.page2, label=_('Rate (sec)'), pos=(20, 30))
		self.rate_list = ['0.1', '0.25', '0.5', '0.75', '1', '1.5', '2']
		self.rate2= wx.ComboBox(self.page2, choices=self.rate_list, style=wx.CB_READONLY, size=(80, 32), pos=(150, 23))
		self.button_ok_rate2 =wx.Button(self.page2, label=_('Ok'),size=(70, 32), pos=(250, 23))
		self.Bind(wx.EVT_BUTTON, self.ok_rate2, self.button_ok_rate2)

		wx.StaticBox(self.page2, size=(330, 50), pos=(350, 10))
		wx.StaticText(self.page2, label=_('Accuracy (sec)'), pos=(360, 30))
		self.accuracy= wx.ComboBox(self.page2, choices=self.rate_list, style=wx.CB_READONLY, size=(80, 32), pos=(500, 23))
		self.button_ok_accuracy =wx.Button(self.page2, label=_('Ok'),size=(70, 32), pos=(600, 23))
		self.Bind(wx.EVT_BUTTON, self.ok_accuracy, self.button_ok_accuracy)

		wx.StaticBox(self.page2, size=(330, 65), pos=(10, 65))
		self.mag_var = wx.CheckBox(self.page2, label=_('Magnetic variation'), pos=(20, 80))
		self.mag_var.Bind(wx.EVT_CHECKBOX, self.nmea_mag_var)
		wx.StaticText(self.page2, label=_('Generated NMEA: $OCHDG'), pos=(20, 105))

		wx.StaticBox(self.page2, size=(330, 65), pos=(10, 130))
		self.heading_t = wx.CheckBox(self.page2, label=_('True heading'), pos=(20, 145))
		self.heading_t.Bind(wx.EVT_CHECKBOX, self.nmea_hdt)
		wx.StaticText(self.page2, label=_('Generated NMEA: $OCHDT'), pos=(20, 170))

		wx.StaticBox(self.page2, size=(330, 65), pos=(10, 195))
		self.rot = wx.CheckBox(self.page2, label=_('Rate of turn'), pos=(20, 210))
		self.rot.Bind(wx.EVT_CHECKBOX, self.nmea_rot)
		wx.StaticText(self.page2, label=_('Generated NMEA: $OCROT'), pos=(20, 235))

		wx.StaticBox(self.page2, label=_(' True wind '), size=(330, 90), pos=(350, 65))
		self.TW_STW = wx.CheckBox(self.page2, label=_('Use speed log'), pos=(360, 80))
		self.TW_STW.Bind(wx.EVT_CHECKBOX, self.TW)
		self.TW_SOG = wx.CheckBox(self.page2, label=_('Use GPS'), pos=(360, 105))
		self.TW_SOG.Bind(wx.EVT_CHECKBOX, self.TW)
		wx.StaticText(self.page2, label=_('Generated NMEA: $OCMWV, $OCMWD'), pos=(360, 130))

		self.show_output7 =wx.Button(self.page2, label=_('Inspector'), pos=(10, 285))
		self.Bind(wx.EVT_BUTTON, self.show_output_window, self.show_output7)
###########################page2
########page3###################
		wx.StaticBox(self.page3, size=(370, 315), pos=(10, 10))
		self.wifi_enable = wx.CheckBox(self.page3, label=_('Enable access point'), pos=(20, 25))
		self.wifi_enable.Bind(wx.EVT_CHECKBOX, self.onwifi_enable)
		
		self.available_wireless = []
		output=subprocess.check_output('ifconfig', stderr=subprocess.STDOUT)
		for i in range (0, 9):
			ii=str(i)
			if 'wlan'+ii in output: self.available_wireless.append('wlan'+ii)

		self.available_share = [_('none')]
		for i in range (0, 9):
			ii=str(i)
			if 'eth'+ii in output: self.available_share.append('eth'+ii)
			if 'ppp'+ii in output: self.available_share.append('ppp'+ii)
			if 'usb'+ii in output: self.available_share.append('usb'+ii)
		for i in self.available_wireless:
			self.available_share.append(i)
		share_old= self.conf.get('WIFI', 'share')
		if share_old!='0' and share_old not in self.available_share: self.available_share.append(share_old)
		self.wlan_label=wx.StaticText(self.page3, label=_('Access point device'), pos=(20, 55))
		self.wlan = wx.ComboBox(self.page3, choices=self.available_wireless, style=wx.CB_READONLY, size=(100, 32), pos=(20, 75))
		
		self.share_label=wx.StaticText(self.page3, label=_('Sharing Internet device'), pos=(180, 55))
		self.share = wx.ComboBox(self.page3, choices=self.available_share, style=wx.CB_READONLY, size=(100, 32), pos=(180, 75))

		self.wifi_settings_label=wx.StaticText(self.page3, label=_('Access point settings'), pos=(20, 120))

		self.ssid = wx.TextCtrl(self.page3, -1, size=(120, 32), pos=(20, 140))
		self.ssid_label=wx.StaticText(self.page3, label=_('SSID \nmaximum 32 characters'), pos=(160, 140))

		self.passw = wx.TextCtrl(self.page3, -1, size=(120, 32), pos=(20, 173))
		self.passw_label=wx.StaticText(self.page3, label=_('Password \nminimum 8 characters required'), pos=(160, 175))
		
		self.wifi_channel_list=['1','2','3','4','5','6','7','8','9','10','11']
		self.wifi_channel = wx.ComboBox(self.page3, choices=self.wifi_channel_list, style=wx.CB_READONLY, size=(120, 32), pos=(20, 208))
		self.wifi_channel_label=wx.StaticText(self.page3, label=_('Channel'), pos=(160, 215))

		self.wifi_mode_list=['IEEE 802.11b', 'IEEE 802.11g']
		self.wifi_mode = wx.ComboBox(self.page3, choices=self.wifi_mode_list, style=wx.CB_READONLY, size=(120, 32), pos=(20, 246))
		self.wifi_mode_label=wx.StaticText(self.page3, label=_('Mode'), pos=(160, 255))

		self.wifi_wpa_list=['WPA','WPA2', _('Both')]
		self.wifi_wpa = wx.ComboBox(self.page3, choices=self.wifi_wpa_list, style=wx.CB_READONLY, size=(120, 32), pos=(20, 285))
		self.wifi_wpa_label=wx.StaticText(self.page3, label=_('WPA'), pos=(160, 290))

		self.wifi_button_default =wx.Button(self.page3, label=_('Defaults'), pos=(275, 280))
		self.Bind(wx.EVT_BUTTON, self.wifi_default, self.wifi_button_default)

		wx.StaticBox(self.page3, label=_(' Addresses '), size=(290, 315), pos=(385, 10))
		self.ip_info = wx.TextCtrl(self.page3, -1, style=wx.TE_MULTILINE|wx.TE_READONLY, size=(270, 245), pos=(395, 30))
		self.ip_info.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_INACTIVECAPTION))

		self.button_refresh_ip =wx.Button(self.page3, label=_('Refresh'), pos=(565, 280))
		self.Bind(wx.EVT_BUTTON, self.show_ip_info, self.button_refresh_ip)
###########################page3
########page4###################
		wx.StaticBox(self.page4, label='', size=(400, 170), pos=(10, 10))

		self.ais_sdr_enable = wx.CheckBox(self.page4, label=_('Enable AIS NMEA generation'), pos=(20, 25))
		self.ais_sdr_enable.Bind(wx.EVT_CHECKBOX, self.OnOffAIS)

		self.gain = wx.TextCtrl(self.page4, -1, size=(55, 32), pos=(150, 60))
		self.gain_label=wx.StaticText(self.page4, label=_('Gain'), pos=(20, 65))
		self.ppm = wx.TextCtrl(self.page4, -1, size=(55, 32), pos=(150, 95))
		self.correction_label=wx.StaticText(self.page4, label=_('Correction (ppm)'), pos=(20, 100))

		self.ais_frequencies1 = wx.CheckBox(self.page4, label=_('Channel A 161.975Mhz'), pos=(220, 60))
		self.ais_frequencies1.Bind(wx.EVT_CHECKBOX, self.ais_frequencies)
		self.ais_frequencies2 = wx.CheckBox(self.page4, label=_('Channel B 162.025Mhz'), pos=(220, 95))
		self.ais_frequencies2.Bind(wx.EVT_CHECKBOX, self.ais_frequencies)

		self.show_output6 =wx.Button(self.page4, label=_('Inspector'), pos=(20, 140))
		self.Bind(wx.EVT_BUTTON, self.show_output_window, self.show_output6)
		self.button_test_ppm =wx.Button(self.page4, label=_('Take a look'), pos=(150, 140))
		self.Bind(wx.EVT_BUTTON, self.test_ppm, self.button_test_ppm)
		self.button_test_gain =wx.Button(self.page4, label=_('Calibration'), pos=(275, 140))
		self.Bind(wx.EVT_BUTTON, self.test_gain, self.button_test_gain)

		wx.StaticBox(self.page4, label=_(' Fine calibration using GSM '), size=(260, 170), pos=(420, 10))
		self.bands_label=wx.StaticText(self.page4, label=_('Band'), pos=(430, 50))
		self.bands_list = ['GSM850', 'GSM-R', 'GSM900', 'EGSM', 'DCS', 'PCS']
		self.band= wx.ComboBox(self.page4, choices=self.bands_list, style=wx.CB_READONLY, size=(100, 32), pos=(430, 70))
		self.band.SetValue('GSM900')
		self.check_bands =wx.Button(self.page4, label=_('Check band'), pos=(540, 70))
		self.Bind(wx.EVT_BUTTON, self.check_band, self.check_bands)
		self.channel_label=wx.StaticText(self.page4, label=_('Channel'), pos=(430, 125))
		self.channel = wx.TextCtrl(self.page4, -1, size=(55, 32), pos=(430, 143))
		self.check_channels =wx.Button(self.page4, label=_('Fine calibration'), pos=(495, 140))
		self.Bind(wx.EVT_BUTTON, self.check_channel, self.check_channels)

		wx.StaticBox(self.page4, label=_(' VHF '), size=(260, 130), pos=(420, 185))

		self.button_vhf_Rx =wx.Button(self.page4, label=_('Receive'), pos=(430, 210))
		self.Bind(wx.EVT_BUTTON, self.vhf_Rx, self.button_vhf_Rx)

		self.button_vhf_Tx =wx.Button(self.page4, label=_('Transmit'), pos=(430, 255))
		self.Bind(wx.EVT_BUTTON, self.vhf_Tx, self.button_vhf_Tx)
		self.Tx_exp_label=wx.StaticText(self.page4, label=_('Experimental'), pos=(540, 263))

###########################page4
########page5###################
		wx.StaticBox(self.page5, label=_(' Inputs '), size=(670, 130), pos=(10, 10))
		self.list_input = CheckListCtrl(self.page5, 102)
		self.list_input.SetPosition((15, 30))
		self.list_input.InsertColumn(0, _('Name'), width=130)
		self.list_input.InsertColumn(1, _('Type'), width=45)
		self.list_input.InsertColumn(2, _('Port/Address'), width=110)
		self.list_input.InsertColumn(3, _('Bauds/Port'))
		self.list_input.InsertColumn(4, _('Filter'))
		self.list_input.InsertColumn(5, _('Filtering'))
		self.add_serial_in =wx.Button(self.page5, label=_('+ serial'), pos=(585, 30))
		self.Bind(wx.EVT_BUTTON, self.add_serial_input, self.add_serial_in)

		self.add_network_in =wx.Button(self.page5, label=_('+ network'), pos=(585, 65))
		self.Bind(wx.EVT_BUTTON, self.add_network_input, self.add_network_in)

		self.button_delete_input =wx.Button(self.page5, label=_('delete'), pos=(585, 100))
		self.Bind(wx.EVT_BUTTON, self.delete_input, self.button_delete_input)

		wx.StaticBox(self.page5, label=_(' Outputs '), size=(670, 130), pos=(10, 145))
		self.list_output = CheckListCtrl(self.page5, 102)
		self.list_output.SetPosition((15, 165))
		self.list_output.InsertColumn(0, _('Name'), width=130)
		self.list_output.InsertColumn(1, _('Type'), width=45)
		self.list_output.InsertColumn(2, _('Port/Address'), width=110)
		self.list_output.InsertColumn(3, _('Bauds/Port'))
		self.list_output.InsertColumn(4, _('Filter'))
		self.list_output.InsertColumn(5, _('Filtering'))
		self.add_serial_out =wx.Button(self.page5, label=_('+ serial'), pos=(585, 165))
		self.Bind(wx.EVT_BUTTON, self.add_serial_output, self.add_serial_out)

		self.add_network_out =wx.Button(self.page5, label=_('+ network'), pos=(585, 200))
		self.Bind(wx.EVT_BUTTON, self.add_network_output, self.add_network_out)

		self.button_delete_output =wx.Button(self.page5, label=_('delete'), pos=(585, 235))
		self.Bind(wx.EVT_BUTTON, self.delete_output, self.button_delete_output)

		self.show_output =wx.Button(self.page5, label=_('Inspector'), pos=(10, 285))
		self.Bind(wx.EVT_BUTTON, self.show_output_window, self.show_output)
		self.restart =wx.Button(self.page5, label=_('Restart'), pos=(130, 285))
		self.Bind(wx.EVT_BUTTON, self.restart_multiplex, self.restart)
		self.advanced =wx.Button(self.page5, label=_('Advanced'), pos=(280, 285))
		self.Bind(wx.EVT_BUTTON, self.advanced_multiplex, self.advanced)
		self.button_apply =wx.Button(self.page5, label=_('Apply changes'), pos=(570, 285))
		self.Bind(wx.EVT_BUTTON, self.apply_changes, self.button_apply)
		self.button_cancel =wx.Button(self.page5, label=_('Cancel changes'), pos=(430, 285))
		self.Bind(wx.EVT_BUTTON, self.cancel_changes, self.button_cancel)
###########################page5
########page7###################
		wx.StaticBox(self.page7, label=_(' Settings '), size=(230, 265), pos=(10, 10))
		self.signalk_enable = wx.CheckBox(self.page7, label=_('Enable Signal K server'), pos=(20, 30))
		self.signalk_enable.Bind(wx.EVT_CHECKBOX, self.onsignalk_enable)

		self.vessel = wx.TextCtrl(self.page7, -1, size=(110, 32), pos=(20, 60))
		self.vessel_label=wx.StaticText(self.page7, label=_('Vessel name'), pos=(140, 65))

		self.mmsi = wx.TextCtrl(self.page7, -1, size=(110, 32), pos=(20, 95))
		self.mmsi_label=wx.StaticText(self.page7, label='MMSI', pos=(140, 100))
		
		self.NMEA2000_label=wx.StaticText(self.page7, label='NMEA 2000', pos=(20, 140))
		self.SerDevLs = []
		self.can_usb= wx.ComboBox(self.page7, choices=self.SerDevLs, style=wx.CB_READONLY, size=(120, 32), pos=(20, 165))
		self.CANUSB_label=wx.StaticText(self.page7, label='CAN-USB', pos=(155, 172))

		wx.StaticBox(self.page7, label=_(' Inputs '), size=(430, 130), pos=(250, 10))
		self.SKinputs_label=wx.StaticText(self.page7, label='NMEA 0183 - system_output - TCP localhost 10110', pos=(260, 30))

		wx.StaticBox(self.page7, label=_(' Outputs '), size=(430, 130), pos=(250, 145))
		wx.StaticText(self.page7, label='Signal K REST\nSignal K Web Socket\nSignal K NMEA 0183 - TCP localhost 10111', pos=(260, 165))

		self.show_outputSK =wx.Button(self.page7, label=_('Show Web Socket'), pos=(10, 285))
		self.Bind(wx.EVT_BUTTON, self.signalKout, self.show_outputSK)
		self.button_restartSK =wx.Button(self.page7, label=_('Restart'), pos=(155, 285))
		self.Bind(wx.EVT_BUTTON, self.restartSK, self.button_restartSK)
		self.button_N2K_setting =wx.Button(self.page7, label=_('N2K Settings'), pos=(250, 285))
		self.Bind(wx.EVT_BUTTON, self.N2K_setting, self.button_N2K_setting)		
###########################page7
########page15###################
		wx.StaticBox(self.page15, label=_(' Settings '), size=(330, 180), pos=(10, 10))
		self.sms_enable = wx.CheckBox(self.page15, label=_('Enable settings'), pos=(20, 30))
		self.sms_enable.Bind(wx.EVT_CHECKBOX, self.onsms_enable)

		self.sms_dev_label=wx.StaticText(self.page15, label='Serial port', pos=(20, 60))
		self.sms_dev= wx.ComboBox(self.page15, choices=self.SerDevLs, style=wx.CB_READONLY, size=(150, 32), pos=(20, 80))
		sms_con_list=['at','at19200','at115200','blueat','bluephonet','bluefbus','blueobex','bluerfgnapbus','bluerfat','blues60','dlr3','dku2','dku2at','dku2phonet','dku5','dku5fbus','fbus','fbusdlr3','fbusdku5','fbusblue','fbuspl2303','irdaphonet','irdaat','irdaobex','irdagnapbus','phonetblue','proxyphonet','proxyfbus','proxyat','proxyobex','proxygnapbus','proxys60','mbus']
		
		self.sms_bt_label=wx.StaticText(self.page15, label=_('Bluetooth address'), pos=(180, 60))
		self.sms_bt = wx.TextCtrl(self.page15, -1, size=(150, 32), pos=(180, 80))

		self.sms_con_label=wx.StaticText(self.page15, label='Connection', pos=(20, 120))
		self.sms_con= wx.ComboBox(self.page15, choices=sms_con_list, style=wx.CB_READONLY, size=(150, 32), pos=(20, 140))
		
		self.button_sms_identify =wx.Button(self.page15, label=_('Identify'), pos=(180, 140))
		self.Bind(wx.EVT_BUTTON, self.sms_identify, self.button_sms_identify)

		wx.StaticBox(self.page15, label=_(' Sending '), size=(330, 180), pos=(350, 10))

		self.sms_enable_send = wx.CheckBox(self.page15, label=_('Enable sending SMS'), pos=(360, 30))
		self.sms_enable_send.Bind(wx.EVT_CHECKBOX, self.onsms_enable_send)

		self.phone_number_label=wx.StaticText(self.page15, label=_('Send to phone'), pos=(360, 60))
		self.phone_number = wx.TextCtrl(self.page15, -1, size=(150, 32), pos=(360, 80))

		self.sms_text_label=wx.StaticText(self.page15, label=_('Text'), pos=(360, 120))
		self.sms_text = wx.TextCtrl(self.page15, -1, size=(150, 32), pos=(360, 140))

		self.button_sms_test =wx.Button(self.page15, label=_('Test'), pos=(520, 140))
		self.Bind(wx.EVT_BUTTON, self.sms_test, self.button_sms_test)
###########################page15
########page6###################
		wx.StaticBox(self.page6, size=(330, 50), pos=(10, 10))
		wx.StaticText(self.page6, label=_('Rate (sec)'), pos=(20, 30))
		self.rate= wx.ComboBox(self.page6, choices=self.rate_list, style=wx.CB_READONLY, size=(80, 32), pos=(150, 23))
		self.button_ok_rate =wx.Button(self.page6, label=_('Ok'),size=(70, 32), pos=(250, 23))
		self.Bind(wx.EVT_BUTTON, self.ok_rate, self.button_ok_rate)

		wx.StaticBox(self.page6, label=_(' IMU '), size=(330, 170), pos=(10, 65))
		self.imu_tag=wx.StaticText(self.page6, label=_('Sensor detected: ')+_('none'), pos=(20, 85))
		self.button_reset_imu =wx.Button(self.page6, label=_('Reset'), pos=(240, 85))
		self.Bind(wx.EVT_BUTTON, self.reset_imu, self.button_reset_imu)
		self.button_calibrate_imu =wx.Button(self.page6, label=_('Calibrate'), pos=(240, 125))
		self.Bind(wx.EVT_BUTTON, self.calibrate_imu, self.button_calibrate_imu)
		self.heading = wx.CheckBox(self.page6, label=_('Heading'), pos=(20, 105))
		self.heading.Bind(wx.EVT_CHECKBOX, self.nmea_hdg)
		self.heading_nmea=wx.StaticText(self.page6, label=_('Generated NMEA: $OSHDG'), pos=(20, 130))
		self.heel = wx.CheckBox(self.page6, label=_('Heel'), pos=(20, 155))
		self.heel.Bind(wx.EVT_CHECKBOX, self.nmea_heel)
		self.pitch = wx.CheckBox(self.page6, label=_('Pitch'), pos=(20, 180))
		self.pitch.Bind(wx.EVT_CHECKBOX, self.nmea_pitch)
		self.heel_nmea=wx.StaticText(self.page6, label=_('Generated NMEA: $OSXDR'), pos=(20, 205))

		wx.StaticBox(self.page6, label=_(' Weather '), size=(330, 270), pos=(350, 10))
		self.press_tag=wx.StaticText(self.page6, label=_('Sensor detected: ')+_('none'), pos=(360, 30))
		self.button_reset_press_hum =wx.Button(self.page6, label=_('Reset'), pos=(580, 30))
		self.Bind(wx.EVT_BUTTON, self.reset_press_hum, self.button_reset_press_hum)
		self.press = wx.CheckBox(self.page6, label=_('Pressure'), pos=(360, 50))
		self.press.Bind(wx.EVT_CHECKBOX, self.nmea_press)
		self.temp_p = wx.CheckBox(self.page6, label=_('Temperature'), pos=(360, 75))
		self.temp_p.Bind(wx.EVT_CHECKBOX, self.nmea_temp_p)
		self.hum_tag=wx.StaticText(self.page6, label=_('Sensor detected: ')+_('none'), pos=(360, 105))
		self.hum = wx.CheckBox(self.page6, label=_('Humidity'), pos=(360, 125))
		self.hum.Bind(wx.EVT_CHECKBOX, self.nmea_hum)
		self.temp_h = wx.CheckBox(self.page6, label=_('Temperature'), pos=(360, 150))
		self.temp_h.Bind(wx.EVT_CHECKBOX, self.nmea_temp_h)

		self.press_nmea=wx.StaticText(self.page6, label=_('Generated NMEA: $OSXDR'), pos=(360, 180))

		self.press_temp_log = wx.CheckBox(self.page6, label=_('Weather data logging'), pos=(360, 210))
		self.press_temp_log.Bind(wx.EVT_CHECKBOX, self.enable_press_temp_log)
		self.button_reset =wx.Button(self.page6, label=_('Reset'), pos=(360, 240))
		self.Bind(wx.EVT_BUTTON, self.reset_graph, self.button_reset)
		self.button_graph =wx.Button(self.page6, label=_('Show'), pos=(475, 240))
		self.Bind(wx.EVT_BUTTON, self.show_graph, self.button_graph)

		self.show_output4 =wx.Button(self.page6, label=_('Inspector'), pos=(10, 285))
		self.Bind(wx.EVT_BUTTON, self.show_output_window, self.show_output4)
###########################page6
########page11###################
		wx.StaticBox(self.page11, label=_(' DS18B20 sensors '), size=(670, 265), pos=(10, 10))
		
		self.list_DS18B20 = CheckListCtrl(self.page11, 237)
		self.list_DS18B20.SetPosition((15, 30))
		self.list_DS18B20.InsertColumn(0, _('Name'), width=275)
		self.list_DS18B20.InsertColumn(1, _('Short'), width=60)
		self.list_DS18B20.InsertColumn(2, _('Unit'), width=40)
		self.list_DS18B20.InsertColumn(3, _('ID'))
		self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.edit_DS18B20, self.list_DS18B20)
			
		self.add_DS18B20_button =wx.Button(self.page11, label=_('add'), pos=(585, 30))
		self.Bind(wx.EVT_BUTTON, self.add_DS18B20, self.add_DS18B20_button)

		self.delete_DS18B20_button =wx.Button(self.page11, label=_('delete'), pos=(585, 65))
		self.Bind(wx.EVT_BUTTON, self.delete_DS18B20, self.delete_DS18B20_button)

		self.show_output5 =wx.Button(self.page11, label=_('Inspector'), pos=(10, 285))
		self.Bind(wx.EVT_BUTTON, self.show_output_window, self.show_output5)

		self.button_apply_DS18B20 =wx.Button(self.page11, label=_('Apply changes'), pos=(570, 285))
		self.Bind(wx.EVT_BUTTON, self.apply_changes_DS18B20, self.button_apply_DS18B20)
		self.button_cancel_DS18B20 =wx.Button(self.page11, label=_('Cancel changes'), pos=(430, 285))
		self.Bind(wx.EVT_BUTTON, self.cancel_changes_DS18B20, self.button_cancel_DS18B20)
###########################page11
########page12###################
		wx.StaticText(self.page12, label=_('Coming soon'), pos=(20, 30))
###########################page12
########page14###################
		wx.StaticBox(self.page14, label=_(' USB Serial ports '), size=(670, 265), pos=(10, 10))
		
		self.list_USBinst = wx.ListCtrl(self.page14, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER, size=(565, 237))
		self.list_USBinst.SetPosition((15, 30))
		self.list_USBinst.InsertColumn(0, _('name'), width=130)
		self.list_USBinst.InsertColumn(1, _('vendor'), width=55)
		self.list_USBinst.InsertColumn(2, _('product'), width=60)
		self.list_USBinst.InsertColumn(3, _('port'), width=90)
		self.list_USBinst.InsertColumn(4, _('serial'), width=130)
		self.list_USBinst.InsertColumn(5, _('remember'), width=100)
			
		self.add_USBinst_button =wx.Button(self.page14, label=_('add'), pos=(585, 30))
		self.Bind(wx.EVT_BUTTON, self.add_USBinst, self.add_USBinst_button)

		self.delete_USBinst_button =wx.Button(self.page14, label=_('delete'), pos=(585, 65))
		self.Bind(wx.EVT_BUTTON, self.delete_USBinst, self.delete_USBinst_button)
###########################page14
########page8###################
		wx.StaticBox(self.page8, label=_(' Switches '), size=(670, 265), pos=(10, 10))
		
		self.list_switches = CheckListCtrl(self.page8, 237)
		self.list_switches.SetPosition((15, 30))
		self.list_switches.InsertColumn(0, _('Name'), width=300)
		self.list_switches.InsertColumn(1, _('Short'), width=80)
		self.list_switches.InsertColumn(2, 'GPIO')
		self.list_switches.InsertColumn(3, 'Pull')
		self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.edit_switches, self.list_switches)
			
		self.add_switches_button =wx.Button(self.page8, label=_('add'), pos=(585, 30))
		self.Bind(wx.EVT_BUTTON, self.add_switches, self.add_switches_button)

		self.delete_switches_button =wx.Button(self.page8, label=_('delete'), pos=(585, 65))
		self.Bind(wx.EVT_BUTTON, self.delete_switches, self.delete_switches_button)

		self.show_output2 =wx.Button(self.page8, label=_('Inspector'), pos=(10, 285))
		self.Bind(wx.EVT_BUTTON, self.show_output_window, self.show_output2)
		self.button_apply_switches =wx.Button(self.page8, label=_('Apply changes'), pos=(570, 285))
		self.Bind(wx.EVT_BUTTON, self.apply_changes_switches, self.button_apply_switches)
		self.button_cancel_switches =wx.Button(self.page8, label=_('Cancel changes'), pos=(430, 285))
		self.Bind(wx.EVT_BUTTON, self.cancel_changes_switches, self.button_cancel_switches)
###########################page8
########page13###################
		wx.StaticBox(self.page13, label=_(' Outputs '), size=(670, 265), pos=(10, 10))
		
		self.list_outputs = CheckListCtrl(self.page13, 237)
		self.list_outputs.SetPosition((15, 30))
		self.list_outputs.InsertColumn(0, _('Name'), width=320)
		self.list_outputs.InsertColumn(1, _('Short'), width=80)
		self.list_outputs.InsertColumn(2, 'GPIO')
		self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.edit_outputs, self.list_outputs)
			
		self.add_outputs_button =wx.Button(self.page13, label=_('add'), pos=(585, 30))
		self.Bind(wx.EVT_BUTTON, self.add_outputs, self.add_outputs_button)

		self.delete_outputs_button =wx.Button(self.page13, label=_('delete'), pos=(585, 65))
		self.Bind(wx.EVT_BUTTON, self.delete_outputs, self.delete_outputs_button)

		self.show_output3 =wx.Button(self.page13, label=_('Inspector'), pos=(10, 285))
		self.Bind(wx.EVT_BUTTON, self.show_output_window, self.show_output3)
		self.button_apply_outputs =wx.Button(self.page13, label=_('Apply changes'), pos=(570, 285))
		self.Bind(wx.EVT_BUTTON, self.apply_changes_outputs, self.button_apply_outputs)
		self.button_cancel_outputs =wx.Button(self.page13, label=_('Cancel changes'), pos=(430, 285))
		self.Bind(wx.EVT_BUTTON, self.cancel_changes_outputs, self.button_cancel_outputs)
###########################page13
########page9###################
		wx.StaticBox(self.page9, label=_(' Twitter '), size=(330, 205), pos=(10, 10))
		self.twitter_enable = wx.CheckBox(self.page9, label=_('Enable'), pos=(20, 32))
		self.twitter_enable.Bind(wx.EVT_CHECKBOX, self.on_twitter_enable)
		
		wx.StaticText(self.page9, label=_('apiKey'), pos=(20, 70))
		self.apiKey = wx.TextCtrl(self.page9, -1, size=(180, 32), pos=(150, 65))
		wx.StaticText(self.page9, label=_('apiSecret'), pos=(20, 105))
		self.apiSecret = wx.TextCtrl(self.page9, -1, size=(180, 32), pos=(150, 100))
		wx.StaticText(self.page9, label=_('accessToken'), pos=(20, 140))
		self.accessToken = wx.TextCtrl(self.page9, -1, size=(180, 32), pos=(150, 135))
		wx.StaticText(self.page9, label=_('accessTokenSecret'), pos=(20, 175))
		self.accessTokenSecret = wx.TextCtrl(self.page9, -1, size=(180, 32), pos=(150, 170))

		wx.StaticBox(self.page9, label=_(' Gmail '), size=(330, 205), pos=(350, 10))
		self.gmail_enable = wx.CheckBox(self.page9, label=_('Enable'), pos=(360, 32))
		self.gmail_enable.Bind(wx.EVT_CHECKBOX, self.on_gmail_enable)
		wx.StaticText(self.page9, label=_('Gmail account'), pos=(360, 70))
		self.Gmail_account = wx.TextCtrl(self.page9, -1, size=(180, 32), pos=(490, 65))
		wx.StaticText(self.page9, label=_('Gmail password'), pos=(360, 105))
		self.Gmail_password = wx.TextCtrl(self.page9, -1, size=(180, 32), pos=(490, 100))
		wx.StaticText(self.page9, label=_('Recipient'), pos=(360, 140))
		self.Recipient = wx.TextCtrl(self.page9, -1, size=(180, 32), pos=(490, 135))
###########################page9
########page16###################
		wx.StaticBox(self.page16, label=_(' MQTT '), size=(670, 265), pos=(10, 10))
		wx.StaticText(self.page16, label=_('Remote broker'), pos=(20, 30))
		self.mqtt_broker = wx.TextCtrl(self.page16, -1, size=(190, 32), pos=(20, 50))
		wx.StaticText(self.page16, label=_('Port'), pos=(220, 30))
		self.mqtt_port = wx.TextCtrl(self.page16, -1, size=(50, 32), pos=(220, 50))

		wx.StaticText(self.page16, label=_('Username'), pos=(280, 30))
		self.mqtt_user = wx.TextCtrl(self.page16, -1, size=(120, 32), pos=(280, 50))
		wx.StaticText(self.page16, label=_('Password'), pos=(410, 30))
		self.mqtt_pass = wx.TextCtrl(self.page16, -1, size=(120, 32), pos=(410, 50))

		wx.StaticText(self.page16, label=_('Topics'), pos=(20, 90))

		self.list_topics = wx.ListCtrl(self.page16, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER, size=(565, 155))
		self.list_topics.SetPosition((15, 110))
		self.list_topics.InsertColumn(0, _('Short'), width=80)
		self.list_topics.InsertColumn(1, _('Topic'), width=485)
		self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.edit_topic, self.list_topics)

		self.add_topic_button =wx.Button(self.page16, label=_('add'), pos=(585, 110))
		self.Bind(wx.EVT_BUTTON, self.add_topic, self.add_topic_button)

		self.delete_topic_button =wx.Button(self.page16, label=_('delete'), pos=(585, 145))
		self.Bind(wx.EVT_BUTTON, self.delete_topic, self.delete_topic_button)

		self.show_output8 =wx.Button(self.page16, label=_('Inspector'), pos=(10, 285))
		self.Bind(wx.EVT_BUTTON, self.show_output_window, self.show_output8)
		self.button_apply_mqtt =wx.Button(self.page16, label=_('Apply changes'), pos=(570, 285))
		self.Bind(wx.EVT_BUTTON, self.apply_changes_mqtt, self.button_apply_mqtt)
		self.button_cancel_mqtt =wx.Button(self.page16, label=_('Cancel changes'), pos=(430, 285))
		self.Bind(wx.EVT_BUTTON, self.cancel_changes_mqtt, self.button_cancel_mqtt)
###########################page16
########page10###################
		wx.StaticBox(self.page10, label=_(' Triggers '), size=(670, 265), pos=(10, 10))
		
		self.list_triggers = CheckListCtrl(self.page10, 125)
		self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.print_actions, self.list_triggers)
		self.list_triggers.SetPosition((15, 30))
		self.list_triggers.InsertColumn(0, _('trigger'), width=275)
		self.list_triggers.InsertColumn(1, _('operator'), width=170)
		self.list_triggers.InsertColumn(2, _('value'))
		self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.edit_triggers, self.list_triggers)

		self.add_trigger_button =wx.Button(self.page10, label=_('add'), pos=(585, 30))
		self.Bind(wx.EVT_BUTTON, self.add_trigger, self.add_trigger_button)

		self.delete_trigger_button =wx.Button(self.page10, label=_('delete'), pos=(585, 65))
		self.Bind(wx.EVT_BUTTON, self.delete_trigger, self.delete_trigger_button)
		
		self.list_actions = wx.ListCtrl(self.page10, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER, size=(565, 102))
		self.list_actions.SetPosition((15, 165))
		self.list_actions.InsertColumn(0, _('action'), width=200)
		self.list_actions.InsertColumn(1, _('data'), width=220)
		self.list_actions.InsertColumn(2, _('repeat'), width=130)
		self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.edit_actions, self.list_actions)

		self.add_action_button =wx.Button(self.page10, label=_('add'), pos=(585, 165))
		self.Bind(wx.EVT_BUTTON, self.add_action, self.add_action_button)

		self.delete_action_button =wx.Button(self.page10, label=_('delete'), pos=(585, 200))
		self.Bind(wx.EVT_BUTTON, self.delete_action, self.delete_action_button)

		self.stop_all=wx.Button(self.page10, label=_('Stop all'), pos=(10, 285))
		self.Bind(wx.EVT_BUTTON, self.stop_actions, self.stop_all)
		self.start_all=wx.Button(self.page10, label=_('Start all'), pos=(130, 285))
		self.Bind(wx.EVT_BUTTON, self.start_actions, self.start_all)

		self.button_apply_actions =wx.Button(self.page10, label=_('Apply changes'), pos=(570, 285))
		self.Bind(wx.EVT_BUTTON, self.apply_changes_actions, self.button_apply_actions)
		self.button_cancel_actions =wx.Button(self.page10, label=_('Cancel changes'), pos=(430, 285))
		self.Bind(wx.EVT_BUTTON, self.cancel_changes_actions, self.button_cancel_actions)
###########################page10

		self.manual_settings=''
		self.read_kplex_conf()
		self.SerialCheck()
		self.SerialWrongPort()
		self.set_layout_conf()

###########################################	general functions

	def set_layout_conf(self):
		if self.language=='en': self.lang.Check(self.lang_item1.GetId(), True)
		if self.language=='ca': self.lang.Check(self.lang_item2.GetId(), True)
		if self.language=='es': self.lang.Check(self.lang_item3.GetId(), True)
		if self.language=='fr': self.lang.Check(self.lang_item4.GetId(), True)
		if self.language=='nl': self.lang.Check(self.lang_item5.GetId(), True)
		if self.language=='de': self.lang.Check(self.lang_item6.GetId(), True)

		self.delay.SetValue(self.conf.get('STARTUP', 'delay'))

		if self.conf.get('STARTUP', 'opencpn')=='1': 
			self.startup_opencpn.SetValue(True)
		else:
			self.startup_opencpn_nopengl.Disable()
			self.startup_opencpn_fullscreen.Disable()
		if self.conf.get('STARTUP', 'opencpn_no_opengl')=='1': self.startup_opencpn_nopengl.SetValue(True)
		if self.conf.get('STARTUP', 'opencpn_fullscreen')=='1': self.startup_opencpn_fullscreen.SetValue(True)
		if self.conf.get('STARTUP', 'kplex')=='1': 
			self.startup_multiplexer.SetValue(True)
		else:
			self.startup_nmea_time.Disable()
		if self.conf.get('STARTUP', 'gps_time')=='1': self.startup_nmea_time.SetValue(True)
		if self.conf.get('STARTUP', 'x11vnc')=='1': 
			self.startup_remote_desktop.SetValue(True)
		else:
			self.startup_vnc_pass.Disable()
		if self.conf.get('STARTUP', 'vnc_pass')=='1': self.startup_vnc_pass.SetValue(True)
		if self.conf.get('STARTUP', 'maximize')=='1':
			self.op_maximize.SetValue(True) 
			self.Maximize()
		self.startup_path_sound.SetValue(self.conf.get('STARTUP', 'sound'))
		if self.conf.get('STARTUP', 'play')=='1':
			self.startup_play_sound.SetValue(True) 

		output=subprocess.check_output('lsusb')
		supported_dev=['0bda:2832','0bda:2838','0ccd:00a9','0ccd:00b3','0ccd:00d3','0ccd:00e0','185b:0620','185b:0650','1f4d:b803','1f4d:c803','1b80:d3a4','1d19:1101','1d19:1102','1d19:1103','0458:707f','1b80:d393','1b80:d394','1b80:d395','1b80:d39d']
		found=False
		for i in supported_dev:
			if i in output:found=True
		if found:
			self.gain.SetValue(self.conf.get('AIS-SDR', 'gain'))
			self.ppm.SetValue(self.conf.get('AIS-SDR', 'ppm'))
			self.band.SetValue(self.conf.get('AIS-SDR', 'band'))
			self.channel.SetValue(self.conf.get('AIS-SDR', 'gsm_channel'))
			if self.conf.get('AIS-SDR', 'enable')=='1': 
				self.ais_sdr_enable.SetValue(True)
				self.disable_sdr_controls()
			if self.conf.get('AIS-SDR', 'channel')=='a': self.ais_frequencies1.SetValue(True)
			if self.conf.get('AIS-SDR', 'channel')=='b': self.ais_frequencies2.SetValue(True)
		else:
			self.ais_sdr_enable.Disable()
			self.disable_sdr_controls()
			self.button_test_gain.Disable()
			self.button_test_ppm.Disable()
			self.bands_label.Disable()
			self.channel_label.Disable()
			self.band.Disable()
			self.channel.Disable()
			self.check_channels.Disable()
			self.check_bands.Disable()
			self.button_vhf_Tx.Disable()
			self.Tx_exp_label.Disable()
			self.button_vhf_Rx.Disable()

		self.rate.SetValue(self.conf.get('STARTUP', 'nmea_rate_sen'))
		self.rate2.SetValue(self.conf.get('STARTUP', 'nmea_rate_cal'))
		self.accuracy.SetValue(self.conf.get('STARTUP', 'cal_accuracy'))
		if self.conf.get('STARTUP', 'nmea_mag_var')=='1': self.mag_var.SetValue(True)
		if self.conf.get('STARTUP', 'nmea_hdt')=='1': self.heading_t.SetValue(True)
		if self.conf.get('STARTUP', 'nmea_rot')=='1': self.rot.SetValue(True)
		if self.conf.get('STARTUP', 'tw_stw')=='1': self.TW_STW.SetValue(True)
		if self.conf.get('STARTUP', 'tw_sog')=='1': self.TW_SOG.SetValue(True)

		detected=subprocess.check_output(['python', currentpath+'/imu/check_sensors.py'], cwd=currentpath+'/imu')
		l_detected=detected.split('\n')
		imu_sensor=l_detected[0]
		calibrated=l_detected[1]
		press_sensor=l_detected[2]
		hum_sensor=l_detected[3]

		if 'none' in imu_sensor:
			self.heading.Disable()
			self.button_calibrate_imu.Disable()
			self.heading_nmea.Disable()
			self.heel.Disable()
			self.pitch.Disable()
			self.heel_nmea.Disable()
			if self.conf.get('STARTUP', 'nmea_hdg')=='1' or self.conf.get('STARTUP', 'nmea_heel')=='1' or self.conf.get('STARTUP', 'nmea_pitch')=='1': 
				self.conf.set('STARTUP', 'nmea_hdg', '0')
				self.conf.set('STARTUP', 'nmea_heel', '0')
				self.conf.set('STARTUP', 'nmea_pitch', '0')
		else:
			self.imu_tag.SetLabel(_('Sensor detected: ')+imu_sensor)
			if calibrated=='1':self.button_calibrate_imu.Disable()
			if self.conf.get('STARTUP', 'nmea_hdg')=='1': self.heading.SetValue(True)
			if self.conf.get('STARTUP', 'nmea_heel')=='1': self.heel.SetValue(True)
			if self.conf.get('STARTUP', 'nmea_pitch')=='1': self.pitch.SetValue(True)

		if 'none' in press_sensor:
			self.press.Disable()
			self.temp_p.Disable()
			if self.conf.get('STARTUP', 'nmea_press')=='1' or self.conf.get('STARTUP', 'nmea_temp_p')=='1': 
				self.conf.set('STARTUP', 'nmea_press', '0')
				self.conf.set('STARTUP', 'nmea_temp_p', '0')
		else:
			self.press_tag.SetLabel(_('Sensor detected: ')+press_sensor)
			if self.conf.get('STARTUP', 'nmea_press')=='1': self.press.SetValue(True)
			if self.conf.get('STARTUP', 'nmea_temp_p')=='1': self.temp_p.SetValue(True)

		if 'none' in hum_sensor:
			self.hum.Disable()
			self.temp_h.Disable()
			if self.conf.get('STARTUP', 'nmea_hum')=='1' or self.conf.get('STARTUP', 'nmea_temp_h')=='1': 
				self.conf.set('STARTUP', 'nmea_hum', '0')
				self.conf.set('STARTUP', 'nmea_temp_h', '0')
		else:
			self.hum_tag.SetLabel(_('Sensor detected: ')+hum_sensor)
			if self.conf.get('STARTUP', 'nmea_hum')=='1': self.hum.SetValue(True)
			if self.conf.get('STARTUP', 'nmea_temp_h')=='1': self.temp_h.SetValue(True)
		
		if 'none' in hum_sensor and 'none' in press_sensor: self.press_nmea.Disable()

		if self.conf.get('STARTUP', 'press_temp_log')=='1': self.press_temp_log.SetValue(True)

		if self.conf.get('TWITTER', 'apiKey'): self.apiKey.SetValue('********************')
		if self.conf.get('TWITTER', 'apiSecret'): self.apiSecret.SetValue('********************')
		if self.conf.get('TWITTER', 'accessToken'): self.accessToken.SetValue('********************')
		if self.conf.get('TWITTER', 'accessTokenSecret'): self.accessTokenSecret.SetValue('********************')
		if self.conf.get('TWITTER', 'enable')=='1':
			self.twitter_enable.SetValue(True)
			self.apiKey.Disable()
			self.apiSecret.Disable()
			self.accessToken.Disable()
			self.accessTokenSecret.Disable()

		if self.conf.get('GMAIL', 'gmail'): self.Gmail_account.SetValue(self.conf.get('GMAIL', 'gmail'))
		if self.conf.get('GMAIL', 'password'): self.Gmail_password.SetValue('********************')
		if self.conf.get('GMAIL', 'recipient'): self.Recipient.SetValue(self.conf.get('GMAIL', 'recipient'))
		if self.conf.get('GMAIL', 'enable')=='1':
			self.gmail_enable.SetValue(True)
			self.Gmail_account.Disable()
			self.Gmail_password.Disable()
			self.Recipient.Disable()

		with open(home+'/.config/signalk-server-node/settings/openplotter-settings.json') as data_file:
			data = json.load(data_file)
		self.vessel.SetValue(data['vessel']['name'])
		self.mmsi.SetValue(data['vessel']['uuid'])
		if self.conf.get('SIGNALK', 'can_usb')=='0': self.can_usb.SetValue(self.SerDevLs[0])
		else: 
			self.can_usb.SetValue(self.conf.get('SIGNALK', 'can_usb'))
			text='NMEA 0183 - system_output - TCP localhost 10110'
			text=text+'\nNMEA 2000 - CAN-USB - '+self.conf.get('SIGNALK', 'can_usb')
			self.SKinputs_label.SetLabel(text)
		if self.conf.get('SIGNALK', 'enable')=='1': 
			self.signalk_enable.SetValue(True)
			self.vessel.Disable()
			self.vessel_label.Disable()
			self.mmsi.Disable()
			self.mmsi_label.Disable()
			self.NMEA2000_label.Disable()
			self.can_usb.Disable()
			self.CANUSB_label.Disable()

		if self.conf.get('SMS', 'serial')=='0': self.sms_dev.SetValue(self.SerDevLs[0])
		else: self.sms_dev.SetValue(self.conf.get('SMS', 'serial'))
		self.sms_bt.SetValue(self.conf.get('SMS', 'bluetooth'))
		self.sms_con.SetValue(self.conf.get('SMS', 'connection'))
		if self.conf.get('SMS', 'enable')=='1': 
			self.sms_enable.SetValue(True)
			self.sms_dev_label.Disable()
			self.sms_dev.Disable()
			self.sms_bt_label.Disable()
			self.sms_bt.Disable()
			self.sms_con_label.Disable()
			self.sms_con.Disable()
		else: 
			self.button_sms_identify.Disable()

		self.phone_number.SetValue(self.conf.get('SMS', 'phone'))
		if self.conf.get('SMS', 'enable_sending')=='1': 
			self.sms_enable_send.SetValue(True)
			self.phone_number_label.Disable()
			self.phone_number.Disable()
		else: 
			self.button_sms_test.Disable()
			self.sms_text.Disable()
			self.sms_text_label.Disable()

		self.read_wifi_conf()
		self.read_triggers()
		self.read_DS18B20()
		self.read_USBinst()
		self.read_switches()
		self.read_outputs()
		self.read_mqtt()

	def ShowMessage(self, w_msg):
			wx.MessageBox(w_msg, 'Info', wx.OK | wx.ICON_INFORMATION)

	def time_zone(self,event):
		subprocess.Popen(['lxterminal', '-e', 'sudo dpkg-reconfigure tzdata'])
		self.SetStatusText(_('Set time zone in the new window'))

	def time_gps(self,event):
		self.SetStatusText(_('Waiting for NMEA time data in localhost:10110 ...'))
		time_gps_result=subprocess.check_output(['sudo', 'python', currentpath+'/time_gps.py'])
		msg=''
		re=time_gps_result.splitlines()
		for current in re:
			if 'Failed to connect with localhost:10110.' in current: msg+=_('Failed to connect with localhost:10110.\n')
			if 'Error: ' in current: msg+=current+'\n'
			if 'Unable to retrieve date or time from NMEA data.' in current: msg+=_('Unable to retrieve date or time from NMEA data.\n')
			if 'UTC' in current:
				if not '00:00:00' in current: msg+=current+'\n'
			if 'Date and time retrieved from NMEA data successfully.' in current: msg+=_('Date and time retrieved from NMEA data successfully.')

		self.SetStatusText('')
		self.ShowMessage(msg)

	def reconfigure_gpsd(self,event):
		subprocess.Popen(['lxterminal', '-e', 'sudo nano /etc/default/gpsd'])
		self.SetStatusText(_('Set GPSD in the new window'))
	
	def clear_lang(self):
		self.lang.Check(self.lang_item1.GetId(), False)
		self.lang.Check(self.lang_item2.GetId(), False)
		self.lang.Check(self.lang_item3.GetId(), False)
		self.lang.Check(self.lang_item4.GetId(), False)
		self.lang.Check(self.lang_item5.GetId(), False)
		self.lang.Check(self.lang_item6.GetId(), False)
		self.ShowMessage(_('The selected language will be enabled when you restart'))
	
	def lang_en(self, e):
		self.clear_lang()
		self.lang.Check(self.lang_item1.GetId(), True)
		self.conf.set('GENERAL', 'lang', 'en')
	def lang_ca(self, e):
		self.clear_lang()
		self.lang.Check(self.lang_item2.GetId(), True)
		self.conf.set('GENERAL', 'lang', 'ca')
	def lang_es(self, e):
		self.clear_lang()
		self.lang.Check(self.lang_item3.GetId(), True)
		self.conf.set('GENERAL', 'lang', 'es')
	def lang_fr(self, e):
		self.clear_lang()
		self.lang.Check(self.lang_item4.GetId(), True)
		self.conf.set('GENERAL', 'lang', 'fr')
	def lang_nl(self, e):
		self.clear_lang()
		self.lang.Check(self.lang_item5.GetId(), True)
		self.conf.set('GENERAL', 'lang', 'nl')
	def lang_de(self, e):
		self.clear_lang()
		self.lang.Check(self.lang_item6.GetId(), True)
		self.conf.set('GENERAL', 'lang', 'de')

	def OnAboutBox(self, e):
		description = _("OpenPlotter is a DIY, open-source, low-cost, low-consumption, modular and scalable sailing platform to run on ARM boards.")			
		licence = """This program is free software: you can redistribute it 
and/or modify it under the terms of the GNU General Public License 
as published by the Free Software Foundation, either version 2 of 
the License, or any later version.

This program is distributed in the hope that it will be useful, but 
WITHOUT ANY WARRANTY; without even the implied warranty of 
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License 
along with this program.  If not, see http://www.gnu.org/licenses/"""

		info = wx.AboutDialogInfo()
		info.SetName('OpenPlotter')
		info.SetVersion(self.conf.get('GENERAL', 'version'))
		info.SetDescription(description)
		info.SetCopyright('2016 Sailoog')
		info.SetWebSite('http://www.sailoog.com')
		info.SetLicence(licence)
		info.AddDeveloper('Sailoog\nhttp://github.com/sailoog/openplotter\n-------------------\nOpenCPN: http://opencpn.org/ocpn/\nzyGrib: http://www.zygrib.org/\nMultiplexer: http://www.stripydog.com/kplex/index.html\nrtl-sdr: http://sdr.osmocom.org/trac/wiki/rtl-sdr\naisdecoder: http://www.aishub.net/aisdecoder-via-sound-card.html\ngeomag: http://github.com/cmweiss/geomag\nIMU sensor: http://github.com/richards-tech/RTIMULib2\nNMEA parser: http://github.com/Knio/pynmea2\ntwython: http://github.com/ryanmcgrath/twython\npyrtlsdr: http://github.com/roger-/pyrtlsdr\nkalibrate-rtl: http://github.com/steve-m/kalibrate-rtl\nSignalK: http://signalk.org/\n\n')
		info.AddDocWriter('Sailoog\n\nDocumentation: http://sailoog.gitbooks.io/openplotter-documentation/')
		info.AddTranslator('Catalan, English and Spanish by Sailoog\nFrench by Nicolas Janvier.')
		wx.AboutBox(info)

	def op_doc(self, e):
		url = "http://sailoog.gitbooks.io/openplotter-documentation/"
		webbrowser.open(url,new=2)

	def check_short_names(self,short,edit,group):
		exist=False
		short_switches=[]
		for i in self.switches:
			short_switches.append(i[2])	
		short_outputs=[]
		for i in self.outputs:
			short_outputs.append(i[2])
		short_1W=[]
		for i in self.DS18B20:
			short_1W.append(i[1])
		short_topics=[]
		for i in self.topics:
			short_topics.append(i[0])
		if short in short_switches:
			if group=='switches':
				if edit==0: exist=True
				else:
					if edit[0]!=short_switches.index(short): exist=True
			else: exist=True
		if short in short_outputs:
			if group=='outputs':
				if edit==0: exist=True
				else:
					if edit[0]!=short_outputs.index(short): exist=True
			else: exist=True
		if short in short_1W:
			if group=='1w':
				if edit==0: exist=True
				else:
					if edit[0]!=short_1W.index(short): exist=True
			else: exist=True
		if short in short_topics:
			if group=='topics':
				if edit==0: exist=True
				else:
					if edit[0]!=short_topics.index(short): exist=True
			else: exist=True
		return exist

###########################################	startup

	def select_sound(self, e):
		dlg = wx.FileDialog(self, message=_('Choose a file'), defaultDir=currentpath+'/sounds', defaultFile='', wildcard=_('Audio files')+' (*.mp3)|*.mp3|'+_('All files')+' (*.*)|*.*', style=wx.OPEN | wx.CHANGE_DIR)
		if dlg.ShowModal() == wx.ID_OK:
			file_path = dlg.GetPath()
			self.startup_path_sound.SetValue(file_path)
			self.conf.set('STARTUP', 'sound', file_path)
		dlg.Destroy()

	def ok_delay(self, e):
		delay=self.delay.GetValue()
		if not re.match('^[0-9]*$', delay):
				self.ShowMessage(_('You can enter only numbers.'))
				return
		else:
			if delay != '0': delay = delay.lstrip('0')
			self.conf.set('STARTUP', 'delay', delay)
			self.ShowMessage(_('Startup delay set to ')+delay+_(' seconds'))

	def startup(self, e):
		sender = e.GetEventObject()

		if sender==self.startup_opencpn:
			if self.startup_opencpn.GetValue():
				self.startup_opencpn_nopengl.Enable()
				self.startup_opencpn_fullscreen.Enable()
				self.conf.set('STARTUP', 'opencpn', '1')
			else:
				self.startup_opencpn_nopengl.Disable()
				self.startup_opencpn_fullscreen.Disable()
				self.conf.set('STARTUP', 'opencpn', '0')

		if sender==self.startup_opencpn_nopengl:
			if self.startup_opencpn_nopengl.GetValue():
				self.conf.set('STARTUP', 'opencpn_no_opengl', '1')
			else:
				self.conf.set('STARTUP', 'opencpn_no_opengl', '0')

		if sender==self.startup_opencpn_fullscreen:
			if self.startup_opencpn_fullscreen.GetValue():
				self.conf.set('STARTUP', 'opencpn_fullscreen', '1')
			else:
				self.conf.set('STARTUP', 'opencpn_fullscreen', '0')

		if sender==self.startup_multiplexer:
			if self.startup_multiplexer.GetValue():
				self.startup_nmea_time.Enable()
				self.conf.set('STARTUP', 'kplex', '1')
			else:
				self.startup_nmea_time.Disable()
				self.conf.set('STARTUP', 'kplex', '0')

		if sender==self.startup_nmea_time:
			if self.startup_nmea_time.GetValue():
				self.conf.set('STARTUP', 'gps_time', '1')
			else:
				self.conf.set('STARTUP', 'gps_time', '0')

		if sender==self.startup_remote_desktop:
			if self.startup_remote_desktop.GetValue():
				self.conf.set('STARTUP', 'x11vnc', '1')
				self.startup_vnc_pass.Enable()
			else:
				self.conf.set('STARTUP', 'x11vnc', '0')
				self.startup_vnc_pass.Disable()

		if sender==self.startup_vnc_pass:
			if self.startup_vnc_pass.GetValue():
				self.conf.set('STARTUP', 'vnc_pass', '1')
				dlg = wx.MessageDialog(None, _('Do you want to change your VNC-Password?'), _('Question'), wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
				if dlg.ShowModal() == wx.ID_YES:
					subprocess.Popen(['lxterminal', '-e', 'x11vnc', '-storepasswd'])
				dlg.Destroy()
			else:
				self.conf.set('STARTUP', 'vnc_pass', '0')

		if sender==self.op_maximize:
			if self.op_maximize.GetValue():
				self.conf.set('STARTUP', 'maximize', '1')
			else:
				self.conf.set('STARTUP', 'maximize', '0')

		if sender==self.startup_play_sound:
			if self.startup_play_sound.GetValue():
				self.conf.set('STARTUP', 'play', '1')
			else:
				self.conf.set('STARTUP', 'play', '0')

########################################### WiFi AP
	
	def read_wifi_conf(self):
		if len(self.available_wireless)>0:
			self.wlan.SetValue(self.conf.get('WIFI', 'device'))
			self.ssid.SetValue(self.conf.get('WIFI', 'ssid'))
			self.wifi_channel.SetValue(self.conf.get('WIFI', 'channel'))
			if self.conf.get('WIFI', 'password'): self.passw.SetValue('**********')
			if self.conf.get('WIFI', 'share')=='0': self.share.SetValue( _('none'))
			else: self.share.SetValue(self.conf.get('WIFI', 'share'))
			if self.conf.get('WIFI', 'hw_mode')=='b': self.wifi_mode.SetValue('IEEE 802.11b')
			if self.conf.get('WIFI', 'hw_mode')=='g': self.wifi_mode.SetValue('IEEE 802.11g')
			if self.conf.get('WIFI', 'wpa')=='1': self.wifi_wpa.SetValue('WPA')
			if self.conf.get('WIFI', 'wpa')=='2': self.wifi_wpa.SetValue('WPA2')
			if self.conf.get('WIFI', 'wpa')=='3': self.wifi_wpa.SetValue(_('Both'))
			if self.conf.get('WIFI', 'enable')=='1':
				self.enable_disable_wifi(1)
		else:
			self.enable_disable_wifi(0)
		self.show_ip_info('')

	def onwifi_enable (self, e):
		isChecked = self.wifi_enable.GetValue()
		if not isChecked:
			dlg = wx.MessageDialog(None, _('Are you sure to disable?\nIf you are connected by remote, you may not be able to reconnect again.'), _('Question'), wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
			if dlg.ShowModal() != wx.ID_YES:
				self.wifi_enable.SetValue(True)
				dlg.Destroy()
				return
			dlg.Destroy()
		wlan=self.wlan.GetValue()
		ssid=self.ssid.GetValue()
		share=self.share.GetValue()
		if '*****' in self.passw.GetValue(): passw=self.conf.get('WIFI', 'password')
		else: passw=self.passw.GetValue()
		
		if not wlan or not passw or not ssid or not share:
			self.ShowMessage(_('You must fill in all of the fields.'))
			self.enable_disable_wifi(0)
			return
		if wlan==share:
			self.ShowMessage(_('"Access point device" and "Sharing Internet device" must be different'))
			self.enable_disable_wifi(0)
			return
		if len(ssid)>32 or len(passw)<8:
			self.ShowMessage(_('Your SSID must have a maximum of 32 characters and your password a minimum of 8.'))
			self.enable_disable_wifi(0)
			return
		self.SetStatusText(_('Configuring WiFi AP, wait please...'))
		channel=self.wifi_channel.GetValue()
		mode=self.wifi_mode.GetValue()
		wpa=self.wifi_wpa.GetValue()
		if share==_('none'):share='0'
		if mode=='IEEE 802.11b':mode='b'
		if mode=='IEEE 802.11g':mode='g'
		if wpa=='WPA':wpa='1'
		if wpa=='WPA2':wpa='2'
		if wpa==_('Both'):wpa='3'
		self.conf.set('WIFI', 'device', wlan)
		self.conf.set('WIFI', 'password', passw)
		self.conf.set('WIFI', 'ssid', ssid)
		self.conf.set('WIFI', 'share', share)
		self.conf.set('WIFI', 'channel', channel)
		self.conf.set('WIFI', 'hw_mode', mode)
		self.conf.set('WIFI', 'wpa', wpa)
		self.passw.SetValue('**********')
		if isChecked:
			self.enable_disable_wifi(1)
			wifi_result=subprocess.check_output(['sudo', 'python', currentpath+'/wifi_server.py', '1'])		
		else:
			self.enable_disable_wifi(0)
			wifi_result=subprocess.check_output(['sudo', 'python', currentpath+'/wifi_server.py', '0'])
		msg=wifi_result
		if 'WiFi access point failed.' in msg:
			self.enable_disable_wifi(0)
		msg=msg.replace('WiFi access point failed.', _('WiFi access point failed.'))
		msg=msg.replace('WiFi access point started.', _('WiFi access point started.'))
		msg=msg.replace('WiFi access point stopped.', _('WiFi access point stopped.'))
		self.SetStatusText('')
		self.ShowMessage(msg)
		self.show_ip_info('')

	def show_ip_info(self, e):
		ip_info=subprocess.check_output(['hostname', '-I'])
		out=_(' Multiplexed NMEA 0183:\n')
		ips=ip_info.split()
		for ip in ips:
			out+=ip+':10110\n'
		out+=_('\n VNC remote desktop:\n')
		for ip in ips:
			out+=ip+':5900\n'
		out+=_('\n RDP remote desktop:\n')
		for ip in ips:
			out+=ip+'\n'
		out+=_('\n MQTT local broker:\n')
		for ip in ips:
			out+=ip+':1883\n'
		out+=_('\n Signal K panel:\n')
		for ip in ips:
			out+=ip+':3000/instrumentpanel\n'
		out+=_('\n Signal K gauge:\n')
		for ip in ips:
			out+=ip+':3000/sailgauge\n'
		out+=_('\n Signal K NMEA 0183:\n')
		for ip in ips:
			out+=ip+':10111\n'
		self.ip_info.SetValue(out)

	def wifi_default(self, e):
		self.ssid.SetValue('OpenPlotter')
		self.passw.SetValue('12345678')
		self.wifi_channel.SetValue('6')
		self.wifi_mode.SetValue('IEEE 802.11g')
		self.wifi_wpa.SetValue('WPA2')

	def enable_disable_wifi(self, s):
		if s==1:
			self.wlan.Disable()
			self.passw.Disable()
			self.ssid.Disable()
			self.share.Disable()
			self.wlan_label.Disable()
			self.passw_label.Disable()
			self.ssid_label.Disable()
			self.share_label.Disable()
			self.wifi_settings_label.Disable()
			self.wifi_channel.Disable()
			self.wifi_channel_label.Disable()
			self.wifi_mode.Disable()
			self.wifi_mode_label.Disable()
			self.wifi_wpa.Disable()
			self.wifi_wpa_label.Disable()
			self.wifi_button_default.Disable()
			self.wifi_enable.SetValue(True)
			self.conf.set('WIFI', 'enable', '1')
		else:
			self.wlan.Enable()
			self.passw.Enable()
			self.ssid.Enable()
			self.share.Enable()
			self.wlan_label.Enable()
			self.passw_label.Enable()
			self.ssid_label.Enable()
			self.share_label.Enable()
			self.wifi_settings_label.Enable()
			self.wifi_channel.Enable()
			self.wifi_channel_label.Enable()
			self.wifi_mode.Enable()
			self.wifi_mode_label.Enable()
			self.wifi_wpa.Enable()
			self.wifi_wpa_label.Enable()
			self.wifi_button_default.Enable()
			self.wifi_enable.SetValue(False)
			self.conf.set('WIFI', 'enable', '0')

###########################################	SDR-AIS

	def kill_sdr(self):
		subprocess.call(['pkill', '-9', 'aisdecoder'])
		subprocess.call(['pkill', '-9', 'rtl_fm'])
		subprocess.call(['pkill', '-f', 'waterfall.py'])
		subprocess.call(['pkill', '-9', 'rtl_test'])
		subprocess.call(['pkill', '-9', 'kal'])
		subprocess.call(['pkill', '-9', 'qtcsdr'])

	def enable_sdr_controls(self):
		self.gain.Enable()
		self.ppm.Enable()
		self.ais_frequencies1.Enable()
		self.ais_frequencies2.Enable()
		self.gain_label.Enable()
		self.correction_label.Enable()
		self.ais_sdr_enable.SetValue(False)
		self.conf.set('AIS-SDR', 'enable', '0')

	def disable_sdr_controls(self):
		self.gain.Disable()
		self.ppm.Disable()
		self.ais_frequencies1.Disable()
		self.ais_frequencies2.Disable()
		self.gain_label.Disable()
		self.correction_label.Disable()
	
	def ais_frequencies(self, e):
		sender = e.GetEventObject()
		self.ais_frequencies1.SetValue(False)
		self.ais_frequencies2.SetValue(False)
		sender.SetValue(True)

	def OnOffAIS(self, e):
		self.kill_sdr()
		isChecked = self.ais_sdr_enable.GetValue()
		if isChecked:
			self.disable_sdr_controls() 
			gain=self.gain.GetValue()
			ppm=self.ppm.GetValue()
			frecuency='161975000'
			channel='a'
			if self.ais_frequencies2.GetValue(): 
				frecuency='162025000'
				channel='b'
			rtl_fm=subprocess.Popen(['rtl_fm', '-f', frecuency, '-g', gain, '-p', ppm, '-s', '48k'], stdout = subprocess.PIPE)
			aisdecoder=subprocess.Popen(['aisdecoder', '-h', '127.0.0.1', '-p', '10110', '-a', 'file', '-c', 'mono', '-d', '-f', '/dev/stdin'], stdin = rtl_fm.stdout)         
			self.conf.set('AIS-SDR', 'enable', '1')
			self.conf.set('AIS-SDR', 'gain', gain)
			self.conf.set('AIS-SDR', 'ppm', ppm)
			self.conf.set('AIS-SDR', 'channel', channel)
			msg=_('SDR-AIS reception enabled')
		else:
			self.enable_sdr_controls()
			self.conf.set('AIS-SDR', 'enable', '0')
			msg=_('SDR-AIS reception disabled')
		self.SetStatusText(msg)

	def test_ppm(self,event):
		self.kill_sdr()
		self.enable_sdr_controls()
		gain='25'
		if self.gain.GetValue():
			gain=self.gain.GetValue()
			gain=gain.replace(',', '.')
		ppm='0'
		if self.ppm.GetValue():
			ppm=self.ppm.GetValue()
			ppm=ppm.replace(',', '.')
		channel='a'
		if self.ais_frequencies2.GetValue(): channel='b'
		w_open=subprocess.Popen(['python', currentpath+'/waterfall.py', gain, ppm, channel])
		msg=_('SDR-AIS reception disabled. After closing the new window enable SDR-AIS reception again.')
		self.SetStatusText(msg)

	def test_gain(self,event):
		self.kill_sdr()
		self.enable_sdr_controls()
		subprocess.Popen(['lxterminal', '-e', 'rtl_test', '-p'])
		msg=_('SDR-AIS reception disabled.\nCheck the new window. Copy the maximum supported gain value. Wait for ppm value to stabilize and copy it too.')
		self.ShowMessage(msg)

	def check_band(self, event):
		self.kill_sdr()
		self.enable_sdr_controls()
		gain=self.gain.GetValue()
		ppm=self.ppm.GetValue()
		band=self.band.GetValue()
		self.conf.set('AIS-SDR', 'gain', gain)
		self.conf.set('AIS-SDR', 'ppm', ppm)
		self.conf.set('AIS-SDR', 'band', band)
		subprocess.Popen(['python',currentpath+'/fine_cal.py', 'b'])

	def check_channel(self, event):
		self.kill_sdr()
		self.enable_sdr_controls()
		gain=self.gain.GetValue()
		ppm=self.ppm.GetValue()
		channel=self.channel.GetValue()
		self.conf.set('AIS-SDR', 'gain', gain)
		self.conf.set('AIS-SDR', 'ppm', ppm)
		self.conf.set('AIS-SDR', 'gsm_channel', channel)
		if channel: subprocess.Popen(['python',currentpath+'/fine_cal.py', 'c'])

	def vhf_Rx(self, event):
		self.kill_sdr()
		self.enable_sdr_controls()
		subprocess.Popen('qtcsdr')
		msg=_('SDR-AIS reception disabled. After closing the new window enable SDR-AIS reception again.')
		self.SetStatusText(msg)

	def vhf_Tx(self, event):
		self.kill_sdr()
		self.enable_sdr_controls()
		subprocess.Popen(['lxterminal', '-e', currentpath+'/classes/rpi-test.sh'])
		msg=_('SDR-AIS reception disabled. After closing the new window enable SDR-AIS reception again.')
		self.SetStatusText(msg)
###########################################	NMEA 0183

	def show_output_window(self,event):
		close=subprocess.call(['pkill', '-f', 'output.py'])
		show_output=subprocess.Popen(['python',currentpath+'/output.py'])

	def restart_multiplex(self,event):
		self.restart_kplex()
		self.read_kplex_conf()

	def advanced_multiplex(self,event):
		self.ShowMessage(_('OpenPlotter will close. Add manual settings at the end of the configuration file. Open OpenPlotter again and restart multiplexer to apply changes.'))
		subprocess.Popen(['leafpad',home+'/.kplex.conf'])
		self.Close()

	def restart_kplex(self):
		self.SetStatusText(_('Closing Kplex'))
		subprocess.call(["pkill", '-9', "kplex"])
		subprocess.Popen('kplex')
		self.SetStatusText(_('Kplex restarted'))
		if self.conf.get('SIGNALK', 'enable')=='1':
			subprocess.call(["pkill", '-9', "node"])
			subprocess.Popen(home+'/.config/signalk-server-node/bin/openplotter', cwd=home+'/.config/signalk-server-node')

	def cancel_changes(self,event):
		self.read_kplex_conf()

	def read_kplex_conf(self):
		self.inputs = []
		self.koutputs = []
		try:
			file=open(home+'/.kplex.conf', 'r')
			data=file.readlines()
			file.close()

			l_tmp=[None]*8
			self.manual_settings=''
			for index, item in enumerate(data):
				if self.manual_settings:
					if item!='\n': self.manual_settings+=item
				else:
					if re.search('\[*\]', item):
						if l_tmp[0]=='in': self.inputs.append(l_tmp)
						if l_tmp[0]=='out': self.koutputs.append(l_tmp)
						l_tmp=[None]*8
						l_tmp[5]='none'
						l_tmp[6]='nothing'
						if '[serial]' in item: l_tmp[2]='Serial'
						if '[tcp]' in item: l_tmp[2]='TCP'
						if '[udp]' in item: l_tmp[2]='UDP'
						if '#[' in item: l_tmp[7]='0'
						else: l_tmp[7]='1'
					if 'direction=in' in item:
						l_tmp[0]='in'
					if 'direction=out' in item:
						l_tmp[0]='out'
					if 'name=' in item and 'filename=' not in item:
						l_tmp[1]=self.extract_value(item)
					if 'address=' in item or 'filename=' in item:
						l_tmp[3]=self.extract_value(item)
					if 'port=' in item or 'baud=' in item:
						l_tmp[4]=self.extract_value(item)
					if 'filter=' in item and '-all' in item:
						l_tmp[5]='accept'
						l_tmp[6]=self.extract_value(item)
					if 'filter=' in item and '-all' not in item:
						l_tmp[5]='ignore'
						l_tmp[6]=self.extract_value(item)
					if '###Manual settings' in item:
						self.manual_settings='###Manual settings\n\n'

			if l_tmp[0]=='in': self.inputs.append(l_tmp)
			if l_tmp[0]=='out': self.koutputs.append(l_tmp)
			self.write_inputs()
			self.write_outputs()

		except IOError:
			self.ShowMessage(_('Multiplexer configuration file does not exist. Add inputs and apply changes.'))

	def extract_value(self,data):
		option, value =data.split('=')
		value=value.strip()
		return value

	def write_inputs(self):
		self.list_input.DeleteAllItems()
		for i in self.inputs:
			if i[1]: index = self.list_input.InsertStringItem(sys.maxint, i[1])
			if i[2]: self.list_input.SetStringItem(index, 1, i[2])
			if i[3]: self.list_input.SetStringItem(index, 2, i[3])
			else: self.list_input.SetStringItem(index, 2, '127.0.0.1')
			if i[4]: self.list_input.SetStringItem(index, 3, i[4])
			if i[5]:
				if i[5]=='none': self.list_input.SetStringItem(index, 4, _('none'))
				if i[5]=='accept': self.list_input.SetStringItem(index, 4, _('accept'))
				if i[5]=='ignore': self.list_input.SetStringItem(index, 4, _('ignore'))
			if i[6]=='nothing':
				self.list_input.SetStringItem(index, 5, _('nothing'))
			else:
				filters=i[6].replace(':-all', '')
				filters=filters.replace('+', '')
				filters=filters.replace('-', '')
				filters=filters.replace(':', ',')
				self.list_input.SetStringItem(index, 5, filters)
			if i[7]=='1': self.list_input.CheckItem(index)
	
	def write_outputs(self):
		self.list_output.DeleteAllItems()
		for i in self.koutputs:
			if i[1]: index = self.list_output.InsertStringItem(sys.maxint, i[1])
			if i[2]: self.list_output.SetStringItem(index, 1, i[2])
			if i[3]: self.list_output.SetStringItem(index, 2, i[3])
			else: self.list_output.SetStringItem(index, 2, 'localhost')
			if i[4]: self.list_output.SetStringItem(index, 3, i[4])
			if i[5]:
				if i[5]=='none': self.list_output.SetStringItem(index, 4, _('none'))
				if i[5]=='accept': self.list_output.SetStringItem(index, 4, _('accept'))
				if i[5]=='ignore': self.list_output.SetStringItem(index, 4, _('ignore'))
			if i[6]=='nothing':
				self.list_output.SetStringItem(index, 5, _('nothing'))
			else:
				filters=i[6].replace(':-all', '')
				filters=filters.replace('+', '')
				filters=filters.replace('-', '')
				filters=filters.replace(':', ',')
				self.list_output.SetStringItem(index, 5, filters)
			if i[7]=='1': self.list_output.CheckItem(index)

	def apply_changes(self,event):
		data='# For advanced manual configuration, please visit: http://www.stripydog.com/kplex/configuration.html\n# Please do not modify defaults nor OpenPlotter GUI settings.\n# Add manual settings at the end of the document.\n\n'

		data=data+'###defaults\n\n[udp]\nname=system_input\ndirection=in\noptional=yes\naddress=127.0.0.1\nport=10110\n\n'
		data=data+'[tcp]\nname=system_output\ndirection=out\nmode=server\nport=10110\n\n###end of defaults\n\n###OpenPlotter GUI settings\n\n'

		for index,item in enumerate(self.inputs):
			if 'system_input' not in item[1]:
				if self.list_input.IsChecked(index): state=''
				else: state='#'
				if 'Serial' in item[2]:
					data=data+state+'[serial]\n'+state+'name='+item[1]+'\n'+state+'direction=in\n'+state+'optional=yes\n'
					if item[5]=='ignore':data=data+state+'ifilter='+item[6]+'\n'
					if item[5]=='accept':data=data+state+'ifilter='+item[6]+'\n'
					data=data+state+'filename='+item[3]+'\n'+state+'baud='+item[4]+'\n\n'
				if 'TCP' in item[2]:
					data=data+state+'[tcp]\n'+state+'name='+item[1]+'\n'+state+'direction=in\n'+state+'optional=yes\n'
					if item[1]=='gpsd':data=data+state+'gpsd=yes\n'
					if item[5]=='ignore':data=data+state+'ifilter='+item[6]+'\n'
					if item[5]=='accept':data=data+state+'ifilter='+item[6]+'\n'
					data=data+state+'mode=client\n'+state+'address='+item[3]+'\n'+state+'port='+item[4]+'\n'
					data=data+state+'persist=yes\n'+state+'retry=10\n\n'				
				if 'UDP' in item[2]:
					data=data+state+'[udp]\n'+state+'name='+item[1]+'\n'+state+'direction=in\n'+state+'optional=yes\n'
					if item[5]=='ignore':data=data+state+'ifilter='+item[6]+'\n'
					if item[5]=='accept':data=data+state+'ifilter='+item[6]+'\n'
					data=data+state+'address='+item[3]+'\n'+state+'port='+item[4]+'\n\n'
		
		for index,item in enumerate(self.koutputs):
			if 'system_output' not in item[1]:
				if self.list_output.IsChecked(index): state=''
				else: state='#'
				if 'Serial' in item[2]:
					data=data+state+'[serial]\n'+state+'name='+item[1]+'\n'+state+'direction=out\n'+state+'optional=yes\n'
					if item[5]=='ignore':data=data+state+'ofilter='+item[6]+'\n'
					if item[5]=='accept':data=data+state+'ofilter='+item[6]+'\n'
					data=data+state+'filename='+item[3]+'\n'+state+'baud='+item[4]+'\n\n'
				if 'TCP' in item[2]:
					data=data+state+'[tcp]\n'+state+'name='+item[1]+'\n'+state+'direction=out\n'+state+'optional=yes\n'
					if item[5]=='ignore':data=data+state+'ofilter='+item[6]+'\n'
					if item[5]=='accept':data=data+state+'ofilter='+item[6]+'\n'
					data=data+state+'mode=server\n'+state+'address='+item[3]+'\n'+state+'port='+item[4]+'\n\n'				
				if 'UDP' in item[2]:
					data=data+state+'[udp]\n'+state+'name='+item[1]+'\n'+state+'direction=out\n'+state+'optional=yes\n'
					if item[5]=='ignore':data=data+state+'ofilter='+item[6]+'\n'
					if item[5]=='accept':data=data+state+'ofilter='+item[6]+'\n'
					data=data+state+'address='+item[3]+'\n'+state+'port='+item[4]+'\n\n'
		
		data=data+'###end of OpenPlotter GUI settings\n\n'
		if self.manual_settings: data+= self.manual_settings
		else: data+= '###Manual settings\n\n'
		
		file = open(home+'/.kplex.conf', 'w')
		file.write(data)
		file.close()
		self.restart_kplex()
		self.read_kplex_conf()

	def delete_input(self,event):
		num = len(self.inputs)
		for i in range(num):
			if self.list_input.IsSelected(i):
				del self.inputs[i]
		self.write_inputs()

	def delete_output(self,event):
		num = len(self.koutputs)
		for i in range(num):
			if self.list_output.IsSelected(i):
				del self.koutputs[i]
		self.write_outputs()

	def process_name(self,r):
		list_tmp=[]
		l=r.split(',')
		for item in l:
			item=item.strip()
			list_tmp.append(item)
		name=list_tmp[1]
		found=False
		for sublist in self.inputs:
			if sublist[1] == name:
				found=True
		for sublist in self.koutputs:
			if sublist[1] == name:
				found=True
		if found==True:
			self.ShowMessage(_('This name already exists.'))
			return False
		else:
			return list_tmp
	
	def add_serial_input(self,event):
		subprocess.call(['pkill', '-f', 'connection.py'])
		p=subprocess.Popen(['python', currentpath+'/connection.py', 'in', 'serial'], stdout=subprocess.PIPE)
		r=stdout = p.communicate()[0]
		if r:
			list_tmp=self.process_name(r)
			if list_tmp:
				new_port=list_tmp[3]
				for sublist in self.inputs:
					if sublist[3] == new_port: 
						self.ShowMessage(_('This input is already in use.'))
						return
				self.inputs.append(list_tmp)
				self.write_inputs()

	def add_serial_output(self,event):
		subprocess.call(['pkill', '-f', 'connection.py'])
		p=subprocess.Popen(['python', currentpath+'/connection.py', 'out', 'serial'], stdout=subprocess.PIPE)
		r=stdout = p.communicate()[0]
		if r:
			list_tmp=self.process_name(r)
			if list_tmp:
				new_port=list_tmp[3]
				for sublist in self.koutputs:
					if sublist[3] == new_port: 
						self.ShowMessage(_('This output is already in use.'))
						return
				self.koutputs.append(list_tmp)
				self.write_outputs()

	def add_network_input(self,event):
		subprocess.call(['pkill', '-f', 'connection.py'])
		p=subprocess.Popen(['python', currentpath+'/connection.py', 'in', 'network'], stdout=subprocess.PIPE)
		r=stdout = p.communicate()[0]
		if r:
			list_tmp=self.process_name(r)
			if list_tmp:
				if list_tmp[4]=='10111':
					self.ShowMessage(_('Cancelled. Port 10111 is being used by Signal K.'))
					return
				new_address_port=str(list_tmp[2])+str(list_tmp[3])+str(list_tmp[4])
				for sublist in self.inputs:					
					old_address_port=str(sublist[2])+str(sublist[3])+str(sublist[4])
					if old_address_port == new_address_port: 
						self.ShowMessage(_('This input is already in use.'))
						return
				self.inputs.append(list_tmp)
				self.write_inputs()

	def add_network_output(self,event):
		subprocess.call(['pkill', '-f', 'connection.py'])
		p=subprocess.Popen(['python', currentpath+'/connection.py', 'out', 'network'], stdout=subprocess.PIPE)
		r=stdout = p.communicate()[0]
		if r:
			list_tmp=self.process_name(r)
			if list_tmp:
				if list_tmp[4]=='10111':
					self.ShowMessage(_('Cancelled. Port 10111 is being used by Signal K.'))
					return
				new_address_port=str(list_tmp[2])+str(list_tmp[3])+str(list_tmp[4])
				for sublist in self.koutputs:					
					old_address_port=str(sublist[2])+str(sublist[3])+str(sublist[4])
					if old_address_port == new_address_port: 
						self.ShowMessage(_('This output is already in use.'))
						return
				self.koutputs.append(list_tmp)
				self.write_outputs()

###################################### I2C sensors

	def start_sensors(self):
		subprocess.call(['pkill', 'RTIMULibDemoGL'])
		subprocess.call(['pkill', '-f', 'i2c.py'])
		if self.heading.GetValue() or self.heel.GetValue() or self.pitch.GetValue() or self.press.GetValue() or self.temp_p.GetValue() or self.hum.GetValue() or self.temp_h.GetValue():
			subprocess.Popen(['python', currentpath+'/i2c.py'], cwd=currentpath+'/imu')

	def ok_rate(self, e):
		rate=self.rate.GetValue()
		self.conf.set('STARTUP', 'nmea_rate_sen', rate)
		self.start_sensors()
		self.start_sensors_b()
		self.ShowMessage(_('Generation rate set to ')+rate+_(' seconds'))
		
	def nmea_hdg(self, e):
		sender = e.GetEventObject()
		if sender.GetValue(): self.conf.set('STARTUP', 'nmea_hdg', '1')
		else: self.conf.set('STARTUP', 'nmea_hdg', '0')
		self.start_sensors()

	def nmea_heel(self, e):
		sender = e.GetEventObject()
		if sender.GetValue(): self.conf.set('STARTUP', 'nmea_heel', '1')
		else: self.conf.set('STARTUP', 'nmea_heel', '0')
		self.start_sensors()

	def nmea_pitch(self, e):
		sender = e.GetEventObject()
		if sender.GetValue(): self.conf.set('STARTUP', 'nmea_pitch', '1')
		else: self.conf.set('STARTUP', 'nmea_pitch', '0')
		self.start_sensors()

	def reset_imu(self, e):
		try:
			os.remove(currentpath+'/imu/RTIMULib.ini')
		except Exception,e: print str(e)
		self.button_calibrate_imu.Enable()
		self.imu_tag.Disable()
		self.heading.SetValue(False)
		self.heel.SetValue(False)
		self.pitch.SetValue(False)
		self.conf.set('STARTUP', 'nmea_hdg', '0')
		self.conf.set('STARTUP', 'nmea_heel', '0')
		self.conf.set('STARTUP', 'nmea_pitch', '0')
		self.start_sensors()
		msg=_('Heading, heel and pitch disabled.\nClose and open OpenPlotter again to autodetect.')
		self.ShowMessage(msg)

	def reset_press_hum(self, e):
		try:
			os.remove(currentpath+'/imu/RTIMULib2.ini')
		except Exception,e: print str(e)
		try:
			os.remove(currentpath+'/imu/RTIMULib3.ini')
		except Exception,e: print str(e)
		self.press_tag.Disable()
		self.hum_tag.Disable()
		self.press.SetValue(False)
		self.temp_p.SetValue(False)
		self.hum.SetValue(False)
		self.temp_h.SetValue(False)
		self.conf.set('STARTUP', 'nmea_press', '0')
		self.conf.set('STARTUP', 'nmea_temp_p', '0')
		self.conf.set('STARTUP', 'nmea_hum', '0')
		self.conf.set('STARTUP', 'nmea_temp_h', '0')
		self.start_sensors()
		msg=_('Temperature, humidity and pressure disabled.\nClose and open OpenPlotter again to autodetect.')
		self.ShowMessage(msg)

	def calibrate_imu(self, e):
		self.heading.SetValue(False)
		self.heel.SetValue(False)
		self.pitch.SetValue(False)
		self.press.SetValue(False)
		self.temp_p.SetValue(False)
		self.hum.SetValue(False)
		self.temp_h.SetValue(False)
		self.conf.set('STARTUP', 'nmea_hdg', '0')
		self.conf.set('STARTUP', 'nmea_heel', '0')
		self.conf.set('STARTUP', 'nmea_pitch', '0')
		self.conf.set('STARTUP', 'nmea_press', '0')
		self.conf.set('STARTUP', 'nmea_temp_p', '0')
		self.conf.set('STARTUP', 'nmea_hum', '0')
		self.conf.set('STARTUP', 'nmea_temp_h', '0')
		self.start_sensors()
		subprocess.Popen('RTIMULibDemoGL', cwd=currentpath+'/imu')
		msg=_('Heading, heel, pitch, temperature, humidity and pressure disabled.\nAfter calibrating, enable them again.')
		self.ShowMessage(msg)
	
	def nmea_press(self, e):
		sender = e.GetEventObject()
		if sender.GetValue(): self.conf.set('STARTUP', 'nmea_press', '1')
		else: self.conf.set('STARTUP', 'nmea_press', '0')
		self.start_sensors()

	def nmea_temp_p(self, e):
		sender = e.GetEventObject()
		if sender.GetValue(): 
			self.temp_h.SetValue(False)
			self.conf.set('STARTUP', 'nmea_temp_h', '0')
			self.conf.set('STARTUP', 'nmea_temp_p', '1')
		else: 
			self.conf.set('STARTUP', 'nmea_temp_p', '0')
		self.start_sensors()

	def nmea_hum(self, e):
		sender = e.GetEventObject()
		if sender.GetValue(): self.conf.set('STARTUP', 'nmea_hum', '1')
		else: self.conf.set('STARTUP', 'nmea_hum', '0')
		self.start_sensors()

	def nmea_temp_h(self, e):
		sender = e.GetEventObject()
		if sender.GetValue(): 
			self.temp_p.SetValue(False)
			self.conf.set('STARTUP', 'nmea_temp_p', '0')
			self.conf.set('STARTUP', 'nmea_temp_h', '1')
		else: 
			self.conf.set('STARTUP', 'nmea_temp_h', '0')
		self.start_sensors()

	def enable_press_temp_log(self, e):
		sender = e.GetEventObject()
		if sender.GetValue(): self.conf.set('STARTUP', 'press_temp_log', '1')
		else: self.conf.set('STARTUP', 'press_temp_log', '0')
		self.start_sensors()

	def show_graph(self, e):
		subprocess.call(['pkill', '-f', 'graph.py'])
		subprocess.Popen(['python', currentpath+'/graph.py'])

	def	reset_graph(self, e):
		data=''
		file = open(currentpath+'/weather_log.csv', 'w')
		file.write(data)
		file.close()
		self.start_sensors()
		self.ShowMessage(_('Weather log restarted'))

###################################### Calculate

	def start_calculate(self):
		subprocess.call(['pkill', '-f', 'calculate.py'])
		if self.mag_var.GetValue() or self.heading_t.GetValue() or self.rot.GetValue() or self.TW_STW.GetValue() or self.TW_SOG.GetValue():
			subprocess.Popen(['python', currentpath+'/calculate.py'])

	def ok_rate2(self, e):
		rate=self.rate2.GetValue()
		self.conf.set('STARTUP', 'nmea_rate_cal', rate)
		self.start_calculate()
		self.ShowMessage(_('Generation rate set to ')+rate+_(' seconds'))

	def ok_accuracy(self,e):
		accuracy=self.accuracy.GetValue()
		self.conf.set('STARTUP', 'cal_accuracy', accuracy)
		self.start_calculate()
		self.ShowMessage(_('Calculation accuracy set to ')+accuracy+_(' seconds'))

	def nmea_mag_var(self, e):
		sender = e.GetEventObject()
		if sender.GetValue(): self.conf.set('STARTUP', 'nmea_mag_var', '1')
		else: self.conf.set('STARTUP', 'nmea_mag_var', '0')
		self.start_calculate()

	def nmea_hdt(self, e):
		sender = e.GetEventObject()
		if sender.GetValue(): self.conf.set('STARTUP', 'nmea_hdt', '1')
		else: self.conf.set('STARTUP', 'nmea_hdt', '0')
		self.start_calculate()

	def nmea_rot(self, e):
		sender = e.GetEventObject()
		if sender.GetValue(): self.conf.set('STARTUP', 'nmea_rot', '1')
		else: self.conf.set('STARTUP', 'nmea_rot', '0')
		self.start_calculate()

	def	TW(self, e):
		sender = e.GetEventObject()
		state=sender.GetValue()
		self.TW_STW.SetValue(False)
		self.TW_SOG.SetValue(False)
		self.conf.set('STARTUP', 'tw_stw', '0')
		self.conf.set('STARTUP', 'tw_sog', '0')
		if state: sender.SetValue(True)
		if self.TW_STW.GetValue(): self.conf.set('STARTUP', 'tw_stw', '1')
		if self.TW_SOG.GetValue(): self.conf.set('STARTUP', 'tw_sog', '1')
		self.start_calculate()

###################################### Switches

	def read_switches(self):
		self.switches=[]
		self.list_switches.DeleteAllItems()
		data=self.conf.get('INPUTS', 'switches')
		try:
			temp_list=eval(data)
		except:temp_list=[]
		for ii in temp_list:
			self.switches.append(ii)
			self.list_switches.Append([ii[1].decode('utf8'),ii[2].decode('utf8'),str(ii[3]),ii[4]])
			if ii[0]=='1':
				last=self.list_switches.GetItemCount()-1
				self.list_switches.CheckItem(last)

	def edit_switches(self,e):
		selected_switch=e.GetIndex()
		edit=[selected_switch,self.switches[selected_switch][1],self.switches[selected_switch][2],self.switches[selected_switch][3],self.switches[selected_switch][4]]
		self.edit_add_switches(edit)

	def add_switches(self,e):
		self.edit_add_switches(0)

	def edit_add_switches(self,edit):
		avalaible_gpio=[]
		edited=''
		if edit!=0: edited=edit[3]
		list_gpio=[5,6,12,13,16,17,18,19,20,21,22,23,24,25,26,27]
		gpio_sw=[]
		for i in self.switches:
			gpio_sw.append(i[3])	
		gpio_out=[]
		for i in self.outputs:
			gpio_out.append(i[3])
		for i in list_gpio:
			if i==edited:
				avalaible_gpio.append(str(i))
			else:
				if i in gpio_sw or i in gpio_out: pass
				else: avalaible_gpio.append(str(i))
		dlg = addSwitch(avalaible_gpio,edit)
		res = dlg.ShowModal()
		if res == wx.ID_OK:
			name=dlg.name.GetValue()
			name=name.encode('utf8')
			short=dlg.short.GetValue()
			short=short.encode('utf8')
			gpio_selection=dlg.gpio_select.GetValue()
			pull_selection=dlg.pull_select.GetValue()
			pull_selection=pull_selection.encode('utf8')
			if not name or not short:
				self.ShowMessage(_('Failed. Write a name and a short name.'))
				dlg.Destroy()
				return				
			if gpio_selection == '':
				self.ShowMessage(_('Failed. Select GPIO.'))
				dlg.Destroy()
				return
			if pull_selection == '':
				self.ShowMessage(_('Failed. Select pull down or pull up.'))
				dlg.Destroy()
				return
			short_exist=self.check_short_names(short,edit,'switches')
			if short_exist:
				self.ShowMessage(_('Failed. This short name is already used.'))
				dlg.Destroy()
				return				
			if edit==0:
				self.list_switches.Append([name.decode('utf8'),short.decode('utf8'),gpio_selection,pull_selection])
				last=self.list_switches.GetItemCount()-1
				self.list_switches.CheckItem(last)
				if len(self.switches)==0: ID='SW0'
				else:
					last=len(self.switches)-1
					x=int(self.switches[last][5][2:])
					ID='SW'+str(x+1)
				self.switches.append(['1',name,short,int(gpio_selection),pull_selection,ID])
			else:
				self.list_switches.SetStringItem(edit[0],0,name.decode('utf8'))
				self.list_switches.SetStringItem(edit[0],1,short.decode('utf8'))
				self.list_switches.SetStringItem(edit[0],2,gpio_selection)
				self.list_switches.SetStringItem(edit[0],3,pull_selection)
				self.switches[edit[0]][1]=name
				self.switches[edit[0]][2]=short
				self.switches[edit[0]][3]=int(gpio_selection)
				self.switches[edit[0]][4]=pull_selection
		dlg.Destroy()

	def delete_switches(self,e):
		selected_switch=self.list_switches.GetFirstSelected()
		if selected_switch==-1: 
			self.ShowMessage(_('Select a switch to delete.'))
			return
		data=self.conf.get('ACTIONS', 'triggers')
		try:
			temp_list=eval(data)
		except:temp_list=[]
		for i in temp_list:
			if i[1]==self.switches[selected_switch][5]:
				self.read_triggers()
				self.ShowMessage(_('You have a trigger defined for this switch. You must delete that action before deleting this switch.'))
				return
		del self.switches[selected_switch]
		self.list_switches.DeleteItem(selected_switch)

	def apply_changes_switches(self, e):	
		gpio_out=[]
		data=self.conf.get('OUTPUTS', 'outputs')
		try:
			temp_list=eval(data)
		except:temp_list=[]
		for i in temp_list:
			gpio_out.append(i[3])
		for i in self.switches:
			if i[3] in gpio_out:
				self.read_outputs()
				self.ShowMessage('GPIO '+str(i[3])+_(' is being used in outputs. Switches changes cancelled.'))
				return
		for i in self.switches:
			index=self.switches.index(i)
			if self.list_switches.IsChecked(index): self.switches[index][0]='1'
			else: self.switches[index][0]='0'
		self.conf.set('INPUTS', 'switches', str(self.switches))
		self.start_monitoring()
		self.SetStatusText(_('Switches changes applied and restarted'))

	def cancel_changes_switches(self, e):
		self.read_switches()
		self.SetStatusText(_('Switches changes cancelled'))

###################################### Outputs

	def read_outputs(self):
		self.outputs=[]
		self.list_outputs.DeleteAllItems()
		data=self.conf.get('OUTPUTS', 'outputs')
		try:
			temp_list=eval(data)
		except:temp_list=[]
		for ii in temp_list:
			self.outputs.append(ii)
			self.list_outputs.Append([ii[1].decode('utf8'),ii[2].decode('utf8'),str(ii[3])])
			if ii[0]=='1':
				last=self.list_outputs.GetItemCount()-1
				self.list_outputs.CheckItem(last)
	
	def edit_outputs(self,e):
		selected_output=e.GetIndex()
		edit=[selected_output,self.outputs[selected_output][1],self.outputs[selected_output][2],self.outputs[selected_output][3]]
		self.edit_add_outputs(edit)

	def add_outputs(self,e):
		self.edit_add_outputs(0)

	def edit_add_outputs(self,edit):
		avalaible_gpio=[]
		edited=''
		if edit!=0: edited=edit[3]
		list_gpio=[5,6,12,13,16,17,18,19,20,21,22,23,24,25,26,27]
		gpio_sw=[]
		for i in self.switches:
			gpio_sw.append(i[3])	
		gpio_out=[]
		for i in self.outputs:
			gpio_out.append(i[3])	
		for i in list_gpio:
			if i==edited:
				avalaible_gpio.append(str(i))
			else:
				if i in gpio_sw or i in gpio_out: pass
				else: avalaible_gpio.append(str(i))	
		dlg = addOutput(avalaible_gpio,edit)
		res = dlg.ShowModal()
		if res == wx.ID_OK:
			name=dlg.name.GetValue()
			name=name.encode('utf8')
			short=dlg.short.GetValue()
			short=short.encode('utf8')
			gpio_selection=dlg.gpio_select.GetValue()
			if not name or not short:
				self.ShowMessage(_('Failed. Write a name and a short name.'))
				dlg.Destroy()
				return				
			if gpio_selection == '':
				self.ShowMessage(_('Failed. Select GPIO.'))
				dlg.Destroy()
				return
			short_exist=self.check_short_names(short,edit,'outputs')
			if short_exist:
				self.ShowMessage(_('Failed. This short name is already used.'))
				dlg.Destroy()
				return
			if edit==0:
				self.list_outputs.Append([name.decode('utf8'),short.decode('utf8'),gpio_selection])
				last=self.list_outputs.GetItemCount()-1
				self.list_outputs.CheckItem(last)
				if len(self.outputs)==0: ID='OUT0'
				else:
					last=len(self.outputs)-1
					x=int(self.outputs[last][4][3:])
					ID='OUT'+str(x+1)
				self.outputs.append(['1',name,short,int(gpio_selection),ID])
			else:
				self.list_outputs.SetStringItem(edit[0],0,name.decode('utf8'))
				self.list_outputs.SetStringItem(edit[0],1,short.decode('utf8'))
				self.list_outputs.SetStringItem(edit[0],2,gpio_selection)
				self.outputs[edit[0]][1]=name
				self.outputs[edit[0]][2]=short
				self.outputs[edit[0]][3]=int(gpio_selection)
		dlg.Destroy()

	def delete_outputs(self,e):
		selected_output=self.list_outputs.GetFirstSelected()
		if selected_output==-1: 
			self.ShowMessage(_('Select an output to delete.'))
			return
		data=self.conf.get('ACTIONS', 'triggers')
		try:
			temp_list=eval(data)
		except:temp_list=[]
		dontdelete=0
		for i in temp_list:
			if i[1]==self.outputs[selected_output][4]: dontdelete=1
			for ii in i[4]:
				if ii[0][1:]==self.outputs[selected_output][4]: dontdelete=1
		if dontdelete==1:
			self.read_triggers()
			self.ShowMessage(_('You have a trigger defined for this output. You must delete that action before deleting this output.'))
			return
		del self.outputs[selected_output]
		self.list_outputs.DeleteItem(selected_output)

	def apply_changes_outputs(self, e):
		gpio_sw=[]
		data=self.conf.get('INPUTS', 'switches')
		try:
			temp_list=eval(data)
		except:temp_list=[]
		for i in temp_list:
			gpio_sw.append(i[3])
		for i in self.outputs:
			if i[3] in gpio_sw:
				self.read_switches()
				self.ShowMessage('GPIO '+str(i[3])+_(' is being used in switches. Output changes cancelled.'))
				return
		for i in self.outputs:
			index=self.outputs.index(i)
			if self.list_outputs.IsChecked(index): self.outputs[index][0]='1'
			else: self.outputs[index][0]='0'
		self.conf.set('OUTPUTS', 'outputs', str(self.outputs))
		self.start_monitoring()
		self.SetStatusText(_('Output changes applied and restarted'))

	def cancel_changes_outputs(self, e):
		self.read_outputs()
		self.SetStatusText(_('Output changes cancelled'))

####################### Accounts

	def start_monitoring(self):
		self.ShowMessage(_('Actions will be restarted.'))
		subprocess.call(['pkill', '-f', 'monitoring.py'])
		subprocess.Popen(['python',currentpath+'/monitoring.py'])

	def on_twitter_enable(self,e):
		if not self.apiKey.GetValue() or not self.apiSecret.GetValue() or not self.accessToken.GetValue() or not self.accessTokenSecret.GetValue():
			self.twitter_enable.SetValue(False)
			self.ShowMessage(_('Enter valid Twitter apiKey, apiSecret, accessToken and accessTokenSecret.'))
			return
		if self.twitter_enable.GetValue():
			self.apiKey.Disable()
			self.apiSecret.Disable()
			self.accessToken.Disable()
			self.accessTokenSecret.Disable()
			self.conf.set('TWITTER', 'enable', '1')
			if not '*****' in self.apiKey.GetValue(): 
				self.conf.set('TWITTER', 'apiKey', self.apiKey.GetValue())
				self.apiKey.SetValue('********************')
			if not '*****' in self.apiSecret.GetValue(): 
				self.conf.set('TWITTER', 'apiSecret', self.apiSecret.GetValue())
				self.apiSecret.SetValue('********************')
			if not '*****' in self.accessToken.GetValue(): 
				self.conf.set('TWITTER', 'accessToken', self.accessToken.GetValue())
				self.accessToken.SetValue('********************')
			if not '*****' in self.accessTokenSecret.GetValue(): 
				self.conf.set('TWITTER', 'accessTokenSecret', self.accessTokenSecret.GetValue())
				self.accessTokenSecret.SetValue('********************')
		else:
			self.conf.set('TWITTER', 'enable', '0')
			self.apiKey.Enable()
			self.apiSecret.Enable()
			self.accessToken.Enable()
			self.accessTokenSecret.Enable()
		self.start_monitoring()

	def on_gmail_enable(self,e):
		if not self.Gmail_account.GetValue() or not self.Gmail_password.GetValue() or not self.Recipient.GetValue():
			self.gmail_enable.SetValue(False)
			self.ShowMessage(_('Enter valid Gmail account, Gmail password and Recipient.'))
			return
		if self.gmail_enable.GetValue():
			self.Gmail_account.Disable()
			self.Gmail_password.Disable()
			self.Recipient.Disable()
			self.conf.set('GMAIL', 'enable', '1')
			self.conf.set('GMAIL', 'gmail', self.Gmail_account.GetValue())
			if not '*****' in self.Gmail_password.GetValue(): 
				self.conf.set('GMAIL', 'password', self.Gmail_password.GetValue())
				self.Gmail_password.SetValue('********************')
			self.conf.set('GMAIL', 'recipient', self.Recipient.GetValue())
		else:
			self.conf.set('GMAIL', 'enable', '0')
			self.Gmail_account.Enable()
			self.Gmail_password.Enable()
			self.Recipient.Enable()
		self.start_monitoring()

####################### Actions

	def read_triggers(self):
		self.a=DataStream(self.conf)
		self.triggers=[]
		self.list_triggers.DeleteAllItems()
		data=self.conf.get('ACTIONS', 'triggers')
		try:
			temp_list=eval(data)
		except:temp_list=[]
		for ii in temp_list:
			if ii[1]==-1:
				self.triggers.append(ii)
				self.list_triggers.Append([_('None (always true)'),'','',])
				if ii[0]==1:
					last=self.list_triggers.GetItemCount()-1
					self.list_triggers.CheckItem(last)
			else:
				x=self.a.getDataListIndex(ii[1])
				if x:
					self.triggers.append(ii)
					self.list_triggers.Append([self.a.DataList[x][0].decode('utf8'),self.a.operators_list[ii[2]].decode('utf8'),ii[3]])
					if ii[0]==1:
						last=self.list_triggers.GetItemCount()-1
						self.list_triggers.CheckItem(last)
				else: self.ShowMessage(_('Problem with Actions detected. Please check and save again.'))

	def print_actions(self, e):
		self.actions=Actions(self.conf)
		selected_trigger=e.GetIndex()
		self.list_actions.DeleteAllItems()
		for i in  self.triggers[selected_trigger][4]:
			if i[2]==0.0: repeat=''
			else: repeat=str(i[2])
			time_units=self.actions.time_units[i[3]]
			repeat2=repeat+' '+time_units
			self.list_actions.Append([self.actions.options[self.actions.getOptionsListIndex(i[0])][0].decode('utf8'),i[1].decode('utf8'),repeat2.decode('utf8')])
	
	def edit_triggers(self,e):
		t=e.GetIndex()
		trigger=self.triggers[t][1]
		operator=self.triggers[t][2]
		value=self.triggers[t][3]
		edit=[t,trigger,operator,value]
		self.edit_add_trigger(edit)

	def add_trigger(self,e):
		self.edit_add_trigger(0)

	def edit_add_trigger(self,edit):
		self.datastream_list=[]
		self.a=DataStream(self.conf)
		for i in self.a.DataList:
			self.datastream_list.append(i[1]+': '+i[0])
		dlg = addTrigger(self.datastream_list, self.a,edit)
		res = dlg.ShowModal()
		if res == wx.ID_OK:
			trigger_selection=dlg.trigger_select.GetCurrentSelection()
			if trigger_selection==len(self.datastream_list):
				if edit==0:
					self.list_triggers.Append([_('None (always true)'),'',''])
					tmp=[]
					tmp.append(1)
					tmp.append(-1)
					tmp.append(-1)
					tmp.append(-1)
					tmp.append([])
					self.triggers.append(tmp)
					total=self.list_triggers.GetItemCount()
					for x in xrange(0, total, 1):
						self.list_triggers.Select(x, on=0)
					self.list_triggers.Select(total-1, on=1)
					self.list_triggers.CheckItem(total-1)
				else:
					self.list_triggers.SetStringItem(edit[0],0,_('None (always true)'))
					self.list_triggers.SetStringItem(edit[0],1,'')
					self.list_triggers.SetStringItem(edit[0],2,'')
					self.triggers[edit[0]][1]=-1
					self.triggers[edit[0]][2]=-1
					self.triggers[edit[0]][3]=-1
			else:
				if trigger_selection == -1 or dlg.operator_select.GetCurrentSelection() == -1:
					self.ShowMessage(_('Failed. Select trigger and operator.'))
					dlg.Destroy()
					return
				trigger0=self.a.DataList[trigger_selection]
				operator_selection=trigger0[7][dlg.operator_select.GetCurrentSelection()]
				if dlg.value.GetValue(): value=dlg.value.GetValue()
				else: value=0
				value2=str(value)
				operator=self.a.operators_list[operator_selection]
				if edit==0:
					self.list_triggers.Append([trigger0[0].decode('utf8'),operator.decode('utf8'),value2.decode('utf8')])				
					tmp=[]
					tmp.append(1)
					tmp.append(trigger0[9])
					tmp.append(operator_selection)
					tmp.append(value2)
					tmp.append([])
					self.triggers.append(tmp)
					total=self.list_triggers.GetItemCount()
					for x in xrange(0, total, 1):
						self.list_triggers.Select(x, on=0)
					self.list_triggers.Select(total-1, on=1)
					self.list_triggers.CheckItem(total-1)
				else:
					self.list_triggers.SetStringItem(edit[0],0,trigger0[0].decode('utf8'))
					self.list_triggers.SetStringItem(edit[0],1,operator.decode('utf8'))
					self.list_triggers.SetStringItem(edit[0],2,value2.decode('utf8'))
					self.triggers[edit[0]][1]=trigger0[9]
					self.triggers[edit[0]][2]=operator_selection
					self.triggers[edit[0]][3]=value2					
			dlg.Destroy()
	
	def edit_actions(self,e):
		self.actions=Actions(self.conf)
		a=e.GetIndex()
		t= self.list_triggers.GetFirstSelected()
		action=self.actions.getOptionsListIndex(self.triggers[t][4][a][0])
		data=self.triggers[t][4][a][1]
		repeat=self.triggers[t][4][a][2]
		unit=self.triggers[t][4][a][3]
		edit=[a,action,data,repeat,unit]
		self.edit_add_action(edit)

	def add_action(self,e):
		self.edit_add_action(0)

	def edit_add_action(self,edit):
		self.actions=Actions(self.conf)
		selected_trigger_position= self.list_triggers.GetFirstSelected()
		if selected_trigger_position==-1:
			self.ShowMessage(_('Select a trigger to add actions.'))
			return
		dlg = addAction(self.conf,self.actions.options,self.actions.time_units,edit)
		res = dlg.ShowModal()
		if res == wx.ID_OK:
			action_selection=dlg.action_select.GetCurrentSelection()
			if action_selection == -1:
				self.ShowMessage(_('Failed. Select an action.'))
				dlg.Destroy()
				return
			if dlg.repeat.GetValue(): repeat=dlg.repeat.GetValue()
			else: repeat='0'
			try: repeat=float(repeat)
			except:
				self.ShowMessage(_('Failed. "Repeat after" must be a number.'))
				dlg.Destroy()
				return
			action=self.actions.options[action_selection][0]
			data0=dlg.data.GetValue()
			data=data0.encode('utf8')
			time_units_selection=dlg.repeat_unit.GetCurrentSelection()
			time_units=self.actions.time_units[time_units_selection]
			if repeat==0.0: repeat2=time_units
			else: repeat2=str(repeat)+' '+time_units
			if edit==0:
				self.list_actions.Append([action.decode('utf8'),data.decode('utf8'),repeat2.decode('utf8')])
				tmp=[]
				tmp.append(self.actions.options[action_selection][3])
				tmp.append(data)
				tmp.append(repeat)
				tmp.append(time_units_selection)
				self.triggers[selected_trigger_position][4].append(tmp)
			else:
				self.list_actions.SetStringItem(edit[0],0,action.decode('utf8'))
				self.list_actions.SetStringItem(edit[0],1,data.decode('utf8'))
				self.list_actions.SetStringItem(edit[0],2,repeat2.decode('utf8'))
				self.triggers[selected_trigger_position][4][edit[0]][0]=self.actions.options[action_selection][3]
				self.triggers[selected_trigger_position][4][edit[0]][1]=data
				self.triggers[selected_trigger_position][4][edit[0]][2]=repeat
				self.triggers[selected_trigger_position][4][edit[0]][3]=time_units_selection			
		dlg.Destroy()

	def delete_trigger(self,e):
		selected=self.list_triggers.GetFirstSelected()
		if selected==-1: 
			self.ShowMessage(_('Select a trigger to delete.'))
		else:
			del self.triggers[selected]
			self.list_triggers.DeleteItem(selected)
			self.list_actions.DeleteAllItems()

	def delete_action(self,e):
		selected_trigger=self.list_triggers.GetFirstSelected()
		selected_action=self.list_actions.GetFirstSelected()
		if selected_action==-1: 
			self.ShowMessage(_('Select an action to delete.'))
		else: 
			del self.triggers[selected_trigger][4][selected_action]
			self.list_actions.DeleteItem(selected_action)

	def apply_changes_actions(self,e):
		i=0
		for ii in self.triggers:
			if self.list_triggers.IsChecked(i): self.triggers[i][0]=1
			else: self.triggers[i][0]=0
			i=i+1
		self.conf.set('ACTIONS', 'triggers', str(self.triggers))
		self.start_monitoring()
		self.SetStatusText(_('Actions changes applied and restarted'))

	def cancel_changes_actions(self,e):
		self.read_triggers()
		self.SetStatusText(_('Actions changes cancelled'))

	def stop_actions(self,e):
		subprocess.call(['python', currentpath+'/ctrl_actions.py', '0'])
		self.SetStatusText(_('Actions stopped'))
		self.conf.read()
		self.read_triggers()
		self.list_actions.DeleteAllItems()

	def start_actions(self,e):
		subprocess.call(['python', currentpath+'/ctrl_actions.py', '1'])
		self.SetStatusText(_('Actions started'))
		self.conf.read()
		self.read_triggers()
		self.list_actions.DeleteAllItems()

####################### 1W sensors

	def start_1w(self):
		subprocess.call(['pkill', '-f', '1w.py'])
		subprocess.Popen(['python',currentpath+'/1w.py'])

	def read_DS18B20(self):
		self.DS18B20=[]
		self.list_DS18B20.DeleteAllItems()
		data=self.conf.get('1W', 'DS18B20')
		try:
			temp_list=eval(data)
		except:temp_list=[]
		for ii in temp_list:
			self.DS18B20.append(ii)
			self.list_DS18B20.Append([ii[0].decode('utf8'),ii[1].decode('utf8'),ii[2],ii[3]])
			if ii[5]=='1':
				last=self.list_DS18B20.GetItemCount()-1
				self.list_DS18B20.CheckItem(last)
	
	def edit_DS18B20(self,e):
		selected_DS18B20=e.GetIndex()
		edit=[selected_DS18B20,self.DS18B20[selected_DS18B20][0],self.DS18B20[selected_DS18B20][1],self.DS18B20[selected_DS18B20][2],self.DS18B20[selected_DS18B20][3]]
		self.edit_add_DS18B20(edit)

	def add_DS18B20(self,e):
		self.edit_add_DS18B20(0)

	def edit_add_DS18B20(self,edit):
		dlg = addDS18B20(edit)
		res = dlg.ShowModal()
		if res == wx.ID_OK:
			name=dlg.name.GetValue()
			name=name.encode('utf8')
			short=dlg.short.GetValue()
			short=short.encode('utf8')
			unit_selection=dlg.unit_select.GetValue()
			id_selection=dlg.id_select.GetValue()
			id_selection=id_selection.encode('utf8')
			if not name or not short:
				self.ShowMessage(_('Failed. Write a name and a short name.'))
				dlg.Destroy()
				return				
			if unit_selection == '':
				self.ShowMessage(_('Failed. Select unit.'))
				dlg.Destroy()
				return
			if id_selection == '':
				self.ShowMessage(_('Failed. Select sensor ID.'))
				dlg.Destroy()
				return
			short_exist=self.check_short_names(short,edit,'1w')
			if short_exist:
				self.ShowMessage(_('Failed. This short name is already used.'))
				dlg.Destroy()
				return	
			if unit_selection=='Celsius': unit_selection='C'
			if unit_selection=='Fahrenheit': unit_selection='F'
			if unit_selection=='Kelvin': unit_selection='K'
			if edit==0:
				self.list_DS18B20.Append([name.decode('utf8'),short.decode('utf8'),unit_selection,id_selection])
				last=self.list_DS18B20.GetItemCount()-1
				self.list_DS18B20.CheckItem(last)
				if len(self.DS18B20)==0: ID='1W0'
				else:
					last=len(self.DS18B20)-1
					x=int(self.DS18B20[last][4][2:])
					ID='1W'+str(x+1)
				self.DS18B20.append([name,short,unit_selection,id_selection,ID,'1'])
			else:
				self.list_DS18B20.SetStringItem(edit[0],0,name.decode('utf8'))
				self.list_DS18B20.SetStringItem(edit[0],1,short.decode('utf8'))
				self.list_DS18B20.SetStringItem(edit[0],2,unit_selection)
				self.list_DS18B20.SetStringItem(edit[0],3,id_selection)
				self.DS18B20[edit[0]][0]=name
				self.DS18B20[edit[0]][1]=short
				self.DS18B20[edit[0]][2]=unit_selection
				self.DS18B20[edit[0]][3]=id_selection
		dlg.Destroy()

	def delete_DS18B20(self,e):
		selected_DS18B20=self.list_DS18B20.GetFirstSelected()
		if selected_DS18B20==-1: 
			self.ShowMessage(_('Select a sensor to delete.'))
			return
		data=self.conf.get('ACTIONS', 'triggers')
		try:
			temp_list=eval(data)
		except:temp_list=[]
		for i in temp_list:
			if i[1]==self.DS18B20[selected_DS18B20][4]:
				self.read_triggers()
				self.ShowMessage(_('You have a trigger defined for this sensor. You must delete that action before deleting this sensor.'))
				return
		del self.DS18B20[selected_DS18B20]
		self.list_DS18B20.DeleteItem(selected_DS18B20)

	def apply_changes_DS18B20(self,e):
		for i in self.DS18B20:
			index=self.DS18B20.index(i)
			if self.list_DS18B20.IsChecked(index): self.DS18B20[index][5]='1'
			else: self.DS18B20[index][5]='0'
		self.conf.set('1W', 'DS18B20', str(self.DS18B20))
		self.start_1w()
		self.start_monitoring()
		self.SetStatusText(_('DS18B20 sensors changes applied and restarted'))

	def cancel_changes_DS18B20(self,e):
		self.read_DS18B20()
		self.SetStatusText(_('DS18B20 sensors changes cancelled'))

####################### USB manager

	def start_udev(self):
		subprocess.call(['sudo','udevadm','control','--reload-rules'])
		subprocess.call(['sudo','udevadm','trigger'])

	def read_USBinst(self):
		self.USBinst=[]
		self.list_USBinst.DeleteAllItems()
		data=self.conf.get('UDEV', 'USBinst')
		sentence=0
		try:
			temp_list=eval(data)
		except:temp_list=[]
		for ii in temp_list:
			self.USBinst.append(ii)
			self.list_USBinst.Append([ii[0].decode('utf8'),ii[1].decode('utf8'),ii[2].decode('utf8'),ii[4].decode('utf8'),ii[3].decode('utf8'),ii[5]])
			sentence=1
		try:		
			filesize=os.stat('/etc/udev/rules.d/10-openplotter.rules').st_size
		except: filesize=0		
			
		if sentence==0 and filesize>10:
			self.apply_changes_USBinst()
		if sentence==1 and filesize<10:
			self.apply_changes_USBinst()

	def add_USBinst(self,e):
		dlg = addUSBinst()
		res = dlg.ShowModal()
		if res == wx.ID_OK:
			OPname_selection=dlg.OPname_select.GetValue()
			if not re.match('^[0-9a-zA-Z]{1,8}$', OPname_selection):
				self.ShowMessage(_('Failed. The new name must be a string between 1 and 8 letters and/or numbers.'))
				dlg.Destroy()
				return
			OPname_selection='ttyOP_'+OPname_selection
			OPname_selection=OPname_selection.encode('utf8')
			vendor=dlg.vendor
			vendor=vendor.encode('utf8')	
			product=dlg.product
			product=product.encode('utf8')
			serial=dlg.serial
			serial=serial.encode('utf8')
			con_port=dlg.con_port
			con_port=con_port.encode('utf8')
			rem=dlg.rem
			self.list_USBinst.Append([OPname_selection.decode('utf8'),vendor.decode('utf8'),product.decode('utf8'),con_port.decode('utf8'),serial.decode('utf8'),rem])
			self.USBinst.append([OPname_selection,vendor,product,serial,con_port,rem])
			self.apply_changes_USBinst()
		dlg.Destroy()

	def delete_USBinst(self,e):
		selected_USBinst=self.list_USBinst.GetFirstSelected()
		if selected_USBinst==-1: 
			self.ShowMessage(_('Select a device to delete.'))
			return
		del self.USBinst[selected_USBinst]
		self.list_USBinst.DeleteItem(selected_USBinst)
		self.apply_changes_USBinst()

	def apply_changes_USBinst(self):
		self.conf.set('UDEV', 'USBinst', str(self.USBinst))
		file = open('10-openplotter.rules', 'w')
		for i in self.USBinst:
			index=self.USBinst.index(i)
			if self.USBinst[index][5]=='port':
				write_str='KERNEL=="ttyUSB*", KERNELS=="'+self.USBinst[index][4]
				write_str=write_str+'" ,SYMLINK+="'+self.USBinst[index][0]+'"\n'
			else:
				if self.USBinst[index][3] == '':
					write_str='SUBSYSTEM=="tty", ATTRS{idVendor}=="'+self.USBinst[index][1]
					write_str=write_str+'",ATTRS{idProduct}=="'+self.USBinst[index][2]
					write_str=write_str+'" ,SYMLINK+="'+self.USBinst[index][0]+'"\n'
				else:	
					write_str='SUBSYSTEM=="tty", ATTRS{idVendor}=="'+self.USBinst[index][1]
					write_str=write_str+'",ATTRS{idProduct}=="'+self.USBinst[index][2]
					write_str=write_str+'",ATTRS{serial}=="'+self.USBinst[index][3]
					write_str=write_str+'" ,SYMLINK+="'+self.USBinst[index][0]+'"\n'
					
			file.write(write_str)
		file.close()
		os.system('sudo mv 10-openplotter.rules /etc/udev/rules.d')
		self.SetStatusText(_('Restarting'))
		self.start_udev()
		time.sleep(1.5)
		self.SetStatusText(_('USB names added and restarted'))
		self.SerialCheck()

###################################### Signal K

	def signalKout(self, e):
		url = 'http://localhost:3000/examples/consumer-example.html'
		webbrowser.open(url,new=2)

	def restartSK(self, e):
		self.SetStatusText(_('Closing Signal K server'))
		subprocess.call(["pkill", '-9', "node"])
		isChecked = self.signalk_enable.GetValue()
		if isChecked:
			subprocess.Popen(home+'/.config/signalk-server-node/bin/openplotter', cwd=home+'/.config/signalk-server-node')
			self.SetStatusText(_('Signal K server restarted'))
	def N2K_setting(self, e):
		if len(self.conf.get('SIGNALK', 'can_usb'))>5:
			self.SetStatusText(_('Closing Signal K server'))
			subprocess.call(["pkill", '-9', "node"])
			subprocess.Popen(['python',currentpath+'/CAN-USB-stick.py'])
			self.SetStatusText(_('you have to restart SignalK server'))		
	
	def SerialCheck(self):
		self.SerDevLs = [_('none')]
		self.context = pyudev.Context()
		for device in self.context.list_devices(subsystem='tty'):
			i=device['DEVNAME']
			if '/dev/ttyU' in i or '/dev/ttyA' in i or '/dev/ttyS' in i or '/dev/ttyO' in i or '/dev/r' in i or '/dev/i' in i:
				self.SerDevLs.append(i)
				try:
					ii=device['DEVLINKS']
					value= ii[ii.rfind('/dev/ttyOP_'):]			
					if value.find('/dev/ttyOP_') >=0:
						self.SerDevLs.append(value)
				except Exception,e: print str(e)
		self.can_usb.Clear()
		self.sms_dev.Clear()
		self.can_usb.AppendItems(self.SerDevLs)
		self.sms_dev.AppendItems(self.SerDevLs)

	def SerialWrongPort(self):
		try:
			self.context		
		except NameError:
			self.context = pyudev.Context()

		data=self.conf.get('UDEV', 'USBinst')
		try:
			temp_list=eval(data)
		except:temp_list=[]
		for ic in temp_list:
			if ic[5] == 'port':	
				for device in self.context.list_devices(subsystem='usb'):
					dp = ""
					imi= ""
					ivi= ""
					imfd=""
					ivfd=""
					if 'DEVPATH' in device: dp=device['DEVPATH']
					if dp.find(ic[4])>0:					
						if 'PRODUCT' in device:
							pr=device['PRODUCT']
							s = pr.split('/')
							imi = s[1].zfill(4)
							ivi = s[0].zfill(4)								
						if imi==ic[2] and ivi==ic[1]: pass
						else:
							if 'ID_MODEL_FROM_DATABASE' in device:	imfd=device['ID_MODEL_FROM_DATABASE']
							if 'ID_VENDOR_FROM_DATABASE' in device:	ivfd=device['ID_VENDOR_FROM_DATABASE']
							self.ShowMessage(_('Warning: You have connected the "')+ivfd+', '+imfd+_('" to the USB port which is reserved for another device'))		

	def onsignalk_enable (self,e):
		isChecked = self.signalk_enable.GetValue()
		if isChecked:
			name=self.vessel.GetValue()
			uuid=self.mmsi.GetValue()
			if name=='' or uuid=='':
				self.ShowMessage(_('You have to provide name and MMSI.'))
				self.signalk_enable.SetValue(False)
				return				
			self.vessel.Disable()
			self.vessel_label.Disable()
			self.mmsi.Disable()
			self.mmsi_label.Disable()
			self.NMEA2000_label.Disable()
			self.can_usb.Disable()
			self.CANUSB_label.Disable()
			subprocess.call(["pkill", '-9', "node"])
			with open(home+'/.config/signalk-server-node/settings/openplotter-settings.json') as data_file:
				data = json.load(data_file)
			data['vessel']['name']=name
			data['vessel']['uuid']=uuid
			if self.can_usb.GetValue()==_('none'): 
				self.conf.set('SIGNALK', 'can_usb', '0')
				ii=0
				for i in data['pipedProviders']:
					if i['id']=='CAN-USB':
						#delete nmea 2000
						del data['pipedProviders'][ii]
					ii=ii+1
				text='NMEA 0183 - system_output - TCP localhost 10110'
				self.SKinputs_label.SetLabel(text)
			else:
				self.conf.set('SIGNALK', 'can_usb', self.can_usb.GetValue())
				exist=0
				ii=0
				for i in data['pipedProviders']:
					if i['id']=='CAN-USB':
						#edit nmea 2000
						data['pipedProviders'][ii]['pipeElements'][0]['options']['command']='actisense-serial '+self.can_usb.GetValue()
						exist=1
					ii=ii+1
				text='NMEA 0183 - system_output - TCP localhost 10110'
				text=text+'\nNMEA 2000 - CAN-USB - '+self.conf.get('SIGNALK', 'can_usb')
				self.SKinputs_label.SetLabel(text)
				if exist==0:
					new={"id":"CAN-USB","pipeElements":[{"type":"providers/execute","options":{"command":"actisense-serial xxx"}},{"type":"providers/liner"},{"type":"providers/n2kAnalyzer"},{"type":"providers/n2k-signalk"}]}
					new['pipeElements'][0]['options']['command']='actisense-serial '+self.can_usb.GetValue()
					data['pipedProviders'].append(new)
					text='NMEA 0183 - system_output - TCP localhost 10110'
					text=text+'\nNMEA 2000 - CAN-USB - '+self.conf.get('SIGNALK', 'can_usb')
					self.SKinputs_label.SetLabel(text)
			with open(home+'/.config/signalk-server-node/settings/openplotter-settings.json', 'w') as outfile:
				json.dump(data, outfile)
			self.conf.set('SIGNALK', 'enable', '1')
			subprocess.Popen(home+'/.config/signalk-server-node/bin/openplotter', cwd=home+'/.config/signalk-server-node')
		else:
			subprocess.call(["pkill", '-9', "node"])
			self.conf.set('SIGNALK', 'enable', '0')
			self.vessel.Enable()
			self.vessel_label.Enable()
			self.mmsi.Enable()
			self.mmsi_label.Enable()
			self.NMEA2000_label.Enable()
			self.can_usb.Enable()
			self.CANUSB_label.Enable()

####################### SMS

	def save_gammu_settings(self,port,con):
		gammu_conf = ConfigParser.SafeConfigParser()
		gammu_conf.read(home+'/.gammurc')
		gammu_conf.set('gammu', 'port', port)
		gammu_conf.set('gammu', 'connection', con)
		with open(home+'/.gammurc', 'wb') as configfile:
			gammu_conf.write(configfile)

	def onsms_enable(self,e):
		isChecked = self.sms_enable.GetValue()
		if isChecked:
			if self.sms_dev.GetValue()==_('none'):
				if self.sms_bt.GetValue()=='':
					self.ShowMessage(_('You have to provide a serial port or a bluetooth address.'))
					self.sms_enable.SetValue(False)
					return
				else:
					bluetooth=self.sms_bt.GetValue()
			else:
				bluetooth = ''
				self.sms_bt.SetValue(bluetooth)
				serial = self.sms_dev.GetValue()
			if self.sms_con.GetValue()=='':
				self.ShowMessage(_('You have to provide a connection type.'))
				self.sms_enable.SetValue(False)
				return
			else: connection = self.sms_con.GetValue()
			self.conf.set('SMS', 'enable', '1')
			if self.sms_dev.GetValue()==_('none'):
				self.conf.set('SMS', 'serial', '0')
				port=bluetooth
			else:
				self.conf.set('SMS', 'serial', serial)
				port=serial
			self.conf.set('SMS', 'bluetooth', bluetooth)
			self.conf.set('SMS', 'connection', connection)
			self.sms_dev_label.Disable()
			self.sms_dev.Disable()
			self.sms_bt_label.Disable()
			self.sms_bt.Disable()
			self.sms_con_label.Disable()
			self.sms_con.Disable()
			self.button_sms_identify.Enable()
			self.save_gammu_settings(port,connection)
		else:
			self.conf.set('SMS', 'enable', '0')
			self.sms_dev_label.Enable()
			self.sms_dev.Enable()
			self.sms_bt_label.Enable()
			self.sms_bt.Enable()
			self.sms_con_label.Enable()
			self.sms_con.Enable()
			self.button_sms_identify.Disable()
			self.save_gammu_settings('','')
			self.sms_enable_send.SetValue(False)
			self.onsms_enable_send(0)

	def onsms_enable_send(self,e):
		isChecked = self.sms_enable_send.GetValue()
		if isChecked:
			if not self.sms_enable.GetValue():
				self.ShowMessage(_('You have to enable settings.'))
				self.sms_enable_send.SetValue(False)
				return
			if self.phone_number.GetValue()=='':
				self.ShowMessage(_('You have to provide a phone number.'))
				self.sms_enable_send.SetValue(False)
				return
			self.conf.set('SMS', 'enable_sending', '1')
			self.conf.set('SMS', 'phone', self.phone_number.GetValue())
			self.phone_number_label.Disable()
			self.phone_number.Disable()
			self.sms_text_label.Enable()
			self.sms_text.Enable()
			self.button_sms_test.Enable()
		else:
			self.conf.set('SMS', 'enable_sending', '0')
			self.phone_number_label.Enable()
			self.phone_number.Enable()
			self.sms_text_label.Disable()
			self.sms_text.Disable()
			self.button_sms_test.Disable()

	def sms_identify(self,e):
		subprocess.call(['pkill', '-f', 'test_sms.py'])
		subprocess.Popen(['python',currentpath+'/test_sms.py', 'i', '0', '0'])

	def sms_test(self,e):
		text=self.sms_text.GetValue()
		if text=='':
			self.ShowMessage(_('You have to provide some text to send.'))
			return
		subprocess.call(['pkill', '-f', 'test_sms.py'])
		subprocess.Popen(['python',currentpath+'/test_sms.py', 't', text, self.phone_number.GetValue()])

####################### MQTT

	def read_mqtt(self):
		if self.conf.get('MQTT', 'broker'): self.mqtt_broker.SetValue(self.conf.get('MQTT', 'broker'))
		if self.conf.get('MQTT', 'port'): self.mqtt_port.SetValue(self.conf.get('MQTT', 'port'))
		if self.conf.get('MQTT', 'username'): self.mqtt_user.SetValue(self.conf.get('MQTT', 'username'))
		if self.conf.get('MQTT', 'password'): self.mqtt_pass.SetValue('***************')

		self.topics=[]
		self.list_topics.DeleteAllItems()
		data=self.conf.get('MQTT', 'topics')
		try:
			temp_list=eval(data)
		except:temp_list=[]
		for ii in temp_list:
			self.topics.append(ii)
			self.list_topics.Append([ii[0].decode('utf8'),ii[1].decode('utf8')])

	def edit_topic(self,e):
		selected_topic=e.GetIndex()
		edit=[selected_topic,self.topics[selected_topic][0],self.topics[selected_topic][1]]
		self.edit_add_topic(edit)

	def add_topic(self,e):
		self.edit_add_topic(0)

	def edit_add_topic(self,edit):
		dlg = addTopic(edit)
		res = dlg.ShowModal()
		if res == wx.ID_OK:
			short=dlg.short.GetValue()
			short=short.encode('utf8')
			topic=dlg.topic.GetValue()
			topic=topic.encode('utf8')
			if not topic or not short:
				self.ShowMessage(_('Failed. Write a topic and a short name.'))
				dlg.Destroy()
				return
			short_exist=self.check_short_names(short,edit,'topics')
			if short_exist:
				self.ShowMessage(_('Failed. This short name is already used.'))
				dlg.Destroy()
				return				
			if edit==0:
				self.list_topics.Append([short.decode('utf8'),topic.decode('utf8')])
				if len(self.topics)==0: ID='MQTT0'
				else:
					last=len(self.topics)-1
					x=int(self.topics[last][2][4:])
					ID='MQTT'+str(x+1)
				self.topics.append([short,topic,ID])
			else:
				self.list_topics.SetStringItem(edit[0],0,short.decode('utf8'))
				self.list_topics.SetStringItem(edit[0],1,topic.decode('utf8'))
				self.topics[edit[0]][0]=short
				self.topics[edit[0]][1]=topic
		dlg.Destroy()

	def delete_topic(self,e):
		selected_topic=self.list_topics.GetFirstSelected()
		if selected_topic==-1: 
			self.ShowMessage(_('Select a topic to delete.'))
			return
		data=self.conf.get('ACTIONS', 'triggers')
		try:
			temp_list=eval(data)
		except:temp_list=[]
		for i in temp_list:
			if i[1]==self.topics[selected_topic][2]:
				self.read_triggers()
				self.ShowMessage(_('You have a trigger defined for this topic. You must delete that action before deleting this topic.'))
				return
		del self.topics[selected_topic]
		self.list_topics.DeleteItem(selected_topic)

	def apply_changes_mqtt(self,e):
		username=self.mqtt_user.GetValue()
		passw=self.mqtt_pass.GetValue()
		if not username or not passw:
			self.ShowMessage(_('Enter at least username and password.'))
			return
		self.conf.set('MQTT', 'broker', self.mqtt_broker.GetValue())
		self.conf.set('MQTT', 'port', self.mqtt_port.GetValue())
		self.conf.set('MQTT', 'username', username)
		self.conf.set('MQTT', 'topics', str(self.topics))
		if not '*******' in passw:
			self.mqtt_pass.SetValue('***************')
			self.conf.set('MQTT', 'password', passw)
		else: passw=self.conf.get('MQTT', 'password')
		subprocess.call(['sudo', 'sh', '-c', 'echo "'+username+':'+passw+'" > /etc/mosquitto/passwd.pw'])
		subprocess.call(['sudo','mosquitto_passwd','-U','/etc/mosquitto/passwd.pw'])
		subprocess.call(['sudo','service','mosquitto','restart'])
		self.start_monitoring()
		self.SetStatusText(_('MQTT topics changes applied and restarted'))

	def cancel_changes_mqtt(self,e):
		self.read_mqtt()
		self.SetStatusText(_('MQTT topics changes cancelled'))

############################## Main

if __name__ == "__main__":
	app = wx.App()

	bitmap = wx.Bitmap(home+'/.config/openplotter/openplotter.ico', wx.BITMAP_TYPE_ICO)
	splash = wx.SplashScreen(bitmap, wx.SPLASH_CENTRE_ON_SCREEN|wx.SPLASH_TIMEOUT, 500, None, style=wx.SIMPLE_BORDER|wx.STAY_ON_TOP)
	wx.Yield()

	MainFrame().Show()
	app.MainLoop()
