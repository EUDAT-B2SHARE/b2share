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

import uuid
import time
import os
from tempfile import mkstemp

from flask.ext.wtf import Form
from flask import render_template, redirect, url_for, current_app, jsonify
from wtforms.ext.sqlalchemy.orm import model_form
from wtforms.ext.csrf.session import SessionSecureForm

from invenio.config import CFG_SITE_SECRET_KEY
from invenio.bibtask import task_low_level_submission
from invenio.config import CFG_TMPSHAREDDIR
from invenio.wtforms_utils import InvenioBaseForm
from invenio.webuser_flask import current_user

from invenio.simplestore_model.HTML5ModelConverter import HTML5ModelConverter
import invenio.simplestore_upload_handler as uph
from invenio.simplestore_model.model import SubmissionMetadata
from invenio.simplestore_model import metadata_classes
import invenio.simplestore_marc_handler as mh


# InvenioBaseForm is taking care of the csrf
class FormWithKey(InvenioBaseForm):
    pass


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
    current_app.logger.error("Adding metadata")
    if sub_id is None:
        #just return to deposit
        return redirect(url_for('.deposit'))
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
    
    current_app.logger.error("about to validate")
    if meta_form.validate_on_submit():
        recid, marc = mh.create_marc(
            request.form, sub_id, current_user['email'])
        tmp_file = write_marc_to_temp_file(marc)
        task_low_level_submission('bibupload', 'webdeposit', '-r', tmp_file)
        return jsonify(valid=True,
                       html=render_template('simplestore-finalize.html',
                                            recid=recid, marc=marc))

    current_app.logger.error("returning form addmeta")
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
