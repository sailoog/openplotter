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
import ConfigParser
from paths import Paths

class Conf:

	def __init__(self):

		self.paths=Paths()

		self.data_conf = ConfigParser.SafeConfigParser()
		
		self.read()

	def read(self):
		self.data_conf.read(self.paths.currentpath+'/openplotter.conf')

	def write(self):
		with open(self.paths.currentpath+'/openplotter.conf', 'wb') as configfile:
			self.data_conf.write(configfile)

	def get(self,section,item):
		return self.data_conf.get(section,item)

	def set(self,section,item,value):
		self.read()
		self.data_conf.set(section, item, value)
		self.write()
