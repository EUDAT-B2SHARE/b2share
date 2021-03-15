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

from ..search import _in_draft_request
from ..links import RECORD_BUCKET_RELATION_TYPE
from b2share.modules.deposit.links import deposit_links_factory
from b2share.modules.deposit.fetchers import b2share_deposit_uuid_fetcher


def add_link_header(response, links):
    """Add a Link HTTP header to a REST response.
    :param response: REST response instance
    :param links: Dictionary of links
    """
    if links is not None:
        response.headers.extend({
            'Link': ', '.join([
                '<{0}>; rel="{1}"'.format(l, r) for r, l in links.items()])
        })

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

def search_responsify(serializer, mimetype):
    """Create a Records-REST search result response serializer.
    :param serializer: Serializer instance.
    :param mimetype: MIME type of response.
    :returns: Function that generates a record HTTP response.
    """
    def view(pid_fetcher, search_result, code=200, headers=None, links=None,
             item_links_factory=None):
        response = current_app.response_class(
            serializer.serialize_search(pid_fetcher, search_result,
                                        links=links,
                                        item_links_factory=item_links_factory),
            mimetype=mimetype)
        response.status_code = code
        if headers is not None:
            response.headers.extend(headers)

        if links is not None:
            add_link_header(response, links)

        return response

    return view


class JSONSerializer(InvenioJSONSerializer):
    def preprocess_record(self, pid, record, links_factory=None, **kwargs):
        g.record = record
        return super(JSONSerializer, self).preprocess_record(
            pid, record, links_factory, **kwargs)

    def serialize(self, pid, record, links_factory=None, **kwargs):
        """B2ShareRecord serializer."""
        return super(JSONSerializer, self).\
            serialize(pid, record, links_factory, **kwargs)

    def transform_search_hit(self, pid, record_hit, links_factory=None, **kwargs):
        g.record_hit = record_hit
        return super(JSONSerializer, self).transform_search_hit(
            pid, record_hit, links_factory, **kwargs)

    def serialize_search(self, pid_fetcher, search_result, links=None,
                         item_links_factory=None, **kwargs):
            """Serialize a search result.
            :param pid_fetcher: Persistent identifier fetcher. It is overriden
                                if the request searches for draft records.
            """
            if _in_draft_request():
                pid_fetcher = b2share_deposit_uuid_fetcher
                item_links_factory = deposit_links_factory
            return super(JSONSerializer, self).serialize_search(
                pid_fetcher=pid_fetcher, search_result=search_result,
                links=links, item_links_factory=item_links_factory, **kwargs)
