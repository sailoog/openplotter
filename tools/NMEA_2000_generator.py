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
import wx, os, sys
from wx.lib.mixins.listctrl import CheckListCtrlMixin, ListCtrlAutoWidthMixin

op_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')
sys.path.append(op_folder+'/classes')
from conf import Conf
from language import Language

class CheckListCtrl(wx.ListCtrl, CheckListCtrlMixin, ListCtrlAutoWidthMixin):
	def __init__(self, parent, height):
		wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER, size=(565, height))
		CheckListCtrlMixin.__init__(self)
		ListCtrlAutoWidthMixin.__init__(self)

class MyFrame(wx.Frame):
	def __init__(self):
		self.conf = Conf()
		self.home = self.conf.home
		self.currentpath = self.home+self.conf.get('GENERAL', 'op_folder')+'/openplotter'
		Language(self.conf)
		
		wx.Frame.__init__(self, None, title=_('Generate N2K from Signal K'), size=(630, 300))
		self.Bind(wx.EVT_CLOSE, self.when_closed)
		#self.SetAutoLayout(1)
		#self.SetupScrolling()

		self.icon = wx.Icon(self.currentpath + '/openplotter.ico', wx.BITMAP_TYPE_ICO)
		self.SetIcon(self.icon)
		
		self.panel = wx.Panel(self)

		self.list_N2Kgen = [
			['126992','System Time',''],
			['127245','Rudder','steering.rudderAngle.value'],
			['127250','Heading','navigation.headingMagnetic.value'],
			['127257','Attitude','navigation.attitude.pitch.value, navigation.attitude.roll.value, navigation.attitude.yaw.value'],
			['127488','Engine_Rapid','propulsion.port.revolutions.value'],
			['127488_1','Engine_Rapid','propulsion.starboard.revolutions.value'],
			['127489','Engine','propulsion.port.oilTemperature.value, propulsion.port.temperature.value'],
			['127489_1','Engine','propulsion.starboard.oilTemperature.value, propulsion.starboard.temperature.value'],
			['127505','FluidLevel','tanks.fuel.standard.capacity.value, tanks.fuel.standard.currentLevel.value'],
			['127505_1','FluidLevel','tanks.liveWell.standard.capacity.value, tanks.liveWell.standard.currentLevel.value'],
			['127505_2','FluidLevel','tanks.wasteWater.standard.capacity.value, tanks.wasteWater.standard.currentLevel.value'],
			['127505_3','FluidLevel','tanks.blackWater.standard.capacity.value, tanks.blackWater.standard.currentLevel.value'],
			['127508','Battery_Status','DC Electrical Properties.dcSource.voltage.value, DC Electrical Properties.dcSource.current.value, DC Electrical Properties.dcSource.temperature.value'],
			['128259','Speed','navigation.speedOverGround.value, navigation.speedThroughWater.value'],
			['128267','Depth','environment.depth.belowTransducer.value, environment.depth.surfaceToTransducer.value'],
			['128275','Distance_Log','navigation.log.value, navigation.logTrip.value'],
			['129025','Position_Rapid','navigation.position.latitude, navigation.position.longitude'],
			['129026','COG_SOG','navigation.courseOverGroundTrue.value, navigation.speedOverGround.value'],
			['130306_2','Wind Data','environment.wind.angleApparent.value, environment.wind.speedApparent.value'],
			['130306_3','Wind Data','environment.wind.angleTrueWater.value, environment.wind.speedTrue.value'],
			['130310','Environmental_Parameters','environment.outside.pressure.value, environment.outside.temperature.value, environment.water.temperature.value'],
			['130311','Environmental_Parameters','environment.outside.pressure.value, environment.inside.humidity.value, environment.water.temperature.value'],
			['130316','Temperature','environment.inside.refrigerator.temperature.value'],
			['130316_1','Temperature','propulsion.port.exhaustTemperature.value']
		]
		
		self.list_N2K = CheckListCtrl(self.panel, 100)
		self.list_N2K.InsertColumn(0, _('PGN'), width=100)
		self.list_N2K.InsertColumn(1, _('description'), width=250)
		self.list_N2K.InsertColumn(2, _('Signal K variable'), width=920)
		self.list_N2K.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_selected)

		OK = wx.Button(self.panel, label=_('OK'))
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
	
		self.when_closed(e)
		
	def on_selected(self,e):
		pass
		
	def when_closed(self,e):
		self.Destroy()

		
app = wx.App()
MyFrame().Show()
app.MainLoop()