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
    record.update(record.get('domain_metadata', {}))
    if record.get('open_access') == False or record.get('open_access') == 'restricted':
        del record['open_access']
    form = ImmutableMultiDict(record)
    metaclass, meta, meta_form = _get_meta_form_data(form.get('domain'), form)
    return render_template('b2share-edit.html', recid=recid,
                            metadata=meta, form=meta_form,
                            files=_bibdoc_file_list(recid),
                            domain=metaclass, getattr=getattr)

def update(recid, form):
    if not is_record_editable(recid):
        abort(401)

    from invenio.legacy.search_engine import get_record
    from invenio.legacy.bibupload.engine import bibupload
    from invenio.modules.formatter import engine as bibformat_engine

    bfo = bibformat_engine.BibFormatObject(recid)
    domain = read_basic_metadata_field_from_marc(bfo, 'domain')
    metaclass, meta, meta_form = _get_meta_form_data(domain, form)

    if meta_form.validate_on_submit():
        current_app.logger.info("Updating record {}".format(recid))

        _bibdoc_modify_files(recid, form)

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

def _get_meta_form_data(domain, form):
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


def get_domain_admin_group(domain):
    return '{}_domain_administrators'.format(domain)

def is_record_editable(recid):
    if current_user.is_super_admin:
        return True
    if current_user.is_guest:
        return False

    (domain, owner_email, is_private, admin_can_edit_published_record) = _get_record_info(recid)

    # if private record, allow owner of the record
    if is_private and current_user['email'] == owner_email:
        return True

    # the user's groups are not updated unless we call reload()
    current_user.reload()

    if get_domain_admin_group(domain) in current_user.get('group', []):
        # if the current user is community admin
        if is_private:
            # allow community admin to edit private records
            return True
        if admin_can_edit_published_record:
            # some domains allow community admin to edit public records
            return True

    return False

def _get_record_info(recid):
    from invenio.modules.formatter import engine as bibformat_engine
    bfo = bibformat_engine.BibFormatObject(recid)
    open_access = read_basic_metadata_field_from_marc(bfo, 'open_access')

    is_private = open_access == "restricted" or open_access == False
    domain = read_basic_metadata_field_from_marc(bfo, 'domain')
    owner_email = read_basic_metadata_field_from_marc(bfo, 'uploaded_by')
    metaclass = metadata_classes().get(domain)
    admin_can_edit_published_record = getattr(metaclass, 'admin_can_edit_published_record', False)

    return (domain, owner_email, is_private, admin_can_edit_published_record)


def _bibdoc_file_list(recid):
    import os, os.path
    from invenio.legacy.bibdocfile.api import BibRecDocs
    try:
        recdocs = BibRecDocs(recid)
    except:
        current_app.logger.error("REST API: Error while building BibRecDocs for record %d" % (recid,))
        return []
    files = []
    for d in recdocs.list_bibdocs():
        df = d.list_latest_files()
        if not df:
            continue
        filename = df[0].get_full_name().decode('utf-8')
        docname, doctype = os.path.splitext(filename)
        if doctype.startswith('.'):
            doctype = doctype[1:]
        files.append({
                'id': d.get_id(),
                'name': docname,
                'type': doctype,
                'size': df[0].get_size(),
            })
    return files

def _bibdoc_modify_files(recid, form):
    from invenio.legacy.bibdocfile.api import BibRecDocs
    try:
        recdocs = BibRecDocs(recid)
    except:
        current_app.logger.error("REST API: Error while building BibRecDocs for record %d" % (recid,))
        return []

    actions = {}

    for (k,v) in form.items():
        if k.startswith('__file__name__'):
            docid = int(k[len('__file__name__'):])
            docname = recdocs.get_docname(docid)
            if docname != v:
                actions[docid] = ('rename', docname, v)
        if k.startswith('__file__delete__') and v == 'Delete':
            docid = int(k[len('__file__delete__'):])
            docname = recdocs.get_docname(docid)
            actions[docid] = ('delete', docname, None) # overwrite rename

    for (_,(act, docname, newname)) in actions.items():
        if act == 'delete':
            current_app.logger.info("deleting bibdoc/file: {}/'{}'".format(recid, docname))
            recdocs.delete_bibdoc(docname)
        elif act == 'rename':
            current_app.logger.info("renaming bibdoc/file: {}/'{}' -> '{}'".format(recid, docname, newname))
            recdocs.change_name(newname=newname, oldname=docname)
