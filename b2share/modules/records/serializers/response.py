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

"""Serialization response factories.

Responsible for creating a HTTP response given the output of a serializer.
"""

from __future__ import absolute_import, print_function

from flask import current_app, url_for, g
from invenio_records_rest.serializers.json import JSONSerializer as \
    InvenioJSONSerializer

from ..links import RECORD_BUCKET_RELATION_TYPE


def record_responsify(serializer, mimetype):
    """Create a Records-REST response serializer.

    :param serializer: Serializer instance.
    :param mimetype: MIME type of response.
    """
    bucket_link_tpl = '{0}; rel="' + RECORD_BUCKET_RELATION_TYPE + '"'

    def view(pid, record, code=200, headers=None, links_factory=None):
        response = current_app.response_class(
            serializer.serialize(pid, record, links_factory=links_factory),
            mimetype=mimetype)
        response.status_code = code
        response.set_etag(str(record.revision_id))
        if headers is not None:
            response.headers.extend(headers)
        # add bucket link in header
        if record.files is not None:
            bucket = record.files.bucket
            link = bucket_link_tpl.format(
                url_for('invenio_files_rest.bucket_api', bucket_id=bucket.id,
                        _external=True))
            response.headers.add('Link', link)
        return response
    return view


class JSONSerializer(InvenioJSONSerializer):
    def preprocess_record(self, pid, record, links_factory=None):
        g.record = record
        try:
            return super(JSONSerializer, self).preprocess_record(
                pid, record, links_factory)
        finally:
            g.pop('record')

    def transform_search_hit(self, pid, record_hit, links_factory=None):
        g.record_hit = record_hit
        try:
            return super(JSONSerializer, self).transform_search_hit(
                pid, record_hit, links_factory)
        finally:
            g.pop('record_hit')
