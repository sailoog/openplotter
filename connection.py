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

import wx, os, sys, re
from classes.paths import Paths
from classes.conf import Conf
from classes.language import Language

paths=Paths()
currentpath=paths.currentpath

class MainFrame(wx.Frame):
		
		def __init__(self):

			self.conf=Conf()
			Language(self.conf.get('GENERAL','lang'))

			wx.Frame.__init__(self, None, title=_('Connection'), size=(550,385))
			
			self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
			
			self.icon = wx.Icon(currentpath+'/openplotter.ico', wx.BITMAP_TYPE_ICO)
			self.SetIcon(self.icon)

			self.in_out=sys.argv[1]
			self.con_type=sys.argv[2]

			wx.StaticText(self, label=_('Name'), pos=(25, 35))
			self.name = wx.TextCtrl(self, -1, size=(120, 32), pos=(20, 55))

			if self.con_type=='serial':
				if self.in_out=='in': wx.StaticBox(self, label=_(' Serial input '), size=(530, 90), pos=(10, 10))
				if self.in_out=='out': wx.StaticBox(self, label=_(' Serial output '), size=(530, 90), pos=(10, 10))
				self.SerDevLs = []
				self.SerialCheck('/dev/rfcomm')
				self.SerialCheck('/dev/ttyUSB')
				self.SerialCheck('/dev/ttyS')
				self.SerialCheck('/dev/ttyACM')
				wx.StaticText(self, label=_('Port'), pos=(155, 35))
				self.deviceComboBox = wx.ComboBox(self, choices=self.SerDevLs, style=wx.CB_DROPDOWN, size=(155, 32), pos=(150, 55))
				if self.SerDevLs : self.deviceComboBox.SetValue(self.SerDevLs[0])
				self.bauds = ['4800', '9600', '19200', '38400', '57600', '115200']
				wx.StaticText(self, label=_('Bauds'), pos=(320, 35))
				self.baudComboBox = wx.ComboBox(self, choices=self.bauds, style=wx.CB_READONLY, size=(90, 32), pos=(315, 55))
				self.baudComboBox.SetValue('4800')

			if self.con_type=='network':
				if self.in_out=='in': 
					wx.StaticBox(self, label=_(' Network input '), size=(530, 90), pos=(10, 10))
					self.gpsd =wx.Button(self, label=_('GPSD'), pos=(440, 55))
					self.Bind(wx.EVT_BUTTON, self.create_gpsd, self.gpsd)
				if self.in_out=='out': wx.StaticBox(self, label=_(' Network output '), size=(530, 90), pos=(10, 10))
				self.type = ['TCP', 'UDP']
				wx.StaticText(self, label=_('Type'), pos=(155, 35))
				self.typeComboBox = wx.ComboBox(self, choices=self.type, style=wx.CB_READONLY, size=(70, 32), pos=(150, 55))
				self.typeComboBox.SetValue('TCP')
				wx.StaticText(self, label=_('Address'), pos=(235, 35))
				self.address = wx.TextCtrl(self, -1, size=(120, 32), pos=(230, 55))
				wx.StaticText(self, label=_('Port'), pos=(365, 35))
				self.port = wx.TextCtrl(self, -1, size=(55, 32), pos=(360, 55))

			wx.StaticBox(self, label=_(' Filter '), size=(530, 195), pos=(10, 105))
			self.mode_filter = [_('none'), _('Accept only sentences:'), _('Ignore sentences:')]
			self.filter = wx.ComboBox(self, choices=self.mode_filter, style=wx.CB_READONLY, size=(220, 32), pos=(20, 130))
			self.filter.SetValue(self.mode_filter[0])
			wx.StaticText(self, label=_('Filtering'), pos=(25, 175))
			self.sentences = wx.TextCtrl(self, -1, style=wx.CB_READONLY, size=(400, 32), pos=(20, 195))
			self.sentences.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_INACTIVECAPTION))
			self.delete =wx.Button(self, label=_('Delete'), pos=(440, 195))
			self.Bind(wx.EVT_BUTTON, self.delete_sentences, self.delete)
			wx.StaticText(self, label=_('Talker - Sentence'), pos=(25, 240))
			self.talker = wx.TextCtrl(self, -1, size=(35, 32), pos=(20, 260))
			wx.StaticText(self, label=_('-'), pos=(60, 265))
			self.sent = wx.TextCtrl(self, -1, size=(45, 32), pos=(70, 260))
			self.add_sent =wx.Button(self, label=_('Add sentence'), pos=(160, 260))
			self.Bind(wx.EVT_BUTTON, self.add_sentence, self.add_sent)

			self.sentences.SetValue(_('nothing'))
			self.talker.SetValue('**')
			self.sent.SetValue('***')

			self.ok =wx.Button(self, label=_('OK'), pos=(440, 310))
			self.Bind(wx.EVT_BUTTON, self.ok_conn, self.ok)
			self.cancel =wx.Button(self, label=_('Cancel'), pos=(330, 310))
			self.Bind(wx.EVT_BUTTON, self.cancel_conn, self.cancel)

			self.Centre()

		def ShowMessage(self, w_msg):
			wx.MessageBox(w_msg, 'Info', wx.OK | wx.ICON_INFORMATION)

		def SerialCheck(self,dev):
			num = 0
			for _ in range(99):
				s = dev + str(num)
				d = os.path.exists(s)
				if d == True:
					self.SerDevLs.append(s)      
				num = num + 1

		def delete_sentences(self,event):
			self.sentences.SetValue(_('nothing'))

		def add_sentence(self,event):
			talker=self.talker.GetValue()
			sent=self.sent.GetValue()

			if not re.match('^[*A-Z]{2}$', talker):
				self.ShowMessage(_('Talker must have 2 uppercase characters. The symbol * matches any character.'))
				return
			if not re.match('^[*A-Z]{3}$', sent):
				self.ShowMessage(_('Sentence must have 3 uppercase characters. The symbol * matches any character.'))
				return

			r_sentence=talker+sent
			if r_sentence=='*****': 
				self.ShowMessage(_('You must enter 2 uppercase characters for talker or 3 uppercase characters for sentence. The symbol * matches any character.'))
				return
			if r_sentence in self.sentences.GetValue(): 
				self.ShowMessage(_('This sentence already exists.'))
				return
			if self.sentences.GetValue()==_('nothing'):
				self.sentences.SetValue(r_sentence)
			else:
				self.sentences.SetValue(self.sentences.GetValue()+','+r_sentence)
		
		def create_gpsd(self,event):
			self.name.SetValue('gpsd')
			self.typeComboBox.SetValue('TCP')
			self.address.SetValue('127.0.0.1')
			self.port.SetValue('2947')

		def ok_conn(self,event):
			name= self.name.GetValue()
			name=name.replace(' ', '_')
			if not re.match('^[_0-9a-z]{1,13}$', name):
				self.ShowMessage(_('"Name" must be a string between 1 and 13 lowercase letters and/or numbers which is not used as name for another input/output.'))
				return

			if self.con_type=='serial':
				type_conn='Serial'
				if self.deviceComboBox.GetValue(): port_address=self.deviceComboBox.GetValue()
				else:
					self.ShowMessage(_('You must select a Port.'))
					return
				bauds_port=self.baudComboBox.GetValue()


			if self.con_type=='network':
				type_conn=self.typeComboBox.GetValue()
				if self.address.GetValue(): port_address=self.address.GetValue()
				else:
					self.ShowMessage(_('You must enter an Address.'))
					return
				if self.port.GetValue(): bauds_port=self.port.GetValue()
				else:
					self.ShowMessage(_('You must enter a Port.'))
					return
			
			if self.filter.GetValue()==_('none') and self.sentences.GetValue()!=_('nothing'):
				self.ShowMessage(_('You must select a Filter type.'))
				return

			filter_type='none'
			filtering='nothing'

			if self.filter.GetValue()==_('Accept only sentences:') and self.sentences.GetValue()!=_('nothing'):
				filter_type='accept'
				filtering=''
				r=self.sentences.GetValue()
				l=r.split(',')
				for index,item in enumerate(l):
					if index!=0: filtering+=':'
					filtering+='+'+item
				filtering+=':-all'
				

			if self.filter.GetValue()==_('Ignore sentences:') and self.sentences.GetValue()!=_('nothing'):
				filter_type='ignore'
				filtering=''
				r=self.sentences.GetValue()
				l=r.split(',')
				for index,item in enumerate(l):
					if index!=0: filtering+=':'
					filtering+='-'+item


			print  self.in_out+','+name+','+type_conn+','+port_address+','+bauds_port+','+filter_type+','+filtering+',1'
			self.Destroy()

		def cancel_conn(self,event):
			self.Destroy()

#Main#############################
if __name__ == "__main__":
	app = wx.App()
	MainFrame().Show()
	app.MainLoop()