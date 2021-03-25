# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2017 CERN.
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

"""Test B2Share deposit module's programmatic API."""


from six import BytesIO
import pytest
from functools import partial
import json

from invenio_files_rest.models import ObjectVersion, Bucket
from invenio_records_files.models import RecordsBuckets
from invenio_records_files.api import Record
from invenio_records_rest.utils import LazyPIDValue
from invenio_search.proxies import current_search
from invenio_pidstore.resolver import Resolver
from b2share.modules.records.api import B2ShareRecord
from invenio_db import db

from b2share.modules.deposit.api import (Deposit, copy_data_from_previous)
from b2share.modules.deposit.errors import (DraftExistsVersioningError,
                                            IncorrectRecordVersioningError,
                                            RecordNotFoundVersioningError)
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_pidrelations.contrib.versioning import PIDVersioning
from b2share.modules.schemas.api import CommunitySchema

from b2share_unit_tests.helpers import authenticated_user, create_deposit, \
    pid_of


def test_deposit_versions_create(app, test_records, test_users):
    """Creating new versions of existing records."""
    with app.app_context():
        # Retrieve a record which will be the first version
        v1 = test_records[0].data
        v1_rec = B2ShareRecord.get_record(test_records[0].record_id)
        v1_pid, v1_id = pid_of(v1)
        assert list_published_pids(v1_pid) == [v1_pid]

        # create draft in version chain:
        # version chain becomes: [v1] -- [v2 draft]
        # v2 = create_deposit({}, version_of=v1_id)
        data = copy_data_from_previous(v1_rec.model.json)
        v2 = create_deposit(data, test_users['deposits_creator'],
                            version_of=v1_id)
        assert filenames(v2) == []
        ObjectVersion.create(v2.files.bucket, 'myfile1',
                             stream=BytesIO(b'mycontent'))
        assert filenames(v2) == ['myfile1']

        assert list_published_pids(v1_pid) == [v1_pid]

        # cannot create another draft if one exists
        # not possible: [v1] -- [v2 draft]
        #                    `- [new draft]
        with pytest.raises(DraftExistsVersioningError):
            data = copy_data_from_previous(v1_rec.model.json)
            create_deposit(data, test_users['deposits_creator'],
                           version_of=v1_id)

        # cannot create a version from a draft pid
        # not possible: [v1] -- [v2 draft] -- [new draft]
        with pytest.raises(IncorrectRecordVersioningError): # record pid not created yet
            data = copy_data_from_previous(v1_rec.model.json)
            create_deposit(data, test_users['deposits_creator'],
                           version_of=v2['_deposit']['id'])

        # publish previous draft
        # version chain becomes: [v1] -- [v2]
        v2.submit()
        v2.publish()
        v2_pid, v2_id = pid_of(v2)
        assert list_published_pids(v1_pid) == [v1_pid, v2_pid]

        # cannot create draft based on the first version in a chain
        # not possible: [v1] -- [v2]
        #                    `- [new draft]
        with pytest.raises(IncorrectRecordVersioningError):
            data = copy_data_from_previous(v1_rec.model.json)
            create_deposit(data, test_users['deposits_creator'],
                           version_of=v1_id)

        # create and publish other versions:
        # version chain becomes: [v1] -- [v2] -- [v3]
        data = copy_data_from_previous(v1_rec.model.json)
        v3 = create_deposit(data, test_users['deposits_creator'],
                            version_of=v2_id)
        # assert files are imported from v2
        assert filenames(v3) == ['myfile1']
        ObjectVersion.create(v3.files.bucket, 'myfile2',
                                stream=BytesIO(b'mycontent'))
        assert filenames(v3) == ['myfile1', 'myfile2']

        assert list_published_pids(v1_pid) == [v1_pid, v2_pid]

        v3.submit()
        v3.publish()
        v3_pid, v3_id = pid_of(v3)
        v3_rec = Record.get_record(v3_id)
        assert filenames(v3_rec) == ['myfile1', 'myfile2']
        assert list_published_pids(v1_pid) == [v1_pid, v2_pid, v3_pid]

        # cannot create draft based on an intermediate version in a chain
        # not possible: [v1] -- [v2] -- [v3]
        #                            `- [new draft]
        with pytest.raises(IncorrectRecordVersioningError):
            create_deposit({}, test_users['deposits_creator'],
                           version_of=v2_id)

        # Create yet another version
        # Version chain becomes: [v1] -- [v2] -- [v3] -- [v4]
        data = copy_data_from_previous(v1_rec.model.json)
        v4 = create_deposit(data, test_users['deposits_creator'],
                            version_of=v3_id)
        v4.submit()
        v4.publish()
        assert filenames(v4) == ['myfile1', 'myfile2']
        v4_pid, v4_id = pid_of(v4)
        assert list_published_pids(v1_pid) == [
            v1_pid, v2_pid, v3_pid, v4_pid]

        # assert that creating a new version from a deleted pid is not allowed
        resolver = Resolver(pid_type=v4_pid.pid_type, object_type='rec',
                            getter=partial(B2ShareRecord.get_record,
                                           with_deleted=True))
        v4_pid, v4_rec = LazyPIDValue(resolver, v4_pid.pid_value).data
        # delete [v4]
        v4_rec.delete()
        with pytest.raises(RecordNotFoundVersioningError):
            v5 = create_deposit(data, test_users['deposits_creator'],
                                version_of=v4_id)


def test_deposit_delete(app, draft_deposits, test_records,
                        test_users, test_communities):
    """Test deposit deletion."""
    with app.app_context():
        # create a deposit with a parent pid which has no other children
        first_deposit = create_deposit(
            {'community': str(test_communities['MyTestCommunity1'])},
            test_users['deposits_creator'])
        parent_pid = first_deposit['_pid'][0]['value']
        deposit_pid_value = first_deposit['_deposit']['id']
        # delete the deposit
        first_deposit.delete()
        deposit = PersistentIdentifier.query.filter_by(pid_value=deposit_pid_value).first()
        parent = PersistentIdentifier.query.filter_by(pid_value=parent_pid).one_or_none()
        # check that deleting it deletes parent from the db because there are
        # no remaining published versions and draft.
        assert not parent
        assert deposit.status == PIDStatus.DELETED

        # check that the buckets are removed
        assert not db.session.query(
            Bucket.query.join(RecordsBuckets).
            filter(RecordsBuckets.bucket_id == Bucket.id,
                   RecordsBuckets.record_id == first_deposit.id).exists()
        ).scalar()

        # create a deposit with a parent which has other children
        v1 = test_records[0].data
        v1_rec = B2ShareRecord.get_record(test_records[0].record_id)
        v1_pid, v1_id = pid_of(v1)
        data = copy_data_from_previous(v1_rec.model.json)
        v2 = create_deposit(data, test_users['deposits_creator'],
                            version_of=v1_id)
        deposit_pid_value = v2['_deposit']['id']
        parent_pid = v2['_pid'][0]['value']

        v2.delete()
        deposit = PersistentIdentifier.query.filter_by(pid_value=deposit_pid_value).first()
        parent = PersistentIdentifier.query.filter_by(pid_value=parent_pid).first()
        # check that the parent status is not changed after deleting
        assert parent.status != PIDStatus.DELETED
        assert parent.get_redirect() == v1_pid
        assert deposit.status == PIDStatus.DELETED


def test_deposit_copy_data_from_previous(app, test_records, test_users):
    """Test copying of metadata from previous version."""
    with app.app_context():
        prev_record = test_records[0]
        _prev_record = B2ShareRecord.get_record(prev_record.record_id)
        copied_data = copy_data_from_previous(_prev_record.model.json)
        for field in copy_data_from_previous.extra_removed_fields:
            del prev_record.data[field]
        data = {k: v for k, v in prev_record.data.items() if not k.startswith('_')}
        assert copied_data == data

def test_new_deposit_versions_preserve_schema(app, test_records, test_users):
    """Creating new versions of existing records."""
    with app.app_context():
        # Retrieve a record which will be the first version, and its deposit
        v1_rec = B2ShareRecord.get_record(test_records[0].record_id)
        _, v1_id = pid_of(test_records[0].data)

        # update the community's schema
        community_id = v1_rec.model.json['community']
        old_schema = CommunitySchema.get_community_schema(community_id)
        json_schema = json.loads(old_schema.model.community_schema)
        new_schema = CommunitySchema.create_version(community_id, json_schema)
        assert new_schema.version > old_schema.version

        # create new, unversioned, draft and records
        data = copy_data_from_previous(v1_rec.model.json)
        unver_dep = create_deposit(data, test_users['deposits_creator'])
        unver_dep.submit()
        unver_dep.publish()
        _, unver_rec = unver_dep.fetch_published()

        # the unversioned draft or record in a version chain have the updated schema
        assert unver_dep['$schema'] != Deposit._build_deposit_schema(v1_rec.model.json)
        assert unver_rec.model.json['$schema'] != v1_rec.model.json['$schema']

        # create new draft and record in the version chain of v1
        data = copy_data_from_previous(v1_rec.model.json)
        v2_dep = create_deposit(data, test_users['deposits_creator'],
                            version_of=v1_id)
        v2_dep.submit()
        v2_dep.publish()
        _, v2_rec = v2_dep.fetch_published()

        # the new draft and record in a version chain preserve the version of the schema
        assert v2_dep['$schema'] == Deposit._build_deposit_schema(v1_rec.model.json)
        assert v2_rec.model.json['$schema'] == v1_rec.model.json['$schema']


def list_published_pids(child_pid):
    """List all the child pids of a versionned record.

    This will return [child_pid + child_pid sibling versions]
    """
    vm = retrieve_version_master(child_pid)
    if not vm:
        return None
    pid_list = [pid for pid in vm.children if pid.pid_type == 'b2rec']
    return pid_list

def filenames(record):
    """Returns the names of the files uploaded in a record."""
    return [f.key for f in record.files]

def retrieve_version_master(child_pid):
    """Retrieve the PIDVersioning from a child PID."""
    if type(child_pid).__name__ == "FetchedPID":
        # when getting a pid-like object from elasticsearch
        child_pid = child_pid.provider.get(child_pid.pid_value).pid
    parent_pid = PIDVersioning(child=child_pid).parent
    if not parent_pid:
        return None
    return PIDVersioning(parent=parent_pid)
