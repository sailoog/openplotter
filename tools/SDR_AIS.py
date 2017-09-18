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

import wx, os, sys, subprocess

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

			wx.Frame.__init__(self, None, title=_('SDR receiver'), size=(690,370))
			
			self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
			
			self.icon = wx.Icon(self.currentpath+'/openplotter.ico', wx.BITMAP_TYPE_ICO)
			self.SetIcon(self.icon)

			wx.StaticBox(self, label='', size=(400, 170), pos=(10, 10))

			self.ais_sdr_enable = wx.CheckBox(self, label=_('Enable AIS reception'), pos=(20, 25))
			self.ais_sdr_enable.Bind(wx.EVT_CHECKBOX, self.OnOffAIS)

			self.gain = wx.TextCtrl(self, -1, size=(55, 32), pos=(150, 60))
			self.gain_label=wx.StaticText(self, label=_('Gain'), pos=(20, 65))
			self.ppm = wx.TextCtrl(self, -1, size=(55, 32), pos=(150, 95))
			self.correction_label=wx.StaticText(self, label=_('Correction (ppm)'), pos=(20, 100))

			self.ais_frequencies1 = wx.CheckBox(self, label=_('Channel A 161.975Mhz'), pos=(220, 60))
			self.ais_frequencies1.Bind(wx.EVT_CHECKBOX, self.ais_frequencies)
			self.ais_frequencies2 = wx.CheckBox(self, label=_('Channel B 162.025Mhz'), pos=(220, 95))
			self.ais_frequencies2.Bind(wx.EVT_CHECKBOX, self.ais_frequencies)

			#self.show_kplex6 =wx.Button(self, label=_('Inspector'), pos=(20, 140))
			#self.Bind(wx.EVT_BUTTON, self.show_kplex, self.show_kplex6)
			self.button_test_ppm =wx.Button(self, label=_('Take a look'), pos=(150, 140))
			self.Bind(wx.EVT_BUTTON, self.test_ppm, self.button_test_ppm)
			self.button_test_gain =wx.Button(self, label=_('Calibration'), pos=(275, 140))
			self.Bind(wx.EVT_BUTTON, self.test_gain, self.button_test_gain)

			wx.StaticBox(self, label=_(' Fine calibration using GSM '), size=(260, 170), pos=(420, 10))
			self.bands_label=wx.StaticText(self, label=_('Band'), pos=(430, 50))
			self.bands_list = ['GSM850', 'GSM-R', 'GSM900', 'EGSM', 'DCS', 'PCS']
			self.band= wx.ComboBox(self, choices=self.bands_list, style=wx.CB_READONLY, size=(100, 32), pos=(430, 70))
			self.band.SetValue('GSM900')
			self.check_bands =wx.Button(self, label=_('Check band'), pos=(540, 70))
			self.Bind(wx.EVT_BUTTON, self.check_band, self.check_bands)
			self.channel_label=wx.StaticText(self, label=_('Channel'), pos=(430, 125))
			self.channel = wx.TextCtrl(self, -1, size=(55, 32), pos=(430, 143))
			self.check_channels =wx.Button(self, label=_('Fine calibration'), pos=(495, 140))
			self.Bind(wx.EVT_BUTTON, self.check_channel, self.check_channels)

			wx.StaticBox(self, label=_(' Radio '), size=(260, 120), pos=(420, 185))

			self.button_vhf_Rx =wx.Button(self, label='Gqrx', pos=(430, 210))
			self.Bind(wx.EVT_BUTTON, self.vhf_Rx, self.button_vhf_Rx)

			self.CreateStatusBar()

			self.Centre()

			self.Show(True)

			output=subprocess.check_output('lsusb')
			supported_dev=['0bda:2832','0bda:2838','0ccd:00a9','0ccd:00b3','0ccd:00d3','0ccd:00d4','0ccd:00e0','185b:0620','185b:0650','1f4d:b803','1f4d:c803','1b80:d3a4','1d19:1101','1d19:1102','1d19:1103','0458:707f','1b80:d393','1b80:d394','1b80:d395','1b80:d39d']
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
				self.button_vhf_Rx.Disable()


		def kill_sdr(self):
			subprocess.call(['pkill', '-9', 'aisdecoder'])
			subprocess.call(['pkill', '-9', 'rtl_fm'])
			subprocess.call(['pkill', '-f', 'SDR_AIS_waterfall.py'])
			subprocess.call(['pkill', '-f', 'SDR_AIS_fine_cal.py'])
			subprocess.call(['pkill', '-9', 'rtl_test'])
			subprocess.call(['pkill', '-9', 'kal'])
			subprocess.call(['pkill', '-9', 'gqrx'])

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
				aisdecoder=subprocess.Popen(['aisdecoder', '-h', 'localhost', '-p', '10110', '-a', 'file', '-c', 'mono', '-d', '-f', '/dev/stdin'], stdin = rtl_fm.stdout)         
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
			w_open=subprocess.Popen(['python', self.currentpath+'/tools/SDR_AIS_waterfall.py', gain, ppm, channel])
			msg=_('AIS reception disabled. After closing the new window enable AIS reception again.')
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
			subprocess.Popen(['python',self.currentpath+'/tools/SDR_AIS_fine_cal.py', 'b'])
			msg=_('AIS reception disabled. After closing the new window enable AIS reception again.')
			self.SetStatusText(msg)
			
		def check_channel(self, event):
			self.kill_sdr()
			self.enable_sdr_controls()
			gain=self.gain.GetValue()
			ppm=self.ppm.GetValue()
			channel=self.channel.GetValue()
			self.conf.set('AIS-SDR', 'gain', gain)
			self.conf.set('AIS-SDR', 'ppm', ppm)
			self.conf.set('AIS-SDR', 'gsm_channel', channel)
			if channel: subprocess.Popen(['python',self.currentpath+'/tools/SDR_AIS_fine_cal.py', 'c'])
			msg=_('AIS reception disabled. After closing the new window enable AIS reception again.')
			self.SetStatusText(msg)

		def vhf_Rx(self, event):
			self.kill_sdr()
			self.enable_sdr_controls()
			subprocess.Popen(self.home+'/.config/gqrx/run_gqrx.sh')
			msg=_('AIS reception disabled. After closing the new window enable AIS reception again.')
			self.SetStatusText(msg)

		def ShowMessage(self, w_msg):
			wx.MessageBox(w_msg, 'Info', wx.OK | wx.ICON_INFORMATION)

app = wx.App()
MyFrame().Show()
app.MainLoop()