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

import wx, sys, os, ConfigParser, re, subprocess, socket

##########################################################################
# You can access to all OpenPlotter classes
home = os.path.expanduser('~')
if 'root' in home:
	home = '/home/'+os.path.expanduser(os.environ["SUDO_USER"])
data_conf = ConfigParser.SafeConfigParser()
data_conf.read(home+'/.openplotter/openplotter.conf')
op_installation_folder = data_conf.get('GENERAL', 'op_folder')
op_folder = home+op_installation_folder+'/openplotter'
sys.path.append(op_folder)
##########################################################################

from classes.conf import Conf, Conf2
from classes.select_key import selectKey
from classes.language import Language

##########################################################################
# If you are using a config file for your tool, edit "conf_file" variable.
# If the file does not exist it will be created in ~/.openplotter.
# If you do not need a config file remove this block.
conf_file = 'demo_tool.conf'

# This will open the config file with the text editor when the button 
# settings is pressed and the argument "settings" is passed.
conf2 = Conf2(conf_file)
if len(sys.argv)>1:
	if sys.argv[1]=='settings':
		subprocess.Popen(['leafpad',home+'/.openplotter/'+conf_file])
	exit()
##########################################################################

class MyFrame(wx.Frame):
		
		def __init__(self):
			# This creates a UDP socket
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

			# This opens the OpenPlotter configuration file in ~/.openplotter/openplotter.conf
			self.conf = Conf()

			Language(self.conf)
			
			title = _('Demo tool')

			wx.Frame.__init__(self, None, title=title, size=(600,330))
			
			self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
			
			self.icon = wx.Icon(op_folder+'/openplotter.ico', wx.BITMAP_TYPE_ICO)
			self.SetIcon(self.icon)

			panel = wx.Panel(self)

			# Getting info from OpenPlotter configuration file. When reading from demo tool conf file or OpenPlotter conf file, if section or option do not exist, they will be created with no value.
			op_data_box = wx.StaticBox(panel, -1, _(' OpenPlotter config data '))
			version = _('OpenPlotter version: ')+self.conf.get('GENERAL', 'version')+' '+ self.conf.get('GENERAL', 'state')
			text1 = wx.StaticText(panel, label = version)

			sk_key_box = wx.StaticBox(panel, -1, _(' Working with Signal K '))
			text2 = wx.StaticText(panel, label = _('Select a Signal K key'))
			self.SKkey = wx.TextCtrl(panel, style=wx.CB_READONLY)
			self.SKkey.SetValue(conf2.get('SIGNALK', 'key'))
			self.edit_skkey = wx.Button(panel, label= _('Edit'))
			# This uses the OpenPlotter class to select a signal k key
			self.edit_skkey.Bind(wx.EVT_BUTTON, self.onEditSkkey)
			text3 = wx.StaticText(panel, label = _('Write some text to publish'))
			self.data = wx.TextCtrl(panel)
			self.data.SetValue(conf2.get('SIGNALK', 'data'))
			self.button_publish = wx.Button(panel, label= _('Publish'))
			self.button_publish.Bind(wx.EVT_BUTTON, self.onPublish)

			button_cancel =wx.Button(panel, label= _('Cancel'))
			self.Bind(wx.EVT_BUTTON, self.on_cancel, button_cancel)

			button_ok =wx.Button(panel, label=_('OK'))
			self.Bind(wx.EVT_BUTTON, self.on_ok, button_ok)

			v_boxSizer1 = wx.StaticBoxSizer(op_data_box, wx.VERTICAL)
			v_boxSizer1.AddSpacer(5)
			v_boxSizer1.Add(text1, 0, wx.ALL | wx.EXPAND, 5)

			h_boxSizer1 = wx.BoxSizer(wx.HORIZONTAL)
			h_boxSizer1.Add(self.SKkey, 1, wx.ALL | wx.EXPAND, 5)
			h_boxSizer1.Add(self.edit_skkey, 0, wx.ALL | wx.EXPAND, 5)

			h_boxSizer2 = wx.BoxSizer(wx.HORIZONTAL)
			h_boxSizer2.Add(self.data, 1, wx.ALL | wx.EXPAND, 5)
			h_boxSizer2.Add(self.button_publish, 0, wx.ALL | wx.EXPAND, 5)

			v_boxSizer2 = wx.StaticBoxSizer(sk_key_box, wx.VERTICAL)
			v_boxSizer2.AddSpacer(5)
			v_boxSizer2.Add(text2, 0, wx.ALL | wx.EXPAND, 5)
			v_boxSizer2.Add(h_boxSizer1, 0, wx.ALL | wx.EXPAND, 5)
			v_boxSizer2.Add(text3, 0, wx.ALL | wx.EXPAND, 5)
			v_boxSizer2.Add(h_boxSizer2, 0, wx.ALL | wx.EXPAND, 5)

			buttons = wx.BoxSizer(wx.HORIZONTAL)
			buttons.Add((0,0), 1, wx.ALL | wx.EXPAND, 0)
			buttons.Add(button_cancel, 0, wx.ALL | wx.EXPAND, 10)
			buttons.Add(button_ok, 0, wx.ALL | wx.EXPAND, 10)

			vbox3 = wx.BoxSizer(wx.VERTICAL)
			vbox3.Add(v_boxSizer1, 0, wx.ALL | wx.EXPAND, 5)
			vbox3.Add(v_boxSizer2, 0, wx.ALL | wx.EXPAND, 5)
			vbox3.Add(buttons, 0, wx.ALL | wx.EXPAND, 0)

			panel.SetSizer(vbox3)

			self.Centre()

		def onEditSkkey(self,e):
			key = self.SKkey.GetValue()
			dlg = selectKey(key)
			res = dlg.ShowModal()
			if res == wx.ID_OK:
				key = dlg.keys_list.GetValue()
				if '*' in key:
					wildcard = dlg.wildcard.GetValue()
					if wildcard:
						if not re.match('^[0-9a-zA-Z]+$', wildcard):
							self.ShowMessage(_('Failed. * must contain only allowed characters.'))
							dlg.Destroy()
							return
						key = key.replace('*',wildcard)
					else:
						self.ShowMessage(_('Failed. You have to provide a name for *.'))
						dlg.Destroy()
						return
				self.SKkey.SetValue(key)
			dlg.Destroy()

		def onPublish(self,e):
			key = self.SKkey.GetValue()
			data = self.data.GetValue()
			# Saving data to demo tool conf file in ~/.openplotter/
			conf2.set('SIGNALK', 'key', key)
			conf2.set('SIGNALK', 'data', data)
			#Sending data to Signal K server. Port 55557 is used to send sensors data.
			SignalK_delta = '{"updates":[{"$source":"OPdemo","values":[{"path":"'+key+'","value":"'+data+'"}]}]}\n'
			self.sock.sendto(SignalK_delta, ('127.0.0.1', 55557))

		def on_ok(self, e):
			self.Close()

		def on_cancel(self, e):
			self.Close()

		def ShowMessage(self, w_msg):
			wx.MessageBox(w_msg, 'Info', wx.OK | wx.ICON_INFORMATION)


app = wx.App()
MyFrame().Show()
app.MainLoop()