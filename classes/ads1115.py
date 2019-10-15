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

import smbus, time
from conf_analog import Conf_analog

class Ads1115():

	def __init__(self):
		self.ADS1115_address = 0x48

		# Select the gain
		# gain = 6144  # 0  +/- 6.144V
		# gain = 4096  # 1  +/- 4.096V
		# gain = 2048  # 2  +/- 2.048V
		# gain = 1024  # 3  +/- 1.024V
		# gain = 512   # 4  +/- 0.512V
		# gain = 256   # 5  +/- 0.256V
		self.gain_mV=[6144,4096,2048,1024,512,256]

		# Select the sample rate
		# self.sps = 8    # 0   8 samples per second
		# self.sps = 16   # 1  16 samples per second
		# self.sps = 32   # 2  32 samples per second
		# self.sps = 64   # 3  64 samples per second
		# self.sps = 128  # 4 128 samples per second
		# self.sps = 250  # 5 250 samples per second
		# self.sps = 475  # 6 475 samples per second
		# self.sps = 860  # 7 860 samples per second
		self.samples_s=[8,16,32,64,128,250,475,860]

		conf_analog=Conf_analog()
		self.bus = smbus.SMBus(1)
		a_index = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
		self.active = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
		self.gain = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
		self.samples = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
		self.ohmmeter = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
		self.fixed_resistor = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
		self.high_voltage = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
		self.voltage_divider = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
		self.upper_resistance = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
		self.lower_resistance = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
		self.adjust = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
		self.adjust_point_b = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
		self.adjust_point = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

		ADS1115='ADS1115_'
		for i in a_index:
			#self.analog_active += 1
			if 0==conf_analog.has_section(ADS1115+str(i)):
				conf_analog.add_section(ADS1115+str(i))
			if 0==conf_analog.has_option(ADS1115+str(i), 'active'):
				conf_analog.set(ADS1115+str(i), 'active','0')
			self.active[i] = conf_analog.get(ADS1115+str(i), 'active')=='1'

			if 0==conf_analog.has_option(ADS1115+str(i), 'gain'):
				conf_analog.set(ADS1115+str(i), 'gain','0')
			if 0==conf_analog.has_option(ADS1115+str(i), 'samples'):
				conf_analog.set(ADS1115+str(i), 'samples','0')
			if 0==conf_analog.has_option(ADS1115+str(i), 'ohmmeter'):
				conf_analog.set(ADS1115+str(i), 'ohmmeter','0')
			if 0==conf_analog.has_option(ADS1115+str(i), 'fixed_resistor'):
				conf_analog.set(ADS1115+str(i), 'fixed_resistor','0')
			if 0==conf_analog.has_option(ADS1115+str(i), 'high_voltage'):
				conf_analog.set(ADS1115+str(i), 'high_voltage','3000')
			if 0==conf_analog.has_option(ADS1115+str(i), 'voltage_divider'):
				conf_analog.set(ADS1115+str(i), 'voltage_divider','0')
			if 0==conf_analog.has_option(ADS1115+str(i), 'upper_resistance'):
				conf_analog.set(ADS1115+str(i), 'upper_resistance','1000')
			if 0==conf_analog.has_option(ADS1115+str(i), 'lower_resistance'):
				conf_analog.set(ADS1115+str(i), 'lower_resistance','1000')
			if 0==conf_analog.has_option(ADS1115+str(i), 'adjust'):
				conf_analog.set(ADS1115+str(i), 'adjust','0')
			if 0==conf_analog.has_option(ADS1115+str(i), 'adjust_points'):
				self.adjust_point_b[i] = 0
			else:
				line = conf_analog.get(ADS1115+str(i), 'adjust_points')			
				if line: 
					self.adjust_point[i]=eval(line)
					self.adjust_point_b[i] = 1
				else: self.adjust_point[i]=[]
								
			if self.active[i]:				
				self.gain[i] = conf_analog.getint(ADS1115+str(i), 'gain')

				if self.gain[i]>5: 
					self.gain[i]=0
					conf_analog.set(ADS1115+str(i), 'gain','0')
				self.samples[i] = conf_analog.getint(ADS1115+str(i), 'samples')
				if self.samples[i]>7: 
					self.samples[i]=0
					conf_analog.set(ADS1115+str(i), 'samples','0')

				self.ohmmeter[i] = conf_analog.get(ADS1115+str(i), 'ohmmeter')=='1'			
				if self.ohmmeter[i]:				
					self.fixed_resistor[i] = conf_analog.getfloat(ADS1115+str(i), 'fixed_resistor')
					if self.fixed_resistor[i] < 100:
						self.fixed_resistor[i]=100
						conf_analog.set(ADS1115+str(i), 'fixed_resistor','100')

					self.high_voltage[i] = conf_analog.getfloat(ADS1115+str(i), 'high_voltage')
					if self.high_voltage[i] < 3000:
						self.high_voltage[i]=3000
						conf_analog.set(ADS1115+str(i), 'high_voltage','3000')
						
						
				self.voltage_divider[i] = conf_analog.get(ADS1115+str(i), 'voltage_divider')=='1'
				if self.voltage_divider[i]:
					self.upper_resistance[i] = conf_analog.getfloat(ADS1115+str(i), 'upper_resistance')

					if self.upper_resistance[i] < 1000:
						self.upper_resistance[i]=1000
						conf_analog.set(ADS1115+str(i), 'upper_resistance','1000')
				
					self.lower_resistance[i] = conf_analog.getfloat(ADS1115+str(i), 'lower_resistance')
					if self.lower_resistance[i] < 1000:
						self.lower_resistance[i]=1000
						conf_analog.set(ADS1115+str(i), 'lower_resistance','1000')

				self.adjust[i] = conf_analog.getfloat(ADS1115+str(i), 'adjust')
				
				

				
	def read(self,allchannel):
		#channel+=1
		ADS1115_address = self.ADS1115_address + allchannel // 4
		channel = allchannel - (allchannel // 4) * 4
		if channel>3:
			channel=0
		#sps=250 -> 32*5 gain=4096 -> 512*1  (channel+4)*4096
		config = 0x8103 + 32*self.samples[channel] + 512*self.gain[channel] + (channel+4)*4096
		list = [(config >> 8) & 0xFF, config & 0xFF]

		self.bus.write_i2c_block_data(ADS1115_address, 0x01, list)
		time.sleep(1/(self.samples_s[self.samples[channel]]+0.0001))
		result = self.bus.read_i2c_block_data(ADS1115_address,0x00, 2)

		self.bus.write_i2c_block_data(ADS1115_address, 0x01, list)
		time.sleep(1/(self.samples_s[self.samples[channel]]+0.0001))
		result = self.bus.read_i2c_block_data(ADS1115_address,0x00, 2)

		#print self.gain[channel],self.gain_mV[self.gain[channel]],self.samples_s[self.samples[channel]]
		erg=((result[0] << 8) | (result[1]) ) * self.gain_mV[self.gain[allchannel]] / 32768.0
		
		if self.ohmmeter[allchannel]:
			mV_dif = erg/self.high_voltage[allchannel]
			erg = mV_dif*self.fixed_resistor[allchannel]/(1-mV_dif)
		
		if self.voltage_divider[allchannel]:
			erg = erg*(self.upper_resistance[allchannel]+self.lower_resistance[allchannel])/self.lower_resistance[allchannel]
		
		erg += self.adjust[allchannel]
		
		if self.adjust_point_b[allchannel]:
			lin = -999999
			for index_,item in enumerate(self.adjust_point[allchannel]):
				if index_==0:
					if erg <= item[0]:
						lin = item[1]
						#print 'under range'
						return lin
					save = item
				else:					
					if erg <= item[0]:
						a = (item[1]-save[1])/(item[0]-save[0])
						b = item[1]-a*item[0]
						lin = a*erg +b
						return lin
					save = item
					
			if lin == -999999:
				#print 'over range'
				lin = save[1]
			return lin
		else:
			return erg
			
	def read_bak(self,channel):
		#channel+=1
		if channel>3:
			channel=0
		#sps=250 -> 32*5 gain=4096 -> 512*1  (channel+4)*4096
		config = 0x8103 + 32*self.samples[channel] + 512*self.gain[channel] + (channel+4)*4096
		list = [(config >> 8) & 0xFF, config & 0xFF]

		self.bus.write_i2c_block_data(self.ADS1115_address, 0x01, list)
		time.sleep(1/(self.samples_s[self.samples[channel]]+0.0001))
		print 1/(self.samples_s[self.samples[channel]]+0.0001)
		result = self.bus.read_i2c_block_data(self.ADS1115_address,0x00, 2)

		self.bus.write_i2c_block_data(self.ADS1115_address, 0x01, list)
		time.sleep(1/(self.samples_s[self.samples[channel]]+0.0001))
		result = self.bus.read_i2c_block_data(self.ADS1115_address,0x00, 2)

		#print self.gain[channel],self.gain_mV[self.gain[channel]],self.samples_s[self.samples[channel]]
		return ((result[0] << 8) | (result[1]) ) * self.gain_mV[self.gain[channel]] / 32768.0
		