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
import re
import wx


class addkplex(wx.Dialog):
	def __init__(self, edit, extkplex, parent):
		self.parent = parent
		self.currentpath = parent.currentpath
		wx.Dialog.__init__(self, None, title=_('Add/Edit NMEA 0183 (KPLEX)'), size=(550, 400))
		self.extkplex = extkplex
		self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
		self.result = 0
		self.index = -1
		if edit != 0:
			self.index = edit[9]

		panel = wx.Panel(self)

		self.icon = wx.Icon(self.currentpath + '/openplotter.ico', wx.BITMAP_TYPE_ICO)
		self.SetIcon(self.icon)

		wx.StaticText(panel, label=_('Type'), pos=(20, 30))
		self.kplex_type_list = ['Serial', 'TCP', 'UDP']
		self.kplex_type = wx.ComboBox(panel, choices=self.kplex_type_list, style=wx.CB_READONLY, size=(80, 32),
									  pos=(20, 55))
		self.Bind(wx.EVT_COMBOBOX, self.on_kplex_type_change, self.kplex_type)

		wx.StaticText(panel, label=_('Name'), pos=(115, 35))
		self.kplex_name = wx.TextCtrl(panel, -1, size=(110, 32), pos=(110, 55))

		wx.StaticBox(panel, label=_(' settings '), size=(530, 90), pos=(10, 10))

		self.SerialCheck()
		self.kplex_ser_T1 = wx.StaticText(panel, label=_('Port'), pos=(230, 35))
		self.kplex_device_select = wx.ComboBox(panel, choices=self.SerDevLs, style=wx.CB_DROPDOWN, size=(140, 32),
											   pos=(225, 55))
		if self.SerDevLs: self.kplex_device_select.SetValue(self.SerDevLs[0])
		self.bauds = ['4800', '9600', '19200', '38400', '57600', '115200']
		#self.bauds = ['4800', '9600', '19200', '38400', '57600', '115200', '230400', '460800']
		self.kplex_ser_T2 = wx.StaticText(panel, label=_('Bauds'), pos=(375, 35))
		self.kplex_baud_select = wx.ComboBox(panel, choices=self.bauds, style=wx.CB_READONLY, size=(90, 32),
											 pos=(370, 55))

		self.kplex_net_T1 = wx.StaticText(panel, label=_('Address'), pos=(235, 35))
		self.kplex_address = wx.TextCtrl(panel, -1, size=(120, 32), pos=(230, 55))
		self.kplex_net_T2 = wx.StaticText(panel, label=_('Port'), pos=(375, 35))
		self.kplex_netport = wx.TextCtrl(panel, -1, size=(55, 32), pos=(370, 55))

		self.ser_io_list = ['in', 'out', 'both']
		self.net_io_list = ['in', 'out']
		wx.StaticText(panel, label=_('in/out'), pos=(470, 35))
		self.kplex_io_ser = wx.ComboBox(panel, choices=self.ser_io_list, style=wx.CB_READONLY, size=(70, 32),
										pos=(465, 55))
		self.kplex_io_net = wx.ComboBox(panel, choices=self.net_io_list, style=wx.CB_READONLY, size=(70, 32),
										pos=(465, 55))
		self.Bind(wx.EVT_COMBOBOX, self.on_kplex_io_change, self.kplex_io_ser)
		self.Bind(wx.EVT_COMBOBOX, self.on_kplex_io_change, self.kplex_io_net)

		self.name_ifilter_list = []
		for i in extkplex:
			if i[3] == 'in' or i[3] == 'both':
				self.name_ifilter_list.append(i[1])

		self.ifilter_T1 = wx.StaticBox(panel, label=_('in Filter '), size=(530, 100), pos=(10, 105))
		self.mode_ifilter = [_('none'), _('Accept only sentences:'), _('Ignore sentences:')]
		self.ifilter_select = wx.ComboBox(panel, choices=self.mode_ifilter, style=wx.CB_READONLY, size=(195, 32),
										  pos=(20, 125))
		self.ifilter_select.SetValue(self.mode_ifilter[0])
		self.italker = wx.TextCtrl(panel, -1, size=(29, 32), pos=(226, 125))
		self.ifilter_T2 = wx.StaticText(panel, label=_('-'), pos=(253, 130))
		self.isent = wx.TextCtrl(panel, -1, size=(39, 32), pos=(260, 125))
		# self.name_ifilter_select = wx.ComboBox(panel, choices=self.name_ifilter_list, style=wx.CB_READONLY, size=(110, 32), pos=(305, 125))
		self.ifilter_add_b = wx.Button(panel, label=_('Add sentence'), pos=(425, 125))
		self.Bind(wx.EVT_BUTTON, self.ifilter_add, self.ifilter_add_b)
		self.ifilter_sentences = wx.TextCtrl(panel, -1, style=wx.CB_READONLY, size=(395, 32), pos=(20, 165))
		self.ifilter_sentences.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_INACTIVECAPTION))
		self.ifilter_del_b = wx.Button(panel, label=_('Delete'), pos=(425, 165))
		self.Bind(wx.EVT_BUTTON, self.ifilter_del, self.ifilter_del_b)

		a = 105
		self.ofilter_T1 = wx.StaticBox(panel, label=_('out Filter '), size=(530, 100), pos=(10, 105 + a))
		self.mode_ofilter = [_('none'), _('Accept only sentences:'), _('Ignore sentences:')]
		self.ofilter_select = wx.ComboBox(panel, choices=self.mode_ofilter, style=wx.CB_READONLY, size=(195, 32),
										  pos=(20, 125 + a))
		self.ofilter_select.SetValue(self.mode_ofilter[0])
		self.otalker = wx.TextCtrl(panel, -1, size=(29, 32), pos=(226, 125 + a))
		self.ofilter_T2 = wx.StaticText(panel, label=_('-'), pos=(253, 130 + a))
		self.osent = wx.TextCtrl(panel, -1, size=(39, 32), pos=(260, 125 + a))
		self.name_ofilter_select = wx.ComboBox(panel, choices=self.name_ifilter_list, style=wx.CB_READONLY,
											   size=(110, 32), pos=(305, 125 + a))
		self.ofilter_add_b = wx.Button(panel, label=_('Add sentence'), pos=(425, 125 + a))
		self.Bind(wx.EVT_BUTTON, self.ofilter_add, self.ofilter_add_b)
		self.ofilter_sentences = wx.TextCtrl(panel, -1, style=wx.CB_READONLY, size=(395, 32), pos=(20, 165 + a))
		self.ofilter_sentences.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_INACTIVECAPTION))
		self.ofilter_del_b = wx.Button(panel, label=_('Delete'), pos=(425, 165 + a))
		self.Bind(wx.EVT_BUTTON, self.ofilter_del, self.ofilter_del_b)

		self.ifilter_sentences.SetValue(_('nothing'))
		self.italker.SetValue('**')
		self.isent.SetValue('***')

		self.ofilter_sentences.SetValue(_('nothing'))
		self.otalker.SetValue('**')
		self.osent.SetValue('***')

		self.AP_examp_b = wx.Button(panel, label=_('AP examp'), pos=(20, 320))
		self.Bind(wx.EVT_BUTTON, self.AP_examp, self.AP_examp_b)

		self.GPS_examp_b = wx.Button(panel, label=_('GPS examp'), pos=(120, 320))
		self.Bind(wx.EVT_BUTTON, self.GPS_examp, self.GPS_examp_b)

		self.gpsd_examp_b = wx.Button(panel, label=_('gpsd examp'), pos=(220, 320))
		self.Bind(wx.EVT_BUTTON, self.gpsd_examp, self.gpsd_examp_b)

		self.ok = wx.Button(panel, label=_('OK'), pos=(425, 320))
		self.Bind(wx.EVT_BUTTON, self.ok_conn, self.ok)
		cancelBtn = wx.Button(panel, wx.ID_CANCEL, pos=(330, 320))

		if edit == 0:
			edit = ['0', '0', '0', '0', '0', '0', '0', '0', '0', -1]
			self.kplex_type.SetValue('Serial')
			self.kplex_baud_select.SetValue('4800')
			self.kplex_io_ser.SetValue('in')
			self.kplex_io_net.SetValue('in')
			self.switch_ser_net(True)
			self.switch_io_out(False)
		else:
			self.kplex_name.SetValue(edit[0])
			self.kplex_type.SetValue(edit[1])
			if edit[1] == 'Serial':
				self.kplex_io_ser.SetValue(edit[2])
				self.switch_ser_net(True)
				self.kplex_device_select.SetValue(edit[3])
				self.kplex_baud_select.SetValue(edit[4])
			else:
				self.kplex_io_net.SetValue(edit[2])
				self.switch_ser_net(False)
				self.kplex_address.SetValue(edit[3])
				self.kplex_netport.SetValue(edit[4])
			self.on_kplex_io_change(0)
			if edit[5] != _('none').decode("utf-8"):
				if edit[5] == _('accept').decode("utf-8"):
					self.ifilter_select.SetValue(self.mode_ifilter[1])
				if edit[5] == _('ignore').decode("utf-8"):
					self.ifilter_select.SetValue(self.mode_ifilter[2])
				self.ifilter_sentences.SetValue(edit[6])
			else:
				self.ifilter_select.SetValue(self.mode_ifilter[0])
			if edit[7] != _('none').decode("utf-8"):
				if edit[7] == _('accept').decode("utf-8"):
					self.ofilter_select.SetValue(self.mode_ofilter[1])
				if edit[7] == _('ignore').decode("utf-8"):
					self.ofilter_select.SetValue(self.mode_ofilter[2])
				self.ofilter_sentences.SetValue(edit[8])
			else:
				self.ofilter_select.SetValue(self.mode_ofilter[0])

	def GPS_examp(self, e):
		self.kplex_type.SetValue('Serial')
		self.kplex_io_ser.SetValue('in')
		self.switch_ser_net(True)
		self.switch_io_out(False)
		self.switch_io_in(True)
		self.kplex_baud_select.SetValue('4800')
		self.kplex_name.SetValue('gps')
		self.ifilter_select.SetValue(self.mode_ifilter[0])
		self.ifilter_sentences.SetValue(_('nothing'))
		self.ofilter_select.SetValue(self.mode_ifilter[0])
		self.ofilter_sentences.SetValue(_('nothing'))

	def AP_examp(self, e):
		self.kplex_type.SetValue('Serial')
		self.kplex_io_ser.SetValue('both')
		self.switch_ser_net(True)
		self.switch_io_out(True)
		self.switch_io_in(True)
		self.kplex_baud_select.SetValue('4800')
		self.kplex_name.SetValue('ap')
		self.ifilter_select.SetValue(self.mode_ifilter[1])
		self.ifilter_sentences.SetValue('**HDM,**RSA')
		self.ofilter_select.SetValue(self.mode_ifilter[1])
		self.ofilter_sentences.SetValue('**RM*,**VHW,**VWR')

	def gpsd_examp(self, e):
		self.kplex_type.SetValue('TCP')
		self.kplex_io_net.SetValue('in')
		self.switch_ser_net(False)
		self.switch_io_out(False)
		self.switch_io_in(True)
		self.switch_ser_net(False)
		self.kplex_address.SetValue('127.0.0.1')
		self.kplex_netport.SetValue('2947')
		self.kplex_baud_select.SetValue('4800')
		self.kplex_name.SetValue('gpsd')
		self.ifilter_select.SetValue(self.mode_ifilter[0])
		self.ifilter_sentences.SetValue(_('nothing'))
		self.ofilter_select.SetValue(self.mode_ifilter[0])
		self.ofilter_sentences.SetValue(_('nothing'))

	def SerialCheck(self):
		self.SerDevLs = [_('none')]
		context = self.parent.context
		for device in context.list_devices(subsystem='tty'):
			i = device['DEVNAME']
			if '/dev/ttyU' in i or '/dev/ttyA' in i or '/dev/ttyS' in i or '/dev/ttyO' in i or '/dev/r' in i or '/dev/i' in i or '/dev/naviDev' in i:
				self.SerDevLs.append(i[5:])
				try:
					ii = device['DEVLINKS']
					value = ii[ii.rfind('/dev/ttyOP_'):]
					if value.find('/dev/ttyOP_') >= 0:
						self.SerDevLs.append(value.split(' ')[0][5:])
				except:
					pass
		self.SerDevLs.sort()

	def ifilter_del(self, event):
		self.ifilter_sentences.SetValue(_('nothing'))

	def ofilter_del(self, event):
		self.ofilter_sentences.SetValue(_('nothing'))

	def ifilter_add(self, event):
		talker = self.italker.GetValue()
		sent = self.isent.GetValue()

		if not re.match('^[*A-Z]{2}$', talker):
			self.ShowMessage(_('Talker must have 2 uppercase characters. The symbol * matches any character.'))
			return
		if not re.match('^[*A-Z]{3}$', sent):
			self.ShowMessage(_('Sentence must have 3 uppercase characters. The symbol * matches any character.'))
			return

		r_sentence = talker + sent
		# if self.name_ifilter_select.GetValue()!='':
		#	r_sentence+='%'+self.name_ifilter_select.GetValue()
		if r_sentence == '*****':
			self.ShowMessage(_(
				'You must enter 2 uppercase characters for talker or 3 uppercase characters for sentence. The symbol * matches any character.'))
			return
		if r_sentence in self.ifilter_sentences.GetValue():
			self.ShowMessage(_('This sentence already exists.'))
			return
		if self.ifilter_sentences.GetValue() == _('nothing'):
			self.ifilter_sentences.SetValue(r_sentence)
		else:
			self.ifilter_sentences.SetValue(self.ifilter_sentences.GetValue() + ',' + r_sentence)

	def ofilter_add(self, event):
		talker = self.otalker.GetValue()
		sent = self.osent.GetValue()

		if not re.match('^[*A-Z]{2}$', talker):
			self.ShowMessage(_('Talker must have 2 uppercase characters. The symbol * matches any character.'))
			return
		if not re.match('^[*A-Z]{3}$', sent):
			self.ShowMessage(_('Sentence must have 3 uppercase characters. The symbol * matches any character.'))
			return

		r_sentence = talker + sent
		if self.name_ofilter_select.GetValue() != '':
			r_sentence += '%' + self.name_ofilter_select.GetValue()
		if r_sentence == '*****':
			self.ShowMessage(_(
				'You must enter 2 uppercase characters for talker or 3 uppercase characters for sentence. The symbol * matches any character.'))
			return
		if r_sentence in self.ofilter_sentences.GetValue():
			self.ShowMessage(_('This sentence already exists.'))
			return
		if self.ofilter_sentences.GetValue() == _('nothing'):
			self.ofilter_sentences.SetValue(r_sentence)
		else:
			self.ofilter_sentences.SetValue(self.ofilter_sentences.GetValue() + ',' + r_sentence)

	def on_kplex_type_change(self, event):
		if self.kplex_type.GetValue() == 'Serial':
			self.switch_ser_net(True)
		else:
			self.switch_ser_net(False)

	def switch_ser_net(self, b):
		self.kplex_ser_T1.Show(b)
		self.kplex_device_select.Show(b)
		self.kplex_ser_T2.Show(b)
		self.kplex_baud_select.Show(b)
		self.kplex_io_ser.Show(b)
		self.kplex_net_T1.Show(not b)
		self.kplex_address.Show(not b)
		self.kplex_net_T2.Show(not b)
		self.kplex_netport.Show(not b)
		self.kplex_io_net.Show(not b)

	def on_kplex_io_change(self, event):
		if self.kplex_type.GetValue() == 'Serial':
			in_out = str(self.kplex_io_ser.GetValue())
		else:
			in_out = str(self.kplex_io_net.GetValue())

		if in_out != 'out':
			self.switch_io_in(True)
		else:
			self.switch_io_in(False)
		if in_out != 'in':
			self.switch_io_out(True)
		else:
			self.switch_io_out(False)

	def switch_io_in(self, b):
		if b:
			self.ifilter_T1.Enable()
			self.ifilter_select.Enable()
			self.italker.Enable()
			self.ifilter_T2.Enable()
			self.isent.Enable()
			# self.name_ifilter_select.Enable()
			self.ifilter_add_b.Enable()
			self.ifilter_sentences.Enable()
			self.ifilter_del_b.Enable()
		else:
			self.ifilter_T1.Disable()
			self.ifilter_select.Disable()
			self.italker.Disable()
			self.ifilter_T2.Disable()
			self.isent.Disable()
			# self.name_ifilter_select.Disable()
			self.ifilter_add_b.Disable()
			self.ifilter_sentences.Disable()
			self.ifilter_del_b.Disable()
			self.ifilter_sentences.SetValue(_('nothing'))
			self.ifilter_select.SetValue(_('none'))

	def switch_io_out(self, b):
		if b:
			self.ofilter_T1.Enable()
			self.ofilter_select.Enable()
			self.otalker.Enable()
			self.ofilter_T2.Enable()
			self.osent.Enable()
			self.name_ofilter_select.Enable()
			self.ofilter_add_b.Enable()
			self.ofilter_sentences.Enable()
			self.ofilter_del_b.Enable()
		else:
			self.ofilter_T1.Disable()
			self.ofilter_select.Disable()
			self.otalker.Disable()
			self.ofilter_T2.Disable()
			self.osent.Disable()
			self.name_ofilter_select.Disable()
			self.ofilter_add_b.Disable()
			self.ofilter_sentences.Disable()
			self.ofilter_del_b.Disable()
			self.ofilter_sentences.SetValue(_('nothing'))
			self.ofilter_select.SetValue(_('none'))

	def create_gpsd(self, event):
		self.name.SetValue('gpsd')
		self.typeComboBox.SetValue('TCP')
		self.address.SetValue('127.0.0.1')
		self.port.SetValue('2947')

	def ok_conn(self, event):
		name = str(self.kplex_name.GetValue())
		name = name.replace(' ', '_')
		self.kplex_name.SetValue(name)
		type_conn = self.kplex_type.GetValue()
		port_address = ''
		bauds_port = ''
		if type_conn == 'Serial':
			in_out = str(self.kplex_io_ser.GetValue())
		else:
			in_out = str(self.kplex_io_net.GetValue())

		if not re.match('^[_0-9a-z]{1,13}$', name):
			self.ShowMessage(_(
				'"Name" must be a string between 1 and 13 lowercase letters and/or numbers which is not used as name for another input/output.'))
			return

		for index, sublist in enumerate(self.extkplex):
			if sublist[1] == name and index != self.index:
				self.ShowMessage(_('This name is already in use.'))
				return

		if name == 'system_input' or name == 'system_output':
			self.ShowMessage(_('This name is reserved by the system.'))
			return

		if type_conn == 'Serial':
			if str(self.kplex_device_select.GetValue()) != 'none':
				port_address = str(self.kplex_device_select.GetValue())
			else:
				self.ShowMessage(_('You must select a Port.'))
				return
			bauds_port = str(self.kplex_baud_select.GetValue())
			for index, sublist in enumerate(self.extkplex):
				if sublist[4] == port_address and index != self.index:
					self.ShowMessage(_('This output is already in use.'))
					return

		if type_conn == 'UDP' or type_conn == 'TCP':
			if self.kplex_address.GetValue():
				port_address = self.kplex_address.GetValue()
			else:
				self.ShowMessage(_('You must enter an Address.'))
				return
			if self.kplex_netport.GetValue():
				bauds_port = self.kplex_netport.GetValue()
			else:
				self.ShowMessage(_('You must enter a Port.'))
				return

			if bauds_port >= '10111' and bauds_port <= '10113' and type_conn == 'TCP':
				self.ShowMessage(_('Cancelled. Port 10111-10113 are reserved.'))
				return

			new_address_port = str(type_conn) + str(port_address) + str(bauds_port)
			for index, sublist in enumerate(self.extkplex):
				old_address_port = str(sublist[2]) + str(sublist[4]) + str(sublist[5])
				if old_address_port == new_address_port and index != self.index:
					self.ShowMessage(_('This input is already in use.'))
					return

		if self.ifilter_select.GetValue() == _('none') and self.ifilter_sentences.GetValue() != _('nothing'):
			self.ShowMessage(_('You must select a Filter type.'))
			return

		if self.ofilter_select.GetValue() == _('none') and self.ofilter_sentences.GetValue() != _('nothing'):
			self.ShowMessage(_('You must select a Filter type.'))
			return

		filter_type = _('none')
		filtering = _('nothing')

		if self.ifilter_select.GetValue().encode('utf8') == _('Accept only sentences:') and self.ifilter_sentences.GetValue() != _(
				'nothing'):
			filter_type = 'accept'
			filtering = ''
			r = self.ifilter_sentences.GetValue()
			l = r.split(',')
			for index, item in enumerate(l):
				if index != 0: filtering += ':'
				filtering += '+' + item
			filtering += ':-all'

		if self.ifilter_select.GetValue() == _('Ignore sentences:') and self.ifilter_sentences.GetValue() != _(
				'nothing'):
			filter_type = 'ignore'
			filtering = ''
			r = self.ifilter_sentences.GetValue()
			l = r.split(',')
			for index, item in enumerate(l):
				if index != 0: filtering += ':'
				filtering += '-' + item

		ofilter_type = _('none')
		ofiltering = _('nothing')

		if self.ofilter_select.GetValue().encode('utf8') == _('Accept only sentences:') and self.ofilter_sentences.GetValue() != _(
				'nothing'):
			ofilter_type = 'accept'
			ofiltering = ''
			r = self.ofilter_sentences.GetValue()
			l = r.split(',')
			for index, item in enumerate(l):
				if index != 0: ofiltering += ':'
				ofiltering += '+' + item
			ofiltering += ':-all'

		if self.ofilter_select.GetValue() == _('Ignore sentences:') and self.ofilter_sentences.GetValue() != _(
				'nothing'):
			ofilter_type = 'ignore'
			ofiltering = ''
			r = self.ofilter_sentences.GetValue()
			l = r.split(',')
			for index, item in enumerate(l):
				if index != 0: ofiltering += ':'
				ofiltering += '-' + item

		self.add_kplex_out = ['None', name, type_conn, in_out, port_address, bauds_port, filter_type, filtering,
							  ofilter_type, ofiltering, '1', self.index]
		# print self.add_kplex_out
		self.result = self.add_kplex_out
		self.Destroy()

	def ShowMessage(self, w_msg):
		wx.MessageBox(w_msg, 'Info', wx.OK | wx.ICON_INFORMATION)
