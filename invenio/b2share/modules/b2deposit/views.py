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

"""B2SHARE Flask Blueprint"""
from flask import request, Blueprint
from flask.ext.login import login_required
from invenio.base.i18n import _
import invenio.b2share.modules.b2deposit.b2share_upload_handler as uph
import invenio.b2share.modules.b2deposit.b2share_deposit_handler as dep

blueprint = Blueprint('b2deposit', __name__, url_prefix="/b2deposit",
                      template_folder='templates', static_folder='static')

@blueprint.route('/', methods=['GET'])
@login_required
def deposit():
    return dep.deposit(request)


@blueprint.route('/addmeta/<sub_id>', methods=['POST'])
@login_required
def addmeta(sub_id):
    return dep.addmeta(request, sub_id)


@blueprint.route('/upload/<sub_id>', methods=['POST'])
@login_required
def upload(sub_id):
    return uph.upload(request, sub_id)


@blueprint.route('/delete/<sub_id>', methods=['POST'])
@login_required
def delete(sub_id):
    return uph.delete(request, sub_id)


@blueprint.route('/get_file/<sub_id>', methods=['GET'])
@login_required
def get_file(sub_id):
    # XXX uses insecure function
    # - option A: should check for UUID of a submission and disallow foreign GETs
    # - option B: should remove a link from the upload form for good and remove the handler
    return uph.get_file(request, sub_id)


@blueprint.route('/getform/<sub_id>/<domain>', methods=['GET'])
@login_required
def getform(sub_id, domain):
    return dep.getform(request, sub_id, domain)


@blueprint.route('/check_status/<sub_id>/', methods=['GET', 'POST'])
@login_required
def check_status(sub_id):
    return uph.check_status(sub_id)


@blueprint.route('/check_status/', methods=['GET', 'POST'])
@login_required
def check_status_noarg():
    return uph.check_status_noarg()
