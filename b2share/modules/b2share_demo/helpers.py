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

"""B2Share demo helpers."""

from __future__ import absolute_import, print_function

import json
from jsonschema.exceptions import ValidationError
import os
import re
import uuid
from collections import namedtuple
import requests
from six import BytesIO
import ssl
import sys, traceback
from uuid import UUID, uuid4
from urllib.parse import urlunsplit
from urllib.request import urlopen


import click
from flask import current_app

from invenio_accounts.models import User
from invenio_db import db
from invenio_files_rest.models import ObjectVersion
from invenio_indexer.api import RecordIndexer
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_records_files.api import Record
from b2share.modules.deposit.api import Deposit
from b2share.modules.deposit.providers import DepositUUIDProvider
from b2share.modules.deposit.minters import b2share_deposit_uuid_minter

from b2share.modules.communities import Community
from b2share.modules.schemas import BlockSchema, CommunitySchema
from b2share.modules.schemas.helpers import resolve_schemas_ref
from b2share.modules.records.providers import RecordUUIDProvider
from b2share.modules.records.indexer import record_to_index

def load_demo_data(path, verbose=0):
    """Load a demonstration located at the given path.

    Args:
        path (str): path of the directory containing the demonstration data.
        verbose (int): verbosity level.
    """
    base_url = urlunsplit((
        current_app.config.get('PREFERRED_URL_SCHEME', 'http'),
        # current_app.config['SERVER_NAME'],
        current_app.config['JSONSCHEMAS_HOST'],
        current_app.config.get('APPLICATION_ROOT') or '', '', ''
    ))
    with db.session.begin_nested():
        user_info = _create_user()
        # Define the base url used for the request context. This is useful
        # for generated URLs which will use the provided url "scheme".
        with current_app.test_request_context('/', base_url=base_url):
            current_app.login_manager.reload_user(user_info['user'])
            communities = _create_communities(path, verbose)
            _create_block_schemas(communities, verbose)
            _create_community_schemas(communities, verbose)
            _create_records(path, verbose)


DemoCommunity = namedtuple('DemoCommunity', ['ref', 'config'])


def _create_user(email=None):
    """Create demo user."""
    click.secho('Creating user', fg='yellow', bold=True)

    if email is None:
        email = 'firstuser@example.com'
        name = 'FirstUser'
    else:
        name = email


    user_info = {
        'id': None,
        'name': name,
        'email': email,
        'password': '1234567890',
    }
    from flask_security.utils import encrypt_password
    accounts = current_app.extensions['invenio-accounts']

    with db.session.begin_nested():
        user = accounts.datastore.create_user(
            email=user_info.get('email'),
            active=True,
        )
        db.session.add(user)
        user_info['id'] = user.id
        user_info['user'] = user

    return user_info


def _create_communities(path, verbose):
    """Create demo communities."""
    if verbose > 0:
        click.secho('Creating communities', fg='yellow', bold=True)
    with db.session.begin_nested():
        communities_dir = os.path.join(path, 'communities')
        communities = dict()
        nb_communities = 0
        for filename in sorted(os.listdir(communities_dir)):
            if os.path.splitext(filename)[1] == '.json':
                with open(os.path.join(communities_dir,
                                       filename)) as json_file:
                    json_config = json.loads(json_file.read())
                    workflow = json_config.get('publication_workflow',
                                               'review_and_publish')
                    is_restricted = json_config.get('restricted_submission',
                                                    False)
                    community = Community.create_community(
                        name=json_config['name'],
                        description=json_config['description'],
                        logo=json_config['logo'],
                        publication_workflow=workflow,
                        restricted_submission=is_restricted,
                        id_=UUID(json_config['id']),
                    )
                    if verbose > 1:
                        click.secho('Created community {0} with ID {1}'.format(
                            community.name, community.id
                        ))
                    communities[community.name] = DemoCommunity(community,
                                                                json_config)
                    nb_communities += 1
    if verbose > 0:
        click.secho('Created {} communities!'.format(nb_communities),
                    fg='green')
    return communities


def _create_block_schemas(communities, verbose):
    """Create demo block schemas."""
    if verbose > 0:
        click.secho('Creating block schemas', fg='yellow', bold=True)
    nb_block_schemas = 0
    with db.session.begin_nested():
        for community in communities.values():
            for schema_name, schema in community.config[
                    'block_schemas'].items():
                block_schema = BlockSchema.create_block_schema(
                    community.ref.id,
                    schema_name,
                    id_=UUID(schema['id']),
                )
                for json_schema in schema['versions']:
                    block_schema.create_version(json_schema)
                nb_block_schemas += 1
    if verbose > 0:
        click.secho('Created {} block schemas!'.format(nb_block_schemas),
                    fg='green')


def _create_community_schemas(communities, verbose):
    """Create demo community schemas."""
    if verbose > 0:
        click.secho('Creating community schemas', fg='yellow', bold=True)
    with db.session.begin_nested():
        for community in communities.values():
            for schema in community.config['community_schemas']:
                json_schema_str = json.dumps(schema['json_schema'])
                # expand variables in the json schema
                json_schema_str = resolve_block_schema_id(json_schema_str)
                json_schema_str = resolve_schemas_ref(json_schema_str)
                CommunitySchema.create_version(
                    community_id=community.ref.id,
                    community_schema=json.loads(json_schema_str),
                    root_schema_version=int(schema['root_schema_version']))
    if verbose > 0:
        click.secho('Created all community schemas!', fg='green')


def _create_records(path, verbose):
    """Create demo records."""
    indexer = RecordIndexer(record_to_index=record_to_index)

    if verbose > 0:
        click.secho('Creating records', fg='yellow', bold=True)
    with db.session.begin_nested():
        records_dir = os.path.join(path, 'records')
        nb_records = 0
        for root, dirs, files in os.walk(records_dir):
            for filename in files:
                split_filename = os.path.splitext(filename)
                if split_filename[1] == '.json':
                    rec_uuid = UUID(split_filename[0])
                    path = os.path.join(records_dir, root, filename)
                    record, deposit = _create_record_from_filepath(
                        path, rec_uuid, indexer, nb_records, verbose)
                    if verbose > 1:
                        click.secho('CREATED RECORD {0}:\n {1}'.format(
                            str(rec_uuid), json.dumps(record, indent=4)
                        ))
                        click.secho('CREATED DEPOSIT {0}:\n {1}'.format(
                            str(rec_uuid), json.dumps(deposit, indent=4)
                        ))
                    nb_records += 1
    if verbose > 0:
        click.secho('Created {} records!'.format(nb_records), fg='green')

def _create_record_from_filepath(path, rec_uuid, indexer, versions, verbose):
    with open(path) as record_file:
        record_str = record_file.read()
    record_str = resolve_community_id(record_str)
    record_str = resolve_block_schema_id(record_str)
    json_data = json.loads(record_str)
    b2share_deposit_uuid_minter(rec_uuid, data=json_data)
    deposit = Deposit.create(json_data, id_=rec_uuid)
    ObjectVersion.create(deposit.files.bucket, 'myfile',
                         stream=BytesIO(b'mycontent'))
    deposit.publish()
    pid, record = deposit.fetch_published()
    indexer.index(record)
    if verbose > 0:
        click.secho('created new record: {}'.format(str(rec_uuid)))

    last_id = pid.pid_value
    for i in range(2*versions):
        rec_uuid = uuid4()
        json_data = json.loads(record_str)
        b2share_deposit_uuid_minter(rec_uuid, data=json_data)
        deposit2 = Deposit.create(json_data, id_=rec_uuid,
                                  version_of=last_id)

        ObjectVersion.create(deposit2.files.bucket, 'myfile-ver{}'.format(i),
                             stream=BytesIO(b'mycontent'))
        deposit2.publish()
        pid, record2 = deposit2.fetch_published()
        indexer.index(record2)
        last_id = pid.pid_value
        if verbose > 0:
            click.secho('created new version: {}'.format(str(rec_uuid)))

    return record, deposit


def resolve_block_schema_id(source):
    """Resolve all references to Block Schema and replace them with their ID.

    Every instance of '$BLOCK_SCHEMA_ID[<schema_name>]' will be replaced with
    the corresponding ID.

    Args:
        source (str): the source string to transform.

    Returns:
        str: a copy of source with the references replaced.
    """
    def block_schema_ref_match(match):
        name = match.group(1)
        found_schemas = BlockSchema.get_all_block_schemas(name=name)
        if len(found_schemas) > 1:
            raise Exception(
                'Too many schemas matching name "{}".'.format(name))
        elif len(found_schemas) == 0:
            raise Exception('No schema matching name "{}" found.'.format(name))
        return found_schemas[0]
    return re.sub(
        r'\$BLOCK_SCHEMA_ID\[([^\]:]+)\]',
        lambda m: str(block_schema_ref_match(m).id),
        source
    )


def resolve_community_id(source):
    """Resolve all references to Community and replace them with their ID.

    Every instance of '$COMMUNITY_ID[<community_name>]' will be replaced with
    the corresponding ID.

    Args:
        source (str): the source string to transform.

    Returns:
        str: a copy of source with the references replaced.
    """
    def community_id_match(match):
        community_name = match.group(1)
        community = Community.get(name=community_name)
        return str(community.id)
    return re.sub(
        r'\$COMMUNITY_ID\[([^\]]+)\]',
        community_id_match,
        source
    )
