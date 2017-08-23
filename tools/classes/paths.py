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
		self.currentpath = os.path.dirname(os.path.realpath(__file__))
		tool_path = os.path.join(self.currentpath, '..')
		op_path = os.path.join(self.currentpath, '../..')
		self.tool_path = os.path.abspath(tool_path)
		self.op_path = os.path.abspath(op_path)
