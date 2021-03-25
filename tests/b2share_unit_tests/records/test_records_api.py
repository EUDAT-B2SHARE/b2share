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

"""Test Record's programmatic API."""

from six import BytesIO
import uuid
from functools import partial

from copy import deepcopy
import pytest
from jsonschema.exceptions import ValidationError
from b2share.modules.records.errors import AlteredRecordError
from invenio_records import Record
from invenio_records_files.api import Record as _Record
from invenio_records_rest.utils import LazyPIDValue
from invenio_files_rest.models import ObjectVersion
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_pidstore.resolver import Resolver
from b2share.modules.records.api import B2ShareRecord
from b2share.modules.deposit.api import Deposit, copy_data_from_previous
from b2share.modules.deposit.minters import b2share_deposit_uuid_minter
from b2share_unit_tests.helpers import create_deposit, pid_of
from invenio_pidrelations.contrib.versioning import PIDVersioning


def test_change_record_schema_fails(app, test_records):
    """Test updating the $schema field fails."""
    with app.app_context():
        record = Record.get_record(test_records[0].record_id)
        del record['$schema']
        with pytest.raises(AlteredRecordError):
            record.commit()


def test_change_record_community(app, test_records):
    """Test updating the community field fails."""
    with app.app_context():
        record = Record.get_record(test_records[0].record_id)
        del record['community']
        with pytest.raises(AlteredRecordError):
            record.commit()

    with app.app_context():
        record = Record.get_record(test_records[0].record_id)
        record['community'] = uuid.uuid4().hex
        with pytest.raises(AlteredRecordError):
            record.commit()


def test_record_add_unknown_fields(app, test_records):
    """Test adding unknown fields in a record. It should fail."""
    for path in [
        # all the following paths point to "object" fields in
        # in the root JSON Schema
        '/new_field',
        '/community_specific/new_field',
        '/creators/0/new_field',
        '/titles/0/new_field',
        '/contributors/0/new_field',
        '/resource_types/0/new_field',
        '/alternate_identifiers/0/new_field',
        '/descriptions/0/new_field',
        '/license/new_field',
    ]:
        with app.app_context():
            record = Record.get_record(test_records[0].record_id)
            record = record.patch([
                {'op': 'add', 'path': path, 'value': 'any value'}
            ])
            with pytest.raises(ValidationError):
                record.commit()


def test_record_commit_with_incomplete_metadata(app,
                                                test_incomplete_records_data):
    """Test commit of an incomplete record fails."""
    for metadata in test_incomplete_records_data:
        with app.app_context():
            data = deepcopy(metadata.complete_data)
            record_uuid = uuid.uuid4().hex
            b2share_deposit_uuid_minter(record_uuid, data=data)
            deposit = Deposit.create(data, id_=record_uuid)
            deposit.submit()
            deposit.publish()
            deposit.commit()
            pid, record = deposit.fetch_published()
            # make the data incomplete
            record = record.patch(metadata.patch)
            with pytest.raises(ValidationError):
                record.commit()


def test_record_delete_version(app, test_records, test_users):
    """Test deletion of a record version."""
    with app.app_context():
        resolver = Resolver(
            pid_type='b2rec',
            object_type='rec',
            getter=B2ShareRecord.get_record,
        )

        v1 = test_records[0].data
        v1_pid, v1_id = pid_of(v1)

        _, v1_rec = resolver.resolve(v1_id)
        data = copy_data_from_previous(v1_rec.model.json)
        v2 = create_deposit(data, test_users['deposits_creator'],
                            version_of=v1_id)
        ObjectVersion.create(v2.files.bucket, 'myfile1',
                             stream=BytesIO(b'mycontent'))
        v2.submit()
        v2.publish()
        v2_pid, v2_id = pid_of(v2)
        data = copy_data_from_previous(v2.model.json)
        v3 = create_deposit(data, test_users['deposits_creator'],
                            version_of=v2_id)
        v3.submit()
        v3.publish()
        v3_pid, v3_id = pid_of(v3)
        v3_pid, v3_rec = resolver.resolve(v3_pid.pid_value)
        # chain is now: [v1] -- [v2] -- [v3]
        version_child = PIDVersioning(child=v2_pid)
        version_master = PIDVersioning(parent=version_child.parent)
        assert len(version_master.children.all()) == 3
        v3_rec.delete()
        assert len(version_master.children.all()) == 2
        # chain is now [v1] -- [v2]
        # assert that we can create again a new version from v2
        data = copy_data_from_previous(v2.model.json)
        v3 = create_deposit(data, test_users['deposits_creator'],
                            version_of=v2_id)
        v3.submit()
        v3.publish()
        v3_pid, v3_id = pid_of(v3)
        v3_pid, v3_rec = resolver.resolve(v3_pid.pid_value)
        assert len(version_master.children.all()) == 3
        v2_pid, v2_rec = resolver.resolve(v2_pid.pid_value)
        # Delete an intermediate version
        v2_rec.delete()
        assert len(version_master.children.all()) == 2
        # chain is now [v1] -- [v3]
        # Add a new version
        data = copy_data_from_previous(v3.model.json)
        v4 = create_deposit(data, test_users['deposits_creator'],
                            version_of=v3_id)
        v4.submit()
        v4.publish()
        assert len(version_master.children.all()) == 3
        # final chain [v1] -- [v3] -- [v4]
        v4_pid, v4_id = pid_of(v4)
        v4_pid, v4_rec = resolver.resolve(v4_pid.pid_value)
        data = copy_data_from_previous(v4)
        draft_child = create_deposit(data, test_users['deposits_creator'],
                                     version_of=v4_id)
        draft_child.submit()

        # delete all children except the draft child
        assert len(version_master.children.all()) == 3
        v4_rec.delete()
        assert len(version_master.children.all()) == 2

        v3_rec.delete()
        assert len(version_master.children.all()) == 1

        v1_rec.delete()
        assert len(version_master.children.all()) == 0

        assert version_master.parent.status != PIDStatus.DELETED

        draft_child.publish()
        draft_child_pid, draft_child_id = pid_of(draft_child)
        draft_child_pid, draft_child_rec = \
            resolver.resolve(draft_child_pid.pid_value)
        # assert that we can create again a new version

        assert len(version_master.children.all()) == 1

        # no child remains and there is no draft_child
        draft_child_rec.delete()
        assert version_master.parent.status == PIDStatus.DELETED

        # TODO: test in ES that the previous version is reindexed
        # and can be found


def test_record_publish_adds_no_handles_for_external_files(app,
                            records_data_with_external_pids,
                            test_records_data):
    """Test that no handle PIDs are created for external files."""
    for metadata in test_records_data:
        with app.app_context():
            app.config.update({'FAKE_EPIC_PID': True})

            external_pids = records_data_with_external_pids['external_pids']
            external_dict = {x['key']: x['ePIC_PID'] for x in external_pids}
            data = deepcopy(metadata)
            data['external_pids'] = deepcopy(external_pids)

            record_uuid = uuid.uuid4().hex
            b2share_deposit_uuid_minter(record_uuid, data=data)

            deposit = Deposit.create(data, id_=record_uuid)
            ObjectVersion.create(deposit.files.bucket, 'real_file_1.txt',
                             stream=BytesIO(b'mycontent'))
            ObjectVersion.create(deposit.files.bucket, 'real_file_2.txt',
                             stream=BytesIO(b'mycontent'))
            deposit.submit()
            deposit.publish()
            deposit.commit()

            _, record = deposit.fetch_published()

            # external files don't get a handle PID, they already have one
            # which is stored in record['_deposit']['external_pids']
            for f in record.files:
                if f['key'] in external_dict:
                    assert f.get('ePIC_PID') is None
                else:
                    assert '0000' in f['ePIC_PID'] # is a new fake PID
