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
import ConfigParser, os

class Conf:
	def __init__(self):

		self.home = os.path.expanduser('~')
		self.data_conf = ConfigParser.SafeConfigParser()

		if 'root' in self.home:
			self.home = '/home/'+os.path.expanduser(os.environ["SUDO_USER"])

		self.conf_folder = self.home+'/.openplotter'
		if not os.path.exists(self.conf_folder):
			print 'creating configuration directory', self.conf_folder
			os.mkdir(self.conf_folder)

		self.op_folder = os.path.normpath(os.path.dirname(os.path.abspath(__file__))+'/..')

		self.conf_file = self.conf_folder+'/openplotter.conf'
		if not os.path.exists(self.conf_file):
			# setup config if it doesn't exist
			print 'openplotter.conf not found, copying default'
			import shutil
			shutil.copy(self.op_folder+'/openplotter.conf', self.conf_file)

		self.read()

		op_folder2 = self.get('GENERAL', 'op_folder')
		if op_folder2 != self.op_folder:
			print 'op_folder:', op_folder2, 'invalid'
			print 'resetting op_folder to', self.op_folder
			self.set('GENERAL', 'op_folder', self.op_folder)

	def read(self):
		self.data_conf.read(self.conf_file)

	def write(self):
		with open(self.conf_file, 'wb') as configfile:
			self.data_conf.write(configfile)

	def get(self, section, item):
		result = ''
		try:
			result = self.data_conf.get(section, item)
		except ConfigParser.NoSectionError:
			self.read()
			try:
				self.data_conf.add_section(section)
			except ConfigParser.DuplicateSectionError: pass
			self.data_conf.set(section, item, '')
			self.write()
		except ConfigParser.NoOptionError:
			self.set(section, item, '')
		return result

	def set(self, section, item, value):
		self.read()
		try:
			self.data_conf.set(section, item, value)
		except ConfigParser.NoSectionError:
			self.data_conf.add_section(section)
			self.data_conf.set(section, item, value)
		self.write()

	def has_option(self, section, item):
		return self.data_conf.has_option(section, item)

	def has_section(self, section):
		return self.data_conf.has_section(section)

	def add_section(self, section):
		return self.data_conf.add_section(section)

class Conf2:
	def __init__(self, folder, file):
		self.home = os.path.expanduser('~')
		if 'root' in self.home:
			self.home = '/home/'+os.path.expanduser(os.environ["SUDO_USER"])
		self.conf_file_path = self.home+'/.openplotter/tools/'+folder+'/'+file
		self.data_conf = ConfigParser.SafeConfigParser()
		if not os.path.isfile(self.conf_file_path):
			with open(self.conf_file_path,'w') as f:
				f.write('[GENERAL]')
		self.read()

	def read(self):
		self.data_conf.read(self.conf_file_path)

	def write(self):
		with open(self.conf_file_path, 'wb') as configfile:
			self.data_conf.write(configfile)

	def get(self, section, item):
		result = ''
		try:
			result = self.data_conf.get(section, item)
		except ConfigParser.NoSectionError:
			self.read()
			try:
				self.data_conf.add_section(section)
			except ConfigParser.DuplicateSectionError: pass
			self.data_conf.set(section, item, '')
			self.write()
		except ConfigParser.NoOptionError:
			self.set(section, item, '')
		return result

	def set(self, section, item, value):
		self.read()
		try:
			self.data_conf.set(section, item, value)
		except ConfigParser.NoSectionError:
			self.data_conf.add_section(section)
			self.data_conf.set(section, item, value)
		self.write()

	def has_option(self, section, item):
		return self.data_conf.has_option(section, item)

	def has_section(self, section):
		return self.data_conf.has_section(section)

	def add_section(self, section):
		return self.data_conf.add_section(section)
