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

class Actions():

	def __init__(self):

		self.options=[None]*18

		self.options[0]= _('nothing')
		self.options[1]= _('command')
		self.options[2]= _('reset')
		self.options[3]= _('shutdown')
		self.options[4]= _('stop NMEA multiplexer')
		self.options[5]= _('reset NMEA multiplexer')
		self.options[6]= _('stop Signal K server')
		self.options[7]= _('reset Signal K server')
		self.options[8]= _('stop WiFi access point')
		self.options[9]= _('start WiFi access point')
		self.options[10]= _('stop SDR-AIS')
		self.options[11]= _('reset SDR-AIS')
		self.options[12]= _('start Twitter monitoring')
		self.options[13]= _('stop Twitter monitoring')
		self.options[14]= _('publish Twitter')
		self.options[15]= _('start Gmail monitoring')
		self.options[16]= _('stop Gmail monitoring')
		self.options[17]= _('send e-mail')

		self.time_units=[_('no repeat'),_('second'), _('minute'), _('hour'), _('day')]
