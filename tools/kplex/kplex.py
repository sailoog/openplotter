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

import wx, os, sys, subprocess, webbrowser, time, re

op_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../..')
sys.path.append(op_folder+'/classes')
from conf import Conf
from language import Language
from add_kplex import addkplex
from wx.lib.mixins.listctrl import CheckListCtrlMixin, ListCtrlAutoWidthMixin

class CheckListCtrl(wx.ListCtrl, CheckListCtrlMixin, ListCtrlAutoWidthMixin):
	def __init__(self, parent, width, height):
		wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER, size=(width, height))
		CheckListCtrlMixin.__init__(self)
		ListCtrlAutoWidthMixin.__init__(self)

class MyFrame(wx.Frame):
		
	def __init__(self):
		self.conf = Conf()
		self.home = self.conf.home
		self.op_folder = op_folder
		self.help_bmp = wx.Bitmap(self.op_folder + "/static/icons/help-browser.png", wx.BITMAP_TYPE_ANY)
		Language(self.conf)
		wx.Frame.__init__(self, None, title=_('Kplex GUI - NMEA 0183 Multiplexer'), size=(710,460))
		self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
		self.icon = wx.Icon(self.op_folder+'/static/icons/kplex.ico', wx.BITMAP_TYPE_ICO)
		self.SetIcon(self.icon)

		self.list_kplex = CheckListCtrl(self, 650, 152)
		self.list_kplex.InsertColumn(0, _('Name'), width=130)
		self.list_kplex.InsertColumn(1, _('Type'), width=45)
		self.list_kplex.InsertColumn(2, _('io'), width=45)
		self.list_kplex.InsertColumn(3, _('Port/Address'), width=95)
		self.list_kplex.InsertColumn(4, _('Bauds/Port'), width=60)
		self.list_kplex.InsertColumn(5, _('inFilter'), width=55)
		self.list_kplex.InsertColumn(6, _('Filtering'), width=80)
		self.list_kplex.InsertColumn(7, _('outFilter'), width=60)
		self.list_kplex.InsertColumn(8, _('Filtering'), width=80)
		self.list_kplex.InsertColumn(9, _('Optional'), width=10)
		self.list_kplex.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.edit_kplex)

		diagnostic = wx.Button(self, label=_('Diagnostic'))
		diagnostic.Bind(wx.EVT_BUTTON, self.on_diagnostic_kplex)

		add = wx.Button(self, label=_('add'))
		add.Bind(wx.EVT_BUTTON, self.on_add_kplex)
		delete = wx.Button(self, label=_('delete'))
		delete.Bind(wx.EVT_BUTTON, self.on_delete_kplex)

		help_button = wx.BitmapButton(self, bitmap=self.help_bmp, size=(self.help_bmp.GetWidth()+40, self.help_bmp.GetHeight()+10))
		help_button.Bind(wx.EVT_BUTTON, self.on_help_kplex)
		restart = wx.Button(self, label=_('Restart'))
		restart.Bind(wx.EVT_BUTTON, self.on_restart_kplex)
		advanced = wx.Button(self, label=_('Advanced'))
		advanced.Bind(wx.EVT_BUTTON, self.on_advanced_kplex)
		apply_changes = wx.Button(self, label=_('Apply changes'))
		apply_changes.Bind(wx.EVT_BUTTON, self.on_apply_changes_kplex)
		cancel_changes = wx.Button(self, label=_('Cancel changes'))
		cancel_changes.Bind(wx.EVT_BUTTON, self.on_cancel_changes_kplex)

		hlistbox = wx.BoxSizer(wx.HORIZONTAL)
		hlistbox.Add(self.list_kplex, 1, wx.ALL | wx.EXPAND, 5)

		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add((0, 0), 1, wx.RIGHT | wx.LEFT, 5)
		hbox.Add(add, 0, wx.RIGHT | wx.LEFT, 5)
		hbox.Add(delete, 0, wx.RIGHT | wx.LEFT, 5)

		hboxb = wx.BoxSizer(wx.HORIZONTAL)
		hboxb.Add(help_button, 0, wx.RIGHT | wx.EXPAND, 5)
		hboxb.Add(diagnostic, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)
		hboxb.Add(restart, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)
		hboxb.Add(advanced, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)
		hboxb.Add((0, 0), 1, wx.RIGHT | wx.LEFT, 5)
		hboxb.Add(apply_changes, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)
		hboxb.Add(cancel_changes, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)

		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.Add(hlistbox, 1, wx.ALL | wx.EXPAND, 0)
		vbox.Add(hbox, 0, wx.ALL | wx.EXPAND, 5)
		vbox.AddSpacer(5)
		vbox.Add(hboxb, 0, wx.ALL | wx.EXPAND, 5)

		self.SetSizer(vbox)
		self.CreateStatusBar()
		font_statusBar = self.GetStatusBar().GetFont()
		font_statusBar.SetWeight(wx.BOLD)
		self.GetStatusBar().SetFont(font_statusBar)
		self.Centre()
		self.manual_settings = ''
		self.read_kplex_conf()

	def on_advanced_kplex(self, event):
		self.ShowMessage(_(
			'Kplex GUI will close. Add manual settings at the end of the configuration file. Open kplex GUI again and restart to apply changes.'))
		subprocess.Popen(['leafpad', self.home + '/.kplex.conf'])
		self.Close()

	def on_restart_kplex(self, event):
		msg = _('Restarting kplex... ')
		seconds = 5
		subprocess.call(['pkill', '-f', 'diagnostic-NMEA.py'])
		subprocess.call(['pkill', '-15', 'kplex'])
		for i in range(seconds, 0, -1):
			self.ShowStatusBarYELLOW(msg+str(i))
			time.sleep(1)
		subprocess.Popen('kplex')
		self.ShowStatusBarGREEN(_('Kplex restarted'))

	def stop_kplex(self):
		subprocess.call(['pkill', '-15', 'kplex'])

	def on_cancel_changes_kplex(self, event):
		self.read_kplex_conf()
		self.ShowStatusBarBLACK('')

	def edit_kplex(self, e):
		idx = e.GetIndex()
		edit = []
		edit.append(self.list_kplex.IsChecked(idx))
		for i in range(10):
			edit.append(self.list_kplex.GetItem(idx, i).GetText())
		edit.append(idx)
		self.edit_add_kplex(edit)

	def on_add_kplex(self, e):
		self.edit_add_kplex(0)

	def edit_add_kplex(self, edit):
		dlg = addkplex(edit, self.kplex, self)
		dlg.ShowModal()
		result = dlg.result
		dlg.Destroy()
		if result != 0:
			k = int(result[11])
			if edit == 0:
				self.kplex.append(result)
				self.set_list_kplex()
			else:
				for i in range(12):
					self.kplex[k][i] = result[i]				
				self.set_list_kplex()

	def read_kplex_conf(self):
		self.kplex = []
		try:
		#if True:
			file = open(self.home + '/.kplex.conf', 'r')
			data = file.readlines()
			file.close()
			#active, name, type_conn, in_out, port_address, bauds_port, filter_type, filtering, ofilter_type, ofiltering, optio, self.index
			#	0	   1	2			3		4				5			6			7			8			9			10		11
			active = False
			name = ''
			type_conn =''
			in_out = ''
			port_address = ''
			bauds_port = ''
			filter_type = ''
			filtering = ''
			ofilter_type = ''
			ofiltering = ''
			optio = '0'
			self.index = -1
			
			self.manual_settings = ''
			for index, item in enumerate(data):
				if self.manual_settings:
					if item != '\n': self.manual_settings += item
				else:
					if re.search('\[*\]', item):
						if in_out in ['in','out','both']:
							self.kplex.append([active, name, type_conn, in_out, port_address, bauds_port, filter_type, filtering, ofilter_type, ofiltering, optio, self.index])
						optio = '0'
						filter_type = 'none'
						filtering = 'nothing'
						ofilter_type = 'none'
						ofiltering = 'nothing'
						if '[serial]' in item: 
							type_conn = 'Serial'
							self.index += 1
						if '[tcp]' in item: 
							type_conn = 'TCP'
							self.index += 1
						if '[udp]' in item: 
							type_conn = 'UDP'
							self.index += 1
						if '#[' in item:
							active = False
							self.index += 1
						else:
							active = True
					if 'direction=in' in item:
						in_out = 'in'
					if 'direction=out' in item:
						in_out = 'out'
					if 'direction=both' in item:
						in_out = 'both'
					if 'name=' in item and 'filename=' not in item:
						name = self.extract_value(item)
					if 'address=' in item or 'filename=' in item:
						port_address = self.extract_value(item)
					if 'port=' in item or 'baud=' in item:
						bauds_port = self.extract_value(item)
					if 'ifilter=' in item and '-all' in item:
						filter_type = 'accept'
						filtering = self.extract_value(item)
					if 'ifilter=' in item and '-all' not in item:
						filter_type = 'ignore'
						filtering = self.extract_value(item)
					if 'ofilter=' in item and '-all' in item:
						ofilter_type = 'accept'
						ofiltering = self.extract_value(item)
					if 'ofilter=' in item and '-all' not in item:
						ofilter_type = 'ignore'
						ofiltering = self.extract_value(item)
					if 'optional=yes' in item:
						optio = '1'
					if '###Manual settings' in item:
						self.manual_settings = '###Manual settings\n\n'

			if in_out in ['in','out','both']:
				self.kplex.append([active, name, type_conn, in_out, port_address, bauds_port, filter_type, filtering, ofilter_type, ofiltering, optio, self.index])

			self.set_list_kplex()

		except: print 'ERROR reading kplex conf file'

	def extract_value(self, data):
		option, value = data.split('=')
		value = value.strip()
		return value

	def set_list_kplex(self):
		self.list_kplex.DeleteAllItems()
		index = 1
		for i in self.kplex:
			if i[1]:
				index = self.list_kplex.InsertStringItem(sys.maxint, i[1])

			if i[2]: self.list_kplex.SetStringItem(index, 1, i[2])
			if i[3]: self.list_kplex.SetStringItem(index, 2, i[3])
			else:    self.list_kplex.SetStringItem(index, 2, '127.0.0.1')
			if i[4]: self.list_kplex.SetStringItem(index, 3, i[4])
			if i[5]: self.list_kplex.SetStringItem(index, 4, i[5])
			if i[6]:
				if i[6] == 'none': self.list_kplex.SetStringItem(index, 5, _('none'))
				if i[6] == 'accept': self.list_kplex.SetStringItem(index, 5, _('accept'))
				if i[6] == 'ignore': self.list_kplex.SetStringItem(index, 5, _('ignore'))
			if i[7] == 'nothing':
				self.list_kplex.SetStringItem(index, 6, _('nothing'))
			else:
				filters = i[7].replace(':-all', '')
				filters = filters.replace('+', '')
				filters = filters.replace('-', '')
				filters = filters.replace(':', ',')
				self.list_kplex.SetStringItem(index, 6, filters)
			if i[8]:
				if i[8] == 'none': self.list_kplex.SetStringItem(index, 7, _('none'))
				if i[8] == 'accept': self.list_kplex.SetStringItem(index, 7, _('accept'))
				if i[8] == 'ignore': self.list_kplex.SetStringItem(index, 7, _('ignore'))
			if i[9] == 'nothing':
				self.list_kplex.SetStringItem(index, 8, _('nothing'))
			else:
				filters = i[9].replace(':-all', '')
				filters = filters.replace('+', '')
				filters = filters.replace('-', '')
				filters = filters.replace(':', ',')
				self.list_kplex.SetStringItem(index, 8, filters)
			self.list_kplex.SetStringItem(index, 9,i[10])
			if i[0]: 
				self.list_kplex.CheckItem(index)
				self.list_kplex.SetItemBackgroundColour(index,(102,205,170))

	def on_apply_changes_kplex(self, event):
		state = ''
		data = '# For advanced manual configuration, please visit: http://www.stripydog.com/kplex/configuration.html\n# Please do not modify kplex GUI settings.\n# Add manual settings at the end of the document.\n\n'
		data += '###kplex GUI settings\n\n'

		for index, item in enumerate(self.kplex):
			if self.list_kplex.IsChecked(index):
				state = ''
			else:
				state = '#'
				
			optional=''
			if item[10] == '1':
				optional = 'optional=yes\n'

			if 'Serial' in item[2]:
				data += state + '[serial]\n' + state + 'name=' + item[1] + '\n' + state + 'direction=' + item[
					3] + '\n' + state + optional
				data += state + 'filename=' + item[4] + '\n' + state + 'baud=' + item[5] + '\n'
			if 'TCP' in item[2]:
				data += state + '[tcp]\n' + state + 'name=' + item[1] + '\n' + state + 'direction=' + item[
					3] + '\n' + state + optional
				if item[1] == 'gpsd': data += state + 'gpsd=yes\n'
				if item[3] <> 'out':
					data += state + 'mode=client\n'
					data += state + 'persist=yes\n' + state + 'retry=10\n'
				else:
					data += state + 'mode=server\n'
				if item[4]: data += state + 'address=' + str(item[4]) + '\n' 
				data += state + 'port=' + str(item[5]) + '\n'
			if 'UDP' in item[2]:
				data += state + '[udp]\n' + state + 'name=' + item[1] + '\n' + state + 'direction=' + item[
					3] + '\n' + state + optional
				data += state + 'address=' + item[4] + '\n' + state + 'port=' + item[5] + '\n'

			if not (item[6] == _('none') or item[6] == 'none') and not (item[7] == _('nothing') or item[7] == 'nothing'): 
				data += state + 'ifilter=' + item[7] + '\n'
			if not (item[8] == _('none') or item[8] == 'none') and not (item[9] == _('nothing') or item[9] == 'nothing'): 
				data += state + 'ofilter=' + item[9] + '\n'
			data += '\n'

		data += '###end of kplex GUI settings\n\n'
		if self.manual_settings:
			data += self.manual_settings
		else:
			data += '###Manual settings\n\n'

		file = open(self.home + '/.kplex.conf', 'w')
		file.write(data)
		file.close()
		self.on_restart_kplex(0)
		self.read_kplex_conf()

	def on_delete_kplex(self, event):
		selected = self.list_kplex.GetFirstSelected()
		if selected == -1:
			self.ShowStatusBarYELLOW(_('Select an item.'))
			return
		num = len(self.kplex)
		for i in range(num):
			if self.list_kplex.IsSelected(i):	
				del self.kplex[i]
		self.set_list_kplex()

	def on_diagnostic_kplex(self, event):
		selected = self.list_kplex.GetFirstSelected()
		if selected == -1:
			self.ShowStatusBarYELLOW(_('Select an item.'))
			return
		num = len(self.kplex)
		for i in range(num):
			if self.list_kplex.IsSelected(i):
				if self.list_kplex.IsChecked(i):
					file = open(self.home + '/.kplex.conf', 'r')
					data = file.read()
					file.close()

					if self.kplex[i][3] == 'in' or self.kplex[i][3] == 'both':
						data = data + '\n\n[tcp]\nname=system_debugi\ndirection=out\nofilter=+*****%' + self.kplex[i][
							1] + ':-all\nmode=server\nport=10112\n\n'
					if self.kplex[i][3] == 'out' or self.kplex[i][3] == 'both':
						data += '\n\n[tcp]\nname=system_debugo\ndirection=out\n'
						if self.kplex[i][8] != 'none' and self.kplex[i] != 'nothing': data += 'ofilter=' + \
																							  self.kplex[i][9] + '\n'
						data += 'mode=server\nport=10113\n\n'

					file = open(self.home + '/.debugkplex.conf', 'w')
					file.write(data)
					file.close()

					self.stop_kplex()
					time.sleep(0.2)
					subprocess.Popen(['kplex', '-f', self.home + '/.debugkplex.conf'])
					time.sleep(0.5)
					subprocess.call(['pkill', '-f', 'diagnostic-NMEA.py'])
					if self.kplex[i][3] == 'in' or self.kplex[i][3] == 'both':
						subprocess.Popen(['python', self.op_folder+'/tools/kplex/diagnostic-NMEA.py', '10112'])
					if self.kplex[i][3] == 'out' or self.kplex[i][3] == 'both':
						subprocess.Popen(['python', self.op_folder+'/tools/kplex/diagnostic-NMEA.py', '10113'])

	def ShowMessage(self, w_msg):
		wx.MessageBox(w_msg, 'Info', wx.OK | wx.ICON_INFORMATION)
		
	def ShowStatusBar(self, w_msg, colour):
		self.GetStatusBar().SetForegroundColour(colour)
		self.SetStatusText(w_msg)

	def ShowStatusBarRED(self, w_msg):
		self.ShowStatusBar(w_msg, wx.RED)

	def ShowStatusBarGREEN(self, w_msg):
		self.ShowStatusBar(w_msg, wx.GREEN)

	def ShowStatusBarBLACK(self, w_msg):
		self.ShowStatusBar(w_msg, wx.BLACK)	

	def ShowStatusBarYELLOW(self, w_msg):
		self.ShowStatusBar(w_msg,(255,140,0))	

	def on_help_kplex(self, e):
		url = self.op_folder+"/docs/html/tools/kplex.html"
		webbrowser.open(url, new=2)

app = wx.App()
MyFrame().Show()
app.MainLoop()