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

"""Test Communities module's REST API."""

from __future__ import absolute_import

import json
import uuid

import pytest
from flask import url_for
from invenio_db import db
from mock import patch
from b2share.modules.schemas.api import CommunitySchema, BlockSchema, \
    BlockSchemaVersion
from b2share.modules.communities.api import Community
from tests.b2share_unit_tests.helpers import subtest_self_link
from tests.b2share_unit_tests.schemas.data import block_schemas_json_schemas


def test_valid_get_community_schema(app, test_communities):
    """Test VALID community get request (GET .../communities/<id>)."""
    with app.app_context():
        community_id = str(test_communities['MyTestCommunity1'])
        with app.test_client() as client:
            for version in [0, 1, 'last']:
                headers = [('Content-Type', 'application/json'),
                           ('Accept', 'application/json')]
                res = client.get(
                    url_for('b2share_schemas.community_schema_item',
                            community_id=community_id,
                            schema_version_nb=version),
                    headers=headers)
                assert res.status_code == 200
                # check that the returned community matches the given data
                response_data = json.loads(res.get_data(as_text=True))
                if isinstance(version, int):
                    expected = CommunitySchema.get_community_schema(
                        community_id, version)
                elif version == 'last':
                    expected = CommunitySchema.get_community_schema(
                        community_id)
                else:
                    raise NotImplementedError('Test not implemented')
                assert (expected.build_json_schema() ==
                        response_data['json_schema'])
                assert response_data['community'] == community_id
                assert response_data['version'] == expected.version

    with app.app_context():
        with app.test_client() as client:
            # check that the returned self link returns the same data
            subtest_self_link(response_data, res.headers, client)

# FIXME: Test is disabled for V2 as it is not used by the UI
# def test_create_block_schema(app, test_communities):
#     """Test creating a new schema."""
#     with app.app_context():
#         community_id = str(test_communities['MyTestCommunity1'])
#         with app.test_client() as client:
#             headers = [('Content-Type', 'application/json'),
#                        ('Accept', 'application/json')]
#             res = client.post(
#                 url_for(
#                     'b2share_schemas.block_schema_list'
#                 ),
#                 data=json.dumps({
#                     'name': 'abc',
#                     'community_id': community_id,
#                 }),
#                 headers=headers)
#             assert res.status_code == 201
#             response_data = json.loads(res.get_data(as_text=True))
#             assert response_data['name'] == BlockSchema.get_block_schema(
#                                                 response_data['schema_id']
#                                             ).name
#             assert str(
#                 BlockSchema.get_block_schema(response_data['schema_id'])
#                     .community
#             ) == community_id


# FIXME: Test is disabled for V2 as it is not used by the UI
# def test_create_block_schema_version(app, test_communities):
#     """Test creating a new version of the schema."""
#     with app.app_context():
#         community_id = str(test_communities['MyTestCommunity1'])
#         json_schema = block_schemas_json_schemas[0][0]
#         block_schema = BlockSchema.create_block_schema(community_id, 'abc')
#         with app.test_client() as client:
#             headers = [('Content-Type', 'application/json'),
#                        ('Accept', 'application/json')]
#             res = client.put(
#                 url_for(
#                     'b2share_schemas.block_schema_versions_item',
#                     schema_id=str(block_schema.id),
#                     schema_version_nb=0
#                 ),
#                 data=json.dumps({
#                     'json_schema': json_schema
#                 }),
#                 headers=headers)
#             assert res.status_code == 201
#             response_data = json.loads(res.get_data(as_text=True))
#             assert response_data['json_schema'] == json_schema


# FIXME: Test is disabled for V2 as it is not used by the UI
# def test_create_existing_block_schema_version(app, test_communities):
#     """Test creating an axisting version of the schema."""
#     with app.app_context():
#         community_id = str(test_communities['MyTestCommunity1'])
#         json_schema = block_schemas_json_schemas[0][0]
#         block_schema = BlockSchema.create_block_schema(community_id, 'abc')
#         all_versions = block_schema.versions
#         with app.test_client() as client:
#             headers = [('Content-Type', 'application/json'),
#                        ('Accept', 'application/json')]
#             res = client.put(
#                 url_for(
#                     'b2share_schemas.block_schema_versions_item',
#                     schema_id=str(block_schema.id),
#                     schema_version_nb=len(all_versions) - 1
#                 ),
#                 data=json.dumps({
#                     'json_schema': json_schema
#                 }),
#                 headers=headers)
#             assert res.status_code == 409


# FIXME: Test is disabled for V2 as it is not used by the UI
# def test_create_invalid_block_schema_version(app, test_communities):
#     """Test creating an invalid version of the schema."""
#     with app.app_context():
#         community_id = str(test_communities['MyTestCommunity1'])
#         json_schema = {"$schema": "http://json-schema.org/draft-04/schema#"}
#         block_schema = BlockSchema.create_block_schema(community_id, 'abc')
#         with app.test_client() as client:
#             headers = [('Content-Type', 'application/json'),
#                        ('Accept', 'application/json')]
#             res = client.put(
#                 url_for(
#                     'b2share_schemas.block_schema_versions_item',
#                     schema_id=str(block_schema.id),
#                     schema_version_nb=5
#                 ),
#                 data=json.dumps({
#                     'json_schema': json_schema
#                 }),
#                 headers=headers)
#             assert res.status_code == 400


def test_get_block_schema_version(app, test_communities):
    """Test getting schema version."""
    with app.app_context():
        community_id = str(test_communities['MyTestCommunity1'])
        json_schema = block_schemas_json_schemas[0][0]
        block_schema = BlockSchema.create_block_schema(community_id, 'abc')
        schema_version1 = block_schema.create_version(json_schema)
        schema_version2 = block_schema.create_version(json_schema)

        with app.test_client() as client:
            headers = [('Content-Type', 'application/json'),
                       ('Accept', 'application/json')]
            res = client.get(
                url_for(
                    'b2share_schemas.block_schema_versions_item',
                    schema_id=str(block_schema.id),
                    schema_version_nb=1,
                ),
                headers=headers)
            assert res.status_code == 200

        with app.test_client() as client:
            headers = [('Content-Type', 'application/json'),
                       ('Accept', 'application/json')]
            res = client.get(
                url_for(
                    'b2share_schemas.block_schema_versions_item',
                    schema_id=str(block_schema.id),
                    schema_version_nb='last',
                ),
                headers=headers)
            assert res.status_code == 200


def test_get_block_schemas(app, test_communities):
    """"Test getting list of given community's schemas."""
    with app.app_context():
        community = Community.create_community('name1', 'desc1')
        community_id = community.id
        community_2 = Community.create_community('name2', 'desc2')
        community_id2 = community_2.id
        block_schema_1 = BlockSchema.create_block_schema(community_id, 'abc')
        block_schema_2 = BlockSchema.create_block_schema(community_id2, 'abc2')
        block_schema_3 = BlockSchema.create_block_schema(community_id2, 'abc3')
        with app.test_client() as client:
            headers = [('Content-Type', 'application/json'),
                       ('Accept', 'application/json')]
            res = client.get(
                url_for(
                    'b2share_schemas.block_schema_list',
                    community_id=community_id2
                ),
                headers=headers)
            assert res.status_code == 200
            response_data = json.loads(res.get_data(as_text=True))
            assert isinstance(response_data['schemas'], list)
            assert len(response_data['schemas']) == 2
            assert response_data['schemas'][0]['name'] == block_schema_2.name
            assert response_data['schemas'][1]['name'] == block_schema_3.name


# FIXME: Test is disabled for V2 as it is not used by the UI
# def test_updating_block_schema(app, test_communities):
#     """Test updating a block schema."""
#     with app.app_context():
#         community = Community.create_community('name1', 'desc1')
#         community_id = community.id
#         block_schema = BlockSchema.create_block_schema(community_id, 'original')
#         with app.test_client() as client:
#             headers = [('Content-Type', 'application/json'),
#                        ('Accept', 'application/json')]
#             res = client.patch(
#                 url_for(
#                     'b2share_schemas.block_schema_item',
#                     schema_id=block_schema.id
#                 ),
#                 data=json.dumps({
#                     'name': 'abc'
#                 }),
#                 headers=headers)
#             assert res.status_code == 200
