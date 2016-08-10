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

"""Test B2Share deposit module's REST API."""

import json

import pytest
from flask import url_for
from b2share.modules.deposit.api import PublicationStates, Deposit
from copy import deepcopy
from b2share_unit_tests.helpers import (
    subtest_self_link, create_deposit, generate_record_data, url_for_file,
    subtest_file_bucket_content, subtest_file_bucket_permissions,
    build_expected_metadata,
)
from b2share.modules.records.providers import RecordUUIDProvider
from six import BytesIO


@pytest.mark.parametrize('test_users', [({
    'users': ['myuser']
})], indirect=['test_users'])
def test_deposit_create(app, test_records_data, test_users, login_user):
    """Test record draft creation."""
    headers = [('Content-Type', 'application/json'),
               ('Accept', 'application/json')]
    def create_record(client, record_data):
        return client.post(
            url_for('b2share_records_rest.b2share_record_list'),
            data=json.dumps(record_data),
            headers=headers
        )
    # test creating a deposit with anonymous user
    with app.app_context():
        with app.test_client() as client:
            draft_create_res = create_record(client, test_records_data[0])
            assert draft_create_res.status_code == 401

    # test creating a deposit with a logged in user
    with app.app_context():
        with app.test_client() as client:
            user = test_users['myuser']
            login_user(user, client)
            # create the deposit
            for record_data in test_records_data:
                draft_create_res = create_record(client, record_data)
                assert draft_create_res.status_code == 201
                draft_create_data = json.loads(
                    draft_create_res.get_data(as_text=True))
                expected_metadata = build_expected_metadata(
                    record_data,
                    PublicationStates.draft.name,
                    owners=[user.id],
                )
                assert expected_metadata == draft_create_data['metadata']
                subtest_self_link(draft_create_data,
                                  draft_create_res.headers,
                                  client)


@pytest.mark.parametrize('test_users, test_deposits', [({
    'users': ['myuser']
}, {
    'deposits_creator': 'myuser'
})], indirect=['test_users', 'test_deposits'])
def test_deposit_submit(app, test_records_data, test_deposits, test_users,
                        login_user):
    """Test record draft submit with HTTP PATCH."""
    with app.app_context():
        deposit = Deposit.get_record(test_deposits[0])
        record_data = test_records_data[0]
        with app.test_client() as client:
            user = test_users['myuser']
            login_user(user, client)

            headers = [('Content-Type', 'application/json-patch+json'),
                       ('Accept', 'application/json')]
            draft_patch_res = client.patch(
                url_for('b2share_deposit_rest.b2share_deposit_item',
                        pid_value=deposit.pid.pid_value),
                data=json.dumps([{
                    "op": "replace", "path": "/publication_state",
                    "value": PublicationStates.submitted.name
                }]),
                headers=headers)
            assert draft_patch_res.status_code == 200
            draft_patch_data = json.loads(
                draft_patch_res.get_data(as_text=True))
            expected_metadata = build_expected_metadata(
                record_data,
                PublicationStates.draft.name,
                owners=[user.id],
            )
    with app.app_context():
        deposit = Deposit.get_record(test_deposits[0])
        with app.test_client() as client:
            user = test_users['myuser']
            login_user(user, client)
            expected_metadata['publication_state'] = \
                PublicationStates.submitted.name
            assert expected_metadata == draft_patch_data['metadata']
            assert (deposit['publication_state']
                    == PublicationStates.submitted.name)
            subtest_self_link(draft_patch_data,
                              draft_patch_res.headers,
                              client)


@pytest.mark.parametrize('test_users, test_deposits', [({
    'users': ['myuser']
}, {
    'deposits_creator': 'myuser'
})], indirect=['test_users', 'test_deposits'])
def test_deposit_publish(app, test_records_data, test_deposits, test_users,
                         login_user):
    """Test record draft publication with HTTP PATCH."""
    record_data = test_records_data[0]
    with app.app_context():
        deposit = Deposit.get_record(test_deposits[0])
        with app.test_client() as client:
            user = test_users['myuser']
            login_user(user, client)

            headers = [('Content-Type', 'application/json-patch+json'),
                       ('Accept', 'application/json')]
            draft_patch_res = client.patch(
                url_for('b2share_deposit_rest.b2share_deposit_item',
                        pid_value=deposit.pid.pid_value),
                data=json.dumps([{
                    "op": "replace", "path": "/publication_state",
                    "value": PublicationStates.published.name
                }]),
                headers=headers)
            assert draft_patch_res.status_code == 200
            draft_patch_data = json.loads(
                draft_patch_res.get_data(as_text=True))
            expected_metadata = build_expected_metadata(
                record_data,
                PublicationStates.published.name,
                owners=[user.id],
            )

    with app.app_context():
        deposit = Deposit.get_record(test_deposits[0])
        with app.test_client() as client:
            user = test_users['myuser']
            login_user(user, client)
            assert expected_metadata == draft_patch_data['metadata']
            assert (deposit['publication_state']
                    == PublicationStates.published.name)
            subtest_self_link(draft_patch_data,
                              draft_patch_res.headers,
                              client)

            pid, published = deposit.fetch_published()
            # check that the published record and the deposit are equal
            assert dict(**published) == dict(**deposit)
            # check "published" link
            assert draft_patch_data['links']['publication'] == \
                url_for('b2share_records_rest.{0}_item'.format(
                    RecordUUIDProvider.pid_type
                ), pid_value=pid.pid_value, _external=True)
            # check that the published record content match the deposit
            headers = [('Accept', 'application/json')]
            self_response = client.get(
                draft_patch_data['links']['publication'],
                headers=headers
            )
            assert self_response.status_code == 200
            published_data = json.loads(self_response.get_data(
                as_text=True))
            # we don't want to compare the links and dates
            cleaned_published_data = deepcopy(published_data)
            cleaned_draft_data = deepcopy(draft_patch_data)
            for item in [cleaned_published_data, cleaned_draft_data]:
                del item['links']
                del item['created']
                del item['updated']
            assert cleaned_draft_data == cleaned_published_data


def test_deposit_files(app, test_communities, create_user, login_user, admin):
    """Test uploading and reading deposit files."""
    with app.app_context():
        creator = create_user('creator')
        uploaded_files = {
            'myfile1.dat': b'contents1',
            'myfile2.dat': b'contents2',
            'replaced.dat': b'old_content',
        }
        test_record_data = generate_record_data()
        # test with anonymous user
        deposit = create_deposit(test_record_data, creator, uploaded_files)
        uploaded_file_name = 'additional.dat'
        uploaded_file_content = b'additional content'
        # Test file upload
        headers = [('Accept', '*/*')]
        with app.test_client() as client:
            login_user(creator, client)

            # try uploading a new file
            file_url = url_for_file(deposit.files.bucket.id, uploaded_file_name)
            file_put_res = client.put(
                file_url,
                input_stream=BytesIO(uploaded_file_content),
                headers=headers
            )
            uploaded_files[uploaded_file_name] = uploaded_file_content

            # try replacing an existing file
            file_url = url_for_file(deposit.files.bucket.id, 'replaced.dat')
            file_put_res = client.put(
                file_url,
                input_stream=BytesIO(b'new_content'),
                headers=headers
            )
            uploaded_files['replaced.dat'] = b'new_content'

            # try removing a file
            file_url2 = url_for_file(deposit.files.bucket.id, 'myfile2.dat')
            file_put_res = client.delete(
                file_url2,
                input_stream=BytesIO(uploaded_file_content),
                headers=headers
            )
            del uploaded_files['myfile2.dat']

            # check that the files can be retrieved properly
            subtest_file_bucket_content(client, deposit.files.bucket,
                                        uploaded_files)


######################
#  Test permissions  #
######################


def test_deposit_read_permissions(app, test_records_data,
                                  create_user, login_user, admin):
    """Test deposit read with HTTP GET."""
    with app.app_context():
        creator = create_user('creator')
        non_creator = create_user('non-creator')

        def test_get(deposit, status, user=None):
            with app.test_client() as client:
                if user is not None:
                    login_user(user, client)
                headers = [('Accept', 'application/json')]
                request_res = client.get(
                    url_for('b2share_deposit_rest.b2share_deposit_item',
                            pid_value=deposit.pid.pid_value),
                    headers=headers)
                assert request_res.status_code == status

        # test with anonymous user
        deposit = create_deposit(test_records_data[0], creator)
        test_get(deposit, 401)
        deposit.submit()
        test_get(deposit, 401)
        deposit.publish()
        test_get(deposit, 401)

        deposit = create_deposit(test_records_data[0], creator)
        test_get(deposit, 403, non_creator)
        deposit.submit()
        test_get(deposit, 403, non_creator)
        deposit.publish()
        test_get(deposit, 403, non_creator)

        deposit = create_deposit(test_records_data[0], creator)
        test_get(deposit, 200, creator)
        deposit.submit()
        test_get(deposit, 200, creator)
        deposit.publish()
        test_get(deposit, 200, creator)

        deposit = create_deposit(test_records_data[0], creator)
        test_get(deposit, 200, admin)
        deposit.submit()
        test_get(deposit, 200, admin)
        deposit.publish()
        test_get(deposit, 200, admin)


def test_deposit_delete_permissions(app, test_records_data,
                                    create_user, login_user, admin):
    """Test deposit delete with HTTP DELETE."""
    with app.app_context():
        def test_delete(deposit, status, user=None):
            with app.test_client() as client:
                if user is not None:
                    login_user(user, client)
                headers = [('Accept', 'application/json')]
                request_res = client.delete(
                    url_for('b2share_deposit_rest.b2share_deposit_item',
                            pid_value=deposit.pid.pid_value),
                    headers=headers)
                assert request_res.status_code == status

        creator = create_user('creator')
        non_creator = create_user('non-creator')
        # test with anonymous user
        deposit = create_deposit(test_records_data[0], creator)
        test_delete(deposit, 401)
        deposit.submit()
        test_delete(deposit, 401)
        deposit.publish()
        test_delete(deposit, 401)

        # test with non creator user
        deposit = create_deposit(test_records_data[0], creator)
        test_delete(deposit, 403, non_creator)
        deposit.submit()
        test_delete(deposit, 403, non_creator)
        deposit.publish()
        test_delete(deposit, 403, non_creator)

        # test with creator user
        deposit = create_deposit(test_records_data[0], creator)
        test_delete(deposit, 204, creator)
        deposit = create_deposit(test_records_data[0], creator)
        deposit.submit()
        test_delete(deposit, 204, creator)
        deposit = create_deposit(test_records_data[0], creator)
        deposit.submit()
        deposit.publish()
        test_delete(deposit, 403, creator)

        # test with admin user
        deposit = create_deposit(test_records_data[0], creator)
        test_delete(deposit, 204, admin)
        deposit = create_deposit(test_records_data[0], creator)
        deposit.submit()
        test_delete(deposit, 204, admin)
        deposit = create_deposit(test_records_data[0], creator)
        deposit.submit()
        deposit.publish()
        # FIXME: handle the deletion of published deposits
        test_delete(deposit, 403, admin)


def test_deposit_publish_permissions(app, test_records_data, login_user,
                                     admin, create_user):
    """Test deposit publication with HTTP PATCH."""
    with app.app_context():
        creator = create_user('creator')
        non_creator = create_user('non-creator')

        def test_publish(status, user=None):
            deposit = create_deposit(test_records_data[0], creator)
            deposit.submit()
            headers = [('Content-Type', 'application/json-patch+json'),
                       ('Accept', 'application/json')]
            with app.test_client() as client:
                if user is not None:
                    login_user(user, client)
                request_res = client.patch(
                    url_for('b2share_deposit_rest.b2share_deposit_item',
                            pid_value=deposit.pid.pid_value),
                    data=json.dumps([{
                        "op": "replace", "path": "/publication_state",
                        "value": PublicationStates.published.name
                    },{
                        "op": "replace", "path": "/title",
                        "value": 'newtitle'
                    }]),
                    headers=headers)
                assert request_res.status_code == status

        # test with anonymous user
        test_publish(401)
        test_publish(403, non_creator)
        test_publish(200, creator)
        test_publish(200, admin)


def test_deposit_modify_published_permissions(app, test_records_data,
                                              login_user, admin, create_user):
    """Test deposit edition after its publication.

    FIXME: This test should evolve when we allow deposit edition.
    """
    with app.app_context():
        creator = create_user('creator')
        non_creator = create_user('non-creator')
        deposit = create_deposit(test_records_data[0], creator)
        deposit.submit()
        deposit.publish()

        def test_edit(status, user=None):
            headers = [('Content-Type', 'application/json-patch+json'),
                        ('Accept', 'application/json')]
            with app.test_client() as client:
                if user is not None:
                    login_user(user, client)
                request_res = client.patch(
                    url_for('b2share_deposit_rest.b2share_deposit_item',
                            pid_value=deposit.pid.pid_value),
                    data=json.dumps([{
                        "op": "replace", "path": "/publication_state",
                        "value": PublicationStates.draft.name
                    }]),
                    headers=headers)
                assert request_res.status_code == status

        # test with anonymous user
        test_edit(401)
        test_edit(403, non_creator)
        test_edit(403, creator)
        test_edit(403, admin)


def test_deposit_files_permissions(app, test_communities, create_user,
                                   login_user, admin):
    """Test deposit read with HTTP GET."""
    with app.app_context():
        creator = create_user('creator')
        non_creator = create_user('non-creator')

        uploaded_files = {
            'myfile1.dat': b'contents1',
            'myfile2.dat': b'contents2'
        }
        test_record_data = generate_record_data()
        def test_files_access(draft_access, submitted_access,
                              published_access, user=None):
            def get_file(deposit, file_access):
                with app.test_client() as client:
                    if user is not None:
                        login_user(user, client)
                    subtest_file_bucket_permissions(
                        client, deposit.files.bucket,
                        access_level=file_access,
                        is_authenticated=user is not None
                    )
            deposit = create_deposit(test_record_data, creator, uploaded_files)
            get_file(deposit, file_access=draft_access)

            deposit = create_deposit(test_record_data, creator, uploaded_files)
            deposit.submit()
            get_file(deposit, file_access=submitted_access)

            deposit = create_deposit(test_record_data, creator, uploaded_files)
            deposit.submit()
            deposit.publish()
            get_file(deposit, file_access=published_access)

        # Anonymous user
        test_files_access(draft_access=None, submitted_access=None,
                          published_access=None)
        # Non creator user
        test_files_access(user=non_creator, draft_access=None,
                          submitted_access=None,
                          published_access=None)
        # Creator
        test_files_access(user=creator, draft_access='write',
                          submitted_access='write',
                          published_access=None)
        # Admin
        test_files_access(user=admin, draft_access='write',
                          submitted_access='write',
                          published_access=None)
