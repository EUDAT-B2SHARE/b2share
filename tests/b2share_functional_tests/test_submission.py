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

import pytest
from b2share.modules.communities import B2ShareCommunities, Community
from b2share.modules.communities.errors import CommunityDoesNotExistError
from b2share.modules.schemas import B2ShareSchemas, BlockSchema, \
    CommunitySchema, RootSchema
from b2share.modules.schemas.helpers import load_root_schemas
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

from b2share_demo.helpers import resolve_community_id, resolve_block_schema_id

records_data=[{
    'title': 'My Test BBMRI Record',
    'community': '$COMMUNITY_ID[MyTestCommunity]',
    "open_access": True,
    'community_specific': {
        '$BLOCK_SCHEMA_ID[MyTestSchema]': {
            'study_design': ['Case-control']
        }
    }
}, {
    'title': 'New BBMRI dataset',
    'community': '$COMMUNITY_ID[MyTestCommunity]',
    "open_access": True,
    'community_specific': {
        '$BLOCK_SCHEMA_ID[MyTestSchema]': {
            'study_design': ['Case-control']
        }
    }
}]

def test_simple_submission(app, test_communities):
    with app.app_context():
        # FIXME test permissions
        with app.test_client() as client:
            record_idx = 0
            recuuid_to_data = dict()
            recidx_to_data = dict()
            for record_data in records_data:
                # Test record creation
                headers = [('Content-Type', 'application/json'),
                        ('Accept', 'application/json')]
                record_str = json.dumps(record_data)
                record_str = resolve_community_id(record_str)
                record_str = resolve_block_schema_id(record_str)
                # record_list_url = url_for('invenio_records_rest.recuuid_list')
                record_list_url = (lambda **kwargs:
                                   url_for('invenio_records_rest.recuuid_list',
                                           **kwargs))
                record_create_res = client.post(record_list_url(),
                                                data=record_str,
                                                headers=headers)
                # import ipdb
                # ipdb.set_trace()
                assert record_create_res.status_code == 201
                record_create_data = json.loads(
                    record_create_res.get_data(as_text=True))
                # check that the '_internal' field has been removed
                assert '_internal' not in record_create_data['metadata']
                # check bucket link
                header_links = record_create_res.headers.get_all('Link')
                is_bucket = http_header_link_regex(RECORD_BUCKET_RELATION_TYPE)
                bucket_links = [link.split(';', 1)[0] for link in filter(
                    lambda i: is_bucket.search(i), header_links)]
                assert len(bucket_links) == 1
                recuuid_to_data[record_create_data['id']] = record_create_data
                recidx_to_data[record_idx] = record_create_data
                record_idx += 1

                # Test record GET
                record_get_res = client.get(
                    url_for('invenio_records_rest.recuuid_item',
                            pid_value=record_create_data['id']),
                    headers=headers)
                assert record_get_res.status_code == 200
                record_get_data = json.loads(
                    record_get_res.get_data(as_text=True))
                assert record_get_data == record_create_data

            # Flush the indices to find the record on the next search
            current_search_client.indices.flush()
            # Test searching all records (without any query)
            record_search_res = client.get(record_list_url(),
                                           headers=headers)
            assert record_search_res.status_code == 200
            record_search_data = json.loads(
                record_search_res.get_data(as_text=True))
            assert record_search_data['hits']['total'] == 2
            # check that the all the records where returned by the search
            hit_ids = set()
            for hit in record_search_data['hits']['hits']:
                assert hit == recuuid_to_data[hit['id']]
                hit_ids.add(hit['id'])
            # check that the same record is not returned multiple times
            assert len(hit_ids) == 2

            # Test searching with a query
            record_search_res = client.get(record_list_url(q='new dataset'),
                                           headers=headers)
            assert record_search_res.status_code == 200
            record_search_data = json.loads(
                record_search_res.get_data(as_text=True))
            assert record_search_data['hits']['total'] == 1
            # check that the all the records where returned by the search
            hit = record_search_data['hits']['hits'][0]
            assert hit == recidx_to_data[1]
            assert hit == recuuid_to_data[hit['id']]

            # Test file upload
            headers = {'Accept': '*/*'}
            object_url = '{0}/{1}'.format(bucket_links[0], 'myfile.dat')
            file_content = b'contents2'
            data = {'file': (BytesIO(file_content), 'file.dat')}
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
