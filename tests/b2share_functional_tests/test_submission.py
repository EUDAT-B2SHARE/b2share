# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2016 University of Tuebingen, CERN.
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

"""Test Invenio integration with submission tests."""

from __future__ import absolute_import, print_function

import json
from io import BytesIO

import pytest
from b2share.modules.communities.api import Community
from tests.b2share_unit_tests.helpers import create_user, generate_record_data
from b2share.modules.deposit.api import PublicationStates
from invenio_search import current_search
from flask import url_for as flask_url_for
from invenio_db import db
from invenio_oauth2server import current_oauth2server
from invenio_oauth2server.models import Token


@pytest.mark.parametrize('authentication', [('user/password'), ('oauth')])
def test_deposit(app, test_communities, login_user, authentication):
    """Test record submission with classic login and access token."""
    with app.app_context():
        allowed_user = create_user('allowed')

        scopes = current_oauth2server.scope_choices()
        allowed_token = Token.create_personal(
            'allowed_token', allowed_user.id,
            scopes=[s[0] for s in scopes]
        )
        # application authentication token header
        allowed_headers = [('Authorization',
                            'Bearer {}'.format(allowed_token.access_token))]

        other_user = create_user('other')
        other_token = Token.create_personal(
            'other_token', other_user.id,
            scopes=[s[0] for s in scopes]
        )
        # application authentication token header
        other_headers = [('Authorization',
                          'Bearer {}'.format(other_token.access_token))]

        community_name = 'MyTestCommunity1'
        community = Community.get(name=community_name)
        com_admin = create_user('com_admin', roles=[community.admin_role])
        com_admin_token = Token.create_personal(
            'com_admin_token', com_admin.id,
            scopes=[s[0] for s in scopes]
        )
        # application authentication token header
        com_admin_headers = [('Authorization',
                              'Bearer {}'.format(com_admin_token.access_token))]

        test_records_data = [generate_record_data(community=community_name)
                             for idx in range(1,3)]

        db.session.commit()

    if authentication == 'user/password':
        subtest_deposit(app, test_communities, allowed_user, other_user,
                        com_admin, [], [], [], login_user, test_records_data)
    else:
        subtest_deposit(app, test_communities, allowed_user, other_user,
                        com_admin, allowed_headers, other_headers,
                        com_admin_headers, lambda u, c: 42, test_records_data)


def subtest_deposit(app, test_communities, allowed_user, other_user,
                    com_admin, allowed_headers, other_headers,
                    com_admin_headers, login_user, test_records_data):
    def url_for(*args, **kwargs):
        """Generate url using flask.url_for and the current app ctx.

        This is necessary as we don't want to share the same application
        context across requests.
        """
        with app.app_context():
            return flask_url_for(*args, **kwargs)

    def test_files(client, bucket_link, uploaded_files):
        headers = [('Accept', '*/*')] + allowed_headers
        file_list_res = client.get(bucket_link,
                                   headers=headers)
        assert file_list_res.status_code == 200
        file_list_data = json.loads(
            file_list_res.get_data(as_text=True))
        assert 'contents' in file_list_data
        assert len(file_list_data['contents']) == len(uploaded_files)
        for draft_file in file_list_data['contents']:
            assert 'size' in draft_file and 'key' in draft_file
            uploaded_content = uploaded_files[draft_file['key']]
            assert draft_file['size'] == len(uploaded_content)

            # download the file and test it
            file_res = client.get(draft_file['links']['self'], headers=headers)
            h = file_res.headers
            # content type is changed from text/html to text/plain by
            # invenio-files-rest in order to avoid XSS attacks.
            assert h['Content-Type'] == 'text/plain; charset=utf-8'
            # XSS prevention
            assert h['Content-Security-Policy'] == 'default-src \'none\';'
            assert h['X-Content-Type-Options'] == 'nosniff'
            assert h['X-Download-Options'] == 'noopen'
            assert h['X-Permitted-Cross-Domain-Policies'] == 'none'
            assert h['X-Frame-Options'] == 'deny'
            assert h['X-XSS-Protection'] == '1; mode=block'
            assert h['Content-Disposition'] == 'inline'
            # check file content
            assert file_res.data == uploaded_content


    headers = [('Content-Type', 'application/json'),
                ('Accept', 'application/json')] + allowed_headers
    patch_headers = [('Content-Type', 'application/json-patch+json'),
                        ('Accept', 'application/json')] + allowed_headers
    publish_headers = [('Content-Type', 'application/json-patch+json'),
                       ('Accept', 'application/json')] + com_admin_headers

    created_records = {}  # dict of created records
    for record_data in test_records_data:
        with app.test_client() as client:
            login_user(allowed_user, client)
            record_list_url = (
                lambda **kwargs:
                url_for('b2share_records_rest.b2rec_list',
                        **kwargs))
            draft_create_res = client.post(record_list_url(),
                                            data=json.dumps(record_data),
                                            headers=headers)
            assert draft_create_res.status_code == 201
            draft_create_data = json.loads(
                draft_create_res.get_data(as_text=True))

            uploaded_files = {
                'myfile1.html': b'contents1',
                'myfile2.html': b'contents2'
            }

            for file_key, file_content in uploaded_files.items():
                # Test file upload
                headers = [
                    ('Accept', '*/*'),
                    ('Content-Type', 'text/html; charset=utf-8')
                ] + allowed_headers
                object_url = '{0}/{1}'.format(
                    draft_create_data['links']['files'], file_key)
                file_put_res = client.put(
                    object_url,
                    input_stream=BytesIO(file_content),
                    headers=headers
                )
                assert file_put_res.status_code == 200
                file_put_data = json.loads(
                    file_put_res.get_data(as_text=True))
                assert 'created' in file_put_data

            # test uploaded files
            test_files(client, draft_create_data['links']['files'],
                        uploaded_files)

            # Test file list

            # test draft PATCH
            headers = [('Content-Type', 'application/json-patch+json'),
                       ('Accept', 'application/json')] + allowed_headers
            draft_patch_res = client.patch(
                url_for('b2share_deposit_rest.b2dep_item',
                        pid_value=draft_create_data['id']),
                data=json.dumps([{"op": "replace", "path": "/titles", "value":
                                    [{"title":"first-patched-title"}]}]),
                headers=headers)
            assert draft_patch_res.status_code == 200
            draft_patch_data = json.loads(
                draft_patch_res.get_data(as_text=True))

            # Test draft GET
            draft_unpublished_get_res = client.get(
                url_for('b2share_deposit_rest.b2dep_item',
                        pid_value=draft_create_data['id']),
                headers=headers)
            assert draft_unpublished_get_res.status_code == 200
            draft_unpublished_get_data = json.loads(
                draft_unpublished_get_res.get_data(as_text=True))

            # test draft submit
            draft_submit_res = client.patch(
                url_for('b2share_deposit_rest.b2dep_item',
                        pid_value=draft_create_data['id']),
                data=json.dumps([{
                    "op": "replace", "path": "/publication_state",
                    "value": PublicationStates.submitted.name
                }]),
                headers=patch_headers)
            assert draft_submit_res.status_code == 200

        with app.test_client() as client:
            login_user(com_admin, client)
            # test draft publish
            draft_publish_res = client.patch(
                url_for('b2share_deposit_rest.b2dep_item',
                        pid_value=draft_create_data['id']),
                data=json.dumps([{
                    "op": "replace", "path": "/publication_state",
                    "value": PublicationStates.published.name
                }]),
                headers=publish_headers)

            assert draft_publish_res.status_code == 200
            draft_publish_data = json.loads(
                draft_publish_res.get_data(as_text=True))

            # Test draft GET
            draft_published_get_res = client.get(
                url_for('b2share_deposit_rest.b2dep_item',
                        pid_value=draft_create_data['id']),
                headers=headers)
            assert draft_published_get_res.status_code == 200
            draft_published_get_data = json.loads(
                draft_published_get_res.get_data(as_text=True))

            # Test record GET
            record_get_res = client.get(
                url_for('b2share_records_rest.b2rec_item',
                        pid_value=draft_publish_data['id']),
                headers=headers)
            assert record_get_res.status_code == 200
            record_get_data = json.loads(
                record_get_res.get_data(as_text=True))

            # FIXME: test draft edition once we support it

            # test that published record's files match too
            test_files(client, record_get_data['links']['files'],
                       uploaded_files)

            created_records[record_get_data['id']] = record_get_data

    with app.test_client() as client:
        login_user(allowed_user, client)
        # refresh index to make records searchable
        with app.app_context():
            current_search._client.indices.refresh()

        # test search  records
        record_search_res = client.get(
            url_for('b2share_records_rest.b2rec_list'),
            data='',
            headers=headers)
        assert record_search_res.status_code == 200
        record_search_data = json.loads(
            record_search_res.get_data(as_text=True))
        # assert the search returns expected records
        search_records = {rec['id'] : rec for rec in
                            record_search_data['hits']['hits']}
        assert search_records == created_records

    # Check non creator records access

    headers = [('Content-Type', 'application/json'),
                ('Accept', 'application/json')] + other_headers
    with app.test_client() as client:
        # test with a user not owning any records
        login_user(other_user, client)
        # test search
        record_search_res = client.get(
            url_for('b2share_records_rest.b2rec_list'),
            data='',
            headers=headers)
        assert record_search_res.status_code == 200
        record_search_data = json.loads(
            record_search_res.get_data(as_text=True))

        # check that all records are returned for non creator too
        open_access_records = {rec['id']: rec for rec in
                                created_records.values()
                                if rec['metadata']['open_access'] == True}
        search_records = {rec['id'] : rec for rec in
                            record_search_data['hits']['hits']}
        assert search_records == created_records

        for recid, record_data in created_records.items():
            # Test record GET permissions
            record_get_res = client.get(
                url_for('b2share_records_rest.b2rec_item',
                        pid_value=recid),
                headers=headers)
            # check that non-creator can access the metadata
            assert record_get_res.status_code == 200
            # TODO: check that the files are not accessible
