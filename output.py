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

import wx, socket, os, threading, time, datetime, gettext, sys, pynmea2

pathname = os.path.dirname(sys.argv[0])
currentpath = os.path.abspath(pathname)

class MyFrame(wx.Frame):
		
		def __init__(self, parent, title):

			gettext.install('openplotter', currentpath+'/locale', unicode=False)
			self.presLan_en = gettext.translation('openplotter', currentpath+'/locale', languages=['en'])
			self.presLan_ca = gettext.translation('openplotter', currentpath+'/locale', languages=['ca'])
			self.presLan_es = gettext.translation('openplotter', currentpath+'/locale', languages=['es'])

			language=sys.argv[1]
			if language=='en':self.presLan_en.install()
			if language=='ca':self.presLan_ca.install()
			if language=='es':self.presLan_es.install()


			wx.Frame.__init__(self, parent, title=title, size=(650,400))
			
			self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
			
			self.icon = wx.Icon(currentpath+'/openplotter.ico', wx.BITMAP_TYPE_ICO)
			self.SetIcon(self.icon)

			self.logger = wx.TextCtrl(self, style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_DONTWRAP, size=(650,150), pos=(0,0))

			wx.StaticText(self, label=_('NMEA inspector'), pos=(525, 160))

			self.button_pause =wx.Button(self, label=_('Pause'), pos=(530, 190))
			self.Bind(wx.EVT_BUTTON, self.pause, self.button_pause)

			self.button_reset =wx.Button(self, label=_('Reset'), pos=(530, 230))
			self.Bind(wx.EVT_BUTTON, self.reset, self.button_reset)

			self.list = wx.ListCtrl(self, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER, size=(500, 220), pos=(5, 155))
			self.list.InsertColumn(0, _('Type'), width=150)
			self.list.InsertColumn(1, _('Value'), width=145)
			self.list.InsertColumn(2, _('Source'), width=90)
			self.list.InsertColumn(3, _('NMEA'), width=50)
			self.list.InsertColumn(4, _('Age'), width=59)

			self.list.InsertStringItem(0,_('Latitude'))
			self.list.InsertStringItem(1,_('Longitude'))
			self.list.InsertStringItem(2,_('Date Time'))
			self.list.InsertStringItem(3,_('Magnetic Variation'))
			self.list.InsertStringItem(4,_('Magnetic Heading'))
			self.list.InsertStringItem(5,_('True Heading'))
			self.list.InsertStringItem(6,_('Course Over Ground'))
			self.list.InsertStringItem(7,_('Speed Over Ground'))
			self.list.InsertStringItem(8,_('Speed Trought Water'))
			self.list.InsertStringItem(9,_('Apparent Wind Angle'))
			self.list.InsertStringItem(10,_('True Wind Angle'))
			self.list.InsertStringItem(11,_('Apparent Wind Speed'))
			self.list.InsertStringItem(12,_('True Wind Speed'))
			self.list.InsertStringItem(13,_('True Wind Direction'))
			self.list.InsertStringItem(14,_('Pressure'))
			self.list.InsertStringItem(15,_('Temperature'))

			tick=time.time()

			self.times=[tick,tick,tick,tick,tick,tick,tick,tick,tick,tick,tick,tick,tick,tick,tick,tick]

			self.pause_all=0

			self.CreateStatusBar()

			self.Centre()

			self.Show(True)

			self.hilo=threading.Thread(target=self.ventanalog)

			self.connect()


		def connect(self):
			try:
				self.s2 = socket.socket()
				self.s2.connect(("localhost", 10110))
				self.s2.settimeout(10)
				self.error_message=""
			except socket.error, error_msg:
				self.error_message=str(error_msg[0])
			if not self.hilo.isAlive():
				self.hilo.start()

		def ventanalog(self):
			while True:
				if self.pause_all==1:pass
				else:
					frase_nmea=""
					if not self.error_message:
						try:
							frase_nmea = self.s2.recv(1024)
						except socket.error, error_msg:
							self.error_message=str(error_msg[0])
					if frase_nmea:
						wx.MutexGuiEnter()
						self.parse_nmea(frase_nmea)
						self.logger.AppendText(frase_nmea)
						self.SetStatusText(_('Multiplexer started'))
						wx.MutexGuiLeave()
					else:
						wx.MutexGuiEnter()
						if self.error_message:
							self.SetStatusText(_('Failed to connect with localhost:10110. ')+_('Error code: ') + self.error_message)
							time.sleep(3)
						else:
							self.SetStatusText(_('No data, trying to reconnect...'))
							time.sleep(3)
						self.SetStatusText(_('No data, trying to reconnect...'))
						wx.MutexGuiLeave()
						time.sleep(4)
						self.connect()
					
		def parse_nmea(self, frase_nmea):
			try:
				now=time.time()
				for i in range(self.list.GetItemCount()):
					item = self.list.GetItem(i, 1)
					value = item.GetText()
					if value:
						seg=now-self.times[i]
						self.list.SetStringItem(i,4,str(round(seg,1)))

				nmea_list=frase_nmea.split()

				for i in nmea_list:
					msg = pynmea2.parse(i)
					nmea_type=msg.sentence_type

					if nmea_type == 'RMC':
						#lat lon
						value='%02d°%07.4f′' % (msg.latitude, msg.latitude_minutes)+' '+msg.lat_dir
						if value: self.write_item(0, str(value), nmea_type, msg.talker)
						value='%02d°%07.4f′' % (msg.longitude, msg.longitude_minutes)+' '+msg.lon_dir
						if value: self.write_item(1, str(value), nmea_type, msg.talker)
						#date time
						value0=msg.datestamp
						value1=msg.timestamp
						value=str(value0)+' '+str(value1)
						if value: self.write_item(2, str(value), nmea_type, msg.talker)
						#magnetic variation
						value0=msg.mag_variation
						value1=msg.mag_var_dir
						value=str(value0)+' '+str(value1)
						if value0: self.write_item(3, str(value), nmea_type, msg.talker)
						#course over ground
						value=msg.true_course
						if value: self.write_item(6, str(value), nmea_type, msg.talker)
						#speed over ground
						value=msg.spd_over_grnd
						if value: self.write_item(7, str(value), nmea_type, msg.talker)

					if nmea_type == 'GGA':
						#lat lon
						value='%02d°%07.4f′' % (msg.latitude, msg.latitude_minutes)+' '+msg.lat_dir
						if value: self.write_item(0, str(value), nmea_type, msg.talker)
						value='%02d°%07.4f′' % (msg.longitude, msg.longitude_minutes)+' '+msg.lon_dir
						if value: self.write_item(1, str(value), nmea_type, msg.talker)

					if nmea_type == 'GNS':
						#lat lon
						value='%02d°%07.4f′' % (msg.latitude, msg.latitude_minutes)+' '+msg.lat_dir
						if value: self.write_item(0, str(value), nmea_type, msg.talker)
						value='%02d°%07.4f′' % (msg.longitude, msg.longitude_minutes)+' '+msg.lon_dir
						if value: self.write_item(1, str(value), nmea_type, msg.talker)

					if nmea_type == 'GLL':
						#lat lon
						value='%02d°%07.4f′' % (msg.latitude, msg.latitude_minutes)+' '+msg.lat_dir
						if value: self.write_item(0, str(value), nmea_type, msg.talker)
						value='%02d°%07.4f′' % (msg.longitude, msg.longitude_minutes)+' '+msg.lon_dir
						if value: self.write_item(1, str(value), nmea_type, msg.talker)

					if nmea_type == 'HDG':
						#magnetic variation
						value0=msg.variation
						value1=msg.var_dir
						value=str(value0)+' '+str(value1)
						if value0: self.write_item(3, str(value), nmea_type, msg.talker)
						#magnetic heading
						value=msg.heading
						if value: self.write_item(4, str(value), nmea_type, msg.talker)

					if nmea_type == 'VHW':
						#magnetic heading
						value=msg.heading_magnetic
						if value: self.write_item(4, str(value), nmea_type, msg.talker)
						#true heading
						value=msg.heading_true
						if value: self.write_item(5, str(value), nmea_type, msg.talker)
						#speed trought water 
						value=msg.water_speed_knots
						if value: self.write_item(8, str(value), nmea_type, msg.talker)

					if nmea_type == 'HDM':
						#magnetic heading
						value=msg.heading
						if value: self.write_item(4, str(value), nmea_type, msg.talker)

					if nmea_type == 'HDT':
						#true heading
						value=msg.heading
						if value: self.write_item(5, str(value), nmea_type, msg.talker)

					if nmea_type == 'VTG':
						#course over ground
						value=msg.true_track
						if value: self.write_item(6, str(value), nmea_type, msg.talker)
						#speed over ground
						value=msg.spd_over_grnd_kts
						if value: self.write_item(7, str(value), nmea_type, msg.talker)

					if nmea_type == 'VBW':
						#speed trought water 
						value=msg.lon_water_spd
						if value: self.write_item(8, str(value), nmea_type, msg.talker)

					if nmea_type == 'VWR':
						#apparent wind angle
						value0=msg.deg_r
						value1=msg.l_r
						value=str(value0)+' '+str(value1)
						if value0: self.write_item(9, str(value), nmea_type, msg.talker)
						#apparent wind speed
						value=msg.wind_speed_kn
						if value: self.write_item(11, str(value), nmea_type, msg.talker)

					if nmea_type == 'MWV':
						#apparent/true wind angle
						value0=msg.reference
						value=msg.wind_angle
						if value0=='R': self.write_item(9, str(value), nmea_type, msg.talker)
						if value0=='T': self.write_item(10, str(value), nmea_type, msg.talker)
						#apparent/true wind speed
						value=msg.wind_speed
						if value0=='R': self.write_item(11, str(value), nmea_type, msg.talker)
						if value0=='T': self.write_item(12, str(value), nmea_type, msg.talker)

					if nmea_type == 'VWT':
						#true wind angle
						value0=msg.wind_angle_vessel
						value1=msg.direction
						value=str(value0)+' '+str(value1)
						if value0: self.write_item(10, str(value), nmea_type, msg.talker)
						#true wind speed
						value=msg.wind_speed_knots
						if value: self.write_item(12, str(value), nmea_type, msg.talker)

					if nmea_type == 'MWD':
						#true wind direction
						value=msg.direction_true
						if value: self.write_item(13, str(value), nmea_type, msg.talker)
						#true wind speed
						value=msg.wind_speed_knots
						if value: self.write_item(12, str(value), nmea_type, msg.talker)

					if nmea_type == 'MDA':
						#pressure
						value=msg.b_presure_bar
						if value: self.write_item(14, str(value), nmea_type, msg.talker)
						#temperature
						value=msg.air_temp
						if value: self.write_item(15, str(value), nmea_type, msg.talker)


			#except Exception,e: print str(e)
			except: pass

		def write_item(self, pos, value, sentence, talker):
			self.list.SetStringItem(pos,1,value)
			if talker=='OP': self.list.SetStringItem(pos,2,_('OpenPlotter'))
			else: self.list.SetStringItem(pos,2,_('External'))
			self.list.SetStringItem(pos,3,sentence)
			self.list.SetStringItem(pos,4,'0')
			self.times[pos]=time.time()

		def pause(self, e):
			if self.pause_all==0: 
				self.pause_all=1
				self.button_pause.SetLabel(_('Resume'))
			else: 
				self.pause_all=0
				self.button_pause.SetLabel(_('Pause'))

		def reset(self, e):
			for i in range(self.list.GetItemCount()):
				self.list.SetStringItem(i,1,'')
				self.list.SetStringItem(i,2,'')
				self.list.SetStringItem(i,3,'')
				self.list.SetStringItem(i,4,'')


app = wx.App(False)
frame = MyFrame(None, 'TCP localhost:10110')
app.MainLoop()

