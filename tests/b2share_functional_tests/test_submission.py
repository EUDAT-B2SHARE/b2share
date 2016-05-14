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
import os
import re
import sys
from io import BytesIO
from datetime import datetime

import pytest

from b2share.modules.communities import B2ShareCommunities, Community
from b2share.modules.communities.errors import CommunityDoesNotExistError
from b2share.modules.schemas import B2ShareSchemas, BlockSchema, \
    CommunitySchema, RootSchema
from b2share.modules.records import B2ShareRecords
from b2share.modules.records.links import http_header_link_regex, \
    RECORD_BUCKET_RELATION_TYPE
from b2share.modules.files import B2ShareFiles
from b2share.modules.schemas.errors import BlockSchemaDoesNotExistError, \
    BlockSchemaIsDeprecated, InvalidBlockSchemaError, InvalidJSONSchemaError, \
    InvalidRootSchemaError, RootSchemaDoesNotExistError
from flask import url_for
from invenio_records.api import Record
from invenio_search import current_search_client
from invenio_db import db

from b2share_demo.helpers import resolve_community_id, resolve_block_schema_id


json_headers = [('Content-Type', 'application/json'),
                ('Accept', 'application/json')]

jsonpatch_headers = [('Content-Type', 'application/json-patch+json'),
                     ('Accept', 'application/json')]


def make_record_str(title):
    record_data = {
        'owner': '',
        'title': title,
        'community': '$COMMUNITY_ID[MyTestCommunity]',
        'open_access': True,
        'creator': ['Anonymous'],
        'community_specific': {
            '$BLOCK_SCHEMA_ID[MyTestSchema]': {
                'study_design': ['Case-control']
            }
        }
    }
    record_str = json.dumps(record_data)
    record_str = resolve_community_id(record_str)
    return resolve_block_schema_id(record_str)


def make_record_patch(old_title):
    return [{
        'op': 'replace',
        'path': '/title',
        'value': old_title + " patched"
    }, {
        'op': 'replace',
        'path': '/open_access',
        'value': False
    }, {
        'op': 'add',
        'path': '/description',
        'value': "Patched record description."
    }, {
        'op': 'add',
        'path': '/embargo_date',
        'value': datetime(datetime.now().year+2, 1, 1).isoformat()
    }, {
        'op': 'remove',
        'path': '/creator'
    }]


def change_record(record_data):
    new_title = "Updated title {}".format(record_data.get('title', ''))
    from copy import deepcopy
    record_new_data = deepcopy(record_data)
    record_new_data.update({
        'title': new_title,
        'description': "An entirely updated description",
        'open_access': True,
        'embargo_date': datetime(datetime.now().year+4, 1, 1).isoformat()
    })
    if record_new_data.get('creator'):
        del record_new_data['creator']
    return record_new_data


record_list_url = (lambda **kwargs:
                   url_for('invenio_records_rest.recuuid_list',
                           **kwargs))

def test_simple_submission(app, test_communities, create_user, login_user):
    with app.app_context():
        # FIXME test permissions
        with app.test_client() as client:
            the_owner = create_user('TheOwner')
            db.session.commit()
            login_user(the_owner, client)

            records_data = [make_record_str('My New Test BBMRI record {}'.format(i))
                            for i in range(5)]

            recuuid_to_data = dict()
            recidx_to_data = dict()
            for record_idx, record_data in enumerate(records_data):
                record_create_data = _test_create_and_update_record(client, record_data, record_idx)
                recidx_to_data[record_idx] = record_create_data
                recuuid_to_data[record_create_data['id']] = record_create_data

            # Flush the indices to find the record on the next search
            current_search_client.indices.flush()

            # Test searching all records (without any query)
            record_search_res = client.get(record_list_url(),
                                           headers=json_headers)
            assert record_search_res.status_code == 200
            record_search_data = json.loads(
                record_search_res.get_data(as_text=True))
            assert record_search_data['hits']['total'] == len(records_data)
            # check that the all the records were returned by the search
            hit_ids = set()
            for hit in record_search_data['hits']['hits']:
                assert hit == recuuid_to_data[hit['id']]
                hit_ids.add(hit['id'])
            # check that the same record is not returned multiple times
            assert len(hit_ids) == len(records_data)

            # Test searching with a query
            record_search_res = client.get(record_list_url(q='new ReCoRd'),
                                           headers=json_headers)
            assert record_search_res.status_code == 200
            record_search_data = json.loads(
                record_search_res.get_data(as_text=True))
            assert record_search_data['hits']['total'] == len(records_data)
            # check that the all the records were returned by the search
            for hit in record_search_data['hits']['hits']:
                assert hit == recuuid_to_data[hit['id']]
            for rec in recidx_to_data.values():
                all_hits = record_search_data['hits']['hits']
                assert [rec] == [h for h in all_hits if h['id'] == rec['id']]


def _test_create_and_update_record(client, record_str, record_index):
    record_url, record_create_data, bucket_links = \
        _test_post_and_get_record(client, record_str)

    _test_patch_and_get_record(client, record_url, record_create_data, bucket_links)
    _test_put_and_get_record(client, record_url, record_create_data, bucket_links)
    _test_file_ops(client, bucket_links, record_index)

    record_get_res = client.get(record_url, headers=json_headers)
    assert record_get_res.status_code == 200
    return json.loads(record_get_res.get_data(as_text=True))


def _test_post_and_get_record(client, record_str):
    record_create_res = client.post(record_list_url(),
                                    data=record_str,
                                    headers=json_headers)

    assert record_create_res.status_code == 201
    record_create_data = json.loads(record_create_res.get_data(as_text=True))
    assert '_internal' not in record_create_data['metadata']

    bucket_links = get_bucket_links(record_create_res.headers)
    assert len(bucket_links) == 1

    record_url = url_for('invenio_records_rest.recuuid_item',
                         pid_value=record_create_data['id'])

    _test_get_record(client, record_url, record_create_data, bucket_links)

    return (record_url, record_create_data, bucket_links)


def get_bucket_links(headers):
    header_links = headers.get_all('Link')
    is_bucket = http_header_link_regex(RECORD_BUCKET_RELATION_TYPE)
    bucket_links_full = [hl for hl in header_links if is_bucket.search(hl)]
    return [link.split(';', 1)[0] for link in bucket_links_full]


def _test_get_record(client, record_url, record_expected_data, bucket_links):
    record_get_res = client.get(record_url, headers=json_headers)
    assert record_get_res.status_code == 200
    record_get_data = json.loads(
        record_get_res.get_data(as_text=True))
    assert '_internal' not in record_get_data['metadata']
    assert record_get_data == record_expected_data
    assert bucket_links == get_bucket_links(record_get_res.headers)


def _test_patch_and_get_record(client, record_url, record_create_data, bucket_links):
    patch = make_record_patch(record_create_data['metadata']['title'])
    record_patch_res = client.patch(record_url,
                                    data=json.dumps(patch),
                                    headers=jsonpatch_headers)
    assert record_patch_res.status_code == 200
    record_patch_data = json.loads(record_patch_res.get_data(as_text=True))
    assert '_internal' not in record_patch_data['metadata']

    from jsonpatch import apply_patch
    expected_data = apply_patch(record_create_data['metadata'], patch)
    assert record_patch_data['metadata'] == expected_data
    assert get_bucket_links(record_patch_res.headers) == bucket_links
    _test_get_record(client, record_url, record_patch_data, bucket_links)


def _test_put_and_get_record(client, record_url, record_create_data, bucket_links):
    record_new_data = change_record(record_create_data['metadata'])
    record_put_res = client.put(record_url,
                                data=json.dumps(record_new_data),
                                headers=json_headers)
    assert record_put_res.status_code == 200
    record_put_data = json.loads(record_put_res.get_data(as_text=True))
    assert '_internal' not in record_put_data['metadata']
    assert record_put_data['metadata'] == record_new_data
    assert get_bucket_links(record_put_res.headers) == bucket_links
    _test_get_record(client, record_url, record_put_data, bucket_links)


def _test_file_ops(client, bucket_links, count):
    for num in range(count):
        # Test file upload
        headers = {'Accept': '*/*'}
        object_url = '{0}/{1}'.format(bucket_links[0], 'myfile.dat')
        content = 'contents2~`!+üøåé+%20+ +\n{}'.format('word ' * num)
        file_content = bytes(content, 'utf-8')
        data = {'file': (BytesIO(file_content), 'file2~!+üøåé+%20+ +{}.dat'.format(num))}
        file_put_res = client.put(object_url,
                                  data=data,
                                  headers=headers)
        assert file_put_res.status_code == 200
        file_put_metadata = json.loads(
            file_put_res.get_data(as_text=True))
        assert file_put_metadata['size'] == len(file_content)

        # Test file GET
        file_get_res = client.get(object_url,
                                  headers=headers)
        assert file_get_res.status_code == 200
        file_get_data = file_get_res.get_data()
        assert file_get_data == file_content
