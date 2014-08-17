# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2013, 2014 CERN.
##
## Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

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


class APIValidator(Validator):

    """Adds new datatype 'raw', that accepts anything."""

    def _validate_type_any(self, field, value):
        pass


#
# Decorators
#
def error_handler(f):
    """Decorator to handle deposition exceptions."""
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
    """Extract error messages from a draft.process() result dictionary."""
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
    """Greater than 0."""
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
    'version': fields.Integer
}


# =========
# Resources
# =========
class DocumentListResource(Resource):

    """Collection of documents."""

    method_decorators = document_decorators

    def get(self):
        """List all files."""
        return Document.storage_engine.search(
            {'creator': current_user.get_id()})

    @require_header('Content-Type', 'application/json')
    def post(self):
        """Create a new document."""
        abort(405)

    @require_header('Content-Length', check_content_length)
    def put(self):
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

    def delete(self):
        abort(405)

    def head(self):
        abort(405)

    def options(self):
        abort(405)

    def patch(self):
        abort(405)


class DocumentFileResource(Resource):

    """ Represent a document file. """

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


class AllDepositionList(Resource):
    """
    Collection of depositions
    """
    method_decorators = document_decorators

    def get(self, oauth, domain_name):
        """
        List all depositions for a specific domain

        """

        from invenio.legacy.bibdocfile.api import BibRecDocs,\
            InvenioBibDocFileError
        from invenio.legacy.bibrecord import create_record,\
            record_get_field_instances, field_get_subfield_values
        from invenio.legacy.search_engine import print_record

        query1 = "SELECT id FROM bib98x WHERE value = '" + domain_name + "'"
        domain_id = run_sql(query1)
        '''
        TODO Check if Domain id is null or not;
            if it is Null the domain has no deposition record
        '''
        new_list = intbitset(domain_id)
        query2 = "SELECT id_bibrec FROM bibrec_bib98x WHERE id_bibxxx = "\
            + str(new_list[0])
        domain_records_id = run_sql(query2)

        files_list = []
        for recid in intbitset(domain_records_id):
            try:
                recdocs = BibRecDocs(recid)
            except InvenioBibDocFileError:
                return []

            latest_files = recdocs.list_latest_files()
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
                '''
                authors is a list, it should be a string
                temp = list(itertools.chain(*authors))
                file_dict['authors'] = authors
                '''
                print "authors: ", authors
                record_title = record_get_field_instances(record, '245')
                print "record_title: ", record_title

                record_description = record_get_field_instances(record, '520')
                print "record_description: ", record_description

                record_domain = record_get_field_instances(record, '980')
                print "record_domain: ", record_domain

                record_date = record_get_field_instances(record, '260')
                print "record_date ", record_date

                record_licence = record_get_field_instances(record, '540')
                print "record_licence ", record_licence

                record_PID = record_get_field_instances(record, '024a')
                print "record_PID ", record_PID

                files_list.append(file_dict)

        return marshal(files_list, output_fields)

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
        AllDepositionList,
        '/api/deposit/depositions/<string:domain_name>',
    )
