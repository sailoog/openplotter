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

import wx, threading, time, websocket, logging, json
from classes.conf import Conf
from classes.language import Language
from classes.N2K_send import N2K_send

class MyFrame(wx.Frame):
		
	def __init__(self):
		logging.basicConfig()
		self.conf = Conf()
		self.home = self.conf.home
		self.currentpath = self.home+self.conf.get('GENERAL', 'op_folder')+'/openplotter'
		#self.Check127488_pos=100
		#self.Check127489_pos=100
		#self.Check127505_pos=100
		#self.Check130316_pos=100
		self.N2K=N2K_send()
		self.tick=0
		self.list_SK=[]

		Language(self.conf)

		wx.Frame.__init__(self, None, title="N2K-from-SK", size=(650,435))
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		
		self.ttimer=100
		self.timer = wx.Timer(self)
		self.Bind(wx.EVT_TIMER, self.timer_act, self.timer)		
		
		self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
		
		self.icon = wx.Icon(self.currentpath+'/openplotter.ico', wx.BITMAP_TYPE_ICO)
		self.SetIcon(self.icon)

		iL=20;
		self.Check126992 = wx.CheckBox(self, label=_('126992 System_Time'), pos=(20, iL))
		iL+=20;
		self.Check127245 = wx.CheckBox(self, label=_('127245 Rudder'), pos=(20, iL))
		iL+=20;
		self.Check127250 = wx.CheckBox(self, label=_('127250 Heading'), pos=(20, iL))
		iL+=20
		self.Check127257 = wx.CheckBox(self, label=_('127257 Attitude'), pos=(20, iL))	
		iL+=20
		self.Check127488 = wx.CheckBox(self, label=_('127488 Engine_Rapid'), pos=(20, iL))	
		iL+=20
		self.Check127488_1 = wx.CheckBox(self, label=_('127488 Engine_Rapid starbord'), pos=(20, iL))	
		iL+=20
		self.Check127489 = wx.CheckBox(self, label=_('127489 Engine'), pos=(20, iL))	
		iL+=20
		self.Check127489_1 = wx.CheckBox(self, label=_('127489 Engine starbord'), pos=(20, iL))	
		iL+=20
		self.Check127505 = wx.CheckBox(self, label=_('127505 FluidLevel fuel'), pos=(20, iL))	
		iL+=20
		self.Check127505_1 = wx.CheckBox(self, label=_('127505 FluidLevel water'), pos=(20, iL))	
		iL+=20
		self.Check127505_2 = wx.CheckBox(self, label=_('127505 FluidLevel gray water'), pos=(20, iL))	
		iL+=20
		self.Check127505_3 = wx.CheckBox(self, label=_('127505 FluidLevel black water'), pos=(20, iL))	
		iL+=20
		self.Check127508 = wx.CheckBox(self, label=_('127508 Battery_Status'), pos=(20, iL))
		iL+=20;
		self.Check128259 = wx.CheckBox(self, label=_('128259 Speed'), pos=(20, iL))	
		iL+=20
		self.Check128267 = wx.CheckBox(self, label=_('128267 Depth'), pos=(20, iL))	
		iL+=20
		self.Check128275 = wx.CheckBox(self, label=_('128275 Distance_Log'), pos=(20, iL))	
		iL+=20
		self.Check129025 = wx.CheckBox(self, label=_('129025 Position_Rapid'), pos=(20, iL))	
		iL+=20
		self.Check129026 = wx.CheckBox(self, label=_('129026 COG_SOG'), pos=(20, iL))	
		iL=100
		self.Check130306 = wx.CheckBox(self, label=_('130306 Wind Data'), pos=(320, iL))	
		iL+=20
		self.Check130310 = wx.CheckBox(self, label=_('130310 Environmental_Parameters'), pos=(320, iL))	
		iL+=20
		self.Check130311 = wx.CheckBox(self, label=_('130311 Environmental_Parameters'), pos=(320, iL))	
		iL+=20
		self.Check130316 = wx.CheckBox(self, label=_('130316 Temperature refrigerator'), pos=(320, iL))	
		iL+=20
		self.Check130316_1 = wx.CheckBox(self, label=_('130316 Temperature exhaust'), pos=(320, iL))
		self.Bind(wx.EVT_CHECKBOX, self.updCB)

		self.XallBtn = wx.Button(self, label=_('all'),size=(70, 32), pos=(550, 20))
		self.Bind(wx.EVT_BUTTON, self.allBtn, self.XallBtn)
		
		self.XnoneBtn = wx.Button(self, label=_('none'),size=(70, 32), pos=(550, 60))
		self.Bind(wx.EVT_BUTTON, self.noneBtn, self.XnoneBtn)
		
		self.Centre()

		self.Show(True)
		
		self.defvar()
		self.aktPGN()

		self.cycle250=time.time()
		self.cycle250_2=time.time()+0.111
		self.cycle500=time.time()+0.123
		self.cycle500_2=time.time()+0.241
		self.cycle500_3=time.time()+0.363
		self.cycle500_4=time.time()-0.025
		self.cycle1000=time.time()+0.087
		self.cycle1000_2=time.time()+0.207
		
		self.start()

		self.timer.Start(self.ttimer)

	def allBtn(self,e):
		self.setCheckbox(True)
		self.aktPGN()
	
	def noneBtn(self,e):
		self.setCheckbox(False)
		self.aktPGN()

	def setCheckbox(self, value):
		self.Check126992.SetValue(value)
		self.Check127245.SetValue(value)
		self.Check127250.SetValue(value)
		self.Check127257.SetValue(value)
		self.Check127488.SetValue(value)
		self.Check127488_1.SetValue(value)
		self.Check127489.SetValue(value)
		self.Check127489_1.SetValue(value)
		self.Check127505.SetValue(value)
		self.Check127505_1.SetValue(value)
		self.Check127505_2.SetValue(value)
		self.Check127505_3.SetValue(value)
		self.Check127508.SetValue(value)
		self.Check128259.SetValue(value)
		self.Check128267.SetValue(value)
		self.Check128275.SetValue(value)
		self.Check129025.SetValue(value)
		self.Check129026.SetValue(value)
		self.Check130306.SetValue(value)
		self.Check130310.SetValue(value)
		self.Check130311.SetValue(value)
		self.Check130316.SetValue(value)
		self.Check130316_1.SetValue(value)

	def updCB(self,event):
		self.aktPGN()

	#self.PGN_list = ['126992','127245','127250','127257','127488','127488_1','127489','127489_1','127505','127505_1','127505_2','127505_3','127508','128259','128267','128275','129025','129026','130306','130310','130311','130316','130316_1']
	self.PGN_list = ['126992','127245']
		
	def aktPGN(self):
		self.akt126992='126992' in self.PGN_list
		self.akt127245='127245' in self.PGN_list
		self.akt127250='127250' in self.PGN_list
		self.akt127257='127257' in self.PGN_list
		self.akt127488='127488' in self.PGN_list
		self.akt127488_1='127488_1' in self.PGN_list
		self.akt127489='127489' in self.PGN_list
		self.akt127489_1='127489_1' in self.PGN_list
		self.akt127505='127505' in self.PGN_list
		self.akt127505_1='127505_1' in self.PGN_list
		self.akt127505_2='127505_2' in self.PGN_list
		self.akt127505_3='127505_3' in self.PGN_list
		self.akt127508='127508' in self.PGN_list
		self.akt128259='128259' in self.PGN_list
		self.akt128267='128267' in self.PGN_list
		self.akt128275='128275' in self.PGN_list
		self.akt129025='129025' in self.PGN_list
		self.akt129026='129026' in self.PGN_list
		self.akt130306='130306' in self.PGN_list
		self.akt130310='130310' in self.PGN_list
		self.akt130311='130311' in self.PGN_list
		self.akt130316='130316' in self.PGN_list
		self.akt130316_1='130316_1' in self.PGN_list

	def setlist(self,list)
		exist=False
		for i in list_SK
			if i == list:
		
		if not exist:
			self.list_SK.append(list)
		return list
			
	def defvar(self):
		for i in self.PGN_list:
	#self.PGN_list = ['127488','akt127488_1','127489','127489_1','127505','127505_1','127505_2','127505_3','127508','128259','128267','128275','129025','129026','130306','130310','130311','130316','130316_1']
			if i == '126992':
			elif i == '127245':
			elif i == '127250':
			elif i == '127257':
			elif i == '127488':
			elif i == '127488_1':
			elif i == '127245':
			elif i == '127245':
			elif i == '127245':
			elif i == '127245':
			elif i == '127245':
			elif i == '127245':
			elif i == '127245':
			elif i == '127245':
			elif i == '127245':
			elif i == '127245':
				self.DC_Electrical_Properties_dcSource_voltage=self.setlist(['DC Electrical Properties.dcSource.voltage',0,0,0])
	
		self.list_SK.append(['DC Electrical Properties.dcSource.voltage',0,0,0])
		self.list_SK.append(['DC Electrical Properties.dcSource.current',0,0,0])
		self.list_SK.append(['DC Electrical Properties.dcSource.temperature',0,0,0])
	
		self.list_SK.append(['environment.depth.belowTransducer',0,0,0])
		self.list_SK.append(['environment.depth.surfaceToTransducer',0,0,0])
		self.list_SK.append(['environment.humidity',0,0,0])
		self.list_SK.append(['environment.inside.refrigerator.temperature',0,0,0])
		self.list_SK.append(['environment.outside.pressure',0,0,0])
		self.list_SK.append(['environment.outside.temperature',0,0,0])
		self.list_SK.append(['environment.water.temperature',0,0,0])
		self.list_SK.append(['environment.wind.directionTrue',0,0,0])
		self.list_SK.append(['environment.wind.speedTrue',0,0,0])
		self.list_SK.append(['navigation.attitude.pitch',0,0,0])
		self.list_SK.append(['navigation.attitude.roll',0,0,0])
		self.list_SK.append(['navigation.attitude.yaw',0,0,0])
		self.list_SK.append(['navigation.courseOverGroundTrue',0,0,0])
		self.list_SK.append(['navigation.headingMagnetic',0,0,0])
		self.list_SK.append(['navigation.log',0,0,0])
		self.list_SK.append(['navigation.logTrip',0,0,0])
		self.list_SK.append(['navigation.position.latitude',0,0,0])
		self.list_SK.append(['navigation.position.longitude',0,0,0])
		self.list_SK.append(['navigation.speedOverGround',0,0,0])
		self.list_SK.append(['navigation.speedThroughWater',0,0,0])
		self.list_SK.append(['propulsion.port.exhaustTemperature',0,0,0])
		self.list_SK.append(['propulsion.port.oilTemperature',0,0,0])
		self.list_SK.append(['propulsion.port.revolutions',0,0,0])
		self.list_SK.append(['propulsion.port.temperature',0,0,0])
		self.list_SK.append(['propulsion.starboard.oilTemperature',0,0,0])
		self.list_SK.append(['propulsion.starboard.revolutions',0,0,0])
		self.list_SK.append(['propulsion.starboard.temperature',0,0,0])
		self.list_SK.append(['steering.rudderAngle',0,0,0])
		self.list_SK.append(['tank.diesel.capacity',0,0,0])
		self.list_SK.append(['tank.diesel.level',0,0,0])
		self.list_SK.append(['tank.freshwater.capacity',0,0,0])
		self.list_SK.append(['tank.freshwater.level',0,0,0])
		self.list_SK.append(['tank.greywater.capacity',0,0,0])
		self.list_SK.append(['tank.greywater.level',0,0,0])
		self.list_SK.append(['tank.holding.capacity',0,0,0])
		self.list_SK.append(['tank.holding.level',0,0,0])
		
		
		self.DC_Electrical_Properties_dcSource_voltage=self.list_SK[self.searchIndex('DC Electrical Properties.dcSource.voltage')]
		self.DC_Electrical_Properties_dcSource_current=self.list_SK[self.searchIndex('DC Electrical Properties.dcSource.current')]
		self.DC_Electrical_Properties_dcSource_temperature=self.list_SK[self.searchIndex('DC Electrical Properties.dcSource.temperature')]
		self.environment_depth_belowTransducer=self.list_SK[self.searchIndex('environment.depth.belowTransducer')]
		self.environment_depth_surfaceToTransducer=self.list_SK[self.searchIndex('environment.depth.surfaceToTransducer')]
		self.environment_humidity=self.list_SK[self.searchIndex('environment.humidity')]
		self.environment_inside_refrigerator_temperature=self.list_SK[self.searchIndex('environment.inside.refrigerator.temperature')]
		self.environment_outside_pressure=self.list_SK[self.searchIndex('environment.outside.pressure')]
		self.environment_outside_temperature=self.list_SK[self.searchIndex('environment.outside.temperature')]
		self.environment_water_temperature=self.list_SK[self.searchIndex('environment.water.temperature')]
		self.environment_wind_directionTrue=self.list_SK[self.searchIndex('environment.wind.directionTrue')]
		self.environment_wind_speedTrue=self.list_SK[self.searchIndex('environment.wind.speedTrue')]
		self.navigation_attitude_pitch=self.list_SK[self.searchIndex('navigation.attitude.pitch')]
		self.navigation_attitude_roll=self.list_SK[self.searchIndex('navigation.attitude.roll')]
		self.navigation_attitude_yaw=self.list_SK[self.searchIndex('navigation.attitude.yaw')]
		self.navigation_courseOverGroundTrue=self.list_SK[self.searchIndex('navigation.courseOverGroundTrue')]
		self.navigation_headingMagnetic=self.list_SK[self.searchIndex('navigation.headingMagnetic')]
		self.navigation_log=self.list_SK[self.searchIndex('navigation.log')]
		self.navigation_logTrip=self.list_SK[self.searchIndex('navigation.logTrip')]
		self.navigation_position_latitude=self.list_SK[self.searchIndex('navigation.position.latitude')]
		self.navigation_position_longitude=self.list_SK[self.searchIndex('navigation.position.longitude')]
		self.navigation_speedOverGround=self.list_SK[self.searchIndex('navigation.speedOverGround')]
		self.navigation_speedThroughWater=self.list_SK[self.searchIndex('navigation.speedThroughWater')]
		self.propulsion_port_exhaustTemperature=self.list_SK[self.searchIndex('propulsion.port.exhaustTemperature')]
		self.propulsion_port_oilTemperature=self.list_SK[self.searchIndex('propulsion.port.oilTemperature')]
		self.propulsion_port_revolutions=self.list_SK[self.searchIndex('propulsion.port.revolutions')]
		self.propulsion_port_temperature=self.list_SK[self.searchIndex('propulsion.port.temperature')]
		self.propulsion_starboard_oilTemperature=self.list_SK[self.searchIndex('propulsion.starboard.oilTemperature')]
		self.propulsion_starboard_revolutions=self.list_SK[self.searchIndex('propulsion.starboard.revolutions')]
		self.propulsion_starboard_temperature=self.list_SK[self.searchIndex('propulsion.starboard.temperature')]
		self.steering_rudderAngle=self.list_SK[self.searchIndex('steering.rudderAngle')]
		self.tank_diesel_capacity=self.list_SK[self.searchIndex('tank.diesel.capacity')]
		self.tank_diesel_level=self.list_SK[self.searchIndex('tank.diesel.level')]
		self.tank_freshwater_capacity=self.list_SK[self.searchIndex('tank.freshwater.capacity')]
		self.tank_freshwater_level=self.list_SK[self.searchIndex('tank.freshwater.level')]
		self.tank_greywater_capacity=self.list_SK[self.searchIndex('tank.greywater.capacity')]
		self.tank_greywater_level=self.list_SK[self.searchIndex('tank.greywater.level')]
		self.tank_holding_capacity=self.list_SK[self.searchIndex('tank.holding.capacity')]
		self.tank_holding_level=self.list_SK[self.searchIndex('tank.holding.level')]
		
	def searchIndex(self,text):
		index=0
		for i in self.list_SK:
			if i[0]==text:
				return index
			index+=1			
		
	# thread
	def timer_act(self, event):
		tick2=time.time()
		
		if tick2>self.cycle250:
			self.cycle250+=0.250
			if self.akt127488:self.N2K.Send_Engine_Rapid(0, self.propulsion_port_revolutions[1], self.N2K.empty16, self.N2K.empty8)

			if self.akt127245: self.N2K.Send_Rudder(self.steering_rudderAngle[1])
			if self.akt127250: self.N2K.Send_Heading(self.navigation_headingMagnetic[1])
			if self.akt128267: self.N2K.Send_Depth(self.environment_depth_belowTransducer[1], self.environment_depth_surfaceToTransducer[1])
			
		if tick2>self.cycle250_2:
			self.cycle250_2+=0.250
			if self.akt127488_1:self.N2K.Send_Engine_Rapid(1, self.propulsion_starboard_revolutions[1], self.N2K.empty16, self.N2K.empty8)			
			
			if self.akt129025: self.N2K.Send_Position_Rapid(self.navigation_position_latitude[1], self.navigation_position_longitude[1])			
			if self.akt129026: self.N2K.Send_COG_SOG(self.navigation_courseOverGroundTrue[1], self.navigation_speedOverGround[1])
			if self.akt130306: self.N2K.Send_Wind_Data(self.environment_wind_speedTrue[1], self.environment_wind_directionTrue[1])				
			
		if tick2>self.cycle500:
			self.cycle500+=0.500
			if self.akt127257: self.N2K.Send_Attitude(self.navigation_attitude_roll[1], self.navigation_attitude_pitch[1], self.navigation_attitude_yaw[1])		
			if self.akt127505: self.N2K.Send_FluidLevel(0, 'diesel', self.tank_diesel_level[1], self.tank_diesel_capacity[1])
			if self.akt130316: self.N2K.Send_Temperature(self.environment_inside_refrigerator_temperature[1],'refrigerator')

		if tick2>self.cycle500_2:
			self.cycle500_2+=0.500
			if self.akt127505_1: self.N2K.Send_FluidLevel(0, 'fresh water', self.tank_freshwater_level[1], self.tank_freshwater_capacity[1])
			if self.akt127489:
				self.N2K.Send_Engine(
				0, 
				self.N2K.empty16,
				self.propulsion_port_oilTemperature[1],
				self.propulsion_port_temperature[1],
				self.N2K.empty16,
				self.N2K.empty16,
				self.N2K.empty32,
				self.N2K.empty16,
				self.N2K.empty16,
				0, 
				self.N2K.empty8,
				self.N2K.empty8)

		if tick2>self.cycle500_3:
			self.cycle500_3+=0.500
			if self.akt127505_2: self.N2K.Send_FluidLevel(0, 'greywater', self.tank_greywater_level[1], self.tank_greywater_capacity[1])
			if self.akt130316_1: self.N2K.Send_Temperature(self.propulsion_port_exhaustTemperature[1],'exhaustTemperature')
		if tick2>self.cycle500_4:
			self.cycle500_4+=0.500
			if self.akt127505_3: self.N2K.Send_FluidLevel(0, 'holding', self.tank_holding_level[1], self.tank_holding_capacity[1])

			if self.akt127489_1:
				self.N2K.Send_Engine(
				1, 
				self.N2K.empty16,
				self.propulsion_starboard_oilTemperature[1],
				self.propulsion_starboard_temperature[1],
				self.N2K.empty16,
				self.N2K.empty16,
				self.N2K.empty32,
				self.N2K.empty16,
				self.N2K.empty16,
				0, 
				self.N2K.empty8,
				self.N2K.empty8)
								
		if tick2>self.cycle1000:
			self.cycle1000+=1.000
			if self.akt128259: self.N2K.Send_Speed(self.navigation_speedThroughWater[1], self.navigation_speedOverGround[1])
			if self.akt126992: self.N2K.Send_System_Time()
			if self.akt127508: self.N2K.Send_Battery_Status(self.DC_Electrical_Properties_dcSource_voltage[1], self.DC_Electrical_Properties_dcSource_current[1], self.DC_Electrical_Properties_dcSource_temperature[1])
		if tick2>self.cycle1000_2:
			self.cycle1000_2+=1.000
			if self.akt130310: self.N2K.Send_Environmental_Parameters(self.environment_water_temperature[1], self.environment_outside_temperature[1], self.environment_outside_pressure[1])
			if self.akt130311: self.N2K.Send_Environmental_Parameters2(self.environment_water_temperature[1], self.environment_humidity[1], self.environment_outside_pressure[1])
			if self.akt128275: self.N2K.Send_Distance_Log(self.navigation_log[1], self.navigation_logTrip[1])				
	# end thread
			
	def OnClose(self, event):
		self.timer.Stop()
		self.stop()
		self.Destroy()

	def on_message(self,ws, message):
		js_up=json.loads(message)
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
				self.update_add(path, value, srclabel, timestamp)
			

	def update_add(self, path, value, src, timestamp):
		# path, value, src, timestamp				
		#  0    1      2     3            			
		if type(value) is float: pass
		elif type(value) is int: value=1.0*value
		else: value=0.0

		exists=False
		for i in self.list_SK:
			if path==i[0]:
				#print 'value ',value,path, src, timestamp
				
				exists=True
				i[1]=value
				if type(i[1]) is float: pass
				else:	i[1]=0.0
				if i[2]!=src and i[2] != 0:
					print 'warning more sources for ',path
				i[3]=timestamp
			if exists:
				i=self.list_SK[-1]
				
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