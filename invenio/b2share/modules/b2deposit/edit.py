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
from wtforms.ext.sqlalchemy.orm import model_form
from werkzeug.datastructures import ImmutableMultiDict
from flask import render_template, url_for, jsonify, current_app, abort
from flask.ext.login import current_user

from restful import get_record_details, read_basic_metadata_field_from_marc
from b2share_deposit_handler import FormWithKey
from b2share_marc_handler import add_basic_fields
from b2share_model import metadata_classes
from b2share_model.HTML5ModelConverter import HTML5ModelConverter

def get_page(recid):
    if not is_record_editable(recid):
        abort(401)
    record = get_record_details(int(recid), current_user['email'])
    form = ImmutableMultiDict(record)
    metaclass, meta, meta_form = get_meta_form_data(form.get('domain'), form)
    return render_template('b2share-edit.html', recid=recid,
                            metadata=meta, form=meta_form,
                            domain=metaclass, getattr=getattr)

def update(recid, form):
    if not is_record_editable(recid):
        abort(401)

    from invenio.legacy.search_engine import get_record
    from invenio.legacy.bibupload.engine import bibupload
    from invenio.modules.formatter import engine as bibformat_engine

    bfo = bibformat_engine.BibFormatObject(recid)
    domain = read_basic_metadata_field_from_marc(bfo, 'domain')
    metaclass, meta, meta_form = get_meta_form_data(domain, form)
    if meta_form.validate_on_submit():
        current_app.logger.info("Updating record {}".format(recid))
        rec_changes = {}
        add_basic_fields(rec_changes, form, meta)
        updated = False

        rec = get_record(recid)
        for (k,v) in rec_changes.items():
            if rec.get(k) != v:
                current_app.logger.info(
                    "Updating key {} from {} to {}".format(k, rec.get(k),v))
                rec[k] = v
                updated = True

        if updated:
            bibupload(rec, 'replace')

        return jsonify(valid=True,
                       newurl=url_for("record.metadata", recid=recid),
                       html=render_template('record_waitforit.html', recid=recid))
    else:
        html = render_template('b2share-addmeta-table.html', recid=recid,
                                metadata=meta, form=meta_form,
                                domain=metaclass, getattr=getattr)
        return jsonify(valid=False, html=html)

def get_meta_form_data(domain, form):
    if domain not in metadata_classes():
        raise Exception("%s is not a domain" %(domain,))

    metaclass = metadata_classes()[domain]
    meta = metaclass()
    MetaForm = model_form(meta.__class__, base_class=FormWithKey,
                          exclude=['submission', 'submission_type'],
                          field_args=meta.field_args,
                          converter=HTML5ModelConverter())
    meta_form = MetaForm(form, meta, csrf_enabled=False)
    return (metaclass, meta, meta_form)


def is_record_editable(recid):
    if current_user.is_super_admin:
        return True
    if current_user.is_guest:
        return False

    # allow owner of the record, only if private access
    # --- disabled for the moment
    # from invenio.modules.formatter import engine as bibformat_engine
    # bfo = bibformat_engine.BibFormatObject(recid)
    # owner_email = read_basic_metadata_field_from_marc(bfo, 'uploaded_by')
    # is_private = (read_basic_metadata_field_from_marc(bfo, 'open_access') == "restricted")
    # if current_user['email'] == owner_email and is_private:
    #     return True

    # allow community administrators, no matter what the access level is
    # --- disabled for the moment
    # domain = read_basic_metadata_field_from_marc(bfo, 'domain')
    # domain_admin_group = domain + '_admin'
    # if domain_admin_group in current_user.get('group', []):
    #     return True

    return False
