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

edit = sys.argv[1]

conf = Conf()
Language(conf)
data = conf.get('SPI', 'value_' + str(edit))
listsave = []
try:
    temp_list = eval(data)
except:
    temp_list = []
for ii in temp_list:
    listsave.append(ii)
plt.plot(*zip(*listsave))
plt.suptitle(
    _('settings to convert raw adc values (unlinear and/or no factor and/or no offset)\n to useable values  for input ') + str(
        edit), fontsize=12)
plt.xlabel(_('row adc value'), fontsize=12)
plt.ylabel(_('value in unit'), fontsize=12)
plt.show()

