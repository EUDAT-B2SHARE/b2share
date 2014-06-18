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


from flask import request
from invenio.webinterface_handler_flask_utils import _, InvenioBlueprint
import invenio.request_data_form as reqdata

blueprint = InvenioBlueprint('request_data_form', __name__,
	url_prefix='/reqdata'
	)

@blueprint.route('/', methods=['GET'])
def request_data_form_noparams():
    return reqdata.request_data_form(request,-1)

@blueprint.route('/<recid>',methods=['GET'])
def request_data_form(recid):
    return reqdata.request_data_form(request,recid)

@blueprint.route('/submit',methods=['POST'])
def request_data_submit():
    return reqdata.request_data_submit(request)
