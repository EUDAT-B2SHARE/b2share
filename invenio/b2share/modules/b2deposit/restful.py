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

# from flask import request, current_app
from flask.ext.login import current_user
from flask.ext.restful import Resource, abort,\
    fields, marshal
# from flask.ext.restful import reqparse,
# from functools import wraps

from invenio.ext.restful import require_api_auth, require_header
# from invenio.ext.restful import error_codes

# from intbitset import intbitset
# from invenio.legacy.dbquery import run_sql
# from invenio.ext.sqlalchemy import db
from invenio.modules.editor.models import Bib98x, BibrecBib98x

MAX_PAGE_SIZE = 20


# =========
# Mix-ins
# =========
deposit_decorators = [
    require_api_auth(),
]

files_fields = {
    'full_name': fields.String,
    'size': fields.Integer,
    'url': fields.String,
    # 'name': fields.String,
    # 'comment': fields.String,
    # 'description': fields.String,
    # 'eformat': fields.String,
    # 'magic': fields.String,
    # 'status': fields.String,
    # 'subformat': fields.String,
    # 'superformat': fields.String,
    # 'type': fields.String,
    # 'version': fields.Integer,
}

output_fields = {
    'recordID': fields.Integer,
    'authors': fields.String,
    'title': fields.String,
    'description': fields.String,
    'domain': fields.String,
    'date': fields.String,
    'pid': fields.String,
    'email': fields.String,
    'file_url': fields.String,
    'licence': fields.String,
    'files': fields.Nested(files_fields),
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


def get_value(res, tag):
    temp = list(flatten(res))

    if len(temp) == 6 and tag == "":
        return temp[1]
    elif len(temp) == 8 and tag == "":
        return temp[3]
    elif tag == "file_url":
        return filter(lambda element: "http" in str(element), temp)
    elif tag == "authors":
        return [temp[i] for i in range(1, len(temp), 6)]
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
        file_dict = {}
        content = []
        atts = {}
        for afile in latest_files:
            atts['full_name'] = afile.get_full_name()
            atts['size'] = afile.get_size()
            atts['url'] = afile.get_url()
            content.append(atts.copy())
            # atts['comment'] = afile.get_comment()
            # atts['description'] = afile.get_description()
            # atts['eformat'] = afile.get_format()
            # atts['magic'] = afile.get_magic()
            # atts['name'] = afile.get_name()
            # atts['status'] = afile.get_status()
            # atts['subformat'] = afile.get_subformat()
            # atts['superformat'] = afile.get_superformat()
            # atts['type'] = afile.get_type()
            # atts['version'] = afile.get_version()

        file_dict['files'] = content
        file_dict['recordID'] = recid

        marcxml = print_record(recid, 'xm')
        record = create_record(marcxml)[0]

        authors = record_get_field_instances(record, '100')
        file_dict['authors'] = get_value(authors, "authors")

        record_title = record_get_field_instances(record, '245')
        file_dict['title'] = get_value(record_title, "")

        record_description = record_get_field_instances(record, '520')
        file_dict['description'] = get_value(record_description, "")

        record_domain = record_get_field_instances(record, '980')
        file_dict['domain'] = get_value(record_domain, "")

        record_date = record_get_field_instances(record, '260')
        file_dict['date'] = get_value(record_date, "")

        record_licence = record_get_field_instances(record, '540')
        file_dict['licence'] = get_value(record_licence, "")

        record_PID = record_get_field_instances(record, '024')
        file_dict['pid'] = get_value(record_PID, "")

        user_email = record_get_field_instances(record, '856', '0')
        file_dict['email'] = get_value(user_email, "")

        file_url = record_get_field_instances(record, '856', '4')
        file_dict['file_url'] = get_value(file_url, "file_url")

        return file_dict


# =========
# Resources
# =========
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
        domain = Bib98x.query.filter_by(value=domain_name).first()
        if domain is None:
            abort(404, message="Please try a valid domain name:\
                 Generic, EUON, DRIHM, Linguistics, BBMRI", status=404)

        domain_records = BibrecBib98x.query.filter_by(id_bibxxx=domain.id).all()
        record_ids = []
        record_ids = [record.id_bibrec for record in domain_records]

        record_list = []
        for record_id in record_ids[page_offset * page_size:page_offset * page_size + page_size]:
            record_details = get_record_details(record_id)
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
        # from invenio.modules.accounts.models import User

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

        email_field = "8560_"
        email = current_user['email']
        record_ids = perform_request_search(f=email_field, p=email, of="id")
        record_list = []

        for record_id in record_ids[page_offset * page_size:page_offset * page_size + page_size]:
            record_details = get_record_details(record_id)
            record_list.append(record_details)
        return marshal(record_list, output_fields)

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
