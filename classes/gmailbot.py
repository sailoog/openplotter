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

import smtplib
from email.mime.text import MIMEText

class GmailBot:
	def __init__(self, GMAIL_USERNAME,GMAIL_PASSWORD,recipient):
		self.SMTP_SERVER = 'smtp.gmail.com'
		self.SMTP_PORT = 587
		self.GMAIL_USERNAME = GMAIL_USERNAME
		self.GMAIL_PASSWORD = GMAIL_PASSWORD
		self.recipient = recipient

	def send(self,subject,body ):
		msg = MIMEText(body)
		msg['Subject'] = subject
		msg['From'] = self.GMAIL_USERNAME
		msg['To'] = self.recipient
		session = smtplib.SMTP(self.SMTP_SERVER, self.SMTP_PORT)
		session.starttls()
		session.login(self.GMAIL_USERNAME, self.GMAIL_PASSWORD)
		session.sendmail(self.GMAIL_USERNAME, self.recipient, msg.as_string())
		session.quit()