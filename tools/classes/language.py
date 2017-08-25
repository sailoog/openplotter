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
import gettext

class Language:

	def __init__(self, conf):

		home = conf.home
		op_folder = conf.get('GENERAL', 'op_folder')+'/openplotter'
		locale_folder = home+op_folder+'/locale'
		language = conf.get('GENERAL', 'lang')

		gettext.install('openplotter', locale_folder, unicode=False)
		presLan_en = gettext.translation('openplotter', locale_folder, languages=['en'])
		presLan_ca = gettext.translation('openplotter', locale_folder, languages=['ca'])
		presLan_es = gettext.translation('openplotter', locale_folder, languages=['es'])
		presLan_fr = gettext.translation('openplotter', locale_folder, languages=['fr'])
		presLan_nl = gettext.translation('openplotter', locale_folder, languages=['nl'])
		presLan_de = gettext.translation('openplotter', locale_folder, languages=['de'])

		if language=='en':presLan_en.install()
		if language=='ca':presLan_ca.install()
		if language=='es':presLan_es.install()
		if language=='fr':presLan_fr.install()
		if language=='nl':presLan_nl.install()
		if language=='de':presLan_de.install()
