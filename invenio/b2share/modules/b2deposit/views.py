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
from flask import request, Blueprint, jsonify
from flask.ext.login import login_required, current_user
from flask.ext.breadcrumbs import default_breadcrumb_root, register_breadcrumb
from invenio.base.i18n import _
import invenio.b2share.modules.b2deposit.edit as edt
import invenio.b2share.modules.b2deposit.b2share_upload_handler as uph
import invenio.b2share.modules.b2deposit.b2share_deposit_handler as dep

blueprint = Blueprint('b2deposit', __name__, url_prefix="/b2deposit",
                      template_folder='templates', static_folder='static')

default_breadcrumb_root(blueprint, 'breadcrumbs.b2deposit')

@blueprint.route('/', methods=['GET'])
@register_breadcrumb(blueprint, '.', _('Deposit'))
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


@blueprint.route('/<recid>/edit', methods=['GET'])
@login_required
def edit(recid):
    return edt.get_page(int(recid))

@blueprint.route('/<recid>/update', methods=['POST'])
@login_required
def updatemeta(recid):
    return edt.update(int(recid), request.form)

@blueprint.route('/b2drop', methods=['POST'])
@login_required
def b2drop():
    import easywebdav
    webdav = easywebdav.connect('b2drop.fz-juelich.de', protocol='https', path='/remote.php/webdav/', \
        username=request.form['username'], password=request.form['password'])
    # import ipdb; ipdb.set_trace()
    current_user.b2drop = webdav
    files = [cleanFile(f) for f in webdav.ls()]
    res = {"files": files}
    return jsonify(res)

def cleanFile(f):
    import string
    name_parts = string.split(f.name, "/")
    name = name_parts[-1]
    if name == "": name = name_parts[-2]
    return {"path":f.name, "name":name, "size":humansize(f.size), "mtime":f.mtime, "isdir":f.name.endswith("/")}


def humansize(v):
    if v < 1024:
        return "%5d B" % v
    elif v < 1024*1024:
        return "%5d KB" % (v/1024.0)
    elif v < 1024*1024*1024:
        return "%5d MB" % (v/(1024*1024))
    elif v < 1024*1024*1024*1024:
        return "%5d GB" % (v/(1024*1024*1024))
    elif v < 1024*1024*1024*1024:
        return "%5d TB" % (v/(1024*1024*1024*1024))




























