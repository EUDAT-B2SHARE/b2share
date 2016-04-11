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
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""B2share records triggers."""

import uuid

from invenio_records.signals import before_record_insert, \
    after_record_insert, after_record_update, \
    after_record_revert, after_record_delete
from invenio_search import current_search_client

from b2share.modules.schemas.api import CommunitySchema
from b2share.modules.schemas.serializers import \
    community_schema_json_schema_link

from .errors import InvalidRecordError
from .config import B2SHARE_RECORDS_INDEX_NAME

DOC_TYPE_RECORD = 'record',


def register_triggers(app):
    before_record_insert.connect(set_record_schema)
    after_record_insert.connect(index_record)
    after_record_update.connect(update_record)
    after_record_revert.connect(update_record)
    after_record_delete.connect(update_record)


def set_record_schema(record, **kwargs):
    if 'community' not in record or not record['community']:
        raise InvalidRecordError(
            'Record\s metadata has no community field.')
    try:
        community_id = uuid.UUID(record['community'])
    except ValueError as e:
        raise InvalidRecordError('Community ID is not a valid UUID.') from e
    schema = CommunitySchema.get_community_schema(community_id)
    record['$schema'] = community_schema_json_schema_link(schema)


def index_record(record, **kwargs):
    current_search_client.index(
        index=B2SHARE_RECORDS_INDEX_NAME,
        doc_type=DOC_TYPE_RECORD,
        id=record.model.id,
        body=record_to_json(record),
        version=record.model.version_id,
        version_type='external_gte',
    )


def update_record(record, **kwargs):
    current_search_client.update(
        index=B2SHARE_RECORDS_INDEX_NAME,
        doc_type=DOC_TYPE_RECORD,
        id=record.model.id,
        body=record_to_json(record),
        version=record.model.version_id,
        version_type='external_gte',
    )


def record_to_json(record):
    # FIXME: the "id" field here is added
    # because the one returned by searching (/api/records) is None
    record_json = dict.copy(record)
    record_json.update({
        'id': str(record.model.id),
    })
    return record_json
