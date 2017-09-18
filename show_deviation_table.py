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
import matplotlib.pyplot as plt
import sys
from classes.conf import Conf
from classes.language import Language

conf = Conf()
Language(conf)

data = conf.get('COMPASS', 'deviation')
listsave = []
try:
	listsave = eval(data)
except:
	listsave = []

x=[]
y=[]
for ii in listsave:
	x.append(ii[1] - ii[0])
	y.append(ii[0])

plt.plot(x,y)
plt.suptitle(_('Show deviation table as curve'), fontsize=12)
plt.xlabel(_('Deviation'), fontsize=12)
plt.ylabel(_('Compass Heading'), fontsize=12)
plt.show()

