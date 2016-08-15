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
from contextlib import contextmanager
from enum import Enum

from flask import url_for, g
from invenio_db import db
from invenio_deposit.api import Deposit as DepositRecord
from invenio_records_files.models import RecordsBuckets
from b2share.modules.schemas.api import CommunitySchema
from b2share.modules.deposit.minters import b2share_deposit_uuid_minter
from b2share.modules.deposit.fetchers import b2share_deposit_uuid_fetcher
from invenio_indexer.api import RecordIndexer
from invenio_records_files.api import Record

from .errors import InvalidDepositDataError, InvalidDepositStateError
from invenio_records.errors import MissingModelError
from b2share.modules.records.errors import InvalidRecordError


class PublicationStates(Enum):
    """States of a record."""
    draft = 1
    """Deposit is a draft. This is the initial state of every new deposit."""
    submitted = 2
    """Deposit is submitted. Only deposit in "draft" state can be submitted."""
    published = 3
    """Deposit is published."""


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

    def build_deposit_schema(self, record):
        """Convert record schema to a valid deposit schema."""
        return record['$schema']

    @contextmanager
    def _process_files(self, record_id, data):
        """Snapshot bucket and add files in record during first publishing.

        This is a temporary fix for data['_files'] not being set when there
        are no files.
        Remove this once inveniosoftware/invenio-deposit#107 is fixed.
        """
        with super(Deposit, self)._process_files(record_id, data):
            if not self.files:
                data['_files'] = []
            create_file_pids(data)
            yield data

    @classmethod
    def create(cls, data, id_=None):
        """Create a deposit."""
        # check that the status field is not set
        assert 'publication_state' not in data
        data['publication_state'] = PublicationStates.draft.name
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
        from b2share.modules.schemas.serializers import \
            community_schema_json_schema_link
        data['$schema'] = community_schema_json_schema_link(schema,
                                                            _external=True)
        deposit = super(Deposit, cls).create(data, id_=id_)

        # create file bucket
        bucket = deposit._create_bucket()
        db.session.add(bucket)
        db.session.add(RecordsBuckets(
            record_id=deposit.id, bucket_id=bucket.id
        ))
        return deposit

    def _prepare_edit(self, record):
        data = super(Deposit, self)._prepare_edit(record)
        data['publication_state'] = PublicationStates.draft.name

    def commit(self):
        """Store changes on current instance in database.

        This method extends the default implementation by publishing the
        deposition when 'publication_state' is set to 'published'.
        """
        if self.model is None or self.model.json is None:
            raise MissingModelError()
        # test invalid state transitions
        if (self['publication_state'] == PublicationStates.submitted.name
                and self.model.json['publication_state'] !=
                PublicationStates.draft.name):
            raise InvalidDepositStateError(
                'Cannot submit a deposit in {} state'.format(
                    self.model.json['publication_state'])
            )

        # publish the deposition if needed
        if (self['publication_state'] == PublicationStates.published.name
                # check invenio-deposit status so that we do not loop
                and self['_deposit']['status'] != 'published'):
            super(Deposit, self).publish()  # publish() already calls commit()
            # save the action for later indexing
            if g:
                g.deposit_action = 'publish'
        else:
            super(Deposit, self).commit()
            if g:
                g.deposit_action = 'update-metadata'
        return self

    def publish(self, pid=None, id_=None):
        self['publication_state'] = PublicationStates.published.name
        return super(Deposit, self).publish(pid=pid, id_=id_)

    def submit(self, commit=True):
        """Submit a record for review.

        For now it immediately publishes the record.
        """
        if (PublicationStates[self['publication_state']] !=
                PublicationStates.draft):
            raise InvalidDepositStateError('Cannot submit a deposit in '
                                           '{} state'.format(
                                               self['publication_state']))
        self['publication_state'] = PublicationStates.submitted.name
        if commit:
            self.commit()


def create_file_pids(record_metadata):
    from flask import current_app
    from b2share.modules.records.b2share_epic import createHandle
    from b2share.modules.records.errors import EpicPIDError
    throw_on_failure = current_app.config.get('CFG_FAIL_ON_MISSING_FILE_PID', False)
    for f in record_metadata.get('_files'):
        if f.get('epic_pid'):
            continue
        file_url = url_for('invenio_files_rest.object_api',
                           bucket_id=f.get('bucket'), key=f.get('key'),
                           _external=True)
        try:
            file_pid = createHandle(file_url, checksum=f.get('checksum'))
            if file_pid is None:
                raise EpicPIDError("EPIC PID allocation for file failed")
            f['epic_pid'] = file_pid
        except EpicPIDError as e:
            if throw_on_failure:
                raise e
            else:
                current_app.logger.warning(e)
