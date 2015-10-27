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

		self.DataList=['Lat','Lon','Date','Time','Var','HDM','HDT','COG','SOG','STW','AWA','TWA','AWS','TWS','TWD','AP','AT','ARH','ROT','Heel','ECT']
		
		#(0 name, 1 short, 2 value, 3 unit, 4 timestamp, 5 talker, 6 sentence)
		self.Lat=[_('Latitude'),_('Lat'),None,None,None,None,None]
		self.Lon=[_('Longitude'),_('Lon'),None,None,None,None,None]
		self.Date=[_('Date'),_('Date'),None,None,None,None,None]
		self.Time=[_('Time'),_('Time'),None,None,None,None,None]
		self.Var=[_('Magnetic Variation'),_('Var'),None,None,None,None,None]
		self.HDM=[_('Magnetic Heading'),_('HDM'),None,None,None,None,None]
		self.HDT=[_('True Heading'),_('HDT'),None,None,None,None,None]
		self.COG=[_('Course Over Ground'),_('COG'),None,None,None,None,None]
		self.SOG=[_('Speed Over Ground'),_('SOG'),None,None,None,None,None]
		self.STW=[_('Speed Trought Water'),_('STW'),None,None,None,None,None]
		self.AWA=[_('Apparent Wind Angle'),_('AWA'),None,None,None,None,None]
		self.TWA=[_('True Wind Angle'),_('TWA'),None,None,None,None,None]
		self.AWS=[_('Apparent Wind Speed'),_('AWS'),None,None,None,None,None]
		self.TWS=[_('True Wind Speed'),_('TWS'),None,None,None,None,None]
		self.TWD=[_('True Wind Direction'),_('TWD'),None,None,None,None,None]
		self.AP=[_('Air Pressure'),_('AP'),None,None,None,None,None]
		self.AT=[_('Air Temperature'),_('AT'),None,None,None,None,None]
		self.ARH=[_('Air Relative Humidity'),_('ARH'),None,None,None,None,None]
		self.ROT=[_('Rate of Turn'),_('ROT'),None,None,None,None,None]
		self.Heel=[_('Heel'),_('Heel'),None,None,None,None,None]
		self.ECT=[_('Engine Coolant Temperature'),_('ECT'),None,None,None,None,None]

	def parse_nmea(self, frase_nmea):
		nmea_list=frase_nmea.split()
		for i in nmea_list:
			try:
				msg = pynmea2.parse(i)
				nmea_type = msg.sentence_type
				talker = msg.talker

				if nmea_type == 'RMC' or nmea_type =='GGA' or nmea_type =='GNS' or nmea_type =='GLL':
					#lat
					value=msg.lat
					if value:
						self.Lat[2]=value
						self.Lat[3]=msg.lat_dir #N, S
						self.Lat[4]=time.time()
						self.Lat[5]=talker
						self.Lat[6]=nmea_type
					#lon
					value=msg.lon
					if value:
						self.Lon[2]=value
						self.Lon[3]=msg.lon_dir #E, W
						self.Lon[4]=time.time()
						self.Lon[5]=talker
						self.Lon[6]=nmea_type
				if nmea_type == 'RMC':
					#date
					value=msg.datestamp
					if value:
						self.Date[2]=value
						self.Date[3]='UTC'
						self.Date[4]=time.time()
						self.Date[5]=talker
						self.Date[6]=nmea_type
					#time
					value=msg.timestamp
					if value:
						self.Time[2]=value
						self.Time[3]='UTC'
						self.Time[4]=time.time()
						self.Time[5]=talker
						self.Time[6]=nmea_type
					#magnetic variation
					value=msg.mag_variation
					if value:
						self.Var[2]=value
						self.Var[3]=msg.mag_var_dir #E, W
						self.Var[4]=time.time()
						self.Var[5]=talker
						self.Var[6]=nmea_type
					#course over ground
					value=msg.true_course
					if value:
						self.COG[2]=value
						self.COG[3]='D'
						self.COG[4]=time.time()
						self.COG[5]=talker
						self.COG[6]=nmea_type
					#speed over ground
					value=msg.spd_over_grnd
					if value:
						self.SOG[2]=value
						self.SOG[3]='N'
						self.SOG[4]=time.time()
						self.SOG[5]=talker
						self.SOG[6]=nmea_type
				if nmea_type == 'HDG':
					#magnetic variation
					value=msg.variation
					if value:
						self.Var[2]=value
						self.Var[3]=msg.var_dir #E, W
						self.Var[4]=time.time()
						self.Var[5]=talker
						self.Var[6]=nmea_type
					#magnetic heading
					value=msg.heading
					if value:
						self.HDM[2]=value
						self.HDM[3]='D'
						self.HDM[4]=time.time()
						self.HDM[5]=talker
						self.HDM[6]=nmea_type
				if nmea_type == 'VHW':
					#magnetic heading
					value=msg.heading_magnetic
					if value:
						self.HDM[2]=value
						self.HDM[3]='D'
						self.HDM[4]=time.time()
						self.HDM[5]=talker
						self.HDM[6]=nmea_type
					#true heading
					value=msg.heading_true
					if value:
						self.HDT[2]=value
						self.HDT[3]='D'
						self.HDT[4]=time.time()
						self.HDT[5]=talker
						self.HDT[6]=nmea_type
					#speed trought water
					value=msg.water_speed_knots
					if value:
						self.STW[2]=value
						self.STW[3]='N'
						self.STW[4]=time.time()
						self.STW[5]=talker
						self.STW[6]=nmea_type
				if nmea_type == 'HDM':
					#magnetic heading
					value=msg.heading
					if value:
						self.HDM[2]=value
						self.HDM[3]='D'
						self.HDM[4]=time.time()
						self.HDM[5]=talker
						self.HDM[6]=nmea_type
				if nmea_type == 'HDT':
					#true heading
					value=msg.heading
					if value:
						self.HDT[2]=value
						self.HDT[3]='D'
						self.HDT[4]=time.time()
						self.HDT[5]=talker
						self.HDT[6]=nmea_type
				if nmea_type == 'VTG':
					#course over ground
					value=msg.true_track
					if value:
						self.COG[2]=value
						self.COG[3]='D'
						self.COG[4]=time.time()
						self.COG[5]=talker
						self.COG[6]=nmea_type
					#speed over ground
					value=msg.spd_over_grnd_kts
					if value:
						self.SOG[2]=value
						self.SOG[3]='N'
						self.SOG[4]=time.time()
						self.SOG[5]=talker
						self.SOG[6]=nmea_type
				if nmea_type == 'VBW':
					#speed trought water
					value=msg.lon_water_spd
					if value:
						self.STW[2]=value
						self.STW[3]='N'
						self.STW[4]=time.time()
						self.STW[5]=talker
						self.STW[6]=nmea_type
				if nmea_type == 'VWR':
					#apparent wind angle
					value=msg.deg_r
					if value:
						self.AWA[2]=value
						self.AWA[3]=msg.l_r #L=Left, R=Right
						self.AWA[4]=time.time()
						self.AWA[5]=talker
						self.AWA[6]=nmea_type
					#apparent wind speed
					value=msg.wind_speed_kn
					if value:
						self.AWS[2]=value
						self.AWS[3]='N'
						self.AWS[4]=time.time()
						self.AWS[5]=talker
						self.AWS[6]=nmea_type
				if nmea_type == 'MWV':
					value0=msg.reference
					if value0=='R':
						#apparent wind angle
						value=msg.wind_angle
						if value:
							self.AWA[2]=value
							self.AWA[3]='D'
							self.AWA[4]=time.time()
							self.AWA[5]=talker
							self.AWA[6]=nmea_type
						#apparent wind speed
						value=msg.wind_speed
						if value:
							self.AWS[2]=value
							self.AWS[3]='N'
							self.AWS[4]=time.time()
							self.AWS[5]=talker
							self.AWS[6]=nmea_type
					if value0=='T':
						#true wind angle
						value=msg.wind_angle
						if value:
							self.TWA[2]=value
							self.TWA[3]='D'
							self.TWA[4]=time.time()
							self.TWA[5]=talker
							self.TWA[6]=nmea_type
						#true wind speed
						value=msg.wind_speed
						if value:
							self.TWS[2]=value
							self.TWS[3]='N'
							self.TWS[4]=time.time()
							self.TWS[5]=talker
							self.TWS[6]=nmea_type
				if nmea_type == 'VWT':
					#true wind angle
					value=msg.wind_angle_vessel
					if value:
						self.TWA[2]=value
						self.TWA[3]=msg.direction #L=Left, R=Right
						self.TWA[4]=time.time()
						self.TWA[5]=talker
						self.TWA[6]=nmea_type
					#true wind speed
					value=msg.wind_speed_knots
					if value:
						self.TWS[2]=value
						self.TWS[3]='N'
						self.TWS[4]=time.time()
						self.TWS[5]=talker
						self.TWS[6]=nmea_type
				if nmea_type == 'MWD':
					#true wind direction
					value=msg.direction_true
					if value:
						self.TWD[2]=value
						self.TWD[3]='D'
						self.TWD[4]=time.time()
						self.TWD[5]=talker
						self.TWD[6]=nmea_type
					#true wind speed
					value=msg.wind_speed_knots
					if value:
						self.TWS[2]=value
						self.TWS[3]='N'
						self.TWS[4]=time.time()
						self.TWS[5]=talker
						self.TWS[6]=nmea_type
				if nmea_type == 'ROT':
					#rate of turn
					value=msg.rate_of_turn
					if value:
						self.ROT[2]=value
						self.ROT[3]='D/M'
						self.ROT[4]=time.time()
						self.ROT[5]=talker
						self.ROT[6]=nmea_type
				if nmea_type == 'XDR':
					n=msg.num_transducers
					for i in range(0, n):
						transducer=msg.get_transducer(i)
						if transducer.id=='AIRP':		
							#pressure
							value=transducer.value
							if value:
								self.AP[2]=value
								self.AP[3]='hPa'
								self.AP[4]=time.time()
								self.AP[5]=talker
								self.AP[6]=nmea_type
						if transducer.id=='AIRT':		
							#temperature
							value=transducer.value
							if value:
								self.AT[2]=value
								self.AT[3]='C'
								self.AT[4]=time.time()
								self.AT[5]=talker
								self.AT[6]=nmea_type
						if transducer.id=='HUMI':		
							#humidity
							value=transducer.value
							if value:
								self.ARH[2]=value
								self.ARH[3]='%'
								self.ARH[4]=time.time()
								self.ARH[5]=talker
								self.ARH[6]=nmea_type
						if transducer.id=='ROLL':		
							#heel
							value=transducer.value
							if value:
								self.Heel[2]=value
								self.Heel[3]='D'
								self.Heel[4]=time.time()
								self.Heel[5]=talker
								self.Heel[6]=nmea_type						
						if transducer.id=='ENGT':		
							#engine temperature
							value=transducer.value
							if value:
								self.ECT[2]=value
								self.ECT[3]='C'
								self.ECT[4]=time.time()
								self.ECT[5]=talker
								self.ECT[6]=nmea_type
			
			#except: pass
			except Exception,e: print str(e)