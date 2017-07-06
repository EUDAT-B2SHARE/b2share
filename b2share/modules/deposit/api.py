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

import copy
import uuid
from contextlib import contextmanager
from enum import Enum
from urllib.parse import urlparse, urlunparse

from flask import url_for, g
from invenio_db import db
from invenio_deposit.api import Deposit as DepositRecord
from invenio_records_files.models import RecordsBuckets
from jsonschema.validators import validator_for
from jsonschema.exceptions import ValidationError
from b2share.modules.schemas.api import CommunitySchema
from b2share.modules.deposit.minters import b2share_deposit_uuid_minter
from b2share.modules.deposit.fetchers import b2share_deposit_uuid_fetcher
from invenio_indexer.api import RecordIndexer
from invenio_records_files.api import Record

from .errors import InvalidDepositError
from b2share.modules.communities.api import Community
from b2share.modules.communities.errors import CommunityDoesNotExistError
from b2share.modules.communities.workflows import publication_workflows
from invenio_records.errors import MissingModelError
from b2share.modules.records.errors import InvalidRecordError
from b2share.modules.access.policies import is_under_embargo
from b2share.modules.schemas.errors import CommunitySchemaDoesNotExistError


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
        parsed = urlparse(self['$schema'])
        return urlunparse(parsed._replace(fragment='/json_schema'))

    def build_deposit_schema(self, record):
        """Convert record schema to a valid deposit schema."""
        parsed = urlparse(record['$schema'])
        return urlunparse(parsed._replace(fragment='/draft_json_schema'))

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
        if 'publication_state' in data:
            raise InvalidDepositError(
                'Field "publication_state" cannot be set.')
        data['publication_state'] = PublicationStates.draft.name
        # Set record's schema
        if '$schema' in data:
            raise InvalidDepositError('"$schema" field should not be set.')
        if 'community' not in data or not data['community']:
            raise ValidationError(
                'Record\s metadata has no community field.')
        try:
            community_id = uuid.UUID(data['community'])
        except ValueError as e:
            raise InvalidDepositError(
                'Community ID is not a valid UUID.') from e
        try:
            schema = CommunitySchema.get_community_schema(community_id)
        except CommunitySchemaDoesNotExistError as e:
            raise InvalidDepositError(
                'No schema for community {}.'.format(community_id)) from e

        from b2share.modules.schemas.serializers import \
            community_schema_draft_json_schema_link
        data['$schema'] = community_schema_draft_json_schema_link(
            schema,
            _external=True
        )
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

    def validate(self, **kwargs):
        if ('publication_state' in self and
            self['publication_state'] == PublicationStates.draft.name):
            if 'community' not in self:
                raise ValidationError('Missing required field "community"')
            try:
                community_id = uuid.UUID(self['community'])
            except (ValueError, KeyError) as e:
                raise InvalidDepositError('Community ID is not a valid UUID.') \
                    from e
            default_validator = validator_for(
                CommunitySchema.get_community_schema(community_id).build_json_schema())
            if 'required' not in default_validator.VALIDATORS:
                raise NotImplementedError('B2Share does not support schemas '
                                          'which have no "required" keyword.')
            DraftDepositValidator = type(
                'DraftDepositValidator',
                (default_validator,),
                dict(VALIDATORS=copy.deepcopy(default_validator.VALIDATORS))
            )
            # function ignoring the validation of the given keyword
            ignore = lambda *args, **kwargs: None
            DraftDepositValidator.VALIDATORS['required'] = ignore
            DraftDepositValidator.VALIDATORS['minItems'] = ignore
            kwargs['validator'] = DraftDepositValidator
        return super(Deposit, self).validate(**kwargs)

    def commit(self):
        """Store changes on current instance in database.

        This method extends the default implementation by publishing the
        deposition when 'publication_state' is set to 'published'.
        """
        if self.model is None or self.model.json is None:
            raise MissingModelError()

        # automatically make embargoed records private
        if self.get('embargo_date') and self.get('open_access'):
            if is_under_embargo(self):
                self['open_access'] = False

        if 'community' in self:
            try:
                community = Community.get(self['community'])
            except CommunityDoesNotExistError as e:
                raise InvalidDepositError('Community {} does not exist.'.format(
                    self['community'])) from e
            workflow = publication_workflows[community.publication_workflow]
            workflow(self.model, self)

        # publish the deposition if needed
        if (self['publication_state'] == PublicationStates.published.name
                # check invenio-deposit status so that we do not loop
                and self['_deposit']['status'] != PublicationStates.published.name):
            super(Deposit, self).publish()  # publish() already calls commit()
            # save the action for later indexing
            if g:
                g.deposit_action = 'publish'
        else:
            super(Deposit, self).commit()
            if g:
                g.deposit_action = 'update-metadata'
        return self

    def publish(self):
        self['publication_state'] = PublicationStates.published.name
        return self.commit() # calls super(Deposit, self).publish()

    def submit(self, commit=True):
        """Submit a record for review.

        For now it immediately publishes the record.
        """
        self['publication_state'] = PublicationStates.submitted.name
        if commit:
            self.commit()


def create_file_pids(record_metadata):
    from flask import current_app
    from b2share.modules.records.b2share_epic import createHandle
    from b2share.modules.records.errors import EpicPIDError
    throw_on_failure = current_app.config.get('CFG_FAIL_ON_MISSING_FILE_PID', False)
    for f in record_metadata.get('_files'):
        if f.get('ePIC_PID'):
            continue
        file_url = url_for('invenio_files_rest.object_api',
                           bucket_id=f.get('bucket'), key=f.get('key'),
                           _external=True)
        try:
            file_pid = createHandle(file_url, checksum=f.get('checksum'))
            if file_pid is None:
                raise EpicPIDError("EPIC PID allocation for file failed")
            f['ePIC_PID'] = file_pid
        except EpicPIDError as e:
            if throw_on_failure:
                raise e
            else:
                current_app.logger.warning(e)
