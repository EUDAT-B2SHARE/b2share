# -*- coding: utf-8 -*-

import uuid
import time
import os
from tempfile import mkstemp

from flask.ext.wtf import Form
from flask import render_template, redirect, url_for, flash
from wtforms.ext.sqlalchemy.orm import model_form

from invenio.config import CFG_SITE_SECRET_KEY
from invenio.bibtask import task_low_level_submission
from invenio.config import CFG_TMPSHAREDDIR

from invenio.simplestore_model.HTML5ModelConverter import HTML5ModelConverter
import invenio.simplestore_upload_handler as uph
from invenio.simplestore_model.model import SubmissionMetadata
from invenio.simplestore_model import metadata_classes
import invenio.simplestore_marc_handler as mh
from invenio.webuser_flask import current_user

from invenio.config import CFG_SIMPLESTORE_UPLOAD_FOLDER
from invenio.webinterface_handler_flask_utils import _


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
        #just return to deposit
        return redirect(url_for('.deposit'))

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
        return jsonify(valid=True,
                       html=render_template('simplestore-finalise.html',
                                            recid=recid, marc=marc))

    return jsonify(valid=False,
                   html=render_template('simplestore-addmeta-table.html',
                                        sub_id=sub_id,
                                        metadata=meta,
                                        form=meta_form,
                                        getattr=getattr))

def write_marc_to_temp_file(marc):
    """
    Writes out the MARCXML to a file.
    """
    tmp_file_fd, tmp_file_name = mkstemp(
        suffix='.marcxml',
        prefix="webdeposit_%s" % time.strftime("%Y-%m-%d_%H:%M:%S"),
        dir=CFG_TMPSHAREDDIR)

    os.write(tmp_file_fd, marc.encode('utf8'))
    os.close(tmp_file_fd)
    os.chmod(tmp_file_name, 0644)

    return tmp_file_name
