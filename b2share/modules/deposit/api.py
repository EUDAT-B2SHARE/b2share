# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2016, 2017 University of Tübingen, CERN.
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
from sqlalchemy.exc import IntegrityError

from flask import url_for, g, current_app
from flask_login import current_user
from jsonschema.validators import validator_for, validate as validate_schema
from jsonschema.exceptions import ValidationError
from b2share.modules.schemas.api import CommunitySchema
from b2share.modules.deposit.minters import b2share_deposit_uuid_minter
from b2share.modules.deposit.fetchers import b2share_deposit_uuid_fetcher
from jsonpatch import apply_patch

from invenio_db import db
from invenio_files_rest.models import Bucket, FileInstance, ObjectVersion
from invenio_deposit.api import Deposit as InvenioDeposit, has_status, preserve, index
from invenio_records_files.api import Record
from invenio_records_files.models import RecordsBuckets
from invenio_records.errors import MissingModelError
from invenio_indexer.api import RecordIndexer
from invenio_pidrelations.contrib.versioning import PIDVersioning
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_pidstore.resolver import Resolver
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_rest.errors import FieldError


from .errors import (InvalidDepositError,
                     DraftExistsVersioningError,
                     IncorrectRecordVersioningError,
                     RecordNotFoundVersioningError)
from b2share.modules.communities.api import Community
from b2share.modules.communities.errors import CommunityDoesNotExistError
from b2share.modules.communities.workflows import publication_workflows
from b2share.modules.records.api import B2ShareRecord
from b2share.modules.records.errors import InvalidRecordError
from b2share.modules.records.utils import is_publication
from b2share.modules.records.providers import RecordUUIDProvider
from b2share.modules.access.policies import is_under_embargo
from b2share.modules.schemas.errors import CommunitySchemaDoesNotExistError
from b2share.modules.schemas.api import CommunitySchema
from b2share.modules.deposit.minters import b2share_deposit_uuid_minter
from b2share.modules.deposit.fetchers import b2share_deposit_uuid_fetcher
from b2share.modules.deposit.providers import DepositUUIDProvider
from b2share.modules.handle.proxies import current_handle
from b2share.modules.handle.errors import EpicPIDError

class MyRecordIndexer(RecordIndexer):

    def delete(self, record, **kwargs):
        """Delete a record.

        :param record: Record instance.
        :param kwargs: Passed to
            :meth:`elasticsearch:elasticsearch.Elasticsearch.delete`.
        """
        index, doc_type = self.record_to_index(record)
        index, doc_type = self._prepare_index(index, doc_type)

        # Pop version arguments for backward compatibility if they were
        # explicit set to None in the function call.
        if 'version' in kwargs and kwargs['version'] is None:
            kwargs.pop('version', None)
            kwargs.pop('version_type', None)
        else:
            kwargs.setdefault('version', record.revision_id)
            kwargs.setdefault('version_type', self._version_type)

        # HK: This was neccessary because Invenio-Index uses str(UUID) instead of UUID.hex ...
        # B2share is still using hex id's for records identifiers.
        # Please note: this is not consistent accross all code, for example communities ID are str(UUID)
        
        return self.client.delete(
            id=record.id.hex,
            index=index,
            doc_type=doc_type,
            **kwargs
        )

class MyInvenioDeposit(InvenioDeposit):

    indexer = MyRecordIndexer()

    """Default deposit indexer."""
    @classmethod
    @index
    def create(cls, data, id_=None):
        id_ = id_ or uuid.uuid4().hex

        if '_deposit' not in data:
            cls.deposit_minter(id_, data)

        data['_deposit'].setdefault('owners', list())
        if current_user and current_user.is_authenticated:
            creator_id = int(current_user.get_id())

            if creator_id not in data['_deposit']['owners']:
                data['_deposit']['owners'].append(creator_id)

            data['_deposit']['created_by'] = creator_id

        # HK: Invoke create method from super of InvenioDeposit, which is invenio-record-files !
        # Reason: That method in that class supports the 'with_bucket' parameter, which we need to set to False

        return super(InvenioDeposit, cls).create(data, id_=id_ , with_bucket=False)


class PublicationStates(Enum):
    """States of a record."""
    draft = 1
    """Deposit is a draft. This is the initial state of every new deposit."""
    submitted = 2
    """Deposit is submitted. Only deposit in "draft" state can be submitted."""
    published = 3
    """Deposit is published."""


class Deposit(MyInvenioDeposit):
    """B2Share Deposit API."""

    published_record_class = B2ShareRecord
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

    @staticmethod
    def _build_deposit_schema(record):
        """Convert record schema to a valid deposit schema."""
        parsed = urlparse(record['$schema'])
        return urlunparse(parsed._replace(fragment='/draft_json_schema'))

    def build_deposit_schema(self, record):
        """Convert record schema to a valid deposit schema."""
        return Deposit._build_deposit_schema(record)

    @has_status
    # check also that these fields are not mutable on the published records too
    @preserve(fields=['_internal', '_files', '_oai', '_deposit', '_bucket'])
    def patch(self, patch):
        """Patch record metadata.
        :params patch: Dictionary of record metadata.
        :returns: A new :class:`Record` instance.
        """
        data = dict(self)
        # Copying temporarily 'external_pids' field in order to give the
        # illusion that this field actually exist.
        # TODO: Note that the 'external_pids' field should in the end
        # be part of the root schema.
        external_pids = generate_external_pids(self)
        if external_pids:
            data['external_pids'] = external_pids
        data = apply_patch(data, patch)

        # if the 'external_pids' field was not modified we can discard it.
        if 'external_pids' in data and \
                data['external_pids'] == data['_deposit'].get('external_pids'):
            del data['external_pids']

        return self.__class__(data, model=self.model)

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

    @property
    def record_pid(self):
        """Return the published/reserved record PID."""
        if isinstance(self.id, uuid.UUID):
            id = self.id.hex
        else:
            id = self.id

        return PersistentIdentifier.get('b2rec', id)

    @property
    def versioning(self):
        """Return the parent versionning PID."""
        return PIDVersioning(child=self.record_pid)

    @classmethod
    def create(cls, data, id_=None, version_of=None):
        """Create a deposit with the optional id.

        :params version_of: PID of an existing record. If set, the new record
        will be marked as a new version of this referenced record. If no data
        is provided the new record will be a copy of this record. Note: this
        PID must reference the current last version of a record.
        """

        # check that the status field is not set
        if 'publication_state' in data:
            raise InvalidDepositError(
                'Field "publication_state" cannot be set.')
        data['publication_state'] = PublicationStates.draft.name
        # Set record's schema
        if '$schema' in data:
            raise InvalidDepositError('"$schema" field should not be set.')

        # Retrieve reserved record PID which should have already been created
        # by the deposit minter (The record PID value is the same
        # as the one of the deposit)
        rec_pid = RecordUUIDProvider.get(data['_deposit']['id']).pid
        version_master, prev_version = None, None
        # if this is a new version of an existing record, add the future
        # record pid in the chain of versions.
        if version_of:
            version_master, prev_version = \
                find_version_master_and_previous_record(version_of)
            # The new version must be in the same community
            if data['community'] != prev_version['community']:
                raise ValidationError(
                    'The community field cannot change between versions.')
            try:
                version_master.insert_draft_child(rec_pid)
            except Exception as exc:
                # Only one draft is allowed per version chain.
                if 'Draft child already exists for this relation' in \
                        exc.args[0]:
                    raise DraftExistsVersioningError(
                        version_master.draft_child
                    )
                raise exc
        else:
            # create parent PID
            parent_pid = RecordUUIDProvider.create().pid
            version_master = PIDVersioning(parent=parent_pid)
            version_master.insert_draft_child(child=rec_pid)

        # Mint the deposit with the parent PID
        data['_pid'] = [{
            'value': version_master.parent.pid_value,
            'type': RecordUUIDProvider.parent_pid_type,
        }]
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

        if version_of:
            data['$schema'] = Deposit._build_deposit_schema(prev_version)
        else:
            from b2share.modules.schemas.serializers import \
                community_schema_draft_json_schema_link
            data['$schema'] = community_schema_draft_json_schema_link(
                schema,
                _external=True
            )

        # prepopulate required boolean fields with false
        if not version_of:
            from b2share.modules.schemas.api import BlockSchema
            import json
            community_schema = json.loads(schema.community_schema)
            if 'required' in community_schema:
                bs_id = json.loads(schema.community_schema)['required'][0]
                bs = BlockSchema.get_block_schema(bs_id)
                bs_version = bs.versions[len(bs.versions) - 1]
                schema_dict = json.loads(bs_version.json_schema)
                required = []
                if 'required' in schema_dict:
                    required = schema_dict['required']
                properties = {}
                if 'properties' in schema_dict:
                    properties = schema_dict['properties']
                try:
                    community_metadata = data['community_specific'][bs_id]
                except KeyError:
                    community_metadata = {}
                for key in required:
                    if properties[key]['type'] == 'boolean' and not key in community_metadata:
                        community_metadata[key] = False
                data['community_specific'] = {bs_id: community_metadata}

        # create file bucket
        if prev_version and prev_version.files:
            # Clone the bucket from the previous version. This doesn't
            # duplicate files.
            bucket = prev_version.files.bucket.snapshot(lock=False)
            bucket.locked = False
        else:
            bucket = Bucket.create(storage_class=current_app.config[
                'DEPOSIT_DEFAULT_STORAGE_CLASS'
            ])

        if 'external_pids' in data:
            create_b2safe_file(data['external_pids'], bucket)
            del data['external_pids']

        deposit = super(Deposit, cls).create(data, id_=id_)
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
        if 'external_pids' in self:
            deposit_id = self['_deposit']['id']
            recid = PersistentIdentifier.query.filter_by(
                pid_value=deposit_id).first()
            assert recid.status == 'R'
            record_bucket = RecordsBuckets.query.filter_by(
                record_id=recid.pid_value).first()
            bucket = Bucket.query.filter_by(id=record_bucket.bucket_id).first()
            object_versions = ObjectVersion.query.filter_by(
                bucket_id=bucket.id).all()
            key_to_pid = {
                ext_pid.get('key'): ext_pid.get('ePIC_PID')
                for ext_pid in self['external_pids']
            }
            # for the existing files
            for object_version in object_versions:
                if object_version.file is None or \
                        object_version.file.storage_class != 'B':
                    continue
                # check that they are still in the file pids list or remove
                if object_version.key not in key_to_pid:
                    ObjectVersion.delete(bucket,
                                         object_version.key)
                # check that the uri is still the same or update it
                elif object_version.file.uri != \
                        key_to_pid[object_version.key]:
                    db.session.query(FileInstance).\
                        filter(FileInstance.id == object_version.file_id).\
                        update({"uri": key_to_pid[object_version.key]})
            create_b2safe_file(self['external_pids'], bucket)
            del self['external_pids']

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

            # Retrieve previous version in order to reindex it later.
            previous_version_pid = None
            # Save the previous "last" version for later use
            if self.versioning.parent.status == PIDStatus.REDIRECTED and \
                    self.versioning.has_children:
                previous_version_pid = self.versioning.last_child
                previous_version_uuid = str(RecordUUIDProvider.get(
                    previous_version_pid.pid_value
                ).pid.object_uuid)
            external_pids = generate_external_pids(self)
            if external_pids:
                self['_deposit']['external_pids'] = external_pids

            super(Deposit, self).publish()  # publish() already calls commit()
            # Register parent PID if necessary and update redirect
            self.versioning.update_redirect()
            # Reindex previous version. This is needed in order to update
            # the is_last_version flag
            if previous_version_pid is not None:
                self.indexer.index_by_id(previous_version_uuid)

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
        return self.commit()  # calls super(Deposit, self).publish()

    def submit(self, commit=True):
        """Submit a record for review.

        For now it immediately publishes the record.
        """
        self['publication_state'] = PublicationStates.submitted.name
        if commit:
            self.commit()

    def delete(self):
        """Delete a deposit."""

        deposit_pid = self.pid
        pid_value = deposit_pid.pid_value
        record_pid = RecordUUIDProvider.get(pid_value).pid
        version_master = PIDVersioning(child=record_pid)
        # every deposit has a parent version after the 2.1.0 upgrade
        # except deleted ones. We check the parent version in case of a delete
        # revert.
        assert version_master is not None, 'Unexpected deposit without versioning.'
        # if the record is unpublished hard delete it
        if record_pid.status == PIDStatus.RESERVED:
            version_master.remove_draft_child()
            db.session.delete(record_pid)
        # if the parent doesn't have any published records hard delete it
        if version_master.parent.status == PIDStatus.RESERVED:
            db.session.delete(version_master.parent)
        deposit_pid.delete()

        # delete all buckets linked to the deposit
        res = Bucket.query.join(RecordsBuckets).\
            filter(RecordsBuckets.bucket_id == Bucket.id,
                   RecordsBuckets.record_id == self.id).all()

        # remove the deposit from ES
        self.indexer.delete(self)

        # we call the super of Invenio deposit instead of B2Share deposit as
        # Invenio deposit doesn't support the deletion of published deposits
        super(InvenioDeposit, self).delete(force=True)

        for bucket in res:
            bucket.locked = False
            bucket.remove()


def create_file_pids(record_metadata):
    from flask import current_app
    throw_on_failure = current_app.config.get(
        'CFG_FAIL_ON_MISSING_FILE_PID', False)
    external_pids = record_metadata['_deposit'].get('external_pids', [])
    external_keys = { x.get('key') for x in external_pids }
    for f in record_metadata.get('_files'):
        if f.get('ePIC_PID') or f.get('key') in external_keys:
            continue
        file_url = url_for('invenio_files_rest.object_api',
                           bucket_id=f.get('bucket'), key=f.get('key'),
                           _external=True)
        try:
            file_pid = current_handle.create_handle(
                file_url, checksum=f.get('checksum'), fixed=True
            )
            if file_pid is None:
                raise EpicPIDError("EPIC PID allocation for file failed")
            f['ePIC_PID'] = file_pid
        except EpicPIDError as e:
            if throw_on_failure:
                raise e
            else:
                current_app.logger.warning(e)


def create_b2safe_file(external_pids, bucket):
    """Create a FileInstance which contains a PID in its uri."""
    validate_schema(external_pids, {
        'type': 'array',
        'items': {
            'type': 'object',
            'properties': {
                'ePIC_PID': {'type': 'string'},
                'key': {'type': 'string'}
            },
            'additionalProperties': False,
            'required': ['ePIC_PID', 'key']
        }
    })

    keys_list = [e['key'] for e in external_pids]
    keys_set = set(keys_list)
    if len(keys_list) != len(keys_set):
        raise InvalidDepositError([FieldError('external_pids',
            'Field external_pids contains duplicate keys.')])
    for external_pid in external_pids:
        if not external_pid['ePIC_PID'].startswith('http://hdl.handle.net/'):
            external_pid['ePIC_PID'] = 'http://hdl.handle.net/' + \
                external_pid['ePIC_PID']
        if external_pid['key'].startswith('/'):
            raise InvalidDepositError(
                [FieldError('external_pids',
                            'File key cannot start with a "/".')])
        try:
            # Create the file instance if it does not already exist
            file_instance = FileInstance.get_by_uri(external_pid['ePIC_PID'])
            if file_instance is None:
                file_instance = FileInstance.create()
                file_instance.set_uri(
                    external_pid['ePIC_PID'], 1, 0, storage_class='B')
            assert file_instance.storage_class == 'B'
            # Add the file to the bucket if it is not already in it
            current_version = ObjectVersion.get(bucket, external_pid['key'])
            if not current_version or \
                    current_version.file_id != file_instance.id:
                ObjectVersion.create(bucket, external_pid['key'],
                                     file_instance.id)
        except IntegrityError as e:
            raise InvalidDepositError(
                [FieldError('external_pids', 'File URI already exists.')])


def find_version_master_and_previous_record(version_of):
    """Retrieve the PIDVersioning and previous record of a record PID.

    :params version_of: record PID.
    """
    try:
        child_pid = RecordUUIDProvider.get(version_of).pid
        if child_pid.status == PIDStatus.DELETED:
            raise RecordNotFoundVersioningError()
    except PIDDoesNotExistError as e:
        raise RecordNotFoundVersioningError() from e

    version_master = PIDVersioning(child=child_pid)

    prev_pid = version_master.last_child
    assert prev_pid.pid_type == RecordUUIDProvider.pid_type
    prev_version = Record.get_record(prev_pid.object_uuid)
    # check that version_of references the last version of a record
    assert is_publication(prev_version.model)
    if prev_pid.pid_value != version_of:
        raise IncorrectRecordVersioningError(prev_pid.pid_value)
    return version_master, prev_version


def copy_data_from_previous(previous_record):
    """Copy metadata from previous record version."""
    data = copy.deepcopy(previous_record)
    # eliminate _deposit, _files, _oai, _pid, etc.
    external_pids = None
    if 'external_pids' in previous_record['_deposit']:
        external_pids = previous_record['_deposit']['external_pids']
        files = []
        for _file in previous_record['_files']:
            if _file['key'] in external_pids:
                files.append(_file)
    copied_data = {k: v for k, v in data.items() if not k.startswith('_') and
                   k not in copy_data_from_previous.extra_removed_fields}
    if external_pids:
        copied_data['_deposit'] = {'external_pids': external_pids}
        copied_data['_files'] = files
    return copied_data


def generate_external_pids(record):
    """Generate the list of external files of a record sorted by key."""
    external_pids = []
    current_file_keys = [f for f in record.files if
                         f.obj.file.storage_class == 'B']
    current_file_keys.sort(key=lambda f: f.obj.key)
    for f in current_file_keys:
        external_pids.append({'key': f.obj.key,
                              'ePIC_PID': f.obj.file.uri})
    return external_pids


copy_data_from_previous.extra_removed_fields = [
    'publication_state', 'publication_date', '$schema'
]
