# -*- coding: utf-8 -*-

import uuid
import time
import os
from tempfile import mkstemp

from flask.ext.wtf import Form
from flask import render_template, url_for, current_app, jsonify
from wtforms.ext.sqlalchemy.orm import model_form

from invenio.config import CFG_SITE_SECRET_KEY
from invenio.bibtask import task_low_level_submission
from invenio.bibfield_jsonreader import JsonReader
from invenio.config import CFG_TMPSHAREDDIR
from invenio.dbquery import run_sql
from invenio.bibrecord import record_add_field, record_xml_output, create_record

from invenio.simplestore_model.HTML5ModelConverter import HTML5ModelConverter
import invenio.simplestore_upload_handler as uph
from invenio.simplestore_model.model import SubmissionMetadata
from invenio.simplestore_model import metadata_classes
from invenio.webuser_flask import current_user

from invenio.config import CFG_SIMPLESTORE_UPLOAD_FOLDER


# Needed to avoid errors in Form Generation
# There is an invenio forms class that should be investigated
class FormWithKey(Form):
    SECRET_KEY = CFG_SITE_SECRET_KEY


def deposit(request, sub_id=None, form=None, metadata=None):
    """ Renders the deposit start page """
    return render_template('simplestore-deposit.html',
                           url_prefix=url_for('.deposit'),
                           domains=metadata_classes.values(),
                           sub_id=uuid.uuid1().hex)


def getform(request, sub_id, domain):
    """
    Returns a metadata form tailored to the given domain.
    """

    domain = domain.lower()
    if domain in metadata_classes:
        meta = metadata_classes[domain]()
    else:
        meta = SubmissionMetadata()

    MetaForm = model_form(meta.__class__, base_class=FormWithKey,
                          exclude=['submission', 'submission_type'],
                          field_args=meta.field_args,
                          converter=HTML5ModelConverter())
    meta_form = MetaForm(request.form, meta)

    return render_template(
        'simplestore-addmeta-table.html',
        sub_id=sub_id,
        metadata=meta,
        form=meta_form,
        getattr=getattr)


def addmeta(request, sub_id):
    """
    Checks the submitted metadata form for validity.
    Returns a new page with success message if valid, otherwise it returns a
    form with the errors marked.
    """

    if sub_id is None:
        return render_template('500.html', message='Submission id not set'), 500

    updir = os.path.join(uph.CFG_SIMPLESTORE_UPLOAD_FOLDER, sub_id)
    if (not os.path.isdir(updir)) or (not os.listdir(updir)):
        return render_template('500.html', message="Uploads not found"), 500

    domain = request.form['domain'].lower()
    if domain in metadata_classes:
        meta = metadata_classes[domain]()
    else:
        meta = SubmissionMetadata()

    MetaForm = model_form(meta.__class__, base_class=FormWithKey,
                          exclude=['submission', 'submission_type'],
                          field_args=meta.field_args,
                          converter=HTML5ModelConverter())
    meta_form = MetaForm(request.form, meta)

    if meta_form.validate_on_submit():
        recid, marc = create_marc_and_ingest(request.form, meta.domain, sub_id)
        return jsonify(valid=True,
                       html=render_template('simplestore-finalise.html',
                                            recid=recid, marc=marc))

    return jsonify(valid=False,
                   html=render_template('simplestore-addmeta-table.html',
                                        sub_id=sub_id,
                                        metadata=meta,
                                        form=meta_form,
                                        getattr=getattr))

def create_marc_and_ingest(form, domain, sub_id):
    """
    Generates MARC data used bu Invenio from the filled out form, then
    submits it to the Invenio system.
    """

    json_reader = JsonReader()
    # just do this by hand to get something working for demo
    # this must be automated
    json_reader['title.title'] = form['title']
    current_app.logger.error("got title")
    json_reader['authors[0].full_name'] = form['creator']
    current_app.logger.error("got creator")
    json_reader['imprint.publisher_name'] = form['publisher']
    current_app.logger.error("got pub")
    json_reader['collection.primary'] = domain

    current_app.logger.error("got data")
    marc = json_reader.legacy_export_as_marc()
    rec, status, errs = create_record(marc)

    fft_status = "firerole: allow any\n"  # Only open access for minute
    upload_dir = os.path.join(CFG_SIMPLESTORE_UPLOAD_FOLDER, sub_id)
    files = os.listdir(upload_dir)
    record_add_field(rec, '856', ind1='0', subfields=[('f', current_user['email'])])
    for f in files:
        record_add_field(rec, 'FFT',
                         subfields=[('a', os.path.join(upload_dir, f)),
                         #('d', 'some description') # TODO
                         #('t', 'Type'), # TODO
                         ('r', fft_status)])

    recid = run_sql("INSERT INTO bibrec(creation_date, modification_date) values(NOW(), NOW())")
    record_add_field(rec, '001', controlfield_value=str(recid))
    marc2 = record_xml_output(rec)

    tmp_file_fd, tmp_file_name = mkstemp(suffix='.marcxml',
                                         prefix="webdeposit_%s" % time.strftime("%Y-%m-%d_%H:%M:%S"),
                                         dir=CFG_TMPSHAREDDIR)
    os.write(tmp_file_fd, marc2)
    os.close(tmp_file_fd)
    os.chmod(tmp_file_name, 0644)

    task_low_level_submission('bibupload', 'webdeposit', '-r', tmp_file_name)
    return recid, marc
