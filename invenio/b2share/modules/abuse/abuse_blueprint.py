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

""" B2SHARE Abuse Form Blueprint"""
from flask import request
from invenio.webinterface_handler_flask_utils import _, InvenioBlueprint
import invenio.abuse_form as abuse

blueprint = InvenioBlueprint('abuse_form', __name__,
	url_prefix='/abuse'
	)

@blueprint.route('/', methods=['GET'])
def abuse_form_noparams():
	return abuse.abuse_form(request,-1)

@blueprint.route('/<recid>',methods=['GET'])
def abuse_form(recid):
	return abuse.abuse_form(request,recid)

@blueprint.route('/submit',methods=['POST'])
def abuse_submit():
	return abuse.abuse_submit(request)
