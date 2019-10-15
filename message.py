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

import wx, sys
from classes.language import Language
from classes.conf import Conf

text=sys.argv[1]
lang=sys.argv[2]

class MyFrame(wx.Frame):
	def __init__(self, parent):
		conf = Conf()
		Language(conf)
		wx.Frame.__init__(self, parent)
		dlg = wx.MessageDialog(self, text, _('Message'), wx.OK | wx.ICON_WARNING)
		dlg.ShowModal()
		sys.exit()

app = wx.App(False)
frame = MyFrame(None)
app.MainLoop()