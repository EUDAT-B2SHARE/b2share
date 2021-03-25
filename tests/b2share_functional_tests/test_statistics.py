# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2017 CERN
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

"""Test B2Share statistics functionality."""
from __future__ import absolute_import, print_function

import json
from uuid import uuid1
from unittest.mock import DEFAULT, patch

import b2share.modules.records.cli as records_cli
import pytest
from mock import Mock
from b2share.modules.communities.api import Community
from b2share.modules.deposit.api import PublicationStates
from tests.b2share_unit_tests.helpers import create_user, generate_record_data
from click.testing import CliRunner
from flask import url_for as flask_url_for
from flask.cli import ScriptInfo
from invenio_accounts.models import User
from invenio_db import db
from invenio_files_rest.models import Bucket
from invenio_records.models import RecordMetadata
from invenio_records_files.models import RecordsBuckets
from invenio_oauth2server import current_oauth2server
from invenio_oauth2server.models import Token
from invenio_search import current_search, current_search_client
from invenio_stats.tasks import aggregate_events, process_events
from invenio_queues import InvenioQueues
from invenio_queues.proxies import current_queues
from io import BytesIO

headers = [('Content-Type', 'application/json'),
           ('Accept', 'application/json')]
patch_headers = [('Content-Type', 'application/json-patch+json'),
                 ('Accept', 'application/json')]


def test_file_download_statistics(app, test_community, test_users,
                                  test_records, login_user):
    """Test checking a record's DOI using CLI commands."""
    with app.app_context():
        def url_for(*args, **kwargs):
            """Generate url using flask.url_for and the current app ctx."""
            with app.app_context():
                return flask_url_for(*args, **kwargs)

        # create user that will create the record and the files
        scopes = current_oauth2server.scope_choices()

        allowed_user = create_user('allowed')

        scopes = current_oauth2server.scope_choices()
        allowed_token = Token.create_personal(
            'allowed_token', allowed_user.id,
            scopes=[s[0] for s in scopes]
        )
        # application authentication token header
        allowed_headers = [('Authorization',
                            'Bearer {}'.format(allowed_token.access_token))]

        community_name = 'MyTestCommunity1'
        community = Community.get(name=community_name)
        com_admin = create_user('com_admin2', roles=[community.admin_role])
        com_admin_token = Token.create_personal(
            'com_admin_token', com_admin.id,
            scopes=[s[0] for s in scopes]
        )
        # application authentication token header
        com_admin_headers = [('Authorization',
                              'Bearer {}'.format(com_admin_token.access_token)),
                             ('User-Agent',
                              'Mozilla/5.0 (Windows NT 6.1; WOW64) '
                              'AppleWebKit/537.36 (KHTML, like Gecko)'
                              'Chrome/45.0.2454.101 Safari/537.36')]
        publish_headers = [('Content-Type', 'application/json-patch+json'),
                           ('Accept', 'application/json')] + com_admin_headers
        submit_headers = [('Content-Type', 'application/json-patch+json'),
                          ('Accept', 'application/json')] + allowed_headers
        stats_headers = [('Content-Type', 'application/json')]

        test_records_data = [generate_record_data(community=test_community.name)
                            for idx in range(1, 3)]

        for record_data in test_records_data:
            with app.test_client() as client:
                login_user(allowed_user, client)

                record_list_url = (
                    lambda **kwargs:
                    url_for('b2share_records_rest.b2rec_list',
                            **kwargs))

                headers = [('Content-Type', 'application/json'),
                        ('Accept', 'application/json')] + allowed_headers
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

                    bucket_id = draft_create_data['links']['files'].split('/')[-1]
                    # make sure that downloads from deposits are skipped
                    client.get(url_for('invenio_files_rest.object_api',
                                    bucket_id=bucket_id,
                                    key=file_key))
                    assert process_events(['file-download']) == \
                        [('file-download', (0, 0))]

                # test draft submit
                draft_submit_res = client.patch(
                    url_for('b2share_deposit_rest.b2dep_item',
                            pid_value=draft_create_data['id']),
                    data=json.dumps([{
                        "op": "replace", "path": "/publication_state",
                        "value": PublicationStates.submitted.name
                    }]),
                    headers=submit_headers)
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

                # Test record GET
                record_get_res = client.get(
                    url_for('b2share_records_rest.b2rec_item',
                            pid_value=draft_publish_data['id']),
                    headers=headers)
                assert record_get_res.status_code == 200
                record_get_data = json.loads(
                    record_get_res.get_data(as_text=True))

                # make sure that templates are in the ES
                list(current_search.put_templates())

                # test that a record is accessible through the rest api
                file1 = record_get_data['files'][0]

                # download once
                client.get(url_for('invenio_files_rest.object_api',
                                bucket_id=file1['bucket'],
                                key=file1['key']),
                        headers=com_admin_headers)
                # make sure that the queue contains the event
                assert list(current_queues.queues['stats-file-download'].consume())

                # download again
                client.get(url_for('invenio_files_rest.object_api',
                                bucket_id=file1['bucket'],
                                key=file1['key']),
                        headers=com_admin_headers)

                process_events(['file-download'])
                current_search_client.indices.refresh('*')
                # make sure that new index for events is created in ES
                current_search_client.indices.exists(
                    index='events-stats-file-download')

                aggregate_events(['file-download-agg'])
                current_search_client.indices.refresh('*')

                # make sure that new aggregation index is created in ES
                current_search_client.indices.exists(
                    index='stats-file-download')

                stats_ret = client.post(url_for('invenio_stats.stat_query'),
                                        data=json.dumps({'mystat': {
                                            'stat': 'bucket-file-download-total',
                                            'params': {
                                                'start_date': '2017-01-01',
                                                'bucket_id': file1['bucket'],
                                            }
                                        }}),
                                        headers=stats_headers)
                stats_ret_data = json.loads(
                    stats_ret.get_data(as_text=True))
                assert stats_ret_data['mystat']['buckets'][0]['value'] == 1.0
