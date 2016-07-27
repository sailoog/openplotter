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

import wx, sys, socket, time, webbrowser, serial, requests, json,websocket,threading,logging
from classes.datastream import DataStream
from classes.paths import Paths
from classes.conf import Conf
from classes.language import Language

class MyFrame(wx.Frame):
		
		def __init__(self):
			

			logging.basicConfig()
			self.buffer=[]
			self.list_SK=[]
			self.sortCol=0
		
			self.home=Paths().home
			self.currentpath=Paths().currentpath
			self.conf=Conf()

			Language(self.conf.get('GENERAL','lang'))

			self.data_SK_unit=''
			with open(self.home+'/.config/openplotter/classes/keyswithmetadata.json') as data_file:    
				self.data_SK_unit = json.load(data_file)

			
			wx.Frame.__init__(self, None, title='diagnostic SignalK input', size=(650,435))
			self.Bind(wx.EVT_CLOSE, self.OnClose)

			self.ttimer=100
			self.timer = wx.Timer(self)
			self.Bind(wx.EVT_TIMER, self.timer_act, self.timer)
			
			self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
			
			self.icon = wx.Icon(self.currentpath+'/openplotter.ico', wx.BITMAP_TYPE_ICO)
			self.SetIcon(self.icon)

			self.list = wx.ListCtrl(self, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER, size=(640, 330), pos=(5, 5))
			self.list.InsertColumn(0, _('SRC'), width=130)
			self.list.InsertColumn(1, _('SignalK'), width=300)
			self.list.InsertColumn(2, _('Value'), wx.LIST_FORMAT_RIGHT, width=100)
			self.list.InsertColumn(3, _('Unit'), width=40)
			self.list.InsertColumn(4, _('Interval'), wx.LIST_FORMAT_RIGHT, width=55)
			self.list.InsertColumn(5, _('Status'), width=50)
			self.list.InsertColumn(6, _('Description'), width=500)

			self.sort_SRC_b =wx.Button(self, label=_('Sort SRC'), pos=(10, 340))
			self.Bind(wx.EVT_BUTTON, self.sort_SRC, self.sort_SRC_b)

			self.sort_SK_b =wx.Button(self, label=_('Sort SK'), pos=(110, 340))
			self.Bind(wx.EVT_BUTTON, self.sort_SK, self.sort_SK_b)			

			self.CreateStatusBar()

			#self.init2()
			self.start()

			self.Show(True)

			self.status=''
			self.data=[]
			self.baudc=0
			self.baud=0

			self.timer.Start(self.ttimer)

		def timer_act(self, event):
			if len(self.buffer)>0:
				for ii in self.buffer:
					if ii[0]>=0 and ii[0]<self.list.GetItemCount():
						self.list.SetStringItem(ii[0], ii[1], ii[2])
					else:
						self.sorting();
					del self.buffer[0]
					#del ii
			
		def json_interval(self,time_old,time_new):
			dif=0
			sek_n = float(time_new[17:22])
			sek_o = float(time_old[17:22])
			if sek_n>=sek_o: dif=sek_n-sek_o
			else: dif =sek_n+60-sek_o
			return float(dif)
					
		def lookup_star(self,name):			
			skip=-1
			index=0
			st=''
			#print name
			for i in name.split('.'):
				if index>-1:
					if skip==0: 
						st+='.*'
					else:
						if i in ['propulsion','inventory']: skip=1
						elif i == 'resources':skip=2
						st+='.'+i
				index+=1
				skip-=1
				#print i,st
						
			st=st[1:]	
			self.SK_unit=''
			self.SK_description=''
			try:
				self.SK_unit=self.data_SK_unit[st]['units']
				self.SK_description=self.data_SK_unit[st]['description']
			except:
				print 'no unit for ',st
				
		def sort_SRC(self, e):
			self.sortCol=0
			self.sorting()			

		def sort_SK(self, e):
			self.sortCol=1
			self.sorting()

		def sorting(self):
			self.list.DeleteAllItems()
			list_new=[]
			for i in sorted(self.list_SK, key=lambda item: (item[self.sortCol])):
				list_new.append(i)
			self.list_SK=list_new
			self.init2()			

		def init2(self):
			index=0
			for i in self.list_SK:
				if type(i[2]) is float: pass
				else:	i[2]=0.0
				self.list.InsertStringItem(index, str(i[0]))			
				self.list.SetStringItem(index, 1, str(i[1]))
				self.list.SetStringItem(index, 2, str('%.3f' % i[2]))
				self.list.SetStringItem(index, 3, str(i[3]))
				self.list.SetStringItem(index, 4, str('%.1f' % i[4]))
				self.list.SetStringItem(index, 5, str(i[5]))
				self.list.SetStringItem(index, 6, str(i[6]))
				index+=1
																
		def OnClose(self, event):
			self.timer.Stop()
			self.stop()
			self.Destroy()

		def on_message(self,ws, message):
			try:
				js_up=json.loads(message)['updates'][0]
			except:
				return
			label=js_up['source']['label']
			
			srcExist=False
			try:
				src=js_up['source']['src']
				srcExist=True
			except:	pass
			if not srcExist:
				try:
					src=js_up['source']['talker']
					srcExist=True
				except:
					src='xx'
			try:
				timestamp=js_up['timestamp']
			except:
				timestamp='2000-01-01T00:00:00.000Z'
						
			values_=js_up['values']
			srclabel2=''
			
			for values in values_:
				path=values['path']
				value=values['value']
				
				if type(value) is dict:
					if 'timestamp' in value:timestamp=value['timestamp']
					if 'source' in value:
						try:
							src2=value['source']['talker']
						except:
							src2='xx'
						srclabel2=label +'.'+ src2
						
					for lvalue in value:
						if lvalue in ['timestamp','source']:pass
						else:
							path2=path+'.'+lvalue
							value2=value[lvalue]
							self.update_add(value2, path2, srclabel2, timestamp)
				else:
					srclabel=label +'.'+ src
					self.update_add(value, path, srclabel, timestamp)
				

		def update_add(self,value, path, src, timestamp):
			# SRC SignalK Value Unit Interval Status Description timestamp				
			#  0    1      2     3      4        5        6          7           			
			if type(value) is float: pass
			elif type(value) is int: value=1.0*value
			else: value=0.0

			index=0
			exists=False
			for i in self.list_SK:
				if path==i[1]:
					if src==i[0]:
						exists=True
						i[2]=value
						if type(i[2]) is float: pass
						else:	i[2]=0.0
						if i[4]==0.0: i[4]=self.json_interval(i[7],timestamp)
						else:         i[4]=i[4]*.8+0.2*self.json_interval(i[7],timestamp)
						i[7]=timestamp
						self.buffer.append([index, 2, str('%.3f' % i[2])])
						self.buffer.append([index, 4, str('%.2f' % i[4])])
				if exists:
					i=self.list_SK[-1]
				index+=1
			if not exists:
				self.lookup_star(path)
				self.list_SK.append([src,path,value,self.SK_unit,0.0,1,self.SK_description,timestamp])
				self.buffer.append([-1, 0,''])						
					
		def on_error(self,ws, error):
			print error

		def on_close(self,ws):
			ws.close()

		def on_open(self,ws):
			pass			

		def run(self):
			self.ws = websocket.WebSocketApp("ws://localhost:3000/signalk/v1/stream?subscribe=self",
					on_message = lambda ws, msg: self.on_message(ws, msg),
					on_error = lambda ws, err: self.on_error(ws,err),
					on_close = lambda ws: self.on_close(ws))
			self.ws.on_open = lambda ws: self.on_open(ws)
			self.ws.run_forever()
			self.ws = None
						
		def start(self):
			def run():
				self.run()
			self.thread = threading.Thread(target=run)
			self.thread.start()
	  
		def stop(self):
			if self.ws is not None:
				self.ws.close()
			self.thread.join()
									
app = wx.App()
MyFrame().Show()
app.MainLoop()