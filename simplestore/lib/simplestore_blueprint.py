# -*- coding: utf-8 -*-
# #
# # This file is part of Invenio.
# # Copyright (C) 2012, 2013 CERN.
# #
# # Invenio is free software; you can redistribute it and/or
# # modify it under the terms of the GNU General Public License as
# # published by the Free Software Foundation; either version 2 of the
# # License, or (at your option) any later version.
# #
# # Invenio is distributed in the hope that it will be useful, but
# # WITHOUT ANY WARRANTY; without even the implied warranty of
# # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# # General Public License for more details.
# #
# # You should have received a copy of the GNU General Public License
# # along with Invenio; if not, write to the Free Software Foundation, Inc.,
# # 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""SimpleStore Flask Blueprint"""
import os
import uuid
import time
from tempfile import mkstemp
from flask import render_template, request, current_app
from flask.ext.wtf import Form
from wtforms.ext.sqlalchemy.orm import model_form
from invenio.webinterface_handler_flask_utils import _, InvenioBlueprint
from invenio.config import CFG_SITE_SECRET_KEY
from invenio.sqlalchemyutils import db
from invenio.simplestore_model.model import (Submission, SubmissionMetadata,
                                             LinguisticsMetadata)
from invenio.bibtask import task_low_level_submission
from invenio.bibfield_jsonreader import JsonReader
from invenio.config import CFG_TMPSHAREDDIR
from invenio.simplestore_model.HTML5ModelConverter import HTML5ModelConverter
import invenio.simplestore_file_uploads as uploads

blueprint = InvenioBlueprint('simplestore', __name__,
                             url_prefix='/simplestore',
                             menubuilder=[('main.simplestore',
                                          _('SimpleStore'),
                                          'simplestore.deposit', 2)],
                             breadcrumbs=[(_('SimpleStore'),
                                          'simplestore.deposit')])


@blueprint.route('/')
def deposit():
    """ Renders the deposit """
    # this will wipe form on reload, does it matter?
    # (if you want to fix this, I would suggest cookies rather than workflow)
    return render_template('simplestore-deposit.html', uuid=uuid.uuid1().hex)


# Needed to avoid errors in Form Generation
# There is an invenio forms class that should be investigated
class FormWithKey(Form):
    SECRET_KEY = CFG_SITE_SECRET_KEY


@blueprint.route('/upload/<uid>', methods=['POST'])
def upload(uid):
    return uploads.upload(request, uid)


@blueprint.route('/delete/<id>', methods=['GET', 'POST'])
def delete(id):
    return uploads.delete(request, id)


@blueprint.route('/get_file/<uuid>', methods=['GET'])
def get_file(uuid):
    return uploads.get_file(uuid)


@blueprint.route('/check_status/<uuid>/', methods=['GET', 'POST'])
def check_status(uuid):
    return uploads.check_status(uuid)


@blueprint.route('/check_status/', methods=['GET', 'POST'])
def check_status_noarg():
    return uploads.check_status_noarg()


@blueprint.route('/addmeta', methods=['POST'])
def addmeta():
    #Uncomment the following line if there are errors regarding db tables
    #not being present. Hacky solution for minute.

    #db.create_all()

    sub = ""
    if 'uuid' in request.form:
        sub = Submission.query.filter_by(uuid=request.form['uuid']).first()
        if sub is None:
            current_app.logger.error("Didn't find uuid")
            sub = Submission(uuid=request.form['uuid'])

            if request.form['domain'] == 'linguistics':
                meta = LinguisticsMetadata()
            else:
                meta = SubmissionMetadata()

            sub.md = meta
            db.session.add(sub)
            db.session.commit()
    else:
        return "ERROR: uuid not set", 500

    MetaForm = model_form(sub.md.__class__, base_class=FormWithKey,
                          exclude=['submission', 'submission_type'],
                          converter=HTML5ModelConverter())
    meta_form = MetaForm(request.form, sub.md)

    if meta_form.validate_on_submit():
        create_marc_and_ingest(request.form)
        return render_template('simplestore-finalise.html', tag=sub.uuid)
    #else:
    #   print meta_form.errors

    files = os.listdir(os.path.join(uploads.CFG_SIMPLESTORE_UPLOAD_FOLDER, request.form['uuid']))

    return render_template(
        'simplestore-addmeta.html',
        domain=request.form['domain'],
        fileret=files,
        form=meta_form,
        uuid=sub.uuid,
        basic_field_iter=sub.md.basicFieldIter,
        opt_field_iter=sub.md.optionalFieldIter,
        getattr=getattr)


def create_marc_and_ingest(form):
    json_reader = JsonReader()
    # just do this by hand to get something working for demo
    # this must be automated
    json_reader['title.title'] = form['title']
    json_reader['authors[0].full_name'] = form['creator']
    json_reader['imprint.publisher_name'] = form['publisher']
    json_reader['collection.primary'] = "Article"
    marc = json_reader.legacy_export_as_marc()
    tmp_file_fd, tmp_file_name = mkstemp(suffix='.marcxml',
                                         prefix="webdeposit_%s" % time.strftime("%Y-%m-%d_%H:%M:%S"),
                                         dir=CFG_TMPSHAREDDIR)
    os.write(tmp_file_fd, marc)
    os.close(tmp_file_fd)
    os.chmod(tmp_file_name, 0644)
    task_low_level_submission('bibupload', 'webdeposit', '-i', tmp_file_name)


@blueprint.route('/finalise', methods=['POST'])
def finalise():
    return render_template('simplestore-finalise.html', tag=uuid.uuid4())
