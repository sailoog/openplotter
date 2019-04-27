#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

op_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../..')
sys.path.append(op_folder+'/classes')
from conf import Conf
from language import Language

class MainFrame(wx.Frame):
		
		def __init__(self):

			self.option=sys.argv[1]

			self.conf = Conf()
			self.home = self.conf.home
			self.currentpath = self.conf.get('GENERAL', 'op_folder')

			Language(self.conf)

			wx.Frame.__init__(self, None, title=_('Fine calibration'), size=(600,320))

			self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
			
			self.icon = wx.Icon(self.currentpath+'/static/icons/openplotter.ico', wx.BITMAP_TYPE_ICO)
			self.SetIcon(self.icon)

			self.text=wx.StaticText(self, label=_('Error'), pos=(10, 10))

			self.ppm=self.conf.get('AIS-SDR', 'ppm')
			self.band=self.conf.get('AIS-SDR', 'band')
			self.channel=self.conf.get('AIS-SDR', 'gsm_channel')

			wx.StaticText(self, label=_('Initial PPM: ').decode('utf8')+self.ppm, pos=(10, 80))

			self.output = wx.TextCtrl(self, style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_DONTWRAP, size=(580,120), pos=(10,100))
			
			self.button_close =wx.Button(self, label=_('Close'), pos=(400, 230))
			self.Bind(wx.EVT_BUTTON, self.close, self.button_close)

			self.button_calculate =wx.Button(self, label=_('Start'), pos=(500, 230))
			self.Bind(wx.EVT_BUTTON, self.calculate, self.button_calculate)

			if self.option=='c': 
				self.text.SetLabel(_('Press Start and wait for the system to calculate the PPM value.\nRound the resulting PPM to the nearest integer and copy it into "PPM" field.\nEstimated time: 1 min.'))
				wx.StaticText(self, label=_('channel: ').decode('utf8')+self.channel, pos=(200, 80))
			if self.option=='b':
				self.text.SetLabel(_('Press Start and wait for the system to check the band.\nWrite down the strongest channel (power).\nIf you do not find any channel try another band.\nEstimated time: 5 min.'))
				wx.StaticText(self, label=_('band: ').decode('utf8')+self.band, pos=(200, 80))

			self.CreateStatusBar()

			self.Centre()
 	
		def calculate(self,e):
			self.SetStatusText(_('Working...'))
			self.output.SetValue('')
			if self.option=='c': 
				try: output=subprocess.check_output(['kal', '-c', self.channel, '-e', self.ppm])
				except Exception, e: output = _("Error: ")+str(e)
			if self.option=='b': 
				try: output=subprocess.check_output(['kal', '-s', self.band, '-e', self.ppm])
				except Exception, e: output = _("Error: ")+str(e)
			self.output.SetValue(output)
			self.SetStatusText(_('Finished'))

		def close(self,e):
			self.Destroy()

if __name__ == "__main__":
	app = wx.App()
	MainFrame().Show()
	app.MainLoop()
