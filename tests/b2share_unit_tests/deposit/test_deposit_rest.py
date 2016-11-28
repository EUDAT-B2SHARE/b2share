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
from invenio_search import current_search_client
from flask import url_for
from b2share.modules.deposit.api import PublicationStates, Deposit
from copy import deepcopy
from b2share_unit_tests.helpers import (
    subtest_self_link, create_deposit, generate_record_data, url_for_file,
    subtest_file_bucket_content, subtest_file_bucket_permissions,
    build_expected_metadata, create_user, create_role,
)
from invenio_access.models import ActionUsers, ActionRoles
from b2share.modules.records.providers import RecordUUIDProvider
from six import BytesIO
from b2share.modules.deposit.permissions import create_deposit_need_factory, \
    read_deposit_need_factory
from b2share.modules.communities.api import Community
from invenio_db import db


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
            user = test_users['normal']
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
                    draft=True,
                )
                assert expected_metadata == draft_create_data['metadata']
                subtest_self_link(draft_create_data,
                                  draft_create_res.headers,
                                  client)


def test_deposit_submit(app, test_records_data, draft_deposits, test_users,
                        login_user):
    """Test record draft submit with HTTP PATCH."""
    with app.app_context():
        deposit = Deposit.get_record(draft_deposits[0].id)
        record_data = test_records_data[0]
        with app.test_client() as client:
            user = test_users['deposits_creator']
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
                draft=True,
            )
    with app.app_context():
        deposit = Deposit.get_record(draft_deposits[0].id)
        with app.test_client() as client:
            user = test_users['deposits_creator']
            login_user(user, client)
            expected_metadata['publication_state'] = \
                PublicationStates.submitted.name
            assert expected_metadata == draft_patch_data['metadata']
            assert (deposit['publication_state']
                    == PublicationStates.submitted.name)
            subtest_self_link(draft_patch_data,
                              draft_patch_res.headers,
                              client)


def test_deposit_publish(app, test_users, test_communities,
                         login_user):
    """Test record draft publication with HTTP PATCH."""
    with app.app_context():
        community_name = 'MyTestCommunity1'
        creator = test_users['deposits_creator']
        record_data = generate_record_data(community=community_name)
        community = Community.get(name=community_name)
        com_admin = create_user('com_admin', roles=[community.admin_role])

        deposit = create_deposit(record_data, creator)
        deposit_id = deposit.id
        deposit.submit()
        db.session.commit()

        with app.test_client() as client:
            login_user(com_admin, client)

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
                owners=[creator.id],
                draft=True,
            )

    with app.app_context():
        deposit = Deposit.get_record(deposit_id)
        with app.test_client() as client:
            login_user(creator, client)
            assert expected_metadata == draft_patch_data['metadata']
            assert (deposit['publication_state']
                    == PublicationStates.published.name)
            subtest_self_link(draft_patch_data,
                              draft_patch_res.headers,
                              client)

            pid, published = deposit.fetch_published()
            # check that the published record and the deposit are equal except
            # for the schema
            cleaned_deposit = {f: v for f, v in deposit.items()
                               if f != '$schema'}
            cleaned_published = {f: v for f, v in deposit.items()
                                 if f != '$schema'}
            assert cleaned_published == cleaned_deposit
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
            # the published record has an extra empty 'files' array
            assert cleaned_published_data['files'] == []
            del cleaned_published_data['files']
            cleaned_draft_data = deepcopy(draft_patch_data)
            for item in [cleaned_published_data, cleaned_draft_data]:
                del item['links']
                del item['created']
                del item['updated']
                del item['metadata']['$schema']
            assert cleaned_draft_data == cleaned_published_data


def test_deposit_files(app, test_communities, login_user, test_users):
    """Test uploading and reading deposit files."""
    with app.app_context():
        admin = test_users['admin']
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


def test_deposit_create_permission(app, test_users, login_user,
                                   test_communities):
    """Test record draft creation."""
    headers = [('Content-Type', 'application/json'),
               ('Accept', 'application/json')]

    with app.app_context():
        community_name = 'MyTestCommunity1'
        record_data = generate_record_data(community=community_name)
        community_id = test_communities[community_name]
        community = Community.get(community_id)

        creator = create_user('creator')
        need = create_deposit_need_factory(str(community_id))
        allowed = create_user('allowed', permissions=[need])
        com_member = create_user('com_member', roles=[community.member_role])
        com_admin = create_user('com_admin', roles=[community.admin_role])

        def restrict_creation(restricted):
            community.update({'restricted_submission':restricted})
            db.session.commit()

        def test_creation(expected_code, user=None):
            with app.test_client() as client:
                if user is not None:
                    login_user(user, client)
                draft_create_res = client.post(
                    url_for('b2share_records_rest.b2share_record_list'),
                    data=json.dumps(record_data),
                    headers=headers
                )
                assert draft_create_res.status_code == expected_code

        # test creating a deposit with anonymous user
        restrict_creation(False)
        test_creation(401)
        restrict_creation(True)
        test_creation(401)

        # test creating a deposit with a logged in user
        restrict_creation(False)
        test_creation(201, creator)
        restrict_creation(True)
        test_creation(403, creator)
        # test with a use who is allowed
        test_creation(201, allowed)
        # test with a community member and admin
        test_creation(201, com_member)
        test_creation(201, com_admin)


def test_deposit_read_permissions(app, login_user, test_users,
                                  test_communities):
    """Test deposit read with HTTP GET."""
    with app.app_context():
        community_name = 'MyTestCommunity1'
        record_data = generate_record_data(community=community_name)
        community = Community.get(name=community_name)

        admin = test_users['admin']
        creator = create_user('creator')
        non_creator = create_user('non-creator')
        com_member = create_user('com_member', roles=[community.member_role])
        com_admin = create_user('com_admin', roles=[community.admin_role])

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
        deposit = create_deposit(record_data, creator)
        test_get(deposit, 401)
        deposit.submit()
        test_get(deposit, 401)
        deposit.publish()
        test_get(deposit, 401)

        deposit = create_deposit(record_data, creator)
        test_get(deposit, 403, non_creator)
        deposit.submit()
        test_get(deposit, 403, non_creator)
        deposit.publish()
        test_get(deposit, 403, non_creator)

        deposit = create_deposit(record_data, creator)
        test_get(deposit, 200, creator)
        deposit.submit()
        test_get(deposit, 200, creator)
        deposit.publish()
        test_get(deposit, 200, creator)

        deposit = create_deposit(record_data, creator)
        test_get(deposit, 200, admin)
        deposit.submit()
        test_get(deposit, 200, admin)
        deposit.publish()
        test_get(deposit, 200, admin)

        deposit = create_deposit(record_data, creator)
        test_get(deposit, 403, com_member)
        deposit.submit()
        test_get(deposit, 403, com_member)
        deposit.publish()
        test_get(deposit, 403, com_member)

        deposit = create_deposit(record_data, creator)
        test_get(deposit, 403, com_admin)
        deposit.submit()
        test_get(deposit, 200, com_admin)
        deposit.publish()
        test_get(deposit, 200, com_admin)


def test_deposit_search_permissions(app, draft_deposits, submitted_deposits,
                                    test_users, login_user, test_communities):
    """Test deposit search permissions."""
    with app.app_context():
        # flush the indices so that indexed deposits are searchable
        current_search_client.indices.flush('*')

        admin = test_users['admin']
        creator = test_users['deposits_creator']
        non_creator = create_user('non-creator')

        permission_to_read_all_submitted_deposits = read_deposit_need_factory(
            community=str(test_communities['MyTestCommunity2']),
            publication_state='submitted',
        )
        allowed_role = create_role(
            'allowed_role',
            permissions=[
                permission_to_read_all_submitted_deposits
            ]
        )
        user_allowed_by_role = create_user('user-allowed-by-role',
                                           roles=[allowed_role])
        user_allowed_by_permission = create_user(
            'user-allowed-by-permission',
            permissions=[
                permission_to_read_all_submitted_deposits
            ]
        )

        community = Community.get(test_communities['MyTestCommunity2'])
        com_member = create_user('com_member', roles=[community.member_role])
        com_admin = create_user('com_admin', roles=[community.admin_role])

        search_deposits_url = url_for(
            'b2share_records_rest.b2share_record_list', drafts=1, size=100)
        headers = [('Content-Type', 'application/json'),
                ('Accept', 'application/json')]

        def test_search(status, expected_deposits, user=None):
            with app.test_client() as client:
                if user is not None:
                    login_user(user, client)
                deposit_search_res = client.get(
                    search_deposits_url,
                    headers=headers)
                assert deposit_search_res.status_code == status
                # test the response data only when the user is allowed to
                # search for deposits
                if status != 200:
                    return
                deposit_search_data = json.loads(
                    deposit_search_res.get_data(as_text=True))

                assert deposit_search_data['hits']['total'] == \
                    len(expected_deposits)

                deposit_pids = [hit['id'] for hit
                            in deposit_search_data['hits']['hits']]
                expected_deposit_pids = [dep.id.hex for dep
                                         in expected_deposits]
                deposit_pids.sort()
                expected_deposit_pids.sort()
                assert deposit_pids == expected_deposit_pids

        test_search(200, draft_deposits + submitted_deposits, creator)
        test_search(200, draft_deposits + submitted_deposits, admin)
        test_search(401, [], None)
        test_search(200, [], non_creator)


        # search for submitted records
        community2_deposits = [dep for dep in submitted_deposits
                                if dep.data['community'] ==
                                str(test_communities['MyTestCommunity2'])]
        test_search(200, community2_deposits, user_allowed_by_role)
        test_search(200,
                    community2_deposits,
                    user_allowed_by_permission)

        # community admin should have access to all submitted records
        # in their community
        test_search(200, [], com_member)
        test_search(200, community2_deposits, com_admin)


def test_deposit_delete_permissions(app, test_records_data,
                                    login_user, test_users):
    """Test deposit delete with HTTP DELETE."""
    with app.app_context():
        admin = test_users['admin']
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



def test_deposit_submit_permissions(app, login_user, test_communities,
                                    test_users):
    """Test deposit publication with HTTP PATCH."""
    with app.app_context():
        community_name = 'MyTestCommunity1'
        record_data = generate_record_data(community=community_name)

        admin = test_users['admin']
        creator = create_user('creator')
        non_creator = create_user('non-creator')

        community = Community.get(name=community_name)
        com_member = create_user('com_member', roles=[community.member_role])
        com_admin = create_user('com_admin', roles=[community.admin_role])

        def test_submit(status, user=None):
            deposit = create_deposit(record_data, creator)
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
                        "value": PublicationStates.submitted.name
                    }, {
                        "op": "replace", "path": "/title",
                        "value": 'newtitle'
                    }]),
                    headers=headers)
                assert request_res.status_code == status

        # test with anonymous user
        test_submit(401)
        test_submit(403, non_creator)
        test_submit(200, creator)
        test_submit(200, admin)
        test_submit(403, com_member)
        test_submit(403, com_admin)


def test_deposit_publish_permissions(app, login_user, test_communities,
                                     test_users):
    """Test deposit publication with HTTP PATCH."""
    with app.app_context():
        community_name = 'MyTestCommunity1'
        record_data = generate_record_data(community=community_name)

        admin = test_users['admin']
        creator = create_user('creator')
        non_creator = create_user('non-creator')

        community = Community.get(name=community_name)
        com_member = create_user('com_member', roles=[community.member_role])
        com_admin = create_user('com_admin', roles=[community.admin_role])

        def test_publish(status, user=None):
            deposit = create_deposit(record_data, creator)
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
                    }, {
                        "op": "replace", "path": "/title",
                        "value": 'newtitle'
                    }]),
                    headers=headers)
                assert request_res.status_code == status

        # test with anonymous user
        test_publish(401)
        test_publish(403, non_creator)
        test_publish(403, creator)
        test_publish(200, admin)
        test_publish(403, com_member)
        test_publish(200, com_admin)


def test_deposit_modify_published_permissions(app, login_user, test_communities,
                                              test_users):
    """Test deposit edition after its publication.

    FIXME: This test should evolve when we allow deposit edition.
    """
    with app.app_context():
        community_name = 'MyTestCommunity1'
        record_data = generate_record_data(community=community_name)

        admin = test_users['admin']
        creator = create_user('creator')
        non_creator = create_user('non-creator')

        community = Community.get(name=community_name)
        com_member = create_user('com_member', roles=[community.member_role])
        com_admin = create_user('com_admin', roles=[community.admin_role])

        deposit = create_deposit(record_data, creator)
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
        test_edit(403, com_member)
        test_edit(403, com_admin)


def test_deposit_files_permissions(app, test_communities, login_user,
                                   test_users):
    """Test deposit read with HTTP GET."""
    with app.app_context():
        community_name = 'MyTestCommunity1'

        admin = test_users['admin']
        creator = create_user('creator')
        non_creator = create_user('non-creator')

        community = Community.get(name=community_name)
        com_member = create_user('com_member', roles=[community.member_role])
        com_admin = create_user('com_admin', roles=[community.admin_role])

        uploaded_files = {
            'myfile1.dat': b'contents1',
            'myfile2.dat': b'contents2'
        }
        test_record_data = generate_record_data(community=community_name)

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
        # Community member
        test_files_access(user=com_member, draft_access=None,
                          submitted_access=None,
                          published_access=None)
        # Community admin
        test_files_access(user=com_admin, draft_access=None,
                          submitted_access='write',
                          published_access=None)
