# -*- coding: utf-8 -*-

"""SimpleStore Flask Blueprint"""
from flask import request
from invenio.webinterface_handler_flask_utils import _, InvenioBlueprint
import invenio.simplestore_upload_handler as uph
import invenio.simplestore_deposit_handler as dep

blueprint = InvenioBlueprint('simplestore', __name__,
                             url_prefix='/simplestore',
                             menubuilder=[('main.simplestore',
                                          _('SimpleStore'),
                                          'simplestore.deposit', 2)],
                             breadcrumbs=[(_('SimpleStore'),
                                          'simplestore.deposit')])


@blueprint.route('/')
def deposit():
    return dep.deposit()


@blueprint.route('/addmeta', methods=['POST'])
def addmeta():
    return dep.addmeta(request)


@blueprint.route('/upload/<uid>', methods=['POST'])
def upload(uid):
    return uph.upload(request, uid)


@blueprint.route('/delete/<id>', methods=['GET', 'POST'])
def delete(id):
    return uph.delete(request, id)


@blueprint.route('/get_file/<uuid>', methods=['GET'])
def get_file(uuid):
    return uph.get_file(uuid)


@blueprint.route('/check_status/<uuid>/', methods=['GET', 'POST'])
def check_status(uuid):
    return uph.check_status(uuid)


@blueprint.route('/check_status/', methods=['GET', 'POST'])
def check_status_noarg():
    return uph.check_status_noarg()
