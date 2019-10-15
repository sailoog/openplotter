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

import wx, os, sys, subprocess

op_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')
sys.path.append(op_folder+'/classes')
from conf import Conf
from language import Language
from add_NMEA_0183 import addNMEA_0183

class MyFrame(wx.Frame):
		
		def __init__(self):

			self.conf = Conf()
			self.home = self.conf.home
			self.currentpath = self.home+self.conf.get('GENERAL', 'op_folder')+'/openplotter'

			Language(self.conf)

			wx.Frame.__init__(self, None, title=_('NMEA 0183 generator'), size=(690,350))
			
			self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
			
			self.icon = wx.Icon(self.currentpath+'/openplotter.ico', wx.BITMAP_TYPE_ICO)
			self.SetIcon(self.icon)

			wx.StaticBox(self, label=_(' NMEA 0183 '), size=(670, 230), pos=(10, 10))
			self.list_nmea = wx.ListCtrl(self, style=wx.LC_REPORT, size=(565, 200), pos=(15, 30))
			self.list_nmea.InsertColumn(0, _('Sentence'), width=100)
			self.list_nmea.InsertColumn(1, _('Rate'), width=50)
			self.list_nmea.InsertColumn(2, _('Fields'), width=1500)

			self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.edit_nmea, self.list_nmea)
				
			self.add_nmea_button =wx.Button(self, label=_('add'), pos=(585, 30))
			self.Bind(wx.EVT_BUTTON, self.add_nmea, self.add_nmea_button)

			self.delete_nmea_button =wx.Button(self, label=_('delete'), pos=(585, 65))
			self.Bind(wx.EVT_BUTTON, self.delete_nmea, self.delete_nmea_button)

			self.compat_nmea_button =wx.Button(self, label=_('opencpn\ndefault'), pos=(585, 189))
			self.Bind(wx.EVT_BUTTON, self.compat_nmea, self.compat_nmea_button)

			self.diagnostic_nmea_button=wx.Button(self, label=_('NMEA Diagnostic'), pos=(10, 250))
			self.Bind(wx.EVT_BUTTON, self.kplex_diagnostic, self.diagnostic_nmea_button)

			self.diagnostic_sk_button=wx.Button(self, label=_('SK Diagnostic'), pos=(180, 250))
			self.Bind(wx.EVT_BUTTON, self.sk_diagnostic, self.diagnostic_sk_button)


			self.CreateStatusBar()

			self.Centre()

			self.Show(True)

			self.read_sentences()


		def start_d(self):
			subprocess.call(['pkill', '-f', 'SK-base_d.py'])
			subprocess.Popen(['python',self.currentpath+'/SK-base_d.py'])
			

		def read_sentences(self):
			self.sentences=[]
			self.list_nmea.DeleteAllItems()
			data=self.conf.get('NMEA0183', 'sentences')
			try:
				temp_list=eval(data)
			except:temp_list=[]
			for ii in temp_list:
				self.sentences.append(ii)
				fields=','
				for i in ii[1]:
					if type(i) is str: fields+=i+','
					elif type(i) is list:
						fields+=i[1]+','
				self.list_nmea.Append([ii[0],ii[2],fields])
		

		def edit_nmea(self,e):
			selected_sentence=e.GetIndex()
			edit=[selected_sentence,self.sentences[selected_sentence]]
			self.edit_add_nmea(edit)

		def add_nmea(self,e):
			self.edit_add_nmea(0)

		def edit_add_nmea(self,edit):
			self.SetStatusText('')
			dlg = addNMEA_0183(edit, self.conf)
			res = dlg.ShowModal()
			if res == wx.ID_OK:
				nmea=dlg.nmea
				if not nmea[0]: return
				if edit==0:
					fields=','
					for i in nmea[1]:
						if type(i) is str: fields+=i+','
						elif type(i) is list:
							fields+=i[1]+','
					self.list_nmea.Append([nmea[0],nmea[2],fields])
					self.sentences.append([nmea[0],nmea[1],nmea[2]])
				else:
					self.list_nmea.SetStringItem(edit[0],0,nmea[0])
					self.list_nmea.SetStringItem(edit[0],1,str(nmea[2]))
					fields=','
					for i in nmea[1]:
						if type(i) is str: fields+=i+','
						elif type(i) is list:
							fields+=i[1]+','
					self.list_nmea.SetStringItem(edit[0],2,fields)
					self.sentences[edit[0]][0]=nmea[0]
					if '[' in nmea[1]: nmea[1]=eval(nmea[1])
					self.sentences[edit[0]][1]=nmea[1]
					self.sentences[edit[0]][2]=nmea[2]
				self.conf.set('NMEA0183', 'sentences', str(self.sentences))
				self.start_d()
			dlg.Destroy()

		def delete_nmea(self,e):
			self.SetStatusText('')
			selected_sentence=self.list_nmea.GetFirstSelected()
			if selected_sentence==-1: 
				self.SetStatusText('Select a sentence to delete.')
				return
			del self.sentences[selected_sentence]
			self.list_nmea.DeleteItem(selected_sentence)
			self.conf.set('NMEA0183', 'sentences', str(self.sentences))
			self.start_d()

		def compat_nmea(self,e):
			if self.list_nmea.GetItemCount()>0:
				self.SetStatusText(_('This function is only allowed when the list is empty.'))
				return
			self.conf.set('NMEA0183', 'sentences', "[['HDG', [['navigation.headingMagnetic', 'x.x|deg', '+', 0.0], '', '', '', ''], 0.5], ['XDR', ['A', ['navigation.attitude.roll', 'x.x|deg', '+', 0.0], 'D', 'ROLL'], 1.0], ['XDR', ['A', ['navigation.attitude.pitch', 'x.x|deg', '+', 0.0], 'D', 'PTCH'], 1.0], ['XDR', ['P', ['environment.outside.pressure', 'x.xxxx', '/', 100000.0], 'B', 'Barometer'], 5.0], ['XDR', ['C', ['environment.outside.temperature', 'x.x|C', '+', 0.0], 'C', 'ENV_OUTAIR_T'], 5.0], ['MTW', [['environment.water.temperature', 'x.x|C', '+', 0.0], 'C'], 5.0]]")
			self.start_d()
			self.read_sentences()
			
		def kplex_diagnostic(self,e):
			wx.MessageBox('use diagnostic on NMEA0183\nselect system\npush diagnostic', 'Info', wx.OK | wx.ICON_INFORMATION)

		def sk_diagnostic(self,e):
			subprocess.call(['pkill', '-f', 'diagnostic-SK-input.py'])
			subprocess.Popen(['python',self.currentpath+'/diagnostic-SK-input.py'])

app = wx.App()
MyFrame().Show()
app.MainLoop()