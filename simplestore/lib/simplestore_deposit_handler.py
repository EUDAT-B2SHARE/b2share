# -*- coding: utf-8 -*-

import uuid
import time
import os
from tempfile import mkstemp

from flask.ext.wtf import Form
from flask import render_template, redirect, url_for, flash
from wtforms.ext.sqlalchemy.orm import model_form

from invenio.config import CFG_SITE_SECRET_KEY
from invenio.sqlalchemyutils import db
from invenio.bibtask import task_low_level_submission
from invenio.bibfield_jsonreader import JsonReader
from invenio.config import CFG_TMPSHAREDDIR
from invenio.dbquery import run_sql
from invenio.bibrecord import record_add_field, record_xml_output, create_record

from invenio.simplestore_model.HTML5ModelConverter import HTML5ModelConverter
import invenio.simplestore_upload_handler as uph
from invenio.simplestore_model.model import (Submission, SubmissionMetadata,
                                             LinguisticsMetadata)
from invenio.webinterface_handler_flask_utils import _
from invenio.config import CFG_SIMPLESTORE_UPLOAD_FOLDER


# Needed to avoid errors in Form Generation
# There is an invenio forms class that should be investigated
class FormWithKey(Form):
    SECRET_KEY = CFG_SITE_SECRET_KEY


def deposit(request):
    """ Renders the deposit start page """
    if request.method == 'POST':
        if not 'sub_id' in request.form:
            return "ERROR: submission id not set", 500

        sub_id = request.form['sub_id']

        updir = os.path.join(uph.CFG_SIMPLESTORE_UPLOAD_FOLDER, sub_id)
        if (not os.path.isdir(updir)) or (not os.listdir(updir)):
            #would probably be better to disable the button in js until
            #upload complete
            flash(_("Please upload a file to deposit"), 'error')
            return render_template('simplestore-deposit.html', sub_id=sub_id)

        sub = Submission(uuid=sub_id)

        if request.form['domain'] == 'linguistics':
            meta = LinguisticsMetadata()
        else:
            meta = SubmissionMetadata()

        sub.md = meta
        db.session.add(sub)
        db.session.commit()
        return redirect(url_for('.addmeta', sub_id=sub_id))
    else:
        return render_template('simplestore-deposit.html',
                               sub_id=uuid.uuid1().hex)


def addmeta(request, sub_id):
    """
    Add metadata to a submission.

    The form is dependent on the domain chosen at the deposit stage.
    """

    #Uncomment the following line if there are errors regarding db tables
    #not being present. Hacky solution for minute.
    #db.create_all()

    #current_app.logger.error("Called addmeta")

    if sub_id is None:
        return "ERROR: submission id not set", 500

    sub = Submission.query.filter_by(uuid=sub_id).first()

    if sub is None:
        return "ERROR: failed to find uuid in DB", 500

    updir = os.path.join(uph.CFG_SIMPLESTORE_UPLOAD_FOLDER, sub_id)
    if (not os.path.isdir(updir)) or (not os.listdir(updir)):
        return "ERROR: Uploads not found", 500

    files = os.listdir(updir)

    MetaForm = model_form(sub.md.__class__, base_class=FormWithKey,
                          exclude=['submission', 'submission_type'],
                          converter=HTML5ModelConverter())
    meta_form = MetaForm(request.form, sub.md)

    if meta_form.validate_on_submit():
        recid, marc = create_marc_and_ingest(request.form, sub_id)
        return render_template('simplestore-finalise.html',
                               recid=recid, marc=marc)
    #else:
    #   print meta_form.errors

    return render_template(
        'simplestore-addmeta.html',
        domain=sub.md.domain,
        fileret=files,
        form=meta_form,
        sub_id=sub.uuid,
        basic_field_iter=sub.md.basicFieldIter,
        opt_field_iter=sub.md.optionalFieldIter,
        getattr=getattr)


def create_marc_and_ingest(form, sub_id):
    """
    Generates MARC data used bu Invenio from the filled out form, then
    submits it to the Invenio system.
    """

    json_reader = JsonReader()
    # just do this by hand to get something working for demo
    # this must be automated
    json_reader['title.title'] = form['title']
    json_reader['authors[0].full_name'] = form['creator']
    json_reader['imprint.publisher_name'] = form['publisher']
    json_reader['collection.primary'] = form['domain']

    marc = json_reader.legacy_export_as_marc()
    rec, status, errs = create_record(marc)

    fft_status = "firerole: allow any\n"  # Only open access for minute
    upload_dir = os.path.join(CFG_SIMPLESTORE_UPLOAD_FOLDER, sub_id)
    files = os.listdir(upload_dir)
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
