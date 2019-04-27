#!/usr/bin/env python

# This file is part of Openplotter.
# Copyright (C) 2019 by sailoog <https://github.com/sailoog/openplotter>
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
import ConfigParser, subprocess
from conf import Conf

class opencpnSettings:

	def __init__(self):

		conf = Conf()
		home = conf.home
		self.confFile = home+'/.opencpn/opencpn.conf'
		self.confData = ConfigParser.SafeConfigParser()

	def getConnectionState(self):
		result = False
		self.confData.read(self.confFile)
		tmp = self.confData.get('Settings/NMEADataSource', 'DataConnections')
		connections = tmp.split('|')
		for connection in connections:
			#0;1;2;3;4;5;6;7;8;9;10;11;12;13;14;15;16;17;18
			#serial/network;TCP/UDP/GPSD;address;port;?;serialport;bauds;?;0=input/1=input+output/2=output;?;?;?;?;?;?;?;?;enabled/disabled;comments
			items = connection.split(';')
			if items[0] == '1':
				if items[1] == '0':
					if items[2] == 'localhost':
						if items[3] == '10110':
							if items[8] == '0' or items[8] == '1':
								if items[17] == '1': result = 'enabled'
								else: result = 'disabled'
		return result
