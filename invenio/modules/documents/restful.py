# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2013, 2014 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

from __future__ import absolute_import

import os

from cerberus import Validator
from fs.opener import opener
from flask import request, current_app
from flask.ext.login import current_user
from flask.ext.restful import Resource, abort,\
    reqparse, fields, marshal
from functools import wraps
from werkzeug.utils import secure_filename
from werkzeug.http import parse_options_header

from invenio.ext.restful import require_api_auth, error_codes, require_header

from . import errors
from .api import Document

from intbitset import intbitset
from invenio.legacy.dbquery import run_sql
import itertools

MAX_PAGE_SIZE = 20


class APIValidator(Validator):
    """
    Adds new datatype 'raw', that accepts anything.
    """
    def _validate_type_any(self, field, value):
        pass


#
# Decorators
#
def error_handler(f):
    """
    Decorator to handle deposition exceptions
    """
    @wraps(f)
    def inner(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except errors.DocumentNotFound:
            abort(404, message="Document does not exists.", status=404)
        # except Exception as e:
        #    current_app.logger.error(e)
        #    if len(e.args) >= 1:
        #        abort(400, message=e.args[0], status=400)
        #    else:
        #        abort(500, message="Internal server error", status=500)
    return inner


def filter_errors(result):
    """
    Extract error messages from a draft.process() result dictionary.
    """
    error_messages = []
    for field, msgs in result.get('messages', {}).items():
        if msgs.get('state', None) == 'error':
            for m in msgs['messages']:
                error_messages.append(dict(
                    field=field,
                    message=m,
                    code=error_codes['validation_error'],
                ))
    return error_messages


def check_content_length(value):
    """greater than 0"""
    return int(value) > 0


def directory_name(document):
    return os.path.join(current_app.instance_path, 'files',
                        document['uuid'].replace('-', '/'))

# =========
# Mix-ins
# =========
document_decorators = [
    require_api_auth(),
    error_handler,
]

deposit_decorators = [
    require_api_auth(),
    error_handler,
]

output_fields = {
    'recordID': fields.Integer,
    'comment': fields.String,
    'description': fields.String,
    'eformat': fields.String,
    'full_name': fields.String,
    'magic': fields.String,
    'name': fields.String,
    'size': fields.Integer,
    'status': fields.String,
    'subformat': fields.String,
    'superformat': fields.String,
    'type': fields.String,
    'url': fields.String,
    'version': fields.Integer,
    'authors': fields.String,
    'title': fields.String,
    'description': fields.String,
    'domain': fields.String,
    'date': fields.String,
    'pid': fields.String,
    'email': fields.String,
    'file_url': fields.String,
}

# =========
# Helpers
# =========


def flatten(lst):
    if type(lst) not in (tuple, list):
        return (lst,)
    if len(lst) == 0:
        return tuple(lst)
    return flatten(lst[0]) + flatten(lst[1:])


def get_value(res):
    temp = list(flatten(res))
    if len(temp) == 6:
        return temp[1]
    elif len(temp) == 8:
        return temp[3]
    return None


def get_record_details(recid):
    from invenio.legacy.bibdocfile.api import BibRecDocs,\
        InvenioBibDocFileError
    from invenio.legacy.bibrecord import create_record,\
        record_get_field_instances
    from invenio.legacy.search_engine import print_record

    try:
        recdocs = BibRecDocs(recid)
    except InvenioBibDocFileError:
        return []

    latest_files = recdocs.list_latest_files()
    if len(latest_files) == 0:
        return []
    else:
        for afile in latest_files:
            file_dict = {}
            file_dict['recordID'] = recid
            file_dict['comment'] = afile.get_comment()
            file_dict['description'] = afile.get_description()
            file_dict['eformat'] = afile.get_format()
            file_dict['full_name'] = afile.get_full_name()
            file_dict['magic'] = afile.get_magic()
            file_dict['name'] = afile.get_name()
            file_dict['size'] = afile.get_size()
            file_dict['status'] = afile.get_status()
            file_dict['subformat'] = afile.get_subformat()
            file_dict['superformat'] = afile.get_superformat()
            file_dict['type'] = afile.get_type()
            file_dict['url'] = afile.get_url()
            file_dict['version'] = afile.get_version()

            marcxml = print_record(recid, 'xm')
            record = create_record(marcxml)[0]

            authors = record_get_field_instances(record, '100')
            file_dict['authors'] = get_value(authors)

            record_title = record_get_field_instances(record, '245')
            file_dict['title'] = get_value(record_title)

            record_description = record_get_field_instances(record, '520')
            file_dict['description'] = get_value(record_description)

            record_domain = record_get_field_instances(record, '980')
            file_dict['domain'] = get_value(record_domain)

            record_date = record_get_field_instances(record, '260')
            file_dict['date'] = get_value(record_date)

            record_licence = record_get_field_instances(record, '540')
            file_dict['licence'] = get_value(record_licence)

            record_PID = record_get_field_instances(record, '024')
            file_dict['pid'] = get_value(record_PID)

            user_email = record_get_field_instances(record, '856', '0')
            file_dict['email'] = get_value(user_email)

            file_url = record_get_field_instances(record, '856', '4')
            file_dict['file_url'] = get_value(file_url)

        return file_dict


# =========
# Resources
# =========
class DocumentListResource(Resource):
    """
    Collection of documents
    """
    method_decorators = document_decorators

    def get(self, oauth):
        """
        List all files.
        """
        return Document.storage_engine.search(
            {'creator': current_user.get_id()})

    @require_header('Content-Type', 'application/json')
    def post(self, oauth):
        """
        Create a new document
        """
        abort(405)

    @require_header('Content-Length', check_content_length)
    def put(self, oauth):
        filename = parse_options_header(
            request.headers.get('Content-Disposition', ''))[1].get('filename')

        d = Document.create({'deleted': False})
        opener.opendir(directory_name(d), create_dir=True)
        d.setcontents(
            request.stream,
            name=lambda s: os.path.join(directory_name(s),
                                        secure_filename(filename))
        )
        return d.dumps()

    def delete(self, oauth):
        abort(405)

    def head(self, oauth):
        abort(405)

    def options(self, oauth):
        abort(405)

    def patch(self, oauth):
        abort(405)


class DocumentFileResource(Resource):
    """
    Represent a document file
    """
    method_decorators = document_decorators

    def get(self, document_uuid):
        """ Stream a document file. """
        d = Document.get_document(document_uuid)
        return d.dumps()

    def delete(self, document_uuid):
        """ Delete existing deposition file. """
        d = Document.get_document(document_uuid)
        d.delete()
        return d.dumps()

    def put(self, document_uuid):
        """ Overwrite document file content. """
        d = Document.get_document(document_uuid)
        d.setcontents(request.stream, name=request.args.get('name'))
        return d.dumps()

    def post(self):
        abort(405)

    def head(self, document_uuid):
        """ Return document metadata. """
        abort(405)

    def options(self, document_uuid):
        abort(405)

    def patch(self, document_uuid):
        """ Create new document version. """
        abort(405)


class DepositionDomains(Resource):
    """
    Collection of depositions: specific Domain
    """
    method_decorators = deposit_decorators

    def get(self, oauth, domain_name, **kwargs):
        """
        List all deposits for a specific domain

        """

        if len(kwargs) == 0:
            page_size = 5
            page_offset = 0
        elif len(kwargs) == 1:
            if kwargs['page_size'] > MAX_PAGE_SIZE:
                page_size = MAX_PAGE_SIZE
            else:
                page_size = kwargs['page_size']
            page_offset = 0
        elif len(kwargs) == 2:
            if kwargs['page_size'] > MAX_PAGE_SIZE:
                page_size = MAX_PAGE_SIZE
            else:
                page_size = kwargs['page_size']
            page_offset = kwargs['page_offset']

        # get domain id from domain name
        domain_id_sql = "SELECT id FROM bib98x WHERE value = %s"
        domain_ids = run_sql(domain_id_sql, [domain_name])
        if len(domain_ids) != 1:
            abort(404, message="Please try a valid domain name", status=404)
            # return []
        new_list = intbitset(domain_ids)
        if len(new_list) != 1:
            abort(404, message="Please try a valid domain name", status=404)
            # return []

        bibrec_id_sql = "SELECT id_bibrec FROM bibrec_bib98x WHERE id_bibxxx =\
            %s limit " + str(page_offset) + "," + str(page_size)

        domain_records_ids = run_sql(bibrec_id_sql, [str(new_list[0])])
        record_list = []
        for recid in intbitset(domain_records_ids):
            record_details = get_record_details(recid)
            record_list.append(record_details)

        return marshal(record_list, output_fields)

    @require_header('Content-Type', 'application/json')
    def post(self, oauth):
        """
        Create a new deposition
        """
        abort(405)

    def put(self, oauth):
        abort(405)

    def delete(self, oauth):
        abort(405)

    def head(self, oauth):
        abort(405)

    def options(self, oauth):
        abort(405)

    def patch(self, oauth):
        abort(405)


class DepositionListRecord(Resource):
    """
    Collection of depositions: specific user
    """
    method_decorators = deposit_decorators

    def get(self, oauth, **kwargs):
        """
        List depositions

        """
        from invenio.legacy.search_engine import perform_request_search
        from invenio.modules.accounts.models import User

        if len(kwargs) == 0:
            page_size = 5
            page_offset = 0
        elif len(kwargs) == 1:
            if kwargs['page_size'] > MAX_PAGE_SIZE:
                page_size = MAX_PAGE_SIZE
            else:
                page_size = kwargs['page_size']
            page_offset = 0
        elif len(kwargs) == 2:
            if kwargs['page_size'] > MAX_PAGE_SIZE:
                page_size = MAX_PAGE_SIZE
            else:
                page_size = kwargs['page_size']
            page_offset = kwargs['page_offset']

        user = User.query.get(current_user.get_id())
        email_field = "8560_"
        email = user.email
        record_ids = perform_request_search(f=email_field, p=email, of="id")
        record_list = []

        for record_id in record_ids[page_offset * page_size:page_offset * page_size + page_size]:
            record_details = get_record_details(record_id)
            record_list.append(record_details)
        return marshal(record_list, output_fields)

#    @require_header('Content-Type', 'application/json')
#    @require_oauth_scopes('deposit:write')
    def post(self, oauth):
        """
        Create a new deposition
        """
        pass

    def put(self, oauth):
        abort(405)

    def delete(self, oauth):
        abort(405)

    def head(self, oauth):
        abort(405)

    def options(self, oauth):
        abort(405)

    def patch(self, oauth):
        abort(405)


class DepositionRecord(Resource):
    """
    Deposition item
    """
    method_decorators = deposit_decorators

    def get(self, oauth, record_id):
        """
        Retrieve requested record

        """
        record_details = get_record_details(record_id)
        if not record_details:
            abort(404, message="Deposition not found", status=404)
        return marshal(record_details, output_fields)

#    @require_header('Content-Type', 'application/json')
#    @require_oauth_scopes('deposit:write')
    def post(self, oauth):
        """
        Create a new deposition
        """
        pass

    def put(self, oauth):
        abort(405)

    def delete(self, oauth):
        abort(405)

    def head(self, oauth):
        abort(405)

    def options(self, oauth):
        abort(405)

    def patch(self, oauth):
        abort(405)


#
# Register API resources
#


def setup_app(app, api):
    api.add_resource(
        DocumentListResource,
        '/api/document/',
    )
    api.add_resource(
        DocumentFileResource,
        '/api/document/<string:document_uuid>',
    )
    api.add_resource(
        DepositionDomains,
        '/api/depositions/<string:domain_name>',
        '/api/depositions/<string:domain_name>/<int:page_size>',
        '/api/depositions/<string:domain_name>/<int:page_size>/<int:page_offset>',
    )
    api.add_resource(
        DepositionListRecord,
        '/api/depositions/',
        '/api/depositions/<int:page_size>/',
        '/api/depositions/<int:page_size>/<int:page_offset>',
    )
    api.add_resource(
        DepositionRecord,
        '/api/deposit/<int:record_id>',
    )
