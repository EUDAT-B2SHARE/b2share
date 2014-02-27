# -*- coding: utf-8 -*-

## This file is part of SimpleStore.
## Copyright (C) 2013 EPCC, The University of Edinburgh.
##
## SimpleStore is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## SimpleStore is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with SimpleStore; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

from flask import render_template, request, redirect, url_for, jsonify

from invenio.config import CFG_SITE_SECRET_KEY
from invenio.bibtask import task_low_level_submission
from invenio.config import CFG_TMPSHAREDDIR
from invenio.wtforms_utils import InvenioBaseForm
from invenio.webuser_flask import current_user
from invenio.htmlutils import remove_html_markup
from invenio.mailutils import send_email
from invenio.config import CFG_SITE_SUPPORT_EMAIL
from recaptcha.client import captcha
from invenio.config import CFG_CAPTCHA_PRIVATE_KEY
from validate_email import validate_email
from invenio.config import CFG_SITE_URL
import re

def check_phone(num):
	if not re.match("^[0-9-+]+",num):
		return False
	return True

def abuse_form(request,recid):
	if(recid == -1):
		link_txt = ""
	else:
		link_txt = CFG_SITE_URL + "/record/" + recid
	return render_template('abuse_form.html',full_link=link_txt)

def abuse_submit(request):
	link = request.form.get('element_9_1','')
	subject = request.form.get('element_1','')	
	reason = request.form.get('element_7','')
	first_name = request.form.get('element_3_1','')
	last_name = request.form.get('element_3_2','')
	affiliation = request.form.get('element_5','')
	email = request.form.get('element_6','')
	street_address = request.form.get('element_2_1','')
	street_address2 = request.form.get('element_2_2','')
	city = request.form.get('element_2_3','')
	state_name = request.form.get('element_2_4','')
	postal_code = request.form.get('element_2_5','')
	phone = request.form.get('element_4','')
	country = request.form.get('element_2_6','')
	recaptcha_challenge = request.form.get('recaptcha_challenge_field','')
	recaptcha_response = request.form.get('recaptcha_response_field','')
	subject_text = "Unknown subject"
	
	if(link == '' or len(link)>256): 
		return render_template('abuse_form.html',warning_msg="Link is missing")	
	
	if(subject == ''):
		return render_template('abuse_form.html',warning_msg="Subject is missing")	
	else:
		if(subject == "1"):
			subject_text = "Abuse or Inappropriate content"
		elif(subject == "2"):
			subject_text = "Copyrighted material"
		elif(subject == "3"):
			subject_text = "No research data"
		elif(subject == "4"):
			subject_text = "Illegal content"

	if(reason == ''):
		return render_template('abuse_form.html',warning_msg="Reason is missing")

	if(first_name == '' or len(first_name) > 256):
		return render_template('abuse_form.html',warning_msg="First Name is missing")

	if(last_name == '' or len(last_name) > 256):
		return render_template('abuse_form.html',warning_msg="Last Name is missing")

	if(affiliation == '' or len(affiliation) > 256):
		return render_template('abuse_form.html',warning_msg="Affiliation is missing")
	
	if(email == '' or validate_email(email,verify=True) == False):
		return render_template('abuse_form.html',warning_msg="Email address missing or format is invalid")

	if(street_address == '' or len(street_address) > 256):	
		return render_template('abuse_form.html',warning_msg="Street Address is missing")

	if(len(street_address2) > 256):
		return render_template('abuse_form.html',warning_msg="Street Address2 format is invalid")

        if(postal_code == '' or len(postal_code) > 20):
                return render_template('abuse_form.html',warning_msg="Postal Code is missing")

        if(country == ''or len(country) > 256):
                return render_template('abuse_form.html',warning_msg="Country is missing")

	if(phone == '' or check_phone(phone) == False or len(phone) > 30):
		return render_template('abuse_form.html',warning_msg="Phone is missing or invalid format")

	if(recaptcha_challenge == ''):
		return render_template('abuse_form.html',warning_msg="Recaptcha Challenge is missing")
	
	if(recaptcha_response == ''):
		return render_template('abuse_form.html',warning_msg="Recaptcha Response is missing")

	submit_response = captcha.submit(
		recaptcha_challenge,
		recaptcha_response,
		CFG_CAPTCHA_PRIVATE_KEY,
		request.remote_addr
	)
	
	if not submit_response.is_valid:
		return render_template('abuse_form.html',warning_msg="Incorrect Captcha response")

	else:
		msg_content = """
We have received new abuse report!

Link: """ + link + """
Subject: """ + subject_text + """
Reason: """ + reason + """
First Name: """ + first_name + """
Last Name: """ + last_name + """
Affiliation: """ + affiliation + """
Email: """ + email + """
Street Address: """ + street_address + """
Street Address2: """ + street_address2 + """
State Name: """ + state_name + """
Postal Code: """ + postal_code + """
Country: """ + country + """
Phone: """ + phone + """

"""

		send_email(email,CFG_SITE_SUPPORT_EMAIL,
			subject='New Abuse Report',content=msg_content)

		return render_template('abuse_form.html',warning_msg="Abuse report submitted!")
