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

import wx, os, sys, subprocess, ConfigParser, webbrowser, time

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
			self.op_folder = self.conf.get('GENERAL', 'op_folder')
			self.help_bmp = wx.Bitmap(self.op_folder + "/static/icons/help-browser.png", wx.BITMAP_TYPE_ANY)
			Language(self.conf)
			self.SK_settings = SK_settings(self.conf)
			self.opencpnSettings = opencpnSettings()

			wx.Frame.__init__(self, None, title=_('SDR receiver'), size=(710,380))
			
			self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
			
			self.icon = wx.Icon(self.op_folder+'/static/icons/sdr.ico', wx.BITMAP_TYPE_ICO)
			self.SetIcon(self.icon)

			calibrationbox = wx.StaticBox(self, label=_(' Calibration '))

			self.button_test_gain = wx.Button(self, label=_('Initial PPM'))
			self.Bind(wx.EVT_BUTTON, self.test_gain, self.button_test_gain)

			bands_label = wx.StaticText(self, label=_('Band'))
			bands_list = ['GSM850', 'GSM-R', 'GSM900', 'EGSM', 'DCS', 'PCS']
			self.band = wx.ComboBox(self, choices = bands_list, style = wx.CB_READONLY)
			self.check_bands = wx.Button(self, label =_('Get channel'))
			self.Bind(wx.EVT_BUTTON, self.check_band, self.check_bands)
			channel_label = wx.StaticText(self, label =_('Channel'))
			self.channel = wx.TextCtrl(self)
			self.check_channels = wx.Button(self, label=_('Get PPM'))
			self.Bind(wx.EVT_BUTTON, self.check_channel, self.check_channels)

			correction_label = wx.StaticText(self, label=_('PPM'))
			self.ppm = wx.TextCtrl(self)

			self.button_saveppm = wx.Button(self, label=_('Save PPM'))
			self.Bind(wx.EVT_BUTTON, self.on_saveppm, self.button_saveppm)

			aisbox = wx.StaticBox(self, label=' AIS ')

			self.ais_sdr_enable = wx.CheckBox(self, label=_('Enable'))
			self.ais_sdr_enable.Bind(wx.EVT_CHECKBOX, self.OnOffAIS)

			self.button_checkppm = wx.Button(self, label=_('Check AIS frequency'))
			self.Bind(wx.EVT_BUTTON, self.on_checkppm, self.button_checkppm)

			radiobox = wx.StaticBox(self, label =_(' Radio '))
			self.button_radio_default = wx.Button(self, label = _('Load defaults'))
			self.Bind(wx.EVT_BUTTON, self.on_radio_default, self.button_radio_default)

			self.button_radio_16 = wx.Button(self, label = _('Channel 16'))
			self.Bind(wx.EVT_BUTTON, self.on_radio_16, self.button_radio_16)

			self.button_radio_9 = wx.Button(self, label = _('Channel 9'))
			self.Bind(wx.EVT_BUTTON, self.on_radio_9, self.button_radio_9)

			self.frequency = wx.SpinCtrl(self, min=24000000, max=1766000000, initial=156800000)
			self.button_radio_freq = wx.Button(self, label = _('Frequency'))
			self.Bind(wx.EVT_BUTTON, self.on_radio_freq, self.button_radio_freq)

			help_button = wx.BitmapButton(self, bitmap=self.help_bmp, size=(self.help_bmp.GetWidth()+40, self.help_bmp.GetHeight()+10))
			help_button.Bind(wx.EVT_BUTTON, self.on_help_sdr)

			self.CreateStatusBar()
			self.Centre()
			self.Show(True)

			ppm = self.conf.get('AIS-SDR', 'ppm')
			if not ppm: self.ppm.SetValue('0')
			else: self.ppm.SetValue(ppm)
			self.band.SetValue(self.conf.get('AIS-SDR', 'band'))
			self.channel.SetValue(self.conf.get('AIS-SDR', 'gsm_channel'))
			if self.conf.get('AIS-SDR', 'enable') == '1': 
				self.ais_sdr_enable.SetValue(True)
				self.disable_sdr_controls()

			h_calibration1 = wx.BoxSizer(wx.HORIZONTAL)
			h_calibration1.AddSpacer(10)
			h_calibration1.Add(self.button_test_gain, 0, wx.RIGHT, 15)
			h_calibration1.Add(bands_label, 0, wx.TOP, 6)
			h_calibration1.Add(self.band, 0, wx.LEFT | wx.RIGHT, 5)
			h_calibration1.Add(self.check_bands, 0, wx.LEFT | wx.RIGHT, 5)
			h_calibration1.AddSpacer(10)
			h_calibration1.Add(channel_label, 0, wx.TOP, 6)
			h_calibration1.Add(self.channel, 0, wx.LEFT | wx.RIGHT, 5)
			h_calibration1.Add(self.check_channels, 0, wx.LEFT | wx.RIGHT, 5)

			h_calibration2 = wx.BoxSizer(wx.HORIZONTAL)
			h_calibration2.Add(correction_label, 0, wx.TOP, 6)
			h_calibration2.Add(self.ppm, 0, wx.LEFT | wx.RIGHT, 5)
			h_calibration2.Add(self.button_saveppm, 0, wx.LEFT | wx.RIGHT, 5)
			
			v_calibrationbox = wx.StaticBoxSizer(calibrationbox, wx.VERTICAL)
			v_calibrationbox.Add(h_calibration1, 0, wx.UP | wx.BOTTOM, 10)
			v_calibrationbox.Add(h_calibration2, 0, wx.LEFT| wx.BOTTOM, 10)

			h_aisbox = wx.StaticBoxSizer(aisbox, wx.HORIZONTAL)
			h_aisbox.Add(self.ais_sdr_enable, 0, wx.ALL, 10)
			h_aisbox.Add(self.button_checkppm, 0, wx.ALL, 10)

			h_radiobox = wx.StaticBoxSizer(radiobox, wx.HORIZONTAL)
			h_radiobox.Add(self.button_radio_default, 0, wx.ALL, 10)
			h_radiobox.Add(self.button_radio_9, 0, wx.ALL, 10)
			h_radiobox.Add(self.button_radio_16, 0, wx.ALL, 10)
			h_radiobox.AddSpacer(10)
			h_radiobox.Add(self.frequency, 0, wx.UP, 10)
			h_radiobox.AddSpacer(5)
			h_radiobox.Add(self.button_radio_freq, 0, wx.UP, 10)

			vbox = wx.BoxSizer(wx.VERTICAL)
			vbox.AddSpacer(5)
			vbox.Add(v_calibrationbox, 0, wx.ALL | wx.EXPAND, 5)
			vbox.Add(h_aisbox, 0, wx.ALL | wx.EXPAND, 5)
			vbox.Add(h_radiobox, 0, wx.ALL | wx.EXPAND, 5)
			vbox.AddStretchSpacer(1)
			vbox.Add(help_button, 0, wx.LEFT | wx.BOTTOM, 10)

			self.SetSizer(vbox)

		def kill_sdr(self):
			subprocess.call(['pkill', '-15', 'rtl_ais'])
			subprocess.call(['pkill', '-f', 'SDR_AIS_fine_cal.py'])
			subprocess.call(['pkill', '-15', 'rtl_test'])
			subprocess.call(['pkill', '-15', 'kal'])
			subprocess.call(['pkill', '-15', 'gqrx'])

		def enable_sdr_controls(self):
			self.ppm.Enable()
			self.button_test_gain.Enable()
			self.button_saveppm.Enable()
			self.button_checkppm.Enable()
			self.band.Enable()
			self.channel.Enable()
			self.check_bands.Enable()
			self.check_channels.Enable()
			self.button_radio_default.Enable()
			self.button_radio_9.Enable()
			self.button_radio_16.Enable()
			self.button_radio_freq.Enable()
			self.frequency.Enable()

		def disable_sdr_controls(self):
			self.ppm.Disable()
			self.button_test_gain.Disable()
			self.button_saveppm.Disable()
			self.button_checkppm.Disable()
			self.band.Disable()
			self.channel.Disable()
			self.check_bands.Disable()
			self.check_channels.Disable()
			self.button_radio_default.Disable()
			self.button_radio_9.Disable()
			self.button_radio_16.Disable()
			self.button_radio_freq.Disable()
			self.frequency.Disable()


		def OnOffAIS(self, e):
			self.kill_sdr()
			isChecked = self.ais_sdr_enable.GetValue()
			if isChecked:
				self.disable_sdr_controls()
				ppm = self.ppm.GetValue()
				try: int(ppm)
				except:
					self.ShowStatusBarRED(_('Failed. Wrong PPM'))
					return
				subprocess.Popen(['rtl_ais', '-R', '-p', ppm])    
				self.conf.set('AIS-SDR', 'enable', '1')
				self.on_saveppm(0)
				msg = _('SDR-AIS reception enabled')
				opencpn = self.opencpnSettings.getConnectionState()
				if not opencpn: 
					msg = _('Failed. The default OpenCPN connection is missing: input TCP localhost:10110')
				elif opencpn == 'disabled': 
					msg = _('Failed. The default OpenCPN connection is disabled: input TCP localhost:10110')
			else:
				self.enable_sdr_controls()
				self.conf.set('AIS-SDR', 'enable', '0')
				msg = _('SDR-AIS reception disabled')

			if self.SK_settings.setSKsettings():
				seconds = 12
				subprocess.call(['sudo', 'systemctl', 'stop', 'signalk.service'])
				subprocess.call(['sudo', 'systemctl', 'stop', 'signalk.socket'])
				subprocess.call(['sudo', 'systemctl', 'start', 'signalk.socket'])
				subprocess.call(['sudo', 'systemctl', 'start', 'signalk.service'])
				for i in range(seconds, 0, -1):
					self.ShowStatusBarRED(_('Restarting Signal K server... ')+str(i))
					time.sleep(1)
			self.ShowStatusBarBLACK(msg)

		def test_gain(self,event):
			self.kill_sdr()
			subprocess.Popen(['lxterminal', '-e', 'rtl_test', '-p'])
			msg=_('Wait for "cumulative PPM" value to stabilize and copy it into "PPM" field')
			self.ShowStatusBarBLACK(msg)

		def check_band(self, event):
			self.kill_sdr()
			band=self.band.GetValue()
			self.on_saveppm(0)
			self.conf.set('AIS-SDR', 'band', band)
			subprocess.Popen(['python',self.op_folder+'/tools/SDR_AIS/SDR_AIS_fine_cal.py', 'b'])
			msg=_('Select the GSM band used in your country to get the strongest channel')
			self.ShowStatusBarBLACK(msg)
			
		def check_channel(self, event):
			self.kill_sdr()
			channel=self.channel.GetValue()
			try: int(channel)
			except:
				self.ShowStatusBarRED(_('Failed. Wrong channel'))
				return
			self.on_saveppm(0)
			self.conf.set('AIS-SDR', 'gsm_channel', channel)
			if channel: subprocess.Popen(['python',self.op_folder+'/tools/SDR_AIS/SDR_AIS_fine_cal.py', 'c'])
			msg=_('Use the strongest channel to calculate the final PPM')
			self.ShowStatusBarBLACK(msg)

		def on_radio_default(self, event):
			self.kill_sdr()
			subprocess.call(['cp', '-f', self.op_folder+'/tools/SDR_AIS/default.conf', self.home+'/.config/gqrx/'])
			self.open_gqrx()

		def on_radio_16(self, event):
			self.kill_sdr()
			self.setconf('156800000')
			self.open_gqrx()

		def on_radio_9(self, event):
			self.kill_sdr()
			self.setconf('156450000')
			self.open_gqrx()

		def on_radio_freq(self, event):
			self.kill_sdr()
			self.setconf(self.frequency.GetValue())
			self.open_gqrx()

		def on_checkppm(self, event):
			self.kill_sdr()
			self.on_saveppm(0)
			self.setconf('162025000')
			self.open_gqrx()

		def setconf(self,frequency):
			self.gqrx_conf = ConfigParser.SafeConfigParser()
			self.gqrx_conf.read(self.home+'/.config/gqrx/default.conf')
			try:
				self.gqrx_conf.set('General', 'crashed', 'false')
			except ConfigParser.NoSectionError:
				self.gqrx_conf.add_section('General')
				self.gqrx_conf.set('General', 'crashed', 'false')
			try:
				self.gqrx_conf.set('input', 'frequency', str(frequency))
			except ConfigParser.NoSectionError:
				self.gqrx_conf.add_section('input')
				self.gqrx_conf.set('input', 'frequency', str(frequency))
			try:
				self.gqrx_conf.set('receiver', 'demod', '3')
			except ConfigParser.NoSectionError:
				self.gqrx_conf.add_section('receiver')
				self.gqrx_conf.set('receiver', 'demod', '3')
			with open(self.home+'/.config/gqrx/default.conf', 'wb') as configfile:
				self.gqrx_conf.write(configfile)

		def on_saveppm(self,event):
			ppm = self.ppm.GetValue()
			try: ppm2 = int(ppm)*1000000
			except:
				self.ShowStatusBarRED(_('Failed. Wrong PPM'))
				return
			self.gqrx_conf = ConfigParser.SafeConfigParser()
			self.gqrx_conf.read(self.home+'/.config/gqrx/default.conf')
			try:
				self.gqrx_conf.set('input', 'corr_freq', str(ppm2))
			except ConfigParser.NoSectionError:
				self.gqrx_conf.add_section('input')
				self.gqrx_conf.set('input', 'corr_freq', str(ppm2))
			with open(self.home+'/.config/gqrx/default.conf', 'wb') as configfile:
				self.gqrx_conf.write(configfile)
			self.conf.set('AIS-SDR', 'ppm', ppm)
			self.ShowStatusBarGREEN(_('Saved PPM'))

		def open_gqrx(self):
			subprocess.Popen('gqrx')

		def on_help_sdr(self, e):
			url = self.op_folder+"/docs/html/tools/sdr_receiver.html"
			webbrowser.open(url, new=2)

		def ShowStatusBar(self, w_msg, colour):
			self.GetStatusBar().SetForegroundColour(colour)
			self.SetStatusText(w_msg)

		def ShowStatusBarRED(self, w_msg):
			self.ShowStatusBar(w_msg, wx.RED)

		def ShowStatusBarGREEN(self, w_msg):
			self.ShowStatusBar(w_msg, wx.GREEN)

		def ShowStatusBarBLACK(self, w_msg):
			self.ShowStatusBar(w_msg, wx.BLACK)	

app = wx.App()
MyFrame().Show()
app.MainLoop()
