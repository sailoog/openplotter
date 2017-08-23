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
import os, sys

class Paths:

	def __init__(self):

		self.home = os.path.expanduser('~')
		if 'root' in self.home:
			self.home = '/home/pi'
		self.path_to_file = sys.argv[0]
		self.file = os.path.basename(self.path_to_file)
		self.pathname = os.path.dirname(self.path_to_file)
		self.currentpath = os.path.abspath(self.pathname)
