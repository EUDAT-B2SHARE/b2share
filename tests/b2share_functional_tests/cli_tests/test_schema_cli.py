# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2017 SurfSara, University of Tübingen
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

"""Test B2Share schema cli module."""
from __future__ import absolute_import, print_function

import os
import json
import pytest
from click.testing import CliRunner
from flask.cli import ScriptInfo
from flask import url_for

from invenio_db import db
from invenio_files_rest.models import Location

from b2share.modules.communities.api import Community
from b2share.modules.communities.cli import communities as communities_cmd
from b2share.modules.schemas.api import CommunitySchema
from b2share.modules.schemas.cli import (schemas as schemas_cmd,
                                         update_or_set_community_schema)
from b2share.modules.schemas.errors import RootSchemaDoesNotExistError
from tests.b2share_unit_tests.helpers import create_user

test_schema = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "Test Schema",
    "description": "This is the blueprint of the metadata block specific for a unit test community",
    "properties": {
        "test_field1": {
            "description": "The first field in this schema",
            "title": "Field nr 1",
            "type": "string",
        },
        "test_field2": {
            "description": "The second field in this schema",
            "title": "Field nr 2",
            "type": "integer",
        }
    },
    "type": "object",
    "additionalProperties": False,
    "required": ["test_field1"]
}

def test_existing_community_set_schema_cmd(app, test_communities):
    """Test the `schemas set_schema` CLI command."""
    with app.app_context():
        runner = CliRunner()
        script_info = ScriptInfo(create_app=lambda info: app)
        comm_name = test_communities.popitem()[0]
        with runner.isolated_filesystem():
            with open("schema.json", "w") as f:
                f.write(json.dumps(test_schema))

            # Run 'set schema' command
            args = ['set_schema', comm_name, 'schema.json']
            result = runner.invoke(communities_cmd, args, obj=script_info)
            if result.exit_code != 0:
                print(result.output)
            assert result.exit_code == 0

            # Run 'set schema' command again
            with open("schema.json", "w") as f:
                f.write(json.dumps(test_schema))
            args = ['set_schema', comm_name, 'schema.json']
            result = runner.invoke(communities_cmd, args, obj=script_info)
            assert result.exit_code == 0


def test_new_community_set_schema_cmd(app, login_user, tmp_location):
    """Test adding a community and setting its schema using CLI commands."""
    with app.app_context():
        tmp_location.default = True
        db.session.merge(tmp_location)
        db.session.commit()

        runner = CliRunner()
        script_info = ScriptInfo(create_app=lambda info: app)
        comm_name = 'MyCom'

        # Create a new community on the command line
        args = ['create', comm_name, 'MyCom description', 'eudat.png']
        result = runner.invoke(communities_cmd, args, obj=script_info)
        assert result.exit_code == 0
        community = Community.get(name=comm_name)
        assert community
        assert community.name == comm_name

        # Create a schema for this new community
        with runner.isolated_filesystem():
            with open("schema.json", "w") as f:
                f.write(json.dumps(test_schema))

            # check RootSchemaDoesNotExistError
            with pytest.raises(RootSchemaDoesNotExistError):
                update_or_set_community_schema(comm_name, 'schema.json')

            # check RootSchemaDoesNotExistError via cli
            args = ['set_schema', comm_name, 'schema.json']
            result = runner.invoke(communities_cmd, args, obj=script_info)
            assert result.exit_code != 0

            # initialize the root schema in the test environment
            result = runner.invoke(schemas_cmd, ['init'], obj=script_info)
            assert result.exit_code == 0

            # Make custom schema via cli
            args = ['set_schema', comm_name, 'schema.json']
            result = runner.invoke(communities_cmd, args, obj=script_info)
            assert result.exit_code == 0

        community_name = 'MyCom'
        community = Community.get(name=community_name)

        # Get the block schema id
        community_schema = CommunitySchema.get_community_schema(
            community.id).community_schema
        props = json.loads(community_schema).get('properties')
        assert len(props) == 1
        block_schema_id = props.popitem()[0]

        # Test the community schema by publishing a record
        with app.test_client() as client:
            user = create_user('allowed')
            login_user(user, client)

            record_data = {
                'titles': [{'title':'My Test Record'}],
                'community': str(community.id),
                'open_access': True,
                'community_specific': {
                    block_schema_id: {
                        'test_field1': "string value",
                        'test_field2': 10,
                    }
                },
            }

            headers = [('Content-Type', 'application/json'),
                       ('Accept', 'application/json')]
            draft_res = client.post(url_for('b2share_records_rest.b2rec_list'),
                                    data=json.dumps(record_data),
                                    headers=headers)
            draft_data = json.loads(draft_res.get_data(as_text=True))
            assert draft_res.status_code == 201

            headers = [('Content-Type', 'application/json-patch+json'),
                       ('Accept', 'application/json')]
            draft_submit_res = client.patch(
                url_for('b2share_deposit_rest.b2dep_item',
                        pid_value=draft_data['id']),
                data=json.dumps([{
                    "op": "replace",
                    "path": "/publication_state",
                    "value": "submitted",
                }]),
                headers=headers)
            assert draft_submit_res.status_code == 200

def test_schemas_group(app, test_communities):
    """Test the `schemas` CLI command group."""
    with app.app_context():
        runner = CliRunner()
        script_info = ScriptInfo(create_app=lambda info: app)
        # Run 'schemas' command
        result = runner.invoke(schemas_cmd, [], obj=script_info)
        assert result.exit_code == 0

def test_block_schema_list(app):
    """Test the b2share schemas block_schema_list command"""
    with app.app_context():
        runner = CliRunner()
        script_info = ScriptInfo(create_app=lambda info: app)
        # Run 'schemas' command
        result = runner.invoke(schemas_cmd, ["block_schema_list"], obj=script_info)
        assert result.exit_code == 0
        test_string = result.output[len(result.output)-10:len(result.output)-1]
        assert test_string == '#VERSIONS' #no block schemas present empty header

def test_create_block_schema(app, test_communities):
    """Test creation of a block schema"""
    #happy flow
    with app.app_context():
        runner = CliRunner()
        script_info = ScriptInfo(create_app=lambda info: app)
        result = runner.invoke(schemas_cmd, [
                'block_schema_add',
                'cccccccc-1111-1111-1111-111111111111',
                'Block Schema Name'],
            obj=script_info)
        assert result.exit_code == 0
        result = runner.invoke(schemas_cmd, [
                'block_schema_list'
            ],
            obj=script_info)
        # search only for "Block Schema Na", as the rest of the string is cut
        # by the pretty printer (multiple columns)
        assert(result.output.find("Block Schema Na") > 0)