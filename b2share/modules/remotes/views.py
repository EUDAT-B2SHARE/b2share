# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2016 University of Tuebingen, CERN.
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
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""B2Share remotes (b2drop) integration REST API."""

from __future__ import absolute_import

from urllib.parse import urlparse

from flask import Blueprint, jsonify, abort, session, request, url_for, current_app
from invenio_rest import ContentNegotiatedMethodView

from invenio_files_rest.serializer import json_serializer

from .errors import UserError
from .b2drop import B2DropClient


blueprint = Blueprint(
    'remotes',
    __name__,
    url_prefix = '/remotes'
)


def dict_to_json_serializer(dictionary, code=200, headers=None):
    response = jsonify(dictionary)
    response.status_code = code
    if headers is not None:
        response.headers.extend(headers)
    return response


class RemoteList(ContentNegotiatedMethodView):
    view_name = 'remotes'

    def __init__(self, **kwargs):
        """Constructor."""
        super(RemoteList, self).__init__(
            serializers={
                'application/json': dict_to_json_serializer,
            },
            default_media_type='application/json',
            **kwargs
        )

    def put(self, service):
        if service == 'b2drop':
            auth = request.get_json()
            config = current_app.config.get('B2DROP_SERVER')
            b2drop_client = B2DropClient(username=auth.get('username'),
                                         password=auth.get('password'),
                                         **config)
            session['b2drop_client'] = b2drop_client
            return b2drop_client.list('/')
        else:
            raise UserError("Remote service unknown")


class B2DropRemote(ContentNegotiatedMethodView):
    view_name = 'b2drop'

    def __init__(self, **kwargs):
        """Constructor."""
        super(B2DropRemote, self).__init__(
            serializers={
                'application/json': dict_to_json_serializer,
            },
            default_method_media_type={
                'GET': 'application/json',
            },
            default_media_type='application/json',
            **kwargs
        )

    def get(self, path):
        b2drop_client = session.get('b2drop_client')
        if not b2drop_client:
            raise UserError("B2DROP remote not initialized")
        return b2drop_client.list(path)


class Jobs(ContentNegotiatedMethodView):
    view_name = 'remotes_jobs'

    def __init__(self, **kwargs):
        """Constructor."""
        super(Jobs, self).__init__(
            serializers={
                'application/json': json_serializer,
            },
            default_method_media_type={
                'POST': 'application/json',
            },
            default_media_type='application/json',
            **kwargs
        )

    def post(self):
        json = request.json
        source_remote_url = json.get('source_remote_url')
        destination_file_url = json.get('destination_file_url')

        if not source_remote_url:
            raise UserError("missing required source_remote_url parameter")
        if not destination_file_url:
            raise UserError("missing required destination_file_url parameter")

        b2drop_urlbase = url_for('remotes.b2drop', path='', _external=True)
        b2drop_urlbase_relative = urlparse(b2drop_urlbase).path
        if source_remote_url.startswith(b2drop_urlbase):
            b2drop_path = source_remote_url[len(b2drop_urlbase):]
        elif source_remote_url.startswith(b2drop_urlbase_relative):
            b2drop_path = source_remote_url[len(b2drop_urlbase_relative):]
        else:
            raise UserError("bad source_remote_url; currently only supporting b2drop remotes")

        fileBucket_urlbase = url_for('invenio_files_rest.location_api', _external=True)
        if not destination_file_url.startswith(fileBucket_urlbase):
            raise UserError("bad destination_file_url; must point to a file bucket object")
        destination_file_url = destination_file_url[len(fileBucket_urlbase):]
        destination_file_url = destination_file_url.strip('/')
        [bucket_id, key] = destination_file_url.split('/', maxsplit=1)
        if not key or not bucket_id:
            raise UserError("bad destination_file_url; must be a correct URL "
                            "pointing to a file in a file bucket object")

        b2drop_client = session.get('b2drop_client')
        if not b2drop_client:
            raise UserError("B2DROP remote not initialized")

        stream = b2drop_client.make_stream_object(b2drop_path)
        return put_file_into_bucket(bucket_id, key, stream, stream.length())


def put_file_into_bucket(bucket_id, key, stream, content_length):
    # TODO: refactor invenio_files_rest to have a proper API and use that one here
    from invenio_db import db
    from invenio_files_rest.models import Bucket, ObjectVersion
    from invenio_files_rest.views import need_bucket_permission
    from invenio_files_rest.errors import FileSizeError

    bucket = Bucket.get(bucket_id)
    if bucket is None:
        abort(404, 'Bucket does not exist.')

    # WARNING: this function should be isomorphic with
    #          invenio_files_rest.views:ObjectResource.create_object
    @need_bucket_permission('bucket-update')
    def create_object(bucket, key):
        size_limit = bucket.size_limit
        if size_limit and int(content_length or 0) > size_limit:
            desc = 'File size limit exceeded.' \
                if isinstance(size_limit, int) else size_limit.reason
            raise FileSizeError(description=desc)

        with db.session.begin_nested():
            obj = ObjectVersion.create(bucket, key)
            obj.set_contents(
                stream, size=content_length, size_limit=size_limit)
        db.session.commit()
        return obj

    return create_object(key=key, bucket=bucket)


blueprint.add_url_rule('/jobs',
                       view_func=Jobs.as_view(Jobs.view_name))

blueprint.add_url_rule('/<service>',
                       view_func=RemoteList.as_view(RemoteList.view_name))

blueprint.add_url_rule('/b2drop/<path:path>',
                       view_func=B2DropRemote.as_view(B2DropRemote.view_name))
