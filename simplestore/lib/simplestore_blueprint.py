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


@blueprint.route('/', methods=['GET', 'POST'])
@blueprint.invenio_authenticated
def deposit():
    return dep.deposit(request)


@blueprint.route('/addmeta/<sub_id>', methods=['GET', 'POST'])
@blueprint.invenio_authenticated
def addmeta(sub_id):
    return dep.addmeta(request, sub_id)


@blueprint.route('/upload/<sub_id>', methods=['POST'])
@blueprint.invenio_authenticated
def upload(sub_id):
    return uph.upload(request, sub_id)


@blueprint.route('/delete/<sub_id>', methods=['GET', 'POST'])
@blueprint.invenio_authenticated
def delete(sub_id):
    return uph.delete(request, sub_id)


@blueprint.route('/get_file/<sub_id>', methods=['GET'])
@blueprint.invenio_authenticated
def get_file(sub_id):
    return uph.get_file(sub_id)


@blueprint.route('/check_status/<sub_id>/', methods=['GET', 'POST'])
@blueprint.invenio_authenticated
def check_status(sub_id):
    return uph.check_status(sub_id)


@blueprint.route('/check_status/', methods=['GET', 'POST'])
@blueprint.invenio_authenticated
def check_status_noarg():
    return uph.check_status_noarg()
