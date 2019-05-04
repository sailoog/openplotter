#!/usr/bin/env python

# This file is part of Openplotter.
# Copyright (C) 2015 by sailoog <https://github.com/sailoog/openplotter>
# 					  e-sailing <https://github.com/e-sailing/openplotter>
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
import wx, subprocess
from wx.lib.mixins.listctrl import CheckListCtrlMixin, ListCtrlAutoWidthMixin
from classes.conf import Conf
from classes.language import Language

class CheckListCtrl(wx.ListCtrl, CheckListCtrlMixin, ListCtrlAutoWidthMixin):
	def __init__(self, parent, height):
		wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER, size=(565, height))
		CheckListCtrlMixin.__init__(self)
		ListCtrlAutoWidthMixin.__init__(self)

class addSKtoN2K(wx.Dialog):
	def __init__(self):
		self.conf = Conf()
		self.home = self.conf.home
		self.currentpath = self.conf.get('GENERAL', 'op_folder')
		Language(self.conf)
		style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
		wx.Dialog.__init__(self, None, title=_('Generate N2K from Signal K'),style=style)
		self.Bind(wx.EVT_CLOSE, self.when_closed)
		self.SetInitialSize((720, 400))
		#self.SetAutoLayout(1)
		#self.SetupScrolling()

		self.icon = wx.Icon(self.currentpath + '/static/icons/openplotter.ico', wx.BITMAP_TYPE_ICO)
		self.SetIcon(self.icon)
		
		self.panel = wx.Panel(self)

		self.list_N2Kgen = [
			['126992','System Time',''],
			['127245','Rudder','steering.rudderAngle'],
			['127250','Heading','navigation.headingMagnetic'],
			['127257','Attitude','navigation.attitude.pitch, navigation.attitude.roll, navigation.attitude.yaw'],
			['127488','Engine_Rapid','propulsion.port.revolutions'],
			['127488_1','Engine_Rapid','propulsion.starboard.revolutions'],
			['127489','Engine','propulsion.port.oilTemperature, propulsion.port.temperature'],
			['127489_1','Engine','propulsion.starboard.oilTemperature, propulsion.starboard.temperature'],
			['127505','FluidLevel','tanks.fuel.standard.capacity, tanks.fuel.standard.currentLevel'],
			['127505_1','FluidLevel','tanks.liveWell.standard.capacity, tanks.liveWell.standard.currentLevel'],
			['127505_2','FluidLevel','tanks.wasteWater.standard.capacity, tanks.wasteWater.standard.currentLevel'],
			['127505_3','FluidLevel','tanks.blackWater.standard.capacity, tanks.blackWater.standard.currentLevel'],
			['127508','Battery_Status','electrical.batteries.service.voltage, electrical.batteries.service.current, electrical.batteries.service.temperature'],
			['128259','Speed','navigation.speedOverGround, navigation.speedThroughWater'],
			['128267','Depth','environment.depth.belowTransducer, environment.depth.surfaceToTransducer'],
			['128275','Distance_Log','navigation.log, navigation.logTrip'],
			['129025','Position_Rapid','navigation.position.latitude, navigation.position.longitude'],
			['129026','COG_SOG','navigation.courseOverGroundTrue, navigation.speedOverGround'],
			['130306_2','Wind Data','environment.wind.angleApparent, environment.wind.speedApparent'],
			['130306_3','Wind Data','environment.wind.angleTrueWater, environment.wind.speedTrue'],
			['130310','Environmental_Parameters','environment.outside.pressure, environment.outside.temperature, environment.water.temperature'],
			['130311','Environmental_Parameters','environment.outside.pressure, environment.inside.humidity, environment.water.temperature'],
			['130316','Temperature','environment.inside.refrigerator.temperature'],
			['130316_1','Temperature','propulsion.port.exhaustTemperature']
		]
		
		self.list_N2K = CheckListCtrl(self.panel, 100)
		self.list_N2K.InsertColumn(0, _('PGN'), width=100)
		self.list_N2K.InsertColumn(1, _('description'), width=250)
		self.list_N2K.InsertColumn(2, _('Signal K variable'), width=920)
		self.list_N2K.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_selected)

		OK = wx.Button(self.panel, label=_('Apply changes'))
		OK.Bind(wx.EVT_BUTTON, self.on_OK)

		hlistbox = wx.BoxSizer(wx.HORIZONTAL)
		hlistbox.Add(self.list_N2K, 1, wx.ALL | wx.EXPAND, 5)

		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.Add(hlistbox, 1, wx.ALL | wx.EXPAND, 0)
		vbox.Add(OK, 0, wx.ALL, 5)

		self.panel.SetSizer(vbox)		
		
		for ii in self.list_N2Kgen:
			self.list_N2K.Append(ii)
		
		data = self.conf.get('N2K', 'pgn_generate')
		try:
			self.PGN_list = eval(data)
		except:
			self.PGN_list = []
		i=0
		for ii in self.list_N2Kgen:
			if str(ii[0]) in self.PGN_list:
				self.list_N2K.CheckItem(i)
			i += 1
			
			
	def on_OK(self,e):
		result = []
		i=0
		for ii in self.list_N2Kgen:
			if self.list_N2K.IsChecked(i):
				result.append(str(ii[0]))
			i += 1
		self.conf.set('N2K', 'pgn_generate', str(result))
		N2K_output=self.conf.get('N2K', 'output')
		if N2K_output == '1':
			subprocess.call(['pkill', '-f', 'SK-base_d.py'])
			subprocess.Popen(['python',self.currentpath+'/SK-base_d.py'])		
	
		self.when_closed(e)
		
	def on_selected(self,e):
		pass
		
	def when_closed(self,e):
		self.Destroy()

		
#app = wx.App()
#MyFrame().Show()
#app.MainLoop()
