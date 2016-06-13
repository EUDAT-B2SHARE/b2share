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

"""B2Share Deposit API."""

import uuid

from flask import current_app, url_for
from invenio_deposit.api import Deposit as DepositRecord
from b2share.modules.schemas.api import CommunitySchema
from b2share.modules.schemas.serializers import \
    community_schema_json_schema_link
from b2share.modules.deposit.minters import b2share_deposit_uuid_minter
from b2share.modules.deposit.fetchers import b2share_deposit_uuid_fetcher
from invenio_indexer.api import RecordIndexer
# from b2share.modules.records.api import Record
from invenio_records_files.api import Record

from .errors import InvalidDepositDataError


class Deposit(DepositRecord):
    """B2Share Deposit API."""

    indexer = RecordIndexer(
        record_to_index=lambda record: ('deposits', 'deposit')
    )
    """Deposit indexer."""

    published_record_class = Record
    """Record API class used for published records."""

    deposit_minter = staticmethod(b2share_deposit_uuid_minter)
    """Deposit minter."""

    deposit_fetcher = staticmethod(b2share_deposit_uuid_fetcher)
    """Deposit fetcher."""


    def __init__(self, *args, **kwargs):
        super(Deposit, self).__init__(*args, **kwargs)

    @property
    def record_schema(self):
        """Convert deposit schema to a valid record schema."""
        return self['$schema']
        # return self['_internal']['record_schema']


    def build_deposit_schema(self, record):
        """Convert record schema to a valid deposit schema."""
        return record['$schema']

    @classmethod
    def create(cls, data, id_=None):
        """Create a deposit."""
        # Set record's schema
        if '$schema' in data:
            raise InvalidDepositDataError('"$schema" field should not be set.')
        if 'community' not in data or not data['community']:
            raise InvalidDepositDataError(
                'Record\s metadata has no community field.')
        try:
            community_id = uuid.UUID(data['community'])
        except ValueError as e:
            raise InvalidRecordError('Community ID is not a valid UUID.') from e
        schema = CommunitySchema.get_community_schema(community_id)
        record_schema = community_schema_json_schema_link(schema)
        # data['_internal'] = {'record_schema': record_schema}
        data['$schema'] = '{}#/json_schema'.format(url_for(
            # 'b2share_deposit_rest.community_deposit_schema',
            'b2share_schemas.community_schema_item',
            community_id=community_id,
            schema_version_nb=schema.version,
            _external=True))
        return super(Deposit, cls).create(data, id_=id_)

    def submit(self):
        """Submit a record for review.

        For now it immediately publishes the record.
        """
        self.publish()
