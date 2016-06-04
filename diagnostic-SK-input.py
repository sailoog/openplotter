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

import wx, sys, socket, time, webbrowser, serial, requests
from classes.datastream import DataStream
from classes.paths import Paths
from classes.conf import Conf
from classes.language import Language

class MyFrame(wx.Frame):
		
		def __init__(self):
			self.ttimer=300
			
			self.home=Paths().home
			self.currentpath=Paths().currentpath
			self.conf=Conf()
			self.ser = serial.Serial(self.conf.get('N2K', 'can_usb'), 115200, timeout=0.5)
			
			Language(self.conf.get('GENERAL','lang'))

			self.init1()			
			
			wx.Frame.__init__(self, None, title='diagnostic SignalK input', size=(650,435))
			self.Bind(wx.EVT_CLOSE, self.OnClose)
			
			self.timer = wx.Timer(self)
			self.Bind(wx.EVT_TIMER, self.timer_act, self.timer)
						
			self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
			
			self.icon = wx.Icon(self.currentpath+'/openplotter.ico', wx.BITMAP_TYPE_ICO)
			self.SetIcon(self.icon)

			self.list = wx.ListCtrl(self, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER, size=(640, 330), pos=(5, 5))
			self.list.InsertColumn(0, _('SRC'), width=140)
			self.list.InsertColumn(1, _('Name'), width=380)
			self.list.InsertColumn(2, _('Value'), wx.LIST_FORMAT_RIGHT, width=100)
			self.list.InsertColumn(4, _('Interval'), wx.LIST_FORMAT_RIGHT, width=45)
			self.list.InsertColumn(5, _('Status'), width=50)

			self.sort_PGN_b =wx.Button(self, label=_('Sort PGN'), pos=(110, 340))
			self.Bind(wx.EVT_BUTTON, self.sort_PGN, self.sort_PGN_b)

			self.sort_SRC_b =wx.Button(self, label=_('Sort SRC'), pos=(10, 340))
			self.Bind(wx.EVT_BUTTON, self.sort_SRC, self.sort_SRC_b)

			self.reset_b =wx.Button(self, label=_('reset'), pos=(210, 340))
			self.Bind(wx.EVT_BUTTON, self.reset, self.reset_b)

			self.CreateStatusBar()

			self.init2()
# var_source var_value var_timestamp name[] source value timestamp Interval activ				
#      0          1          2         3     4      5    6        7        8       			
			self.Show(True)

			self.status=''
			self.data=[]
			self.baudc=0
			self.baud=0

			self.timer.Start(self.ttimer)

		def skprint(self,sks,data):
			#for i in data:
			#	print sks+'.'+i+' =',data[i]
			self.sk_list(sks,data)

		def sk_list(self,sks,data):
			timestamp=''
			source=''
			for i in data:
				if 'timestamp'==i: timestamp=i
				elif '$source'==i: source=i
			if timestamp!='' and source!='':
				for i in data:
					if 'timestamp'!=i and '$source'!=i and 'source'!=i and 'sentence'!=i and 'pgn'!=i:
						sk_json=["vessels","xxxxxxxx"]
						for j in sks.split('.'):
							sk_json.append(str(j))
						self.list_SK.append([source,i,timestamp,sk_json,data[source],data[i],data[timestamp],0,1])				
# var_source var_value var_timestamp name[] source value timestamp Interval activ				
#      0          1          2         3     4      5    6        7        8       			
				
		def timer_act(self, event):
			try:
				self.response = requests.get('http://localhost:3000/signalk/v1/api/')
			except:
				time.sleep(0.1)
				return
			self.data = self.response.json()
			index=0
			for i in self.list_SK:
				if i[8]==1:
					if self.lookup(i[3]):
						if self.SKselect[i[2]]!=i[6]:
							i[6]=self.SKselect[i[2]]
							if i[5]!=self.SKselect[i[1]]:
								i[5]=self.SKselect[i[1]]
								self.list.SetStringItem(index, 2, str('%.3f' % i[5]))
						#str(i[5]))
					else:
						i[8]==0
						self.list.SetStringItem(index, 4, str(i[8]))
				index+=1
			
		def lookup(self,name):
			self.SKselect=self.data
			try:
				for i in name:
					self.SKselect=self.SKselect[i]
				return 1
			except:
				return 0
			
		def sort_PGN(self, e):
			self.timer.Stop()
			self.list.DeleteAllItems()
			list_new=[]
			for i in sorted(self.list_SK, key=lambda item: (item[3])):
				list_new.append(i)
			self.list_SK=list_new
			self.init2()
			self.timer.Start(self.ttimer)

		def sort_SRC(self, e):
			self.timer.Stop()
			self.list.DeleteAllItems()
			list_new=[]
			for i in sorted(self.list_SK, key=lambda item: (item[4])):
				list_new.append(i)
			self.list_SK=list_new
			self.init2()			
			self.timer.Start(self.ttimer)

		def reset(self, e):		
			self.init1()
			self.sort_SRC(0)
			
		def init1(self):
			self.list_SK=[]
			self.SKselect=''
			self.response = requests.get('http://localhost:3000/signalk/v1/api/')
			self.data = self.response.json()
			
#var_data var_source var_value var_timestamp name source value timestamp Interval activ
			sks2=["vessels","xxxxxxxx"]
			sks3=[]
			sks4=[]
			sks5=[]
			sks6=[]
			sk2=self.data["vessels"]["xxxxxxxx"]
			for i2 in sk2:
				i=i2
				sk3=sk2[i]
				sks3=i
				if isinstance(sk3, dict):
					if 'timestamp' in sk3:
						self.skprint(sks3,sk3)
					else:
						for i3 in sk3:
							i=i3
							sk4=sk3[i]
							sks4=sks3+'.'+i
							if isinstance(sk4, dict):
								if 'timestamp' in sk4:
									self.skprint(sks4,sk4)
								else:
									for i4 in sk4:
										i=i4
										sk5=sk4[i]
										sks5=sks4+'.'+i
										if isinstance(sk5, dict):
											if 'timestamp' in sk5:
												self.skprint(sks5,sk5)
											else:
												for i5 in sk5:
														i=i5
														sk6=sk5[i]
														sks6=sks5+'.'+i
														if isinstance(sk6, dict):
															if 'timestamp' in sk6:
																self.skprint(sks6,sk6)

		def init2(self):
			index=0
			for i in self.list_SK:
				self.list.InsertStringItem(index, str(i[4]))
				text=''
				index2=0
				for j in i[3]:
					if index2>1:
						text+=j+'.'
					index2+=1
				text+=i[1]
				
				self.list.SetStringItem(index, 1, text)
				self.list.SetStringItem(index, 2, str('%.3f' % i[5]))
				self.list.SetStringItem(index, 3, str(i[7]))
				self.list.SetStringItem(index, 4, str(i[8]))
				index+=1
																
		def OnClose(self, event):
			self.timer.Stop()
			self.Destroy()

		def refresh_loop(self,arg1,stop_event):
			self.getCharfromSerial()
			
										
app = wx.App()
MyFrame().Show()
app.MainLoop()