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

"""Test B2Share Storage Class."""

from datetime import datetime, timedelta
import json
import pytest
from flask import url_for
from b2share.modules.deposit.errors import InvalidDepositError
from invenio_files_rest.models import Bucket, FileInstance, \
    ObjectVersion, Location
from invenio_db import db
from invenio_records_rest.utils import allow_all
from invenio_files_rest.proxies import current_files_rest
from b2share.modules.communities.api import Community
from b2share.modules.deposit.api import Deposit, PublicationStates
from b2share_unit_tests.helpers import assert_external_files, \
    build_expected_metadata, subtest_file_bucket_permissions, create_user


def test_b2share_storage_with_pid(base_app, app, tmp_location,
                                  login_user, test_users):
    """Check that the storage class will redirect pid files."""
    pid = 'http://hdl.handle.net/11304/74c66f0b-f814-4202-9dcb-4889ba9b1047'
    with app.app_context():
        # Disable access control for this test
        tmp_location = Location.query.first()
        with db.session.begin_nested():
            bucket = Bucket.create(tmp_location, storage_class='B')
            pid_file = FileInstance.create()
            pid_file.set_uri(pid, 1, 0, storage_class='B')
            ObjectVersion.create(bucket, 'test.txt', pid_file.id)

        db.session.commit()
        url = url_for('invenio_files_rest.object_api',
                        bucket_id=bucket.id,
                        key='test.txt')
    try:
        with app.app_context():
            permission = current_files_rest.permission_factory
            current_files_rest.permission_factory = allow_all
        # Check that accessing the file redirects to the PID
        with app.test_client() as client:
            resp = client.get(url)
            assert resp.headers['Location'] == pid
            assert resp.status_code == 302
    finally:
        with app.app_context():
            current_files_rest.permission_factory = permission


@pytest.mark.parametrize('new_external_pids',
                         [[{
                             "key": "existing_pid_with_checksum.txt",
                             "ePIC_PID":
                             "http://hdl.handle.net/11304/dad1a76c-4311-46d6-bb55-085525f8dd18"
                         }], [{
                             "key": "non_existing_pid.txt",
                             "ePIC_PID":
                             "http://hdl.handle.net/11304/dad1a76c-4311-46d6-bb55-999999999999"
                         }]])
def test_modify_external_files(app, deposit_with_external_pids,
                               new_external_pids):
    """Test changing PID, renaming and deletion of external files."""
    with app.app_context():
        if new_external_pids[0]['key'] == 'non_existing_pid.txt':
            with pytest.raises(InvalidDepositError):
                deposit = Deposit.get_record(
                    deposit_with_external_pids.deposit_id)
                deposit = deposit.patch([
                    {'op': 'replace', 'path': '/external_pids',
                     'value': new_external_pids}
                ])
                deposit.commit()
                assert_external_files(deposit, new_external_pids)
        else:
            deposit = Deposit.get_record(deposit_with_external_pids.deposit_id)
            deposit = deposit.patch([
                {'op': 'replace', 'path': '/external_pids',
                 'value': new_external_pids}
            ])
            deposit.commit()
            for file in deposit.files:
                assert file.obj.file.checksum != 0
            assert_external_files(deposit, new_external_pids)


def test_adding_external_files(app, records_data_with_external_pids,
                               deposit_with_external_pids):
    """Test the addition of external files."""
    with app.app_context():
        # renaming a file to have a duplicate key
        records_data_with_external_pids['external_pids'][0]['key'] = \
            'file2.txt'
        deposit = Deposit.get_record(deposit_with_external_pids.deposit_id)
        # this should be caught and return an InvalidDepositError
        with pytest.raises(InvalidDepositError):
            deposit = deposit.patch([
                {'op': 'replace', 'path': '/external_pids',
                 'value': records_data_with_external_pids['external_pids']}
            ])
            deposit.commit()

    with app.app_context():
        records_data_with_external_pids['external_pids'][0]['key'] = \
            'file1.txt'
        records_data_with_external_pids['external_pids'].append({
            "key": "file3.txt",
            "ePIC_PID":
            "http://hdl.handle.net/11304/0d8dbdec-74e4-4774-954e-1a98e5c0cfa3"
        })
        deposit = deposit.patch([
            {'op': 'replace', 'path': '/external_pids',
             'value': records_data_with_external_pids['external_pids']}
        ])
        deposit.commit()
        assert_external_files(deposit,
                              records_data_with_external_pids['external_pids'])


def test_missing_handle_prefix(app, test_users, login_user,
                               records_data_with_external_pids,
                               deposit_with_external_pids):
    """Test external files that are registered without a handle prefix."""
    with app.app_context():
        no_prefix_external_pid = \
            [{"key": "no_prefix.txt",
              "ePIC_PID": "11304/0d8dbdec-74e4-4774-954e-1a98e5c0cfa3"}]
        correct_external_pid = \
            [{"key": "no_prefix.txt",
              "ePIC_PID":
              "http://hdl.handle.net/11304/0d8dbdec-74e4-4774-954e-1a98e5c0cfa3"}]
        deposit = Deposit.get_record(deposit_with_external_pids.deposit_id)
        deposit = deposit.patch([
            {'op': 'replace', 'path': '/external_pids',
             'value': no_prefix_external_pid}
        ])
        deposit.commit()
        assert_external_files(deposit, correct_external_pid)

    headers = [('Content-Type', 'application/json'),
               ('Accept', 'application/json')]

    def create_record(client, record_data):
        return client.post(
            url_for('b2share_records_rest.b2rec_list'),
            data=json.dumps(record_data),
            headers=headers
        )

    with app.app_context():
        with app.test_client() as client:
            user = test_users['normal']
            login_user(user, client)
            # create the deposit with the missing prefix
            records_data_with_external_pids['external_pids'] = \
                no_prefix_external_pid
            draft_data_with_external_pids = records_data_with_external_pids
            draft_create_res = create_record(
                client, draft_data_with_external_pids)
            assert draft_create_res.status_code == 201
            draft_create_data = json.loads(
                draft_create_res.get_data(as_text=True))
            # assert that when returned the external pid has the prefix
            assert draft_create_data['metadata']['external_pids'] == \
                correct_external_pid


def test_embargoed_records_with_external_pids(app, test_users,
                                              login_user,
                                              deposit_with_external_pids):
    """Test that embargoed records handle external pids correctly."""
    with app.app_context():
        deposit = Deposit.get_record(deposit_with_external_pids.deposit_id)
        deposit = deposit.patch([
            {'op': 'add', 'path': '/embargo_date',
             'value': (datetime.utcnow() + timedelta(days=1)).isoformat()}
        ])
        deposit = deposit.patch([
            {'op': 'replace', 'path': '/open_access',
             'value': False}
        ])
        deposit.commit()
        deposit.submit()
        deposit.publish()

    with app.app_context():
        with app.test_client() as client:
            # anonymous user tries to download the external file
            for file in deposit.files:
                ext_file_url = url_for('invenio_files_rest.object_api',
                                       bucket_id=file.obj.bucket,
                                       key=file.obj.key)
                resp = client.get(ext_file_url)
                # 404
                assert resp.status_code == 404
                # test that when getting the record the external_pids field
                # is not visible in the metadata

    with app.app_context():
        with app.test_client() as client:
            # the owner can download the external file
            login_user(test_users['deposits_creator'], client)
            for file in deposit.files:
                ext_file_url = url_for('invenio_files_rest.object_api',
                                       bucket_id=file.obj.bucket,
                                       key=file.obj.key)
                resp = client.get(ext_file_url)
                assert resp.status_code == 302
