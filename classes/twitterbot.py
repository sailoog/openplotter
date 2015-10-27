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

from twython import Twython

class TwitterBot:

	def __init__(self, apiKey, apiSecret, accessToken, accessTokenSecret):
		self._apiKey = apiKey
		self._apiSecret = apiSecret
		self._accessToken = accessToken
		self._accessTokenSecret = accessTokenSecret
	
	def send(self, tweetStr):
		self.tweetStr = tweetStr
		api = Twython(self._apiKey,self._apiSecret,self._accessToken,self._accessTokenSecret)
		api.update_status(status=self.tweetStr)
