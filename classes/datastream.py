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

import pynmea2, time

class DataStream:

	def __init__(self):

		self.DataList=[]
		
		#(0 name, 1 short, 2 value, 3 unit, 4 timestamp, 5 talker, 6 sentence, 7 valid operators, 8 disable field, 9 unique id)
		self.DataList.append([_('Latitude'),_('Lat'),None,None,None,None,None,(0,1,2,3,4,5,6),1,'Lat'])
		self.DataList.append([_('Longitude'),_('Lon'),None,None,None,None,None,(0,1,2,3,4,5,6),1,'Lon'])
		self.DataList.append([_('Date'),_('Date'),None,None,None,None,None,(0,1),1,'Date'])
		self.DataList.append([_('Time'),_('Time'),None,None,None,None,None,(0,1),1,'Time'])
		self.DataList.append([_('Magnetic Variation'),_('Var'),None,None,None,None,None,(0,1,2,3,4,5,6),1,'Var'])
		self.DataList.append([_('Magnetic Heading'),_('HDM'),None,None,None,None,None,(0,1,2,3,4,5,6),1,'HDM'])
		self.DataList.append([_('True Heading'),_('HDT'),None,None,None,None,None,(0,1,2,3,4,5,6),1,'HDT'])
		self.DataList.append([_('Course Over Ground'),_('COG'),None,None,None,None,None,(0,1,2,3,4,5,6),1,'COG'])
		self.DataList.append([_('Speed Over Ground'),_('SOG'),None,None,None,None,None,(0,1,2,3,4,5,6),1,'SOG'])
		self.DataList.append([_('Speed Trought Water'),_('STW'),None,None,None,None,None,(0,1,2,3,4,5,6),1,'STW'])
		self.DataList.append([_('Water Depth (from transducer)'),_('DPT'),None,None,None,None,None,(0,1,2,3,4,5,6),1,'DPT'])
		self.DataList.append([_('Apparent Wind Angle'),_('AWA'),None,None,None,None,None,(0,1,2,3,4,5,6),1,'AWA'])
		self.DataList.append([_('True Wind Angle'),_('TWA'),None,None,None,None,None,(0,1,2,3,4,5,6),1,'TWA'])
		self.DataList.append([_('Apparent Wind Speed'),_('AWS'),None,None,None,None,None,(0,1,2,3,4,5,6),1,'AWS'])
		self.DataList.append([_('True Wind Speed'),_('TWS'),None,None,None,None,None,(0,1,2,3,4,5,6),1,'TWS'])
		self.DataList.append([_('True Wind Direction'),_('TWD'),None,None,None,None,None,(0,1,2,3,4,5,6),1,'TWD'])
		self.DataList.append([_('Air Pressure'),_('AP'),None,None,None,None,None,(0,1,2,3,4,5,6),1,'AP'])
		self.DataList.append([_('Air Temperature'),_('AT'),None,None,None,None,None,(0,1,2,3,4,5,6),1,'AT'])
		self.DataList.append([_('Air Relative Humidity'),_('ARH'),None,None,None,None,None,(0,1,2,3,4,5,6),1,'ARH'])
		self.DataList.append([_('Rate of Turn'),_('ROT'),None,None,None,None,None,(0,1,2,3,4,5,6),1,'ROT'])
		self.DataList.append([_('Heel'),_('Heel'),None,None,None,None,None,(0,1,2,3,4,5,6),1,'Heel'])
		self.DataList.append([_('Engine Coolant Temperature'),_('ECT'),None,None,None,None,None,(0,1,2,3,4,5,6),1,'ECT'])
		self.DataList.append([_('Switch 1 status'),_('SW1'),None,None,None,None,None,(7,8),0,'SW1'])
		self.DataList.append([_('Switch 2 status'),_('SW2'),None,None,None,None,None,(7,8),0,'SW2'])
		self.DataList.append([_('Switch 3 status'),_('SW3'),None,None,None,None,None,(7,8),0,'SW3'])
		self.DataList.append([_('Switch 4 status'),_('SW4'),None,None,None,None,None,(7,8),0,'SW4'])
		self.DataList.append([_('Switch 5 status'),_('SW5'),None,None,None,None,None,(7,8),0,'SW5'])
		self.DataList.append([_('Switch 6 status'),_('SW6'),None,None,None,None,None,(7,8),0,'SW6'])
		self.DataList.append([_('Output 1 status'),_('OUT1'),None,None,None,None,None,(7,8),0,'OUT1'])
		self.DataList.append([_('Output 2 status'),_('OUT2'),None,None,None,None,None,(7,8),0,'OUT2'])
		self.DataList.append([_('Output 3 status'),_('OUT3'),None,None,None,None,None,(7,8),0,'OUT3'])
		self.DataList.append([_('Output 4 status'),_('OUT4'),None,None,None,None,None,(7,8),0,'OUT4'])
		
		#ATENTION. If order changes, edit monitoring.py: "#actions"
		self.operators_list=[_('was not present in the last (sec.)'),_('was present in the last (sec.)'),_('is equal to'), _('is less than'), _('is less than or equal to'), _('is greater than'), _('is greater than or equal to'), _('is on'), _('is off')]

	def getDataListIndex(self, data):
		for index, item in enumerate(self.DataList):
			if item[9]==data: return index

	def validate(self,data,now,accuracy):
		timestamp=self.DataList[self.getDataListIndex(data)][4]
		if timestamp:
			age=now-timestamp
			if age <= accuracy: 
				if data !='Date':
					return float(self.DataList[self.getDataListIndex(data)][2])
				else:
					return self.DataList[self.getDataListIndex('Date')][2]
			else: return None
	
	def updateDataList(self,data,value,unit,talker,nmea_type):
		i=self.getDataListIndex(data)
		self.DataList[i][2]=value
		self.DataList[i][3]=unit
		self.DataList[i][4]=time.time()
		self.DataList[i][5]=talker
		self.DataList[i][6]=nmea_type

	def parse_nmea(self, frase_nmea):
		nmea_list=frase_nmea.split()
		for i in nmea_list:
			try:
				msg = pynmea2.parse(i)
				nmea_type = msg.sentence_type
				talker = msg.talker

				if nmea_type == 'RMC' or nmea_type =='GGA' or nmea_type =='GNS' or nmea_type =='GLL':
					#lat
					value=round(msg.latitude,4)
					if value:
						unit=msg.lat_dir #N, S
						self.updateDataList('Lat',value,unit,talker,nmea_type)
					#lon
					value=round(msg.longitude,4)
					if value:
						unit=msg.lon_dir #E, W
						self.updateDataList('Lon',value,unit,talker,nmea_type)						
				if nmea_type == 'RMC':
					#date
					value=msg.datestamp
					if value:
						unit='UTC'
						self.updateDataList('Date',value,unit,talker,nmea_type)
					#time
					value=msg.timestamp
					if value:
						unit='UTC'
						self.updateDataList('Time',value,unit,talker,nmea_type)
					#magnetic variation
					value=msg.mag_variation
					if value:
						unit=msg.mag_var_dir #E, W
						self.updateDataList('Var',value,unit,talker,nmea_type)
					#course over ground
					value=msg.true_course
					if value:
						unit='D'
						self.updateDataList('COG',value,unit,talker,nmea_type)
					#speed over ground
					value=msg.spd_over_grnd
					if value:
						unit='N'
						self.updateDataList('SOG',value,unit,talker,nmea_type)
				if nmea_type == 'HDG':
					#magnetic variation
					value=msg.variation
					if value:
						unit=msg.var_dir #E, W
						self.updateDataList('Var',value,unit,talker,nmea_type)
					#magnetic heading
					value=msg.heading
					if value:
						unit='D'
						self.updateDataList('HDM',value,unit,talker,nmea_type)
				if nmea_type == 'VHW':
					#magnetic heading
					value=msg.heading_magnetic
					if value:
						unit='D'
						self.updateDataList('HDM',value,unit,talker,nmea_type)
					#true heading
					value=msg.heading_true
					if value:
						unit='D'
						self.updateDataList('HDT',value,unit,talker,nmea_type)
					#speed trought water
					value=msg.water_speed_knots
					if value:
						unit='N'
						self.updateDataList('STW',value,unit,talker,nmea_type)
				if nmea_type == 'HDM':
					#magnetic heading
					value=msg.heading
					if value:
						unit='D'
						self.updateDataList('HDM',value,unit,talker,nmea_type)
				if nmea_type == 'HDT':
					#true heading
					value=msg.heading
					if value:
						unit='D'
						self.updateDataList('HDT',value,unit,talker,nmea_type)
				if nmea_type == 'VTG':
					#course over ground
					value=msg.true_track
					if value:
						unit='D'
						self.updateDataList('COG',value,unit,talker,nmea_type)
					#speed over ground
					value=msg.spd_over_grnd_kts
					if value:
						unit='N'
						self.updateDataList('SOG',value,unit,talker,nmea_type)
				if nmea_type == 'VBW':
					#speed trought water
					value=msg.lon_water_spd
					if value:
						unit='N'
						self.updateDataList('STW',value,unit,talker,nmea_type)
				if nmea_type == 'VWR':
					#apparent wind angle
					value=msg.deg_r
					if value:
						unit=msg.l_r #L=Left, R=Right
						self.updateDataList('AWA',value,unit,talker,nmea_type)
					#apparent wind speed
					value=msg.wind_speed_kn
					if value:
						unit='N'
						self.updateDataList('AWS',value,unit,talker,nmea_type)
				if nmea_type == 'MWV':
					value0=msg.reference
					if value0=='R':
						#apparent wind angle
						value=msg.wind_angle
						if value:
							unit='D'
							self.updateDataList('AWA',value,unit,talker,nmea_type)
						#apparent wind speed
						if msg.wind_speed_units=='N':
							value=msg.wind_speed
						if value:
							unit='N'
							self.updateDataList('AWS',value,unit,talker,nmea_type)
					if value0=='T':
						#true wind angle
						value=msg.wind_angle
						if value:
							unit='D'
							self.updateDataList('TWA',value,unit,talker,nmea_type)
						#true wind speed
						value=msg.wind_speed
						if value:
							unit='N'
							self.updateDataList('TWS',value,unit,talker,nmea_type)
				if nmea_type == 'VWT':
					#true wind angle
					value=msg.wind_angle_vessel
					if value:
						unit=msg.direction #L=Left, R=Right
						self.updateDataList('TWA',value,unit,talker,nmea_type)
					#true wind speed
					value=msg.wind_speed_knots
					if value:
						unit='N'
						self.updateDataList('TWS',value,unit,talker,nmea_type)
				if nmea_type == 'MWD':
					#true wind direction
					value=msg.direction_true
					if value:
						unit='D'
						self.updateDataList('TWD',value,unit,talker,nmea_type)
					#true wind speed
					value=msg.wind_speed_knots
					if value:
						unit='N'
						self.updateDataList('TWS',value,unit,talker,nmea_type)
				if nmea_type == 'ROT':
					#rate of turn
					value=msg.rate_of_turn
					if value:
						unit='D/M'
						self.updateDataList('ROT',value,unit,talker,nmea_type)
				if nmea_type == 'DPT':
					#water Depth
					value=msg.depth
					if value:
						unit='M'
						self.updateDataList('DPT',value,unit,talker,nmea_type)
				if nmea_type == 'DBT':
					#water Depth
					value=msg.depth_meters
					if value:
						unit='M'
						self.updateDataList('DPT',value,unit,talker,nmea_type)
				if nmea_type == 'XDR':
					n=msg.num_transducers
					for i in range(0, n):
						transducer=msg.get_transducer(i)
						if transducer.id=='AIRP':		
							#pressure
							value=transducer.value
							if value:
								unit='hPa'
								self.updateDataList('AP',value,unit,talker,nmea_type)
						if transducer.id=='AIRT':		
							#temperature
							value=transducer.value
							if value:
								unit='C'
								self.updateDataList('AT',value,unit,talker,nmea_type)
						if transducer.id=='HUMI':		
							#humidity
							value=transducer.value
							if value:
								unit='%'
								self.updateDataList('ARH',value,unit,talker,nmea_type)
						if transducer.id=='ROLL':		
							#heel
							value=transducer.value
							if value:
								unit='D'
								self.updateDataList('Heel',value,unit,talker,nmea_type)						
						if transducer.id=='ENGT':		
							#engine temperature
							value=transducer.value
							if value:
								unit='C'
								self.updateDataList('ECT',value,unit,talker,nmea_type)
			#except Exception,e: print str(e)
			except: pass