# -*- coding: utf-8 -*-

## This file is part of B2SHARE.
## Copyright (C) 2013 EPCC, The University of Edinburgh.
##
## B2SHARE is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## B2SHARE is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with B2SHARE; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.



from flask import render_template, current_app

from invenio_ext.email import send_email
from recaptcha.client import captcha
from validate_email import validate_email
import re

def check_phone(num):
	if not re.match("^[0-9-+]+",num):
		return False
	return True

def request_data_form(request,recid):
	if(recid == -1):
		link_txt = ""
	else:
		link_txt = current_app.config['CFG_SITE_URL'] + "/record/" + recid
	return render_template('request_data.html',full_link=link_txt, recaptcha_public_key=current_app.config['CFG_CAPTCHA_PUBLIC_KEY'])

def request_data_submit(request):
	link = request.form.get('element_9_1','')
	#subject = request.form.get('element_1','')
	reason = request.form.get('element_7','')
	first_name = request.form.get('element_3_1','')
	last_name = request.form.get('element_3_2','')
	affiliation = request.form.get('element_5','')
	email = request.form.get('element_6','')
	phone = request.form.get('element_4','')
	country = request.form.get('element_2_6','')
	recaptcha_challenge = request.form.get('recaptcha_challenge_field','')
	recaptcha_response = request.form.get('recaptcha_response_field','')
	subject_text = "Request Data"
	recaptcha_public_key=current_app.config['CFG_CAPTCHA_PUBLIC_KEY']

	if(link == '' or len(link)>256):
		return render_template('request_data.html',warning_msg="Link is missing", recaptcha_public_key=recaptcha_public_key)

	if(reason == ''):
		return render_template('request_data.html',warning_msg="Message body is missing", recaptcha_public_key=recaptcha_public_key)

	if(first_name == '' or len(first_name) > 256):
		return render_template('request_data.html',warning_msg="First Name is missing", recaptcha_public_key=recaptcha_public_key)

	if(last_name == '' or len(last_name) > 256):
		return render_template('request_data.html',warning_msg="Last Name is missing", recaptcha_public_key=recaptcha_public_key)

	if(affiliation == '' or len(affiliation) > 256):
		return render_template('request_data.html',warning_msg="Affiliation is missing", recaptcha_public_key=recaptcha_public_key)

	if(email == '' or validate_email(email,verify=False) == False):
		return render_template('request_data.html',warning_msg="Email address missing or format is invalid", recaptcha_public_key=recaptcha_public_key)

	if(country == ''or len(country) > 256):
		return render_template('request_data.html',warning_msg="Country is missing", recaptcha_public_key=recaptcha_public_key)

	if(phone == '' or check_phone(phone) == False or len(phone) > 30):
		return render_template('request_data.html',warning_msg="Phone is missing or invalid format", recaptcha_public_key=recaptcha_public_key)

	if(recaptcha_challenge == ''):
		return render_template('request_data.html',warning_msg="Recaptcha Challenge is missing", recaptcha_public_key=recaptcha_public_key)

	if(recaptcha_response == ''):
		return render_template('request_data.html',warning_msg="Recaptcha Response is missing", recaptcha_public_key=recaptcha_public_key)

	submit_response = captcha.submit(
		recaptcha_challenge,
		recaptcha_response,
		current_app.config['CFG_CAPTCHA_PRIVATE_KEY'],
		request.remote_addr
	)

	if not submit_response.is_valid:
		return render_template('request_data.html',warning_msg="Incorrect Captcha response", recaptcha_public_key=recaptcha_public_key)

	else:
		msg_content = """
You have a request for your data!

Link: """ + link + """
Subject: """ + subject_text + """
Reason: """ + reason + """
First Name: """ + first_name + """
Last Name: """ + last_name + """
Affiliation: """ + affiliation + """
Email: """ + email + """
Country: """ + country + """
Phone: """ + phone + """

"""

		send_email(email,current_app.config['CFG_SITE_SUPPORT_EMAIL'],
			subject='Request Data',content=msg_content)

		return render_template('request_data.html',warning_msg="Request Data submitted!", recaptcha_public_key=recaptcha_public_key)
