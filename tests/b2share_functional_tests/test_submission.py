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

from b2share.modules.deposit.api import PublicationStates
from invenio_search import current_search
from flask import url_for
from invenio_db import db


def test_deposit(app, test_communities, create_user, login_user,
                 test_records_data):

    def test_files(client, bucket_link, uploaded_files):
        headers = {'Accept': '*/*'}
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

    with app.app_context():
        allowed_user = create_user('allowed')
        db.session.commit()

    with app.app_context():
        with app.test_client() as client:
            login_user(allowed_user, client)
            headers = [('Content-Type', 'application/json'),
                       ('Accept', 'application/json')]
            patch_headers = [('Content-Type', 'application/json-patch+json'),
                             ('Accept', 'application/json')]

            created_records = {}  # dict of created records
            for record_data in test_records_data:
                record_list_url = (
                    lambda **kwargs:
                    url_for('b2share_records_rest.b2share_record_list',
                            **kwargs))
                draft_create_res = client.post(record_list_url(),
                                               data=json.dumps(record_data),
                                               headers=headers)
                assert draft_create_res.status_code == 201
                draft_create_data = json.loads(
                    draft_create_res.get_data(as_text=True))

                uploaded_files = {
                    'myfile1.dat': b'contents1',
                    'myfile2.dat': b'contents2'
                }

                for file_key, file_content in uploaded_files.items():
                    # Test file upload
                    headers = {'Accept': '*/*'}
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
                           ('Accept', 'application/json')]
                draft_patch_res = client.patch(
                    url_for('b2share_deposit_rest.b2share_deposit_item',
                            pid_value=draft_create_data['id']),
                    data=json.dumps([{"op": "replace", "path": "/title", "value":
                                      "first-patched-title"}]),
                    headers=headers)
                assert draft_patch_res.status_code == 200
                draft_patch_data = json.loads(
                    draft_patch_res.get_data(as_text=True))

                # Test draft GET
                draft_unpublished_get_res = client.get(
                    url_for('b2share_deposit_rest.b2share_deposit_item',
                            pid_value=draft_create_data['id']),
                    headers=headers)
                assert draft_unpublished_get_res.status_code == 200
                draft_unpublished_get_data = json.loads(
                    draft_unpublished_get_res.get_data(as_text=True))

                # test draft submit
                draft_submit_res = client.patch(
                    url_for('b2share_deposit_rest.b2share_deposit_item',
                            pid_value=draft_create_data['id']),
                    data=json.dumps([{
                        "op": "replace", "path": "/publication_state",
                        "value": PublicationStates.submitted.name
                    }]),
                    headers=patch_headers)
                assert draft_submit_res.status_code == 200

                # test draft publish
                draft_publish_res = client.patch(
                    url_for('b2share_deposit_rest.b2share_deposit_item',
                            pid_value=draft_create_data['id']),
                    data=json.dumps([{
                        "op": "replace", "path": "/publication_state",
                        "value": PublicationStates.published.name
                    }]),
                    headers=patch_headers)

                assert draft_publish_res.status_code == 200
                draft_publish_data = json.loads(
                    draft_publish_res.get_data(as_text=True))

                # Test draft GET
                draft_published_get_res = client.get(
                    url_for('b2share_deposit_rest.b2share_deposit_item',
                            pid_value=draft_create_data['id']),
                    headers=headers)
                assert draft_published_get_res.status_code == 200
                draft_published_get_data = json.loads(
                    draft_published_get_res.get_data(as_text=True))

                # Test record GET
                record_get_res = client.get(
                    url_for('b2share_records_rest.b2share_record_item',
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

    with app.app_context():
        with app.test_client() as client:
            login_user(allowed_user, client)
            # refresh index to make records searchable
            current_search._client.indices.refresh()

            # test search  records
            record_search_res = client.get(
                url_for('b2share_records_rest.b2share_record_list'),
                data='',
                headers=headers)
            assert record_search_res.status_code == 200
            record_search_data = json.loads(
                record_search_res.get_data(as_text=True))
            # assert the search returns expected records
            search_records = {rec['id'] : rec for rec in
                              record_search_data['hits']['hits']}
            assert search_records == created_records

    with app.app_context():
        other_user = create_user('other')
        with app.test_client() as client:
            # test with a user not owning any records
            login_user(other_user, client)
            # test search
            record_search_res = client.get(
                url_for('b2share_records_rest.b2share_record_list'),
                data='',
                headers=headers)
            assert record_search_res.status_code == 200
            record_search_data = json.loads(
                record_search_res.get_data(as_text=True))

            # check that only open_access records are returned
            open_access_records = {rec['id']: rec for rec in
                                   created_records.values()
                                   if rec['metadata']['open_access'] == True}
            search_records = {rec['id'] : rec for rec in
                              record_search_data['hits']['hits']}
            assert search_records == open_access_records

            for recid, record_data in created_records.items():
                # Test record GET permissions
                record_get_res = client.get(
                    url_for('b2share_records_rest.b2share_record_item',
                            pid_value=recid),
                    headers=headers)

                if recid in open_access_records.keys():
                    assert record_get_res.status_code == 200
                else:
                    assert record_get_res.status_code == 403
