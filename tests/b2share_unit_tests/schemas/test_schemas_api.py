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

"""Test B2Share schemas module's API."""

import json
import uuid
from collections import namedtuple

import jsonschema
import pytest
from flask import url_for
from invenio_db import db
from jsonpatch import JsonPatchConflict

from b2share.modules.communities import B2ShareCommunities, Community
from b2share.modules.communities.errors import CommunityDoesNotExistError
from b2share.modules.schemas import B2ShareSchemas, BlockSchema, \
    CommunitySchema, RootSchema
from b2share.modules.schemas.errors import BlockSchemaDoesNotExistError, \
    BlockSchemaIsDeprecated, InvalidBlockSchemaError, InvalidJSONSchemaError, \
    InvalidRootSchemaError, RootSchemaDoesNotExistError, \
    InvalidSchemaVersionError, SchemaVersionExistsError
from b2share.modules.schemas.models import CommunitySchemaVersion
from b2share_unit_tests.communities.helpers import community_metadata
from b2share_unit_tests.schemas.data import (
    communities_metadata, root_schemas_json_schemas,
    block_schemas_json_schemas)

@pytest.mark.parametrize('app', [({'extensions':
                                   [B2ShareCommunities, B2ShareSchemas]})],
                         indirect=['app'])
def test_root_schema(app):
    """Test valid usage of the RootSchema API."""
    with app.app_context():
        version = 0
        for json_schema in root_schemas_json_schemas:
            RootSchema.create_new_version(
                version=version,
                json_schema=json_schema,
            )
            version += 1
        db.session.commit()

    with app.app_context():
        version = 0
        for json_schema in root_schemas_json_schemas:
            root_schema = RootSchema.get_root_schema(version)
            assert root_schema.version == version
            assert json.loads(root_schema.json_schema) == json_schema
            version += 1


@pytest.mark.parametrize('app', [({'extensions':
                                   [B2ShareCommunities, B2ShareSchemas]})],
                         indirect=['app'])
def test_root_schema_errors(app):
    """Test invalid usage of the RootSchema API."""
    with app.app_context():
        # creating first root schema with a version != 0 should fail
        with pytest.raises(InvalidRootSchemaError):
            RootSchema.create_new_version(
                version=42,
                json_schema=root_schemas_json_schemas[0],
            )
        # test creating a root schema with a negative version when no schema
        # exist
        with pytest.raises(InvalidRootSchemaError):
            RootSchema.create_new_version(
                version=-1,
                json_schema=root_schemas_json_schemas[0],
            )
        # test skipping a version when creating a root schema
        RootSchema.create_new_version(
            version=0,
            json_schema=root_schemas_json_schemas[0],
        )
        with pytest.raises(InvalidRootSchemaError):
            RootSchema.create_new_version(
                version=2,
                json_schema=root_schemas_json_schemas[0],
            )
        # test creating a root schema with a negative version when one schema
        # exists
        with pytest.raises(InvalidRootSchemaError):
            RootSchema.create_new_version(
                version=-1,
                json_schema=root_schemas_json_schemas[0],
            )
        # test creating a root schema with an already used version
        with pytest.raises(InvalidRootSchemaError):
            RootSchema.create_new_version(
                version=0,
                json_schema=root_schemas_json_schemas[0],
            )
        # test creating a root schema with no JSON Schema
        with pytest.raises(InvalidJSONSchemaError):
            RootSchema.create_new_version(
                version=1,
                json_schema=None,
            )
        with pytest.raises(InvalidJSONSchemaError):
            RootSchema.create_new_version(
                version=1,
                json_schema={},
            )
        with pytest.raises(InvalidJSONSchemaError):
            RootSchema.create_new_version(
                version=1,
                json_schema={'$schema': 'invalid-url'},
            )
        with pytest.raises(InvalidJSONSchemaError):
            RootSchema.create_new_version(
                version=1,
                json_schema={'$schema': 'http://examples.com'},
            )
        # try getting a non existing root schema
        with pytest.raises(RootSchemaDoesNotExistError):
            RootSchema.get_root_schema(42)


@pytest.mark.parametrize('app', [({'extensions':
                                   [B2ShareCommunities, B2ShareSchemas]})],
                         indirect=['app'])
def test_block_schemas(app):
    """Test valid usage of the BlockSchema API."""
    with app.app_context():
        new_community = Community.create_community(**communities_metadata[0])
        new_community_id = new_community.id
        db.session.commit()

        block_schema_name = "schema 1"
        block_schema_1 = BlockSchema.create_block_schema(
            community_id=new_community.id, name=block_schema_name
        )
        block_schema_1_id = block_schema_1.id
        db.session.commit()

    with app.app_context():
        retrieved_block_schema = BlockSchema.get_block_schema(
            block_schema_1_id)
        assert retrieved_block_schema.name == block_schema_name
        assert retrieved_block_schema.community == new_community_id
        # test changing the community maintaining the block schema
        new_community_2 = Community.create_community(**communities_metadata[1])
        retrieved_block_schema.community = new_community_2.id
        assert retrieved_block_schema.community == new_community_2.id
        # test setting the schema name
        retrieved_block_schema.name = new_name = 'new name'
        assert retrieved_block_schema.name == new_name


@pytest.mark.parametrize('app', [({'extensions':
                                   [B2ShareCommunities, B2ShareSchemas]})],
                         indirect=['app'])
def test_block_schema_errors(app):
    """Test invalid usage of the BlockSchema API."""
    with app.app_context():
        unknown_uuid = uuid.uuid4()
        # test with an invalid community ID
        with pytest.raises(InvalidBlockSchemaError):
            BlockSchema.create_block_schema(community_id=unknown_uuid,
                                            name='test')
        new_community = Community.create_community(**communities_metadata[0])
        db.session.commit()
        # test with name == None
        with pytest.raises(InvalidBlockSchemaError):
            BlockSchema.create_block_schema(community_id=new_community.id,
                                            name=None)
        # test with len(name) too short
        with pytest.raises(InvalidBlockSchemaError):
            BlockSchema.create_block_schema(community_id=new_community.id,
                                            name='t')
        # test with len(name) too long
        with pytest.raises(InvalidBlockSchemaError):
            BlockSchema.create_block_schema(community_id=new_community.id,
                                            name='t'*500)
        # test getting non existing block schema
        with pytest.raises(BlockSchemaDoesNotExistError):
            BlockSchema.get_block_schema(unknown_uuid)

        block_schema = BlockSchema.create_block_schema(
            community_id=new_community.id, name='test'
        )
        # test setting the community to an unknown uuid
        with pytest.raises(CommunityDoesNotExistError):
            block_schema.community = unknown_uuid
        assert block_schema.community == new_community.id

        # test setting the name to None
        with pytest.raises(InvalidBlockSchemaError):
            block_schema.name = None
        # test setting the name to a too short string
        with pytest.raises(InvalidBlockSchemaError):
            block_schema.name = 't'
        # test setting the name to a too long string
        with pytest.raises(InvalidBlockSchemaError):
            block_schema.name = 't'*500
            db.session.commit()


@pytest.mark.parametrize('app', [({'extensions':
                                   [B2ShareCommunities, B2ShareSchemas]})],
                         indirect=['app'])
def test_block_schemas_versions(app):
    """Test valid usage of the BlockSchemaVersion API."""
    with app.app_context():
        new_community = Community.create_community(**communities_metadata[0])
        db.session.commit()

        block_schema_name = "schema 1"
        block_schema_1 = BlockSchema.create_block_schema(
            community_id=new_community.id, name=block_schema_name
        )

        # test the versions iterator with no versions created
        assert len(block_schema_1.versions) == 0
        for version in block_schema_1.versions:
            pytest.fail('No versions have been added yet.')

        # create the versions
        for json_schema in block_schemas_json_schemas[0]:
            block_schema_1.create_version(
                json_schema=json_schema,
            )
        block_schema_1_id = block_schema_1.id
        db.session.commit()

    with app.app_context():
        retrieved_block_schema = BlockSchema.get_block_schema(
            block_schema_1_id)
        all_versions = retrieved_block_schema.versions
        assert len(all_versions) == 2

        expected_version = 0
        for version in all_versions:
            # retrieving by version number should return the same
            # BlockSchemaVersion
            retrieved_version = all_versions[expected_version]
            assert json.loads(version.json_schema) == \
                json.loads(retrieved_version.json_schema) == \
                block_schemas_json_schemas[0][version.version]
            # test sorting
            assert version.version == retrieved_version.version == \
                expected_version
            # test __contains__
            assert expected_version in all_versions
            expected_version += 1
        # check access for not existing version
        assert len(block_schemas_json_schemas[0]) not in all_versions
        with pytest.raises(IndexError):
            all_versions[len(block_schemas_json_schemas[0])]

    with app.app_context():
        retrieved_block_schema = BlockSchema.get_block_schema(
            block_schema_1_id)
        all_versions = retrieved_block_schema.versions
        assert len(all_versions) == 2

        retrieved_block_schema.create_version(
            block_schemas_json_schemas[0][0],
            len(all_versions)
        )

        with pytest.raises(SchemaVersionExistsError):
            retrieved_block_schema.create_version(
                block_schemas_json_schemas[0][0],
                1
            )


@pytest.mark.parametrize('app', [({'extensions':
                                   [B2ShareCommunities, B2ShareSchemas]})],
                         indirect=['app'])
def test_block_schema_version_errors(app):
    """Test invalid usage of the BlockSchemaVersion API."""
    with app.app_context():
        new_community = Community.create_community(**communities_metadata[0])
        block_schema = BlockSchema.create_block_schema(
            community_id=new_community.id, name='test'
        )
        db.session.commit()

        # test create block schema version with json_schema == None
        with pytest.raises(InvalidJSONSchemaError):
            block_schema.create_version(None)
        # test invalid $schema URLs
        with pytest.raises(InvalidJSONSchemaError):
            block_schema.create_version({})
        with pytest.raises(InvalidJSONSchemaError):
            block_schema.create_version({'$schema': 'invalid-url'})
        with pytest.raises(InvalidJSONSchemaError):
            block_schema.create_version({'$schema': 'http://examples.com'})

        block_schema.deprecated = True
        # test adding a version to a deprecated schema
        with pytest.raises(BlockSchemaIsDeprecated):
            block_schema.create_version(block_schemas_json_schemas[0][0])

        # try accessing a non existing version
        with pytest.raises(IndexError):
            block_schema.versions[0]

        assert len(block_schema.versions) == 0


@pytest.mark.parametrize('app', [({'extensions':
                                   [B2ShareCommunities, B2ShareSchemas]})],
                         indirect=['app'])
def test_community_schema(app, flask_http_responses, test_communities):
    """Test valid usage of the CommunitySchema API."""
    with app.app_context():
        new_community = Community.create_community(**communities_metadata[0])

        db.session.commit()

        BlockSchemaRef = namedtuple('BlockSchemaRef', [
            'block_schema',
            'versions'
        ])
        BlockSchemaVersionRef = namedtuple('BlockSchemaVersionRef', [
            'version',
            'url'
        ])

        # create root schemas
        root_schemas = [
            RootSchema.create_new_version(
                version=version+1,
                json_schema=root_schemas_json_schemas[version],
            ) for version in range(len(root_schemas_json_schemas))
        ]
        # create block schemas
        block_schemas = []
        for block_index in range(len(block_schemas_json_schemas)):
            block_schema = BlockSchema.create_block_schema(
                community_id=new_community.id,
                name="schema {}".format(block_index)
            )
            block_schemas.append(
                BlockSchemaRef(block_schema=block_schema, versions=[
                    BlockSchemaVersionRef(
                        version=block_schema.create_version(
                            json_schema=block_schemas_json_schemas[
                                block_index][version],
                        ),
                        url=url_for(
                            'b2share_schemas.block_schema_versions_item',
                            schema_id=block_schema.id,
                            schema_version_nb=version,
                            _external=True,
                        ))
                    for version in
                    range(len(block_schemas_json_schemas[block_index]))
                ])
            )
        community_schemas = []
        # create a community schema
        community_schema_v1_json_schema = {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'properties': {
                str(block_schemas[0].block_schema.id): {
                    '$ref':  "{}#/json_schema".format(
                        block_schemas[0].versions[0].url),
                },
                str(block_schemas[1].block_schema.id): {
                    '$ref':  "{}#/json_schema".format(
                        block_schemas[1].versions[0].url),
                },
            },
            'additionalProperties': False,
        }
        community_schemas.append(CommunitySchema.create_version(
            community_id=new_community.id,
            root_schema_version=root_schemas[0].version,
            community_schema=community_schema_v1_json_schema
        ))

        # test with another block schema version
        community_schema_v2_json_schema = {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'properties': {
                str(block_schemas[0].block_schema.id): {
                    '$ref':  "{}#/json_schema".format(
                        block_schemas[0].versions[1].url),
                },
                str(block_schemas[1].block_schema.id): {
                    '$ref':  "{}#/json_schema".format(
                        block_schemas[1].versions[0].url),
                },
            },
            'additionalProperties': False,
        }
        community_schemas.append(CommunitySchema.create_version(
            community_id=new_community.id,
            root_schema_version=root_schemas[0].version,
            community_schema=community_schema_v2_json_schema
        ))

        # test with another root schema
        community_schemas.append(CommunitySchema.create_version(
            community_id=new_community.id,
            root_schema_version=root_schemas[1].version,
            community_schema=community_schema_v2_json_schema
        ))

        db.session.commit()

        # test invalid schema numbers
        last_schema = CommunitySchemaVersion.query.filter(
                        CommunitySchemaVersion.community == new_community.id
                    ).order_by(
                        CommunitySchemaVersion.version.desc()
                    ).limit(1).one()

        with pytest.raises(SchemaVersionExistsError):
            CommunitySchema.create_version(
                community_id=new_community.id,
                root_schema_version=root_schemas[0].version,
                community_schema=community_schema_v2_json_schema,
                version_number=last_schema.version,
            )
        with pytest.raises(InvalidSchemaVersionError):
            CommunitySchema.create_version(
                community_id=new_community.id,
                root_schema_version=root_schemas[0].version,
                community_schema=community_schema_v2_json_schema,
                version_number=last_schema.version + 2,
            )

        # create a metadata block matching each community schema
        metadatas = [
            {
                'authors': ['C. Arthur', 'D. Albert'],
                'community_specific': {
                    str(block_schemas[0].block_schema.id): {
                        'experiment_nb': 42,
                    },
                    str(block_schemas[1].block_schema.id): {
                        'analysis_result': 'success',
                    },
                }
            },
            {
                'authors': ['C. Arthur', 'D. Albert'],
                'community_specific': {
                    str(block_schemas[0].block_schema.id): {
                        'experiment_nb': 42,
                        'experiment_date': '4242'
                    }
                }
            },
            {
                'authors': ['C. Arthur', 'D. Albert'],
                'files': ['/path/to/the/file.txt'],
                'community_specific': {
                    str(block_schemas[0].block_schema.id): {
                        'experiment_nb': 42,
                        'experiment_date': '4242'
                    }
                }
            }
        ]

        validation_schemas = [schema.build_json_schema()
                              for schema in community_schemas]
        for index in range(len(community_schemas)):
            with flask_http_responses():
                # check that the community schema validates the corresponding
                # JSON metadata
                jsonschema.validate(metadatas[index],
                                    validation_schemas[index])
                for index2 in range(len(community_schemas)):
                    if index != index2:
                        with pytest.raises(
                                jsonschema.exceptions.ValidationError):
                            # check that the community schema does not validate
                            # the others JSON metadata
                            jsonschema.validate(metadatas[index2],
                                                validation_schemas[index])

        # getting all schemas
        schemas = CommunitySchema.get_all_community_schemas()
        assert len(schemas) == CommunitySchemaVersion.query.count()


def test_patch(app):
    """Test BlockSchema.patch()."""
    with app.app_context():
        created_community = Community.create_community(**community_metadata)
        block_schema = BlockSchema.create_block_schema(
            created_community.id,
            'abc'
        )
        block_schema_id = block_schema.id
        db.session.commit()

        retrieved = BlockSchema.get_block_schema(block_schema_id)
        retrieved.patch(
            [{'op': 'replace', 'path': '/name', 'value': 'patched'}]
        )
        db.session.commit()

    with app.app_context():
        patched = BlockSchema.get_block_schema(block_schema_id)
        assert block_schema_id == patched.id
        assert getattr(patched, 'name') == 'patched'

        with pytest.raises(JsonPatchConflict):
            patched.patch(
                [{'op': 'replace', 'path': '/non_exist_name', 'value': None}]
            )
        assert getattr(patched, 'name') == 'patched'


def test_update(app):
    """Test BlockSchema.update()."""
    with app.app_context():
        created_community = Community.create_community(**community_metadata)
        block_schema = BlockSchema.create_block_schema(
            created_community.id,
            'abc'
        )
        block_schema_id = block_schema.id
        db.session.commit()

    with app.app_context():
        retrieved = BlockSchema.get_block_schema(block_schema_id)
        retrieved.update({'name': 'updated'})
        db.session.commit()

    with app.app_context():
        updated = BlockSchema.get_block_schema(block_schema_id)
        assert block_schema_id == updated.id
        assert getattr(updated, 'name') == 'updated'

        with pytest.raises(InvalidBlockSchemaError):
            updated.update({'name': None})
        assert getattr(updated, 'name') == 'updated'
