#!/usr/bin/env python

# This file is part of Openplotter.
# Copyright (C) 2016 by sailoog <https://github.com/sailoog/openplotter>
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

import wx, os, sys, socket, time, ConfigParser, subprocess

op_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')
sys.path.append(op_folder+'/classes')
from conf import Conf
from language import Language

class MyFrame(wx.Frame):
	def __init__(self):
		self.conf = conf
		self.home = home
		self.currentpath = self.home+self.conf.get('GENERAL', 'op_folder')+'/openplotter'

		self.tick=0
		self.deg2rad=0.0174533
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

		self.Slider=[]
		self.Slider_v=[]
		self.HSlider=[]
		self.Slider_list=[]
		
		Language(self.conf)
		
		wx.Frame.__init__(self, None, title="SK-Simulator", size=(650,435))
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		self.panel = wx.Panel(self)
		self.vbox = wx.BoxSizer(wx.VERTICAL)

		self.ttimer=500
		self.timer = wx.Timer(self)
		self.Bind(wx.EVT_TIMER, self.timer_act, self.timer)		
		
		self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
		
		self.icon = wx.Icon(self.currentpath+'/openplotter.ico', wx.BITMAP_TYPE_ICO)
		self.SetIcon(self.icon)

		self.read_conf()
		
		#self.SK_Slider(0,'navigation.courseOverGroundTrue',0,0,360,self.deg2rad,0)
		for i in self.Slider_list:
			self.SK_Slider_conf(i[0],i[1],i[2],i[3],i[4],i[5],i[6])
		
		self.Bind(wx.EVT_CHECKBOX, self.on_change_checkbox)
		
		allBtn = wx.Button(self.panel, label=_('all'),size=(70, 32), pos=(450, 360))
		allBtn.Bind(wx.EVT_BUTTON, self.allBtn)
		
		noneBtn = wx.Button(self.panel, label=_('none'),size=(70, 32), pos=(550, 360))
		noneBtn.Bind(wx.EVT_BUTTON, self.noneBtn)
		
		HButton = wx.BoxSizer(wx.HORIZONTAL)
		HButton.Add((0,0), 1, wx.ALL|wx.EXPAND, 5)
		HButton.Add(noneBtn, 0, wx.ALL|wx.EXPAND, 5)
		HButton.Add(allBtn, 0, wx.ALL|wx.EXPAND, 5)
		
		self.vbox.Add((0,0), 1, wx.ALL|wx.EXPAND, 5)		
		self.vbox.Add(HButton, 0, wx.ALL|wx.EXPAND, 5)		
		self.panel.SetSizer(self.vbox)				
		
		self.Centre()

		self.Show(True)
		
		self.timer.Start(self.ttimer)
		

	def SK_Slider(self,index,get_label,get_start,get_min,get_max,get_factor,get_offset):
		self.Slider.append([])
		self.Slider_v.append([])
		self.HSlider.append([])
		self.Slider_list.append([index,get_label,get_start,get_min,get_max,get_factor,get_offset,False])
		self.Slider[index]= wx.CheckBox(self.panel, label=get_label)
		
		self.Slider_v[index] = wx.Slider(self.panel, -1, get_start, get_min, get_max, (-1,-1), (250, -1), wx.SL_AUTOTICKS | wx.SL_HORIZONTAL | wx.SL_VALUE_LABEL)
		
		self.HSlider[index] = wx.BoxSizer(wx.HORIZONTAL)
		self.HSlider[index].Add(self.Slider[index], 0, wx.ALL|wx.EXPAND, 5)
		self.HSlider[index].Add((0,0), 1, wx.ALL|wx.EXPAND, 0)
		self.HSlider[index].Add(self.Slider_v[index], 0, wx.ALL|wx.EXPAND, 5)
		self.vbox.Add(self.HSlider[index], 0, wx.ALL|wx.EXPAND, 5)
		
	def SK_Slider_conf(self,index,get_label,get_start,get_min,get_max,get_factor,get_offset):
		self.Slider.append([])
		self.Slider_v.append([])
		self.HSlider.append([])
		self.Slider[index]= wx.CheckBox(self.panel, label=get_label)
		
		self.Slider_v[index] = wx.Slider(self.panel, -1, get_start, get_min, get_max, (-1,-1), (250, -1), wx.SL_AUTOTICKS | wx.SL_HORIZONTAL | wx.SL_VALUE_LABEL)
		
		self.HSlider[index] = wx.BoxSizer(wx.HORIZONTAL)
		self.HSlider[index].Add(self.Slider[index], 0, wx.ALL|wx.EXPAND, 5)
		self.HSlider[index].Add((0,0), 1, wx.ALL|wx.EXPAND, 0)
		self.HSlider[index].Add(self.Slider_v[index], 0, wx.ALL|wx.EXPAND, 5)
		self.vbox.Add(self.HSlider[index], 0, wx.ALL|wx.EXPAND, 5)
		
	def read_conf(self):
		self.data_conf = ConfigParser.SafeConfigParser()
		self.data_conf.read(self.home+'/.openplotter/SK-simulator.conf')
		if not self.data_conf.has_section('main'):
			value=[0,'navigation.courseOverGroundTrue',0,0,360,self.deg2rad,0]
			cfgfile = open(self.home+'/.openplotter/SK-simulator.conf','w')
			self.data_conf.add_section('main')
			self.data_conf.set('main','item_0', str(value))
			self.data_conf.write(cfgfile)
			
			self.data_conf.read(self.home+'/.openplotter/SK-simulator.conf')			
			
		self.Slider_list=[]
		for i in range(40):
			if self.data_conf.has_option('main','item_'+str(i)):
				data=self.data_conf.get('main','item_'+str(i))
				try:
					temp_list=eval(data)
				except:temp_list=[]
				if temp_list!=[]:
					temp_list.append(0)
				self.Slider_list.append(temp_list)
		
	def allBtn(self,e):
		self.setCheckbox(True)
	
	def noneBtn(self,e):
		self.setCheckbox(False)

	def setCheckbox(self, value):
		for i in self.Slider_list:
			self.Slider[i[0]].SetValue(value)
			i[7]=value

	def on_change_checkbox(self,e):
		for i in self.Slider_list:
			i[7]=self.Slider[i[0]].GetValue()
			
	# thread
	def timer_act(self, event):
		SignalK = '{"updates": [{"$source":"OPsimulation","values":[ '
		Erg=''
		for i in self.Slider_list:
			if i[7]:
				Erg += '{"path": "'+i[1]+'","value":'+str(self.Slider_v[i[0]].GetValue()*i[5]+i[6])+'},'
		if Erg!='':
			SignalK +=Erg[0:-1]+']}]}\n'
			self.sock.sendto(SignalK, ('127.0.0.1', 55557))
	# end thread

	def OnClose(self, event):
		self.timer.Stop()
		self.Destroy()

conf = Conf()
home = conf.home

if len(sys.argv)>1:
	if sys.argv[1]=='settings':
		subprocess.Popen(['leafpad', home+'/.openplotter/SK-simulator.conf'])
else:
	app = wx.App()
	MyFrame().Show()
	app.MainLoop()