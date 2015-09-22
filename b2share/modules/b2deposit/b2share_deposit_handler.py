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

import uuid
import time
import os
import os.path
from tempfile import mkstemp

from flask import render_template, redirect, url_for, current_app, jsonify
from wtforms.ext.sqlalchemy.orm import model_form

from invenio.utils.forms import InvenioBaseForm
from invenio_ext.login import current_user

from b2share_model.HTML5ModelConverter import HTML5ModelConverter
from b2share_model import metadata_classes
import b2share_marc_handler



# InvenioBaseForm is taking care of the csrf
class FormWithKey(InvenioBaseForm):
    pass


def deposit(request):
    """ Renders the deposit start page """
    return render_template('b2share-deposit.html',
                           url_prefix=url_for('.deposit'),
                           domains=metadata_classes().values(),
                           sub_id=uuid.uuid1().hex)


def getform(request, sub_id, domain):
    """
    Returns a metadata form tailored to the given domain.
    """

    domain = domain.lower()
    if domain in metadata_classes():
        meta = metadata_classes()[domain]()
    else:
        from b2share_model.model import SubmissionMetadata
        meta = SubmissionMetadata()

    MetaForm = model_form(meta.__class__, base_class=FormWithKey,
                          exclude=['submission', 'submission_type'],
                          field_args=meta.field_args,
                          converter=HTML5ModelConverter())
    meta_form = MetaForm(request.form, meta)

    return render_template(
        'b2share-addmeta-table.html',
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

    CFG_B2SHARE_UPLOAD_FOLDER = current_app.config.get("CFG_B2SHARE_UPLOAD_FOLDER")
    updir = os.path.join(CFG_B2SHARE_UPLOAD_FOLDER, sub_id)
    if (not os.path.isdir(updir)) or (not os.listdir(updir)):
        return render_template('500.html', message="Uploads not found"), 500

    domain = request.form['domain'].lower()
    if domain in metadata_classes():
        meta = metadata_classes()[domain]()
    else:
        from b2share_model.model import SubmissionMetadata
        meta = SubmissionMetadata()

    MetaForm = model_form(meta.__class__, base_class=FormWithKey,
                          exclude=['submission', 'submission_type'],
                          field_args=meta.field_args,
                          converter=HTML5ModelConverter())

    meta_form = MetaForm(request.form, meta)

    if meta_form.validate_on_submit():
        recid, marc = b2share_marc_handler.create_marc(
            request.form, sub_id, current_user['email'], meta)
        tmp_file = write_marc_to_temp_file(marc)
        # all usual tasks have priority 0; we want the bibuploads to run first
        from invenio.legacy.bibsched.bibtask import task_low_level_submission
        task_low_level_submission('bibupload', 'webdeposit', '--priority', '1', '-r', tmp_file)
        return jsonify(valid=True,
                       newurl=url_for("record.metadata", recid=recid),
                       html=render_template('record_waitforit.html', recid=recid, marc=marc))

    return jsonify(valid=False,
                   html=render_template('b2share-addmeta-table.html',
                                        sub_id=sub_id,
                                        metadata=meta,
                                        form=meta_form,
                                        getattr=getattr))


def write_marc_to_temp_file(marc):
    """
    Writes out the MARCXML to a file.
    """
    # CFG_TMPDIR is used by bibupload, must be there
    tmpdir = current_app.config.get("CFG_TMPDIR")
    if not os.path.exists(tmpdir):
        os.makedirs(tmpdir)
    # CFG_TMPDIR is used to write the marc file, create if necessary
    tmpsharedir = current_app.config.get("CFG_TMPSHAREDDIR")
    if not os.path.exists(tmpsharedir):
        os.makedirs(tmpsharedir)
    tmp_file_fd, tmp_file_name = mkstemp(
        suffix='.marcxml',
        prefix="webdeposit_%s" % time.strftime("%Y-%m-%d_%H:%M:%S"),
        dir=tmpsharedir)

    os.write(tmp_file_fd, marc.encode('utf8'))
    os.close(tmp_file_fd)
    os.chmod(tmp_file_name, 0644)

    return tmp_file_name
