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

import wx, gettext, os, sys, ConfigParser, subprocess
import wx.lib.scrolledpanel as scrolled

home = os.path.expanduser('~')
pathname = os.path.dirname(sys.argv[0])
currentpath = os.path.abspath(pathname)

class MainFrame(wx.Frame):
####layout###################
	def __init__(self):
		wx.Frame.__init__(self, None, title="OpenPlotter", size=(700,420))
########reading configuration###################
		self.read_conf()
###########################reading configuration
########language###################
		gettext.install('openplotter', currentpath+'/locale', unicode=False)
		self.presLan_en = gettext.translation('openplotter', currentpath+'/locale', languages=['en'])
		self.presLan_ca = gettext.translation('openplotter', currentpath+'/locale', languages=['ca'])
		self.presLan_es = gettext.translation('openplotter', currentpath+'/locale', languages=['es'])
		self.language=self.data_conf.get('GENERAL', 'lang')
		if self.language=='en':self.presLan_en.install()
		if self.language=='ca':self.presLan_ca.install()
		if self.language=='es':self.presLan_es.install()
##########################language
		self.p = scrolled.ScrolledPanel(self, -1, style = wx.TAB_TRAVERSAL|wx.SUNKEN_BORDER)
		self.p.SetAutoLayout(1)
		self.p.SetupScrolling()
		self.nb = wx.Notebook(self.p)

		self.page1 = wx.Panel(self.nb)
		self.page2 = wx.Panel(self.nb)
		self.page3 = wx.Panel(self.nb)
		self.page4 = wx.Panel(self.nb)
		self.page5 = wx.Panel(self.nb)

		self.nb.AddPage(self.page5, _('NMEA multiplexer'))
		self.nb.AddPage(self.page3, _('WiFi access point'))
		self.nb.AddPage(self.page4, _('SDR-AIS reception'))
		self.nb.AddPage(self.page2, _('STW simulation'))
		self.nb.AddPage(self.page1, _('Startup'))

		sizer = wx.BoxSizer()
		sizer.Add(self.nb, 1, wx.EXPAND)
		self.p.SetSizer(sizer)

		self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))

		self.icon = wx.Icon(currentpath+'/openplotter.ico', wx.BITMAP_TYPE_ICO)
		self.SetIcon(self.icon)

		self.CreateStatusBar()
		self.Centre()
########menu###################
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
		self.menubar.Append(self.lang, _('Language'))

		self.helpm = wx.Menu()
		self.helpm_item1=self.helpm.Append(wx.ID_ANY, _('&About'), _('About OpenPlotter'))
		self.Bind(wx.EVT_MENU, self.OnAboutBox, self.helpm_item1)
		self.menubar.Append(self.helpm, _('&Help'))

		self.SetMenuBar(self.menubar)
###########################menu
########page1###################
		wx.StaticBox(self.page1, size=(400, 295), pos=(10, 10))
		self.startup_opencpn = wx.CheckBox(self.page1, label=_('OpenCPN'), pos=(20, 20))
		self.startup_opencpn.Bind(wx.EVT_CHECKBOX, self.startup)

		self.startup_opencpn_nopengl = wx.CheckBox(self.page1, label=_('no OpenGL'), pos=(40, 50))
		self.startup_opencpn_nopengl.Bind(wx.EVT_CHECKBOX, self.startup)

		self.startup_opencpn_fullscreen = wx.CheckBox(self.page1, label=_('fullscreen'), pos=(40, 80))
		self.startup_opencpn_fullscreen.Bind(wx.EVT_CHECKBOX, self.startup)

		self.startup_multiplexer = wx.CheckBox(self.page1, label=_('NMEA-0183 Multiplexer (kplex)'), pos=(20, 120))
		self.startup_multiplexer.Bind(wx.EVT_CHECKBOX, self.startup)

		self.startup_nmea_time = wx.CheckBox(self.page1, label=_('Set time from NMEA'), pos=(40, 150))
		self.startup_nmea_time.Bind(wx.EVT_CHECKBOX, self.startup)

		self.startup_remote_desktop = wx.CheckBox(self.page1, label=_('Remote desktop (x11vnc)'), pos=(20, 190))
		self.startup_remote_desktop.Bind(wx.EVT_CHECKBOX, self.startup)
###########################page1
########page2###################
		wx.StaticBox(self.page2, size=(400, 35), pos=(10, 10))
		self.water_speed_enable = wx.CheckBox(self.page2, label=_('Enable'), pos=(20, 20))
		self.water_speed_enable.Bind(wx.EVT_CHECKBOX, self.onoffwaterspeed)
###########################page2
########page3###################
		wx.StaticBox(self.page3, size=(400, 35), pos=(10, 10))
		self.wifi_enable = wx.CheckBox(self.page3, label=_('Enable'), pos=(20, 20))
		self.wifi_enable.Bind(wx.EVT_CHECKBOX, self.onwifi_enable)

		wx.StaticBox(self.page3, label=_(' Settings '), size=(400, 150), pos=(10, 50))

		self.available_wireless = []
		output=subprocess.check_output('iwconfig')
		for i in range (0, 10):
			ii=str(i)
			if 'wlan'+ii in output: self.available_wireless.append('wlan'+ii)
		self.wlan = wx.ComboBox(self.page3, choices=self.available_wireless, style=wx.CB_READONLY, size=(100, 30), pos=(20, 75))
		self.wlan_label=wx.StaticText(self.page3, label=_('WiFi device'), pos=(140, 80))

		self.passw = wx.TextCtrl(self.page3, -1, size=(100, 30), pos=(20, 110))
		self.passw_label=wx.StaticText(self.page3, label=_('Password \nminimum 8 characters required'), pos=(140, 115))
###########################page3
########page4###################
		wx.StaticBox(self.page4, size=(400, 35), pos=(10, 10))
		self.ais_sdr_enable = wx.CheckBox(self.page4, label=_('Enable'), pos=(20, 20))
		self.ais_sdr_enable.Bind(wx.EVT_CHECKBOX, self.OnOffAIS)

		wx.StaticBox(self.page4, label=_(' Settings '), size=(400, 150), pos=(10, 50))

		self.gain = wx.TextCtrl(self.page4, -1, size=(55, 30), pos=(150, 75))
		self.gain_label=wx.StaticText(self.page4, label=_('Gain'), pos=(20, 80))
		self.button_test_gain =wx.Button(self.page4, label=_('check gain'), pos=(260, 75))
		self.Bind(wx.EVT_BUTTON, self.test_gain, self.button_test_gain)

		self.ppm = wx.TextCtrl(self.page4, -1, size=(55, 30), pos=(150, 110))
		self.correction_label=wx.StaticText(self.page4, label=_('Correction (ppm)'), pos=(20, 115))
		self.button_test_ppm =wx.Button(self.page4, label=_('take a look'), pos=(260, 110))
		self.Bind(wx.EVT_BUTTON, self.test_ppm, self.button_test_ppm)

		self.ais_frequencies1 = wx.CheckBox(self.page4, label=_('Channel A 161.975Mhz'), pos=(20, 145))
		self.ais_frequencies1.Bind(wx.EVT_CHECKBOX, self.ais_frequencies)
		self.ais_frequencies2 = wx.CheckBox(self.page4, label=_('Channel B 162.025Mhz'), pos=(20, 170))
		self.ais_frequencies2.Bind(wx.EVT_CHECKBOX, self.ais_frequencies)

		wx.StaticBox(self.page4, label=_(' Calibrate using GSM base stations '), size=(400, 100), pos=(10, 205))
		self.bands_label=wx.StaticText(self.page4, label=_('Band'), pos=(20, 235))
		self.bands_list = ['GSM850', 'GSM-R', 'GSM900', 'EGSM', 'DCS', 'PCS']
		self.band= wx.ComboBox(self.page4, choices=self.bands_list, style=wx.CB_READONLY, size=(100, 30), pos=(150, 230))
		self.band.SetValue('GSM900')
		self.check_bands =wx.Button(self.page4, label=_('check channels'), pos=(260, 230))
		self.Bind(wx.EVT_BUTTON, self.check_band, self.check_bands)
		self.channel_label=wx.StaticText(self.page4, label=_('Channel'), pos=(20, 270))
		self.channel = wx.TextCtrl(self.page4, -1, size=(55, 30), pos=(150, 265))
		self.check_channels =wx.Button(self.page4, label=_('calibrate'), pos=(260, 265))
		self.Bind(wx.EVT_BUTTON, self.check_channel, self.check_channels)
###########################page4
########page5###################
		wx.StaticBox(self.page5, label=_(' Inputs '), size=(670, 140), pos=(10, 10))
		self.list_input = wx.ListCtrl(self.page5, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER, size=(295, 112), pos=(15, 30))
		self.list_input.InsertColumn(0, _('Type'), width=50)
		self.list_input.InsertColumn(1, _('Port/Address'), width=130)
		self.list_input.InsertColumn(2, _('Bauds/Port'), width=115)
		self.add_serial_in =wx.Button(self.page5, label=_('+ serial'), pos=(315, 30))
		self.Bind(wx.EVT_BUTTON, self.add_serial_input, self.add_serial_in)
		self.SerDevLs = []
		self.SerialCheck('/dev/rfcomm')
		self.SerialCheck('/dev/ttyUSB')
		self.SerialCheck('/dev/ttyS')
		self.SerialCheck('/dev/ttyACM')
		self.deviceComboBox = wx.ComboBox(self.page5, choices=self.SerDevLs, style=wx.CB_DROPDOWN, size=(130, 30), pos=(445, 30))
		if self.SerDevLs : self.deviceComboBox.SetValue(self.SerDevLs[0])
		self.bauds = ['2400', '4800', '9600', '19200', '38400', '57600', '115200']
		self.baudComboBox = wx.ComboBox(self.page5, choices=self.bauds, style=wx.CB_READONLY, size=(90, 30), pos=(580, 30))
		self.baudComboBox.SetValue('4800')
		self.add_network_in =wx.Button(self.page5, label=_('+ network'), pos=(315, 70))
		self.Bind(wx.EVT_BUTTON, self.add_network_input, self.add_network_in)
		self.type = ['TCP', 'UDP']
		self.typeComboBox = wx.ComboBox(self.page5, choices=self.type, style=wx.CB_READONLY, size=(65, 30), pos=(420, 70))
		self.typeComboBox.SetValue('TCP')
		self.address = wx.TextCtrl(self.page5, -1, size=(120, 30), pos=(490, 70))
		self.port = wx.TextCtrl(self.page5, -1, size=(55, 30), pos=(615, 70))
		self.button_delete_input =wx.Button(self.page5, label=_('- selected'), pos=(315, 110))
		self.Bind(wx.EVT_BUTTON, self.delete_input, self.button_delete_input)
		self.add_gpsd_in =wx.Button(self.page5, label=_('+ GPSD'), pos=(575, 110))
		self.Bind(wx.EVT_BUTTON, self.add_gpsd_input, self.add_gpsd_in)

		wx.StaticBox(self.page5, label=_(' Outputs '), size=(670, 140), pos=(10, 150))
		self.list_output = wx.ListCtrl(self.page5, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER, size=(295, 112), pos=(15, 170))
		self.list_output.InsertColumn(0, _('Type'), width=50)
		self.list_output.InsertColumn(1, _('Port/Address'), width=130)
		self.list_output.InsertColumn(2, _('Bauds/Port'), width=115)
		self.add_serial_out =wx.Button(self.page5, label=_('+ serial'), pos=(315, 170))
		self.Bind(wx.EVT_BUTTON, self.add_serial_output, self.add_serial_out)
		self.deviceComboBox2 = wx.ComboBox(self.page5, choices=self.SerDevLs, style=wx.CB_DROPDOWN, size=(130, 30), pos=(445, 170))
		if self.SerDevLs : self.deviceComboBox2.SetValue(self.SerDevLs[0])
		self.baudComboBox2 = wx.ComboBox(self.page5, choices=self.bauds, style=wx.CB_READONLY, size=(90, 30), pos=(580, 170))
		self.baudComboBox2.SetValue('4800')
		self.add_network_out =wx.Button(self.page5, label=_('+ network'), pos=(315, 210))
		self.Bind(wx.EVT_BUTTON, self.add_network_output, self.add_network_out)
		self.adress_label=wx.StaticText(self.page5, label=_('TCP'), pos=(435, 215))
		self.address2 = wx.TextCtrl(self.page5, -1, size=(120, 30), pos=(490, 210))
		self.port2 = wx.TextCtrl(self.page5, -1, size=(55, 30), pos=(615, 210))
		self.button_delete_output =wx.Button(self.page5, label=_('- selected'), pos=(315, 250))
		self.Bind(wx.EVT_BUTTON, self.delete_output, self.button_delete_output)

		self.button_apply =wx.Button(self.page5, label=_('Apply changes'), pos=(315, 293))
		self.Bind(wx.EVT_BUTTON, self.apply_changes, self.button_apply)
		self.restart =wx.Button(self.page5, label=_('Restart'), pos=(490, 293))
		self.Bind(wx.EVT_BUTTON, self.restart_multiplex, self.restart)
		self.show_output =wx.Button(self.page5, label=_('Show output'), pos=(15, 293))
		self.Bind(wx.EVT_BUTTON, self.show_output_window, self.show_output)
###########################page5
		self.read_kplex_conf()
		self.set_layout_conf()
###########################layout



####definitions###################
	def read_conf(self):
		self.data_conf = ConfigParser.SafeConfigParser()
		self.data_conf.read(currentpath+'/openplotter.conf')

	def set_layout_conf(self):
		language=self.data_conf.get('GENERAL', 'lang')
		if language=='en': self.lang.Check(self.lang_item1.GetId(), True)
		if language=='ca': self.lang.Check(self.lang_item2.GetId(), True)
		if language=='es': self.lang.Check(self.lang_item3.GetId(), True)

		if self.data_conf.get('STARTUP', 'opencpn')=='1': 
			self.startup_opencpn.SetValue(True)
		else:
			self.startup_opencpn_nopengl.Disable()
			self.startup_opencpn_fullscreen.Disable()
		if self.data_conf.get('STARTUP', 'opencpn_no_opengl')=='1': self.startup_opencpn_nopengl.SetValue(True)
		if self.data_conf.get('STARTUP', 'opencpn_fullscreen')=='1': self.startup_opencpn_fullscreen.SetValue(True)
		if self.data_conf.get('STARTUP', 'kplex')=='1': 
			self.startup_multiplexer.SetValue(True)
		else:
			self.startup_nmea_time.Disable()
		if self.data_conf.get('STARTUP', 'gps_time')=='1': self.startup_nmea_time.SetValue(True)
		if self.data_conf.get('STARTUP', 'x11vnc')=='1': self.startup_remote_desktop.SetValue(True)

		if self.data_conf.get('STARTUP', 'iivbw')=='1': self.water_speed_enable.SetValue(True)

		if len(self.available_wireless)>0:
			self.wlan.SetValue(self.data_conf.get('WIFI', 'device'))
			self.passw.SetValue(self.data_conf.get('WIFI', 'password'))
			if self.data_conf.get('WIFI', 'enable')=='1':
				self.wifi_enable.SetValue(True)
				self.wlan.Disable()
				self.passw.Disable()
				self.wlan_label.Disable()
				self.passw_label.Disable()
		else:
			self.wifi_enable.Disable()
			self.wlan.Disable()
			self.passw.Disable()
			self.wlan_label.Disable()
			self.passw_label.Disable()			

		output=subprocess.check_output('lsusb')
		if 'DVB-T' in output:
			self.gain.SetValue(self.data_conf.get('AIS-SDR', 'gain'))
			self.ppm.SetValue(self.data_conf.get('AIS-SDR', 'ppm'))
			self.channel.SetValue(self.data_conf.get('AIS-SDR', 'gsm_channel'))
			if self.data_conf.get('AIS-SDR', 'enable')=='1': 
				self.ais_sdr_enable.SetValue(True)
				self.disable_sdr_controls()
			if self.data_conf.get('AIS-SDR', 'channel')=='a': self.ais_frequencies1.SetValue(True)
			if self.data_conf.get('AIS-SDR', 'channel')=='b': self.ais_frequencies2.SetValue(True)
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
		subprocess.Popen(['lxterminal', '-e', 'sudo dpkg-reconfigure gpsd'])
		self.SetStatusText(_('Set GPSD in the new window'))
	
	def clear_lang(self):
		self.lang.Check(self.lang_item1.GetId(), False)
		self.lang.Check(self.lang_item2.GetId(), False)
		self.lang.Check(self.lang_item3.GetId(), False)
		self.ShowMessage(_('The selected language will be enabled when you restart'))
	
	def lang_en(self, e):
		self.clear_lang()
		self.lang.Check(self.lang_item1.GetId(), True)
		self.data_conf.set('GENERAL', 'lang', 'en')
		self.write_conf()
	def lang_ca(self, e):
		self.clear_lang()
		self.lang.Check(self.lang_item2.GetId(), True)
		self.data_conf.set('GENERAL', 'lang', 'ca')
		self.write_conf()
	def lang_es(self, e):
		self.clear_lang()
		self.lang.Check(self.lang_item3.GetId(), True)
		self.data_conf.set('GENERAL', 'lang', 'es')
		self.write_conf()

	def OnAboutBox(self, e):
		description = _("OpenPlotter is a DIY, open-source, low-cost and low-consumption sailing platform to run on x86 laptops and ARM boards (Raspberry Pi, BeagleBone Black, Odroid C1...)")			
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
		info.SetVersion(self.data_conf.get('GENERAL', 'version'))
		info.SetDescription(description)
		info.SetCopyright('2013 - 2015 Sailoog')
		info.SetWebSite('http://www.sailoog.com')
		info.SetLicence(licence)
		info.AddDeveloper('Sailoog\n\nhttps://github.com/sailoog')
		info.AddDocWriter('Sailoog\n\nhttps://www.gitbook.com/@sailoog')
		info.AddArtist('Sailoog')
		info.AddTranslator('Catalan, English and Spanish by Sailoog')
		wx.AboutBox(info)

	def startup(self, e):
		if self.startup_opencpn.GetValue():
			self.startup_opencpn_nopengl.Enable()
			self.startup_opencpn_fullscreen.Enable()
			self.data_conf.set('STARTUP', 'opencpn', '1')
		else:
			self.startup_opencpn_nopengl.Disable()
			self.startup_opencpn_fullscreen.Disable()
			self.data_conf.set('STARTUP', 'opencpn', '0')

		if self.startup_opencpn_nopengl.GetValue():
			self.data_conf.set('STARTUP', 'opencpn_no_opengl', '1')
		else:
			self.data_conf.set('STARTUP', 'opencpn_no_opengl', '0')

		if self.startup_opencpn_fullscreen.GetValue():
			self.data_conf.set('STARTUP', 'opencpn_fullscreen', '1')
		else:
			self.data_conf.set('STARTUP', 'opencpn_fullscreen', '0')

		if self.startup_multiplexer.GetValue():
			self.startup_nmea_time.Enable()
			self.data_conf.set('STARTUP', 'kplex', '1')
		else:
			self.startup_nmea_time.Disable()
			self.data_conf.set('STARTUP', 'kplex', '0')

		if self.startup_nmea_time.GetValue():
			self.data_conf.set('STARTUP', 'gps_time', '1')
		else:
			self.data_conf.set('STARTUP', 'gps_time', '0')

		if self.startup_remote_desktop.GetValue():
			self.data_conf.set('STARTUP', 'x11vnc', '1')
		else:
			self.data_conf.set('STARTUP', 'x11vnc', '0')

		self.write_conf()

	def onoffwaterspeed(self, e):
		if self.water_speed_enable.GetValue():
			self.SetStatusText(_('Searching NMEA Speed Over Ground data in localhost:10110 ...'))
			sog_result=subprocess.Popen(['python', currentpath+'/sog2sow.py'], stdout=subprocess.PIPE)
			msg=''
			self.data_conf.set('STARTUP', 'iivbw', '1')
			while sog_result.poll() is None:
				l = sog_result.stdout.readline()
				if 'Failed to connect with localhost:10110.' in l:
					msg+=_('Failed to connect with localhost:10110.')
				if 'Error: ' in l: msg+='\n'+l
				if 'No data, trying to reconnect...' in l:
					msg+=_('No data, trying to reconnect...')
					break
				if 'Speed Over Ground data not found, waiting for NMEA data...' in l:
					msg+=_('Speed Over Ground data not found, waiting for NMEA data...')
					break
				if '$IIVBW' in l: msg+=l
				if '$IIVHW' in l:
					msg+=l
					msg+=_('\nSpeed Over Ground retrieved from NMEA data successfully.')
					break
			sog_result.stdout.close()
			self.SetStatusText('')
			self.ShowMessage(msg)
		else:
			subprocess.call(['pkill', '-f', 'sog2sow.py'])
			self.SetStatusText('')
			self.ShowMessage(_('Speed Through Water simulation stopped'))
			self.data_conf.set('STARTUP', 'iivbw', '0')
		self.write_conf()

	def onwifi_enable (self, e):
		self.SetStatusText(_('Configuring NMEA WiFi server, wait please...'))
		isChecked = self.wifi_enable.GetValue()
		wlan=self.wlan.GetValue()
		passw=self.passw.GetValue()
		if isChecked:
			self.enable_disable_wifi(1)
			if len(passw)>=8:
				wifi_result=subprocess.check_output(['sudo', 'python', currentpath+'/wifi_server.py', '1', wlan, passw])
			else:
				wifi_result=_('Your password must have a minimum of 8 characters')
				self.enable_disable_wifi(0)
		else: 
			self.enable_disable_wifi(0)
			wifi_result=subprocess.check_output(['sudo', 'python', currentpath+'/wifi_server.py', '0', wlan, passw])
			
		msg=wifi_result
		if 'NMEA WiFi Server failed.' in msg:
			self.enable_disable_wifi(0)
			self.data_conf.set('WIFI', 'device', '')
			self.data_conf.set('WIFI', 'password', '')
		if'NMEA WiFi Server started.' in msg:
			wlan=self.wlan.GetValue()
			passw=self.passw.GetValue()
			self.data_conf.set('WIFI', 'device', wlan)
			self.data_conf.set('WIFI', 'password', passw)
		msg=msg.replace('NMEA WiFi Server failed.', _('NMEA WiFi Server failed.'))
		msg=msg.replace('NMEA WiFi Server started.', _('NMEA WiFi Server started.'))
		msg=msg.replace('NMEA WiFi Server stopped.', _('NMEA WiFi Server stopped.'))
		self.SetStatusText('')
		self.ShowMessage(msg)
		self.write_conf()
		
	def enable_disable_wifi(self, s):
		if s==1:
			self.wlan.Disable()
			self.passw.Disable()
			self.wlan_label.Disable()
			self.passw_label.Disable()
			self.wifi_enable.SetValue(True)
			self.data_conf.set('WIFI', 'enable', '1')
		else:
			self.wlan.Enable()
			self.passw.Enable()
			self.wlan_label.Enable()
			self.passw_label.Enable()
			self.wifi_enable.SetValue(False)
			self.data_conf.set('WIFI', 'enable', '0')

	def kill_sdr(self):
		subprocess.call(['pkill', '-9', 'aisdecoder'])
		subprocess.call(['pkill', '-9', 'rtl_fm'])
		subprocess.call(['pkill', '-f', 'waterfall.py'])
		subprocess.call(['pkill', '-9', 'rtl_test'])
		subprocess.call(['pkill', '-9', 'kal'])

	def enable_sdr_controls(self):
		self.gain.Enable()
		self.ppm.Enable()
		self.ais_frequencies1.Enable()
		self.ais_frequencies2.Enable()
		self.gain_label.Enable()
		self.correction_label.Enable()
		self.ais_sdr_enable.SetValue(False)
		self.data_conf.set('AIS-SDR', 'enable', '0')
		self.write_conf()

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
			self.data_conf.set('AIS-SDR', 'enable', '1')
			self.data_conf.set('AIS-SDR', 'gain', gain)
			self.data_conf.set('AIS-SDR', 'ppm', ppm)
			self.data_conf.set('AIS-SDR', 'channel', channel)
			msg=_('SDR-AIS reception enabled')
		else: 
			self.enable_sdr_controls()
			self.data_conf.set('AIS-SDR', 'enable', '0')
			msg=_('SDR-AIS reception disabled')
		self.write_conf()
		self.SetStatusText('')
		self.ShowMessage(msg)

	def test_ppm(self,event):
		self.kill_sdr()
		self.enable_sdr_controls()
		gain=self.gain.GetValue()
		gain1=gain.replace(',', '.')
		gain2=float(gain1)
		gain3=str(gain2)
		ppm=self.ppm.GetValue()
		ppm1=ppm.replace(',', '.')
		ppm2=int(float(ppm1))
		ppm3=str(ppm2)
		channel='a'
		if self.ais_frequencies2.GetValue(): channel='b'
		w_open=subprocess.Popen(['python', currentpath+'/waterfall.py', gain3, ppm3, channel])
		msg=_('SDR-AIS reception disabled.\nAfter checking the new window enable SDR-AIS reception again.')
		self.ShowMessage(msg)

	def test_gain(self,event):
		self.kill_sdr()
		self.enable_sdr_controls()
		subprocess.Popen(['lxterminal', '-e', 'rtl_test'])
		msg=_('SDR-AIS reception disabled.\nCheck the new window, copy the maximum supported gain value and enable SDR-AIS reception again.')
		self.ShowMessage(msg)

	def check_band(self, event):
		self.kill_sdr()
		self.enable_sdr_controls()
		subprocess.Popen(("lxterminal -e 'bash -c \"kal -s "+self.band.GetValue()+"; echo 'Press [ENTER] to close the window'; read -p ---------------------------------; exit 0; exec bash\"'"), shell=True)
		msg=_('Wait for the system to check the band and select the strongest channel (power). If you do not find any channel try another band.')
		self.ShowMessage(msg)

	def check_channel(self, event):
		self.kill_sdr()
		self.enable_sdr_controls()
		channel=self.channel.GetValue()
		if channel:
			subprocess.Popen(("lxterminal -e 'bash -c \"kal -c "+self.channel.GetValue()+"; echo 'Press [ENTER] to close the window'; read -p ---------------------------------; exit 0; exec bash\"'"), shell=True)
			msg=_('Wait for the system to calculate the ppm value with the selected channel. Put the obtained value in the "Correction (ppm)" field and enable SDR-AIS reception again.')
			self.data_conf.set('AIS-SDR', 'gsm_channel', channel)
			self.write_conf()
			self.ShowMessage(msg)

########multimpexer###################################	

	def show_output_window(self,event):
		close=subprocess.call(['pkill', '-f', 'output.py'])
		show_output=subprocess.Popen(['python', currentpath+'/output.py', self.language])

	def restart_multiplex(self,event):
		self.restart_kplex()

	def restart_kplex(self):
		self.SetStatusText(_('Closing Kplex'))
		subprocess.call(["pkill", '-9', "kplex"])
		subprocess.Popen('kplex')
		self.SetStatusText(_('Kplex restarted'))

	def read_kplex_conf(self):
		self.inputs = []
		self.outputs = []
		try:
			file=open(home+'/.kplex.conf', 'r')
			data=file.readlines()
			file.close()
			for index,item in enumerate(data):
				if '[serial]' in item:
					if 'direction=in' in data[index+1]:
						input_tmp=[]
						input_tmp.append('Serial')
						item2=self.extract_value(data[index+2])
						input_tmp.append(item2)
						item3=self.extract_value(data[index+3])
						input_tmp.append(item3)
						self.inputs.append(input_tmp)
					if 'direction=out' in data[index+1]:
						output_tmp=[]
						output_tmp.append('Serial')
						item2=self.extract_value(data[index+2])
						output_tmp.append(item2)
						item3=self.extract_value(data[index+3])
						output_tmp.append(item3)
						self.outputs.append(output_tmp)
				if '[tcp]' in item:
					if 'direction=in' in data[index+1]:
						input_tmp=[]
						input_tmp.append('TCP')
						item2=self.extract_value(data[index+2])
						input_tmp.append(item2)
						item3=self.extract_value(data[index+3])
						input_tmp.append(item3)
						self.inputs.append(input_tmp)
					if 'direction=out' in data[index+1]:
						output_tmp=[]
						output_tmp.append('TCP')
						output_tmp.append(_('all address'))
						item2=self.extract_value(data[index+2])
						output_tmp.append(item2)
						self.outputs.append(output_tmp)
				if '[broadcast]' in item:
					if 'direction=in' in data[index+1]:
						input_tmp=[]
						input_tmp.append('UDP')
						input_tmp.append(_('all address'))
						item2=self.extract_value(data[index+2])
						input_tmp.append(item2)
						self.inputs.append(input_tmp)
			self.write_inputs()
			self.write_outputs()

		except IOError:
			self.ShowMessage(_('Configuration file does not exist. Add inputs and apply changes.'))

	def extract_value(self,data):
		option, value =data.split('=')
		value=value.strip()
		return value

	def write_inputs(self):
		self.list_input.DeleteAllItems()
		for i in self.inputs:
			index = self.list_input.InsertStringItem(sys.maxint, i[0])
			self.list_input.SetStringItem(index, 1, i[1])
			self.list_input.SetStringItem(index, 2, i[2])
	
	def write_outputs(self):
		self.list_output.DeleteAllItems()
		for i in self.outputs:
			index = self.list_output.InsertStringItem(sys.maxint, i[0])
			self.list_output.SetStringItem(index, 1, i[1])
			self.list_output.SetStringItem(index, 2, i[2])

	def apply_changes(self,event):
		data='# For advanced manual configuration, please visit: http://www.stripydog.com/kplex/configuration.html\n# Editing this file by openplotter GUI, can eliminate manual settings.\n# You should not modify defaults.\n\n'
		for index,item in enumerate(self.inputs):
			if 'Serial' in item[0]:
				data=data+'[serial]\ndirection=in\nfilename='+item[1]+'\nbaud='+item[2]+'\noptional=yes\n\n'
			if 'TCP' in item[0]:
				data=data+'[tcp]\ndirection=in\naddress='+item[1]+'\nport='+item[2]+'\nmode=client\npersist=yes\nkeepalive=yes\noptional=yes\n\n'
			if 'UDP' in item[0]:
				data=data+'[broadcast]\ndirection=in\nport='+item[2]+'\noptional=yes\n\n'
		if not '[broadcast]\ndirection=in\nport=10110' in data: data=data+'#default input\n[broadcast]\ndirection=in\nport=10110\noptional=yes\n\n'
		for index,item in enumerate(self.outputs):
			if 'Serial' in item[0]:
				data=data+'[serial]\ndirection=out\nfilename='+item[1]+'\nbaud='+item[2]+'\noptional=yes\n\n'
			if 'TCP' in item[0]:
				data=data+'[tcp]\ndirection=out\nport='+item[2]+'\nmode=server\n\n'
		if not '[tcp]\ndirection=out\nport=10110' in data: data=data+'#default output\n[tcp]\ndirection=out\nport=10110\nmode=server\n\n'
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
		num = len(self.outputs)
		for i in range(num):
			if self.list_output.IsSelected(i):
				del self.outputs[i]
		self.write_outputs()

	def SerialCheck(self,dev):
		num = 0
		for _ in range(99):
			s = dev + str(num)
			d = os.path.exists(s)
			if d == True:
				self.SerDevLs.append(s)      
			num = num + 1
	
	def add_serial_input(self,event):
		input_tmp=[]
		found=False
		input_tmp.append('Serial')
		port=self.deviceComboBox.GetValue()
		input_tmp.append(port)
		bauds=self.baudComboBox.GetValue()
		input_tmp.append(bauds)
		for sublist in self.inputs:
			if sublist[1] == port:found=True
		for sublist in self.outputs:
			if sublist[1] == port:found=True
		if found==False:
			self.inputs.append(input_tmp)
			self.write_inputs()
		else:
			self.ShowMessage(_('It is impossible to set input because this port is already in use.'))
	
	def add_network_input(self,event):
		input_tmp=[]
		type_=self.typeComboBox.GetValue()
		address=self.address.GetValue()
		port=self.port.GetValue()
		input_tmp.append(type_)
		input_tmp.append(address)
		input_tmp.append(port)
		if port:
			self.inputs.append(input_tmp)
			self.write_inputs()
		else:
			self.ShowMessage(_('You have to enter at least a port number.'))

	def add_serial_output(self,event):
		output_tmp=[]
		found=False
		output_tmp.append('Serial')
		port=self.deviceComboBox2.GetValue()
		output_tmp.append(port)
		bauds=self.baudComboBox2.GetValue()
		output_tmp.append(bauds)
		for sublist in self.inputs:
			if sublist[1] == port:found=True
		for sublist in self.outputs:
			if sublist[1] == port:found=True
		if found==False:
			self.outputs.append(output_tmp)
			self.write_outputs()
		else:
			self.ShowMessage(_('It is impossible to set output because this port is already in use.'))

	def add_network_output(self,event):
		output_tmp=[]
		found=False
		type_='TCP'
		address=self.address2.GetValue()
		port=self.port2.GetValue()
		output_tmp.append(type_)
		output_tmp.append(address)
		output_tmp.append(port)
		if port:
			self.outputs.append(output_tmp)
			self.write_outputs()
		else:
			self.ShowMessage(_('You have to enter at least a port number.'))
	
	def add_gpsd_input(self,event):
		input_tmp=[]
		type_='TCP'
		address='127.0.0.1'
		port='2947'
		input_tmp.append(type_)
		input_tmp.append(address)
		input_tmp.append(port)
		self.inputs.append(input_tmp)
		self.write_inputs()


######################################multiplexer


	def write_conf(self):
		with open(currentpath+'/openplotter.conf', 'wb') as configfile:
			self.data_conf.write(configfile)

	def ShowMessage(self, w_msg):
			wx.MessageBox(w_msg, 'Info', wx.OK | wx.ICON_INFORMATION)
#######################definitions



#Main#############################
if __name__ == "__main__":
	app = wx.App()
	MainFrame().Show()
	app.MainLoop()