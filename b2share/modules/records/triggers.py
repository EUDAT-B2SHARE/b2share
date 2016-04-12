# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2016 CERN.
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

"""B2share records triggers."""

from __future__ import absolute_import, print_function

import uuid

import pytz
from invenio_records.signals import before_record_insert, after_record_insert

from b2share.modules.schemas.api import CommunitySchema
from b2share.modules.schemas.serializers import \
    community_schema_json_schema_link
from invenio_files_rest.models import Bucket
from invenio_search import current_search_client

from .errors import InvalidRecordError
from .constants import (RECORDS_INTERNAL_FIELD as interal_field,
                        RECORDS_BUCKETS_FIELD as buckets_field)


def register_triggers(app):
    before_record_insert.connect(set_record_schema)
    before_record_insert.connect(create_record_files_bucket)
    after_record_insert.connect(index_record)


def set_record_schema(record, **kwargs):
    """Set the record schema when it is created."""
    if 'community' not in record or not record['community']:
        raise InvalidRecordError(
            'Record\s metadata has no community field.')
    try:
        community_id = uuid.UUID(record['community'])
    except ValueError as e:
        raise InvalidRecordError('Community ID is not a valid UUID.') from e
    schema = CommunitySchema.get_community_schema(community_id)
    record['$schema'] = community_schema_json_schema_link(schema)


def create_record_files_bucket(record, **kwargs):
    """Create the corresponding file bucket when a record is inserted."""
    bucket = Bucket.create()
    if interal_field not in record:
        record[interal_field] = {}
    internals = record[interal_field]
    internals[buckets_field] = [str(bucket.id)]


def index_record(record):
    """Index the given record."""
    metadata = record.dumps()
    metadata['_created'] = pytz.utc.localize(record.created).isoformat()
    metadata['_updated'] = pytz.utc.localize(record.updated).isoformat()
    current_search_client.index(
        index='records',
        doc_type='record',
        id=record.id,
        body=metadata,
        version=record.revision_id,
        version_type='external_gte',
    )
