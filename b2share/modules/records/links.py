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

"""Link helper and types."""

import re

from flask import url_for, g

from .providers import RecordUUIDProvider
from .fetchers import b2share_parent_pid_fetcher


RECORD_BUCKET_RELATION_TYPE = \
    'http://b2share.eudat.eu/relation_types/record_bucket'
"""Relation type used for a record's submission bucket links."""


def http_header_link_regex(relation_type):
    """Create a regex matching the http header links of the given type."""
    return re.compile(r'.*;+\s*rel="{}"\s*(;.*)?'.format(
        re.escape(relation_type)))


def url_for_bucket(bucket_id):
    """Build the url for the given bucket."""
    return url_for(
        'invenio_files_rest.bucket_api',
        bucket_id=bucket_id,
        _external=True
    )

def record_links_factory(pid, **kwargs):
    """Factory for record links generation."""
    def _url(name, pid_value):
        endpoint = 'b2share_records_rest.{0}_{1}'.format(pid.pid_type, name)
        return url_for(endpoint, pid_value=pid_value, _external=True)

    links = dict(self=_url('item', pid.pid_value))

    if hasattr(g, 'record'): # set by the serializer
        metadata = g.record
        # FIXME: index the record bucket with the bucket so that we can
        # add the "files" link
        if metadata.files is not None:
            links['files'] = url_for_bucket(metadata.files.bucket)

    if hasattr(g, 'record_hit'): # set when retrieving search results
        metadata = g.record_hit['_source']
        if 'files_bucket_id' in metadata.get('_internal', {}):
            links['files'] = url_for_bucket(
                metadata['_internal']['files_bucket_id']
            )

    parent_pid = b2share_parent_pid_fetcher(None, metadata).pid_value
    links['versions'] = _url('versions', parent_pid)

    return links
