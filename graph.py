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

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os, sys, datetime, csv
from matplotlib.widgets import Cursor

pathname = os.path.dirname(sys.argv[0])
currentpath = os.path.abspath(pathname)

ifile  = open(currentpath+'/weather_log.csv', "r")
reader = csv.reader(ifile)
log_list = []
for row in reader:
	log_list.append(row)
ifile.close()

dates=[]
pressure=[]
temperature=[]

for i in range(0,len(log_list)):
	dates.append(datetime.datetime.fromtimestamp(float(log_list[i][0])))
	pressure.append(round(float(log_list[i][1]),1))
	temperature.append(round(float(log_list[i][2]),1))

fig=plt.figure()
plt.rc("font", size=10)
fig.canvas.set_window_title('Thermograph / Barograph')
ax1 = fig.add_subplot(211)
ax2 = fig.add_subplot(212, sharex=ax1)

ax1.plot(dates,temperature,'ro-')
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M\n%d-%m'))
ax1.set_title('Temperature (Cel)')
ax1.grid(True)

ax2.plot(dates,pressure,'go-')
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M\n%d-%m'))
ax2.set_title('Pressure (hPa)')
ax2.grid(True)

plt.tight_layout()
cursor = Cursor(ax1, useblit=True, color='gray', linewidth=1 )
cursor2 = Cursor(ax2, useblit=True, color='gray', linewidth=1 )
plt.show()
