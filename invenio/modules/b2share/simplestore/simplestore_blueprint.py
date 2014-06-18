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

"""SimpleStore Flask Blueprint"""
from flask import request
from invenio.webinterface_handler_flask_utils import _, InvenioBlueprint
import invenio.simplestore_upload_handler as uph
import invenio.simplestore_deposit_handler as dep

blueprint = InvenioBlueprint('simplestore', __name__,
                             url_prefix='/deposit',
                             menubuilder=[('main.simplestore',
                                          _('Deposit'),
                                          'simplestore.deposit', 2)],
                             breadcrumbs=[(_('Deposit'),
                                          'simplestore.deposit')])


@blueprint.route('/', methods=['GET'])
@blueprint.invenio_authenticated
def deposit():
    return dep.deposit(request)


@blueprint.route('/addmeta/<sub_id>', methods=['POST'])
@blueprint.invenio_authenticated
def addmeta(sub_id):
    return dep.addmeta(request, sub_id)


@blueprint.route('/upload/<sub_id>', methods=['POST'])
@blueprint.invenio_authenticated
def upload(sub_id):
    return uph.upload(request, sub_id)


@blueprint.route('/delete/<sub_id>', methods=['POST'])
@blueprint.invenio_authenticated
def delete(sub_id):
    return uph.delete(request, sub_id)


@blueprint.route('/get_file/<sub_id>', methods=['GET'])
@blueprint.invenio_authenticated
def get_file(sub_id):
    # XXX uses insecure function
    # - option A: should check for UUID of a submission and disallow foreign GETs
    # - option B: should remove a link from the upload form for good and remove the handler
    return uph.get_file(request, sub_id)


@blueprint.route('/getform/<sub_id>/<domain>', methods=['GET'])
@blueprint.invenio_authenticated
def getform(sub_id, domain):
    return dep.getform(request, sub_id, domain)


@blueprint.route('/check_status/<sub_id>/', methods=['GET', 'POST'])
@blueprint.invenio_authenticated
def check_status(sub_id):
    return uph.check_status(sub_id)


@blueprint.route('/check_status/', methods=['GET', 'POST'])
@blueprint.invenio_authenticated
def check_status_noarg():
    return uph.check_status_noarg()
