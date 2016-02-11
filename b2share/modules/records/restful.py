# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2016 University of Tuebingen, CERN.
# Copyright (C) 2015 University of Tuebingen.
#
# B2Share is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# B2Share is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with B2Share; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.


from __future__ import absolute_import

import pytz

from flask import Blueprint, jsonify, abort, request, current_app

from invenio_rest import ContentNegotiatedMethodView
from invenio_records_rest.serializers import record_to_json_serializer
from .api import Record, RecordSearchFilter


blueprint = Blueprint('b2share_records', __name__, url_prefix='/xrecords')

def record_to_dict(record):
    json = record.json.copy()
    json.update({
        'id': record.id,
        'created': pytz.utc.localize(record.created).isoformat(),
        'updated': pytz.utc.localize(record.updated).isoformat(),
        'version_id': record.version_id,
    })
    if 'control_number' in json:
        del json['control_number']
    return json


def json_serializer(data, code=200, headers=None):
    """Build a json flask response using the given data.
    :Returns: A flask response with json data.
    :Returns Type: :py:class:`flask.Response`
    """
    if isinstance(data, Record):
        data = record_to_dict(data.record)
    response = jsonify(data)
    response.status_code = code
    if headers is not None:
        response.headers.extend(headers)
    return response


class HttpResource(ContentNegotiatedMethodView):
    def __init__(self, *args):
        super(HttpResource, self).__init__(*args)
        self.serializers = {
            'text/html': json_serializer,
            'application/json': json_serializer,
        }


def record_or_else(record_id):
    record = Record.get_by_id(record_id)
    if not record:
        abort(404)
    return record


class HttpRecordList(HttpResource):
    def get(self, **kwargs):
        """
        Retrieve list of records.
        """
        start = request.args.get('start') or 0
        stop = request.args.get('stop') or 10
        records = Record.list(start, stop)
        return {'records': [record_to_dict(r.record) for r in records]}

    def post(self):
        """
        Creates a new record object (it can be empty or with metadata), owned
        by current user. The default state of record status is 'draft'
        """

        if request.content_type != 'application/json':
            abort(415)
        data = request.get_json()
        if data is None:
            return abort(400)

        record = Record.create(data)
        return record, 201

class HttpRecord(HttpResource):
    def get(self, record_id):
        """
        Returns the requested record
        """
        record = record_or_else(record_id)
        # import ipdb; ipdb.set_trace()
        return record

    def patch(self, record_id):
        """
        Edits the Record and submit it.
        """
        record = record_or_else(record_id)
        return record.patch()

    def delete(self, record_id):
        """
        Deletes the record:
            - if the state of record is draft: it will be deleted
            - if the state is released: it will be marked as deleted.
                Only available to superadmins
        """
        return None


class HttpFileList(HttpResource):
    def get(self, record_id):
        """
        Retrieve list of files in a record.
        """
        record = record_or_else(record_id)
        return record.get_file_container()

    def post(self, record_id):
        """
        Add a new file to the record. The record state should be 'draft'
        """
        return None


class HttpFile(HttpResource):
    def get(self, record_id, file_id):
        """
        Get a file metadata
        """
        record = record_or_else(record_id)
        return record.get_file_container().get_file(file_id)

    def patch(self, record_id, file_id):
        """
        Rename the file or container
        """
        return None

    def delete(self, record_id, file_id):
        """
        Delete a file/container (only possible for draft records).
        If it is a container it deletes recursively its children.
        """
        return None


class HttpFileContent(HttpResource):
    def get(self, record_id, file_id):
        """
        Get a file's content
        """
        return None


class HttpRecordRefList(HttpResource):
    def get(self, record_id):
        """
        Returns the record's references
        """
        return None

    def post(self, record_id):
        """
        Create a new reference
        """
        return None


class HttpRecordRef(HttpResource):
    def get(self, record_id, ref_id):
        """
        Returns a Reference with the specified id
        """
        return None

    def delete(self, record_id, ref_id):
        """
        Deletes a reference
        """
        return None


blueprint.add_url_rule('/', view_func=HttpRecordList.as_view("record_list"))
blueprint.add_url_rule('/<int:record_id>', view_func=HttpRecord.as_view("record"))
blueprint.add_url_rule('/<uuid:record_id>', view_func=HttpRecord.as_view("record_uuid"))
blueprint.add_url_rule('/<int:record_id>/files', view_func=HttpFileList.as_view("file_list"))
blueprint.add_url_rule('/<int:record_id>/files/<int:file_id>', view_func=HttpFile.as_view("file"))
blueprint.add_url_rule('/<int:record_id>/references', view_func=HttpRecordRefList.as_view("record_reference_list"))
blueprint.add_url_rule('/<int:record_id>/references/<int:ref_id>', view_func=HttpRecordRef.as_view("record_reference"))
