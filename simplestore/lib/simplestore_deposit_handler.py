# -*- coding: utf-8 -*-

import uuid
import time
import os
from tempfile import mkstemp

from flask.ext.wtf import Form
from flask import render_template, redirect, url_for, flash, current_app
from wtforms.ext.sqlalchemy.orm import model_form

from invenio.config import CFG_SITE_SECRET_KEY
from invenio.sqlalchemyutils import db
from invenio.bibtask import task_low_level_submission
from invenio.config import CFG_TMPSHAREDDIR

from invenio.simplestore_model.HTML5ModelConverter import HTML5ModelConverter
import invenio.simplestore_upload_handler as uph
from invenio.simplestore_model.model import Submission, SubmissionMetadata
from invenio.simplestore_model import metadata_classes
import invenio.simplestore_marc_handler as mh
from invenio.webuser_flask import current_user

from invenio.webinterface_handler_flask_utils import _


# Needed to avoid errors in Form Generation
# There is an invenio forms class that should be investigated
class FormWithKey(Form):
    SECRET_KEY = CFG_SITE_SECRET_KEY


def deposit(request):
    """ Renders the deposit start page """
    if request.method == 'POST':
        if not 'sub_id' in request.form:
            return render_template('500.html', message='Submission id not set'), 500

        sub_id = request.form['sub_id']

        updir = os.path.join(uph.CFG_SIMPLESTORE_UPLOAD_FOLDER, sub_id)
        if (not os.path.isdir(updir)) or (not os.listdir(updir)):
            #would probably be better to disable the button in js until
            #upload complete
            flash(_("Please upload a file to deposit"), 'error')
            return render_template('simplestore-deposit.html',
                                   domains=metadata_classes.values(),
                                   sub_id=sub_id)

        sub = Submission(uuid=sub_id)

        sub.domain = request.form['domain'].lower()

        #Following line creates Submission table if it doesn't exist
        #Should be moved to some one time set-up script for efficiency
        #Note that we only want the Submission table but all the metadata
        #tables are created. I can't figure out how to avoid this currently.
        #db.create_all()

        db.session.add(sub)
        db.session.commit()
        return redirect(url_for('.addmeta', sub_id=sub_id))
    else:
        return render_template('simplestore-deposit.html',
                               domains=metadata_classes.values(),
                               sub_id=uuid.uuid1().hex)


def addmeta(request, sub_id):
    """
    Add metadata to a submission.

    The form is dependent on the domain chosen at the deposit stage.
    """

    #current_app.logger.error("Called addmeta")

    if sub_id is None:
        return render_template('500.html', message='Submission id not set'), 500

    sub = Submission.query.filter_by(uuid=sub_id).first()

    if sub is None:
        return render_template('500.html', message="UUID not found in database"), 500

    updir = os.path.join(uph.CFG_SIMPLESTORE_UPLOAD_FOLDER, sub_id)
    if (not os.path.isdir(updir)) or (not os.listdir(updir)):
        return render_template('500.html', message="Uploads not found"), 500

    files = os.listdir(updir)

    if sub.domain in metadata_classes:
        meta = metadata_classes[sub.domain]()
    else:
        meta = SubmissionMetadata()

    MetaForm = model_form(meta.__class__, base_class=FormWithKey,
                          exclude=['submission', 'submission_type'],
                          field_args=meta.field_args,
                          converter=HTML5ModelConverter())
    meta_form = MetaForm(request.form, meta)

    if meta_form.validate_on_submit():
        recid, marc = mh.create_marc(
            request.form, sub_id, current_user['email'])
        tmp_file = write_marc_to_temp_file(marc)
        task_low_level_submission('bibupload', 'webdeposit', '-r', tmp_file)
        db.session.delete(sub)
        return render_template('simplestore-finalise.html',
                               recid=recid, marc=marc)

    return render_template(
        'simplestore-addmeta.html',
        metadata=meta,
        fileret=files,
        form=meta_form,
        sub_id=sub.uuid,
        getattr=getattr)


def write_marc_to_temp_file(marc):
    """
    Writes out the MARCXML to a file.
    """
    tmp_file_fd, tmp_file_name = mkstemp(
        suffix='.marcxml',
        prefix="webdeposit_%s" % time.strftime("%Y-%m-%d_%H:%M:%S"),
        dir=CFG_TMPSHAREDDIR)

    os.write(tmp_file_fd, marc)
    os.close(tmp_file_fd)
    os.chmod(tmp_file_name, 0644)

    return tmp_file_name
