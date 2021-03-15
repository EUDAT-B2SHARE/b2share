# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2016 University of Tuebingen, CERN.
# Copyright (C) 2015 University of Tuebingen.
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

"""B2Share Schemas module Command Line Interface."""

from __future__ import absolute_import

import json
import os
from uuid import UUID
import click
from flask.cli import with_appcontext

from flask import current_app
from invenio_db import db
from urllib.parse import urlunsplit

from .errors import CommunitySchemaDoesNotExistError
from .errors import RootSchemaAlreadyExistsError, BlockSchemaDoesNotExistError
from .helpers import load_root_schemas
from .validate import validate_metadata_schema
from .api import BlockSchema, CommunitySchema
from .serializers import block_schema_version_json_schema_link

from b2share.modules.communities.api import Community


@click.group()
def schemas():
    """Schemas management commands."""


@schemas.command()
@with_appcontext
@click.option('-v', '--verbose', is_flag=True, default=False)
@click.option('-f', '--force', is_flag=True, default=False)
def init(verbose, force):
    """CLI command loading Root Schema files in the database."""
    try:
        load_root_schemas(cli=True, verbose=verbose, force=force)
        db.session.commit()
    except RootSchemaAlreadyExistsError as e:
        raise click.ClickException(str(e))


@schemas.command()
@with_appcontext
@click.option('-v', '--verbose', is_flag=True, default=False)
@click.argument('community')
@click.argument('name')
def block_schema_add(verbose, community, name):
    """Adds a block schema to the database. Community is the ID or NAME of the
    maintaining community for this block schema. Name is the name as displayed
    in block_schema_list command."""

    from b2share.modules.communities.helpers import get_community_by_name_or_id

    if verbose:
        click.secho("""Creating block schema with name %s to be maintained by
        community %s""" % (name, community))
    comm = get_community_by_name_or_id(community)
    if not comm:
        raise click.BadParameter("There is no community by this name or ID: %s"
                                 % community)
    if len(name) > 255:
        raise click.BadParameter("""NAME parameter is longer than the 255
        character maximum""")
    block_schema = BlockSchema.create_block_schema(comm.id, name)
    db.session.commit()
    if verbose:
        click.secho("Created block schema with name %s and id %s" %
                    (name, block_schema.id))


@schemas.command()
@with_appcontext
@click.option('-v', '--verbose', is_flag=True, default=False)
@click.option('-c', '--community',
              help='show only block schemas filtered by maintaining community id or name')
def block_schema_list(verbose, community):
    """Lists all block schemas for this b2share instance (filtered for a
    community)."""

    from b2share.modules.communities.helpers import get_community_by_name_or_id

    comm = None
    if community:
        comm = get_community_by_name_or_id(community)
    community_id = None
    if comm:
        community_id = comm.id
    if verbose:
        click.secho("filtering for community %s" % comm)
    try:
        block_schemas = \
        BlockSchema.get_all_block_schemas(community_id=community_id)
    except BlockSchemaDoesNotExistError:
        raise click.ClickException("""No block schemas found, community
            parameter was: %s""" % community)
    click.secho("""BLOCK SCHEMA ID\t\t\t\tNAME\t\tMAINTAINER\tDEPRECATED\t#VERSIONS""")
    for bs in block_schemas:
        bs_comm = Community.get(id=bs.community)
        click.secho("%s\t%s\t%s\t%s\t\t%d" % (
            bs.id,
            bs.name[0:15].ljust(15),
            bs_comm.name[0:15].ljust(15),
            bs.deprecated,
            len(bs.versions)
        ))


@schemas.command()
@with_appcontext
@click.option('-v', '--verbose', is_flag=True, default=False)
@click.option('-n', '--name', help='set the name of the community')
@click.option('-c', '--community',
              help='set the maintaining community by name or id')
@click.option('-d', '--deprecated',
              help='(un)set deprecated bit, 1 is deprecated, 0 is not deprecated')
@click.argument('block_schema_id')
def block_schema_edit(verbose, name, community, deprecated, block_schema_id):
    from b2share.modules.communities.helpers import get_community_by_name_or_id

    try:
        UUID(block_schema_id, version=4)
    except ValueError:
        raise click.BadParameter("""BLOCK_SCHEMA_ID is not a valid UUID
         (hexadecimal numbers and dashes e.g.
         fa52bec3-a847-4602-8af5-b8d41a5215bc )""")
    try:
        block_schema = BlockSchema.get_block_schema(schema_id=block_schema_id)
    except BlockSchemaDoesNotExistError:
        raise click.BadParameter("No block_schema with id %s" % block_schema_id)
    if not(name or community or deprecated):
        raise click.ClickException("""Noting to edit - at least one of name,
        community or deprecated must be provided.""")
    data = {}
    if name:
        data['name'] = name
    if community:
        comm = get_community_by_name_or_id(community)
        if comm:
            data['community'] = comm.id
        else:
            click.secho("""Community not changed : no community exists with
            name or id: %s""" % community)
    if deprecated:
        if type(deprecated) != bool:
            raise click.BadParameter("""Deprecated should be True or False
             starting with a capital""")
        data['deprecated'] = deprecated
    block_schema.update(data)
    db.session.commit()


@schemas.command()
@with_appcontext
@click.option('-v', '--verbose', is_flag=True, default=False)
@click.argument('block_schema_id')
@click.argument('json_file')
def block_schema_create_version(verbose, block_schema_id, json_file):
    """Assign a json-schema file conforming to the EUDAT block-schema part of
    the root-schema that defines metadata format for this block schema. Upon
    success, this creates a new version, the old versions are maintained and
    can be obtained by block_schema_list_versions subcommand."""
    try:
        UUID(block_schema_id, version=4)
    except ValueError:
        raise click.BadParameter("""BLOCK_SCHEMA_ID is not a valid UUID
        (hexadecimal numbers and dashes e.g.
        fa52bec3-a847-4602-8af5-b8d41a5215bc )""")

    try:
        block_schema = BlockSchema.get_block_schema(schema_id=block_schema_id)
    except BlockSchemaDoesNotExistError:
        raise click.BadParameter("No block_schema with id %s" % block_schema_id)

    if not os.path.isfile(json_file):
        raise click.ClickException("%s does not exist on the filesystem" %
                                   json_file)

    schema_dict = {}
    with open(json_file, 'r') as f:
        try:
            schema_dict = json.load(f)
        except ValueError: # json decode error is subclass of ValueError
            raise click.ClickException("%s is not valid JSON" % json_file)

    try:
        validate_metadata_schema(schema_dict)
    except Exception as e:
        print("schema validation error:", e)
        raise click.ClickException("""%s is not a valid metadata schema for
        a B2SHARE community""" % json_file)

    block_schema_version = block_schema.create_version(schema_dict)
    db.session.commit()
    click.secho("Block schema version %d created for block schema %s" %
                (block_schema_version.version, block_schema.name))


@schemas.command()
@with_appcontext
@click.option('-v', '--verbose', is_flag=True, default=False)
@click.argument('block_schema_id')
def block_schema_list_versions(verbose, block_schema_id):
    """show the version number and release date of the versions of a block
        schema."""
    try:
        UUID(block_schema_id, version=4)
    except ValueError:
        raise click.BadParameter("""BLOCK_SCHEMA_ID is not a valid UUID
         (hexadecimal numbers and dashes e.g.
         fa52bec3-a847-4602-8af5-b8d41a5215bc )""")
    try:
        block_schema = BlockSchema.get_block_schema(schema_id=block_schema_id)
    except BlockSchemaDoesNotExistError:
        raise click.BadParameter("No block_schema with id %s" % block_schema_id)
    click.secho("BLOCK SCHEMA VERSIONS FOR community %s, block schema %s" % (
        Community.get(id=block_schema.community).name, block_schema.name))
    click.secho("Version no.\tRelease date")
    for bl_schema_version in block_schema.versions:
        click.secho("%s\t%s" % (
            bl_schema_version.version,
            bl_schema_version.released))


@schemas.command()
@with_appcontext
@click.option('-v', '--verbose', is_flag=True, default=False)
@click.argument('block_schema_id')
@click.option('--version')
def block_schema_version_generate_json(verbose, block_schema_id, version=None):
    """print json_schema of a particular block schema version."""
    try:
        UUID(block_schema_id, version=4)
    except ValueError:
        raise click.BadParameter("""BLOCK_SCHEMA_ID is not a valid UUID
        (hexadecimal numbers and dashes e.g.
        fa52bec3-a847-4602-8af5-b8d41a5215bc )""")
    try:
        block_schema = BlockSchema.get_block_schema(schema_id=block_schema_id)
    except BlockSchemaDoesNotExistError:
        raise click.BadParameter("No block_schema with id %s" % block_schema_id)
    result = ""
    if version is None or version == 'last':
        result = block_schema.versions[len(block_schema.versions)-1].json_schema
    else:
        result = block_schema.versions[version].json_schema
    result = json.loads(result)
    result = json.dumps(result, indent=4)
    click.secho(result)


@schemas.command()
@with_appcontext
@click.option('-v', '--verbose', is_flag=True, default=False)
@click.argument('community')
@click.option('--version')
def community_schema_list_block_schema_versions(verbose, community, version=None):
    """Show the block schema versions in the community schema element of a
        specific community"""
    from b2share.modules.communities.helpers import get_community_by_name_or_id

    comm = get_community_by_name_or_id(community)
    if not comm:
        raise click.BadParameter("There is no community by this name or ID: %s"%
                                 community)
    community_schema = CommunitySchema.get_community_schema(comm.id, version)
    if not community_schema:
        raise click.ClickException("""Community %s does not have a community
            schema""" % comm.name)
    community_schema_dict = json.loads(community_schema.community_schema)
    props = community_schema_dict['properties']
    click.secho("""The following block schema versions are listed for community
        %s, community schema version %s""" % (
            comm.name,
            "latest %d" % community_schema.version if not version else version))
    for key in props:
        click.secho("Block schema: %s, version url: %s" % (
            key, props[key]['$ref']))



# this function should be called from the communities' cli module
def update_or_set_community_schema(community, json_file):
    """Updates or sets the schema for a community.

    The complete schema of a community contains a copy of the root metadata
    schema and a set of community-specific metadata block schemas. Currently
    we assume there's only one allowed metadata block schema for a community,
    and this command creates it or makes a new version for it.

    - community is the ID or NAME of the community to be updated.
    - json_file is a file path to the json-schema file describing the
    community-specific block schema.

    See also `b2share schemas block_schema_version_generate_json`"""

    from b2share.modules.communities.helpers import get_community_by_name_or_id

    comm = get_community_by_name_or_id(community)
    if not comm:
        raise click.BadParameter("There is no community by this name or ID: %s" %
                                 community)
    if not os.path.isfile(json_file):
        raise click.ClickException("%s does not exist on the filesystem" %
                                   json_file)

    schema_dict = {}
    with open(json_file, 'r') as f:
        try:
            schema_dict = json.load(f)
        except ValueError:
            raise click.ClickException("%s is not valid JSON" % json_file)

    try:
        validate_metadata_schema(schema_dict)
    except Exception as e:
        print("schema validation error:", e)
        raise click.ClickException("""%s is not a valid metadata schema for
        a B2SHARE community""" % json_file)

    #create new block version schema
    try:
        community_schema = CommunitySchema.get_community_schema(comm.id)
        comm_schema_json = json.loads(community_schema.community_schema)
        if 'properties' not in comm_schema_json.keys():
            raise click.ClickException("""Invalid community schema
                for community %s""" % community.name)

        if len(comm_schema_json['properties']) > 1:
            raise click.ClickException("""Multiple block schemas not supported.""")
        #we can by configuration also have a community schema that does not refer to a blockschema
        if len (comm_schema_json['properties']) == 0:
            _create_community_schema(comm, schema_dict)
        else:
            _update_community_schema(comm, comm_schema_json, schema_dict)
    except CommunitySchemaDoesNotExistError:
        _create_community_schema(comm, schema_dict)
    db.session.commit()
    click.secho("Succesfully processed new metadata schema", fg='green')


def _update_community_schema(community, comm_schema_json, schema_dict):
    base_url = urlunsplit((
        current_app.config.get('PREFERRED_URL_SCHEME', 'http'),
        current_app.config['JSONSCHEMAS_HOST'],
        current_app.config.get('APPLICATION_ROOT') or '', '', ''
    ))
    with current_app.test_request_context('/', base_url=base_url):
        block_schema_id = comm_schema_json['properties'].popitem()[0]
        try:
            block_schema = BlockSchema.get_block_schema(block_schema_id)
        except BlockSchemaDoesNotExistError:
            raise click.ClickException("""CommunitySchema refers to block
                schema with id: %s. This schema does not
                exist""" % block_schema_id)
        new_block_schema_version = block_schema.create_version(schema_dict)
        block_schema_version_url = block_schema_version_json_schema_link(
            new_block_schema_version, _external=True
        )
        comm_schema_json['properties'][str(block_schema.id)] = {
            '$ref': block_schema_version_url,
        }
        return CommunitySchema.create_version(community.id, comm_schema_json)


def _create_community_schema(community, schema_dict):
    base_url = urlunsplit((
        current_app.config.get('PREFERRED_URL_SCHEME', 'http'),
        current_app.config['JSONSCHEMAS_HOST'],
        current_app.config.get('APPLICATION_ROOT') or '', '', ''
    ))
    with current_app.test_request_context('/', base_url=base_url):
        block_schema = BlockSchema.create_block_schema(
            community.id, community.name
        )
        block_schema_version = block_schema.create_version(schema_dict)
        block_schema_version_url = block_schema_version_json_schema_link(
            block_schema_version, _external=True
        )
        community_schema = {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'properties': {
                str(block_schema.id): {
                    '$ref': block_schema_version_url,
                }
            },
            'type': "object",
            'additionalProperties': False,
            'required': [str(block_schema.id)],
        }
        click.secho(json.dumps(community_schema, indent=4))
        result = CommunitySchema.create_version(community.id, community_schema)
    return result
