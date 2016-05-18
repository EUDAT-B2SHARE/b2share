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

from flask import abort
from flask_login import current_user

from invenio_records.signals import (
        before_record_insert, after_record_insert,
        before_record_update, after_record_update)

from b2share.modules.schemas.api import CommunitySchema
from b2share.modules.schemas.serializers import \
    community_schema_json_schema_link
from invenio_files_rest.models import Bucket
from invenio_search import current_search_client
from invenio_rest.errors import FieldError

from .errors import InvalidRecordError, AlteredRecordError
from .constants import (RECORDS_INTERNAL_FIELD as internal_field,
                        RECORDS_BUCKETS_FIELD as buckets_field)


def register_triggers(app):
    before_record_insert.connect(set_record_schema)
    before_record_insert.connect(set_record_owner)
    before_record_insert.connect(create_record_files_bucket)
    after_record_insert.connect(index_record)

    # TODO(edima): replace this check with explicit permissions
    before_record_update.connect(check_record_immutable_fields)

    # don't trust the user, reset record schema on update
    before_record_update.connect(set_updated_record_schema)
    before_record_update.connect(set_updated_record_files_bucket)
    after_record_update.connect(index_record)



def set_record_schema(record, **kwargs):
    """Set the record schema when it is created."""
    if 'community' not in record or not record['community']:
        raise InvalidRecordError(errors=[
            FieldError('community', 'Record metadata has no community field.')
        ])
    try:
        community_id = uuid.UUID(record['community'])
    except ValueError as e:
        raise InvalidRecordError(errors=[
            FieldError('community', 'Community ID is not a valid UUID.')
        ])
    schema = CommunitySchema.get_community_schema(community_id)
    record['$schema'] = community_schema_json_schema_link(schema)


def set_record_owner(record, **kwargs):
    if not current_user.is_authenticated:
         # double check, the permission module should have rejected the request
        abort(401)
    record['owner'] = str(current_user.id)


def create_record_files_bucket(record, **kwargs):
    """Create the corresponding file bucket when a record is inserted."""
    bucket = Bucket.create()
    if internal_field not in record:
        record[internal_field] = {}
    internals = record[internal_field]
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


# TODO(edima): replace this check with explicit permissions
def check_record_immutable_fields(record):
    """Checks that the previous community and owner fields are preserved"""
    previous_md = record.model.json
    if previous_md.get('owner') != record.get('owner'):
        raise AlteredRecordError(errors=[
            FieldError('owner', 'The owner field cannot be changed.')
        ])
    if previous_md.get('community') != record.get('community'):
        raise AlteredRecordError(errors=[
            FieldError('community', 'The community field cannot be changed.')
        ])


def set_updated_record_files_bucket(record):
    previous_md = record.model.json
    record[internal_field] = previous_md[internal_field]


def set_updated_record_schema(record):
    previous_md = record.model.json
    if record['community'] == previous_md['community']:
        record['$schema'] = previous_md['$schema']
    else:
        set_record_schema(record)
