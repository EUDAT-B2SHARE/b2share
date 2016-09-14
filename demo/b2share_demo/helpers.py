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
import os
import re
import uuid
from collections import namedtuple
import requests
from six import BytesIO
import ssl
import sys, traceback
from uuid import UUID
from urllib.parse import urlunsplit
from urllib.request import urlopen

import click
from flask import current_app

from invenio_db import db
from invenio_files_rest.models import ObjectVersion
from invenio_indexer.api import RecordIndexer
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_records_files.api import Record
from b2share.modules.deposit.api import Deposit
from b2share.modules.deposit.providers import DepositUUIDProvider

from b2share.modules.communities import Community
from b2share.modules.schemas import BlockSchema, CommunitySchema
from b2share.modules.schemas.helpers import resolve_schemas_ref
from b2share.modules.records.providers import RecordUUIDProvider

def load_demo_data(path, verbose=0):
    """Load a demonstration located at the given path.

    Args:
        path (str): path of the directory containing the demonstration data.
        verbose (int): verbosity level.
    """
    with db.session.begin_nested():
        user_info = _create_user(verbose)
        # Define the base url used for the request context. This is useful
        # for generated URLs which will use the provided url "scheme".
        base_url = urlunsplit((
            current_app.config.get('PREFERRED_URL_SCHEME', 'http'),
            # current_app.config['SERVER_NAME'],
            current_app.config['JSONSCHEMAS_HOST'],
            current_app.config.get('APPLICATION_ROOT') or '', '', ''
        ))
        with current_app.test_request_context('/', base_url=base_url):
            current_app.login_manager.reload_user(user_info['user'])
            communities = _create_communities(path, verbose)
            _create_block_schemas(communities, verbose)
            _create_community_schemas(communities, verbose)
            _create_records(path, verbose)


DemoCommunity = namedtuple('DemoCommunity', ['ref', 'config'])


def _create_user(verbose):
    """Create demo user."""
    if verbose > 0:
        click.secho('Creating user', fg='yellow', bold=True)

    user_info = {
        'id': None,
        'name': 'FirstUser',
        'email': 'firstuser@example.com',
        'password': '1234567890',
    }
    from flask_security.utils import encrypt_password
    accounts = current_app.extensions['invenio-accounts']

    with db.session.begin_nested():
        user = accounts.datastore.create_user(
            email=user_info.get('email'),
            password=encrypt_password(user_info.get('password')),
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
                    community = Community.create_community(
                        name=json_config['name'],
                        description=json_config['description'],
                        logo=json_config['logo'],
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
    indexer = RecordIndexer(
        record_to_index=lambda record: ('records', 'record')
    )
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
                    with open(os.path.join(records_dir, root,
                                           filename)) as record_file:
                        record_str = record_file.read()
                    record_str = resolve_community_id(record_str)
                    record_str = resolve_block_schema_id(record_str)
                    deposit = Deposit.create(json.loads(record_str),
                                             id_=rec_uuid)
                    ObjectVersion.create(deposit.files.bucket, 'myfile',
                        stream=BytesIO(b'mycontent'))
                    deposit.publish()
                    pid, record = deposit.fetch_published()
                    # index the record
                    indexer.index(record)
                    if verbose > 1:
                        click.secho('CREATED RECORD {0}:\n {1}'.format(
                            str(rec_uuid), json.dumps(record,
                                                  indent=4)
                        ))
                        click.secho('CREATED DEPOSIT {0}:\n {1}'.format(
                            str(rec_uuid), json.dumps(deposit,
                                                  indent=4)
                        ))
                    nb_records += 1
    if verbose > 0:
        click.secho('Created {} records!'.format(nb_records), fg='green')


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
    
        
def download_v1_data(token, target_dir, limit=None):
    """
    Download the data from B2SHARE V1 records using token in to target_dir .
    """
    V1_URL_BASE = 'https://b2share.eudat.eu/api/'
    url = "%srecords" % V1_URL_BASE
    params = {}
    params['access_token'] = token
    params['page_size']=100
    params['page_offset']=0
    finished = False
    counter = 0
    if not(limit is None) and counter*100 + 100 > limit:
        params['page_size']= limit
    while not finished:
        r = requests.get(url, params=params, verify=False)
        target_file = os.path.join(target_dir, "%d.txt" % counter)
        f = open(target_file,'w')
        f.write(r.text)
        f.close()
        recs = json.loads(r.text)['records'] 
        if len(recs)<100:
            finished = True
        counter = counter + 1
        params['page_offset']=counter

def process_v1_file(filename, download, download_directory):
    """
    Parse a downloaded file containing records
    """
    indexer = RecordIndexer(
        record_to_index=lambda record: ('records', 'record')
    )
    f = open(filename,'r')
    file_content = f.read()
    try:
        recs = json.loads(file_content)['records']
    except:
        current_app.logger.error("Not a JSON file %s" % filename)
        return None
    f.close()
    recs = [r for r in recs if not(r['domain']=='') ]
    for r in recs:
        record = _process_record(r)
        if record is not None:
            try:
                deposit = Deposit.create(record)
                #add/link the files
                _process_files(deposit,r, download, download_directory)
                deposit.publish()
                pid, record = deposit.fetch_published()
                # index the record
                indexer.index(record)
                db.session.commit()
            except:
                current_app.logger.warning("Exception in trying to create deposit for %s" % str(record['title']) + str(record['_deposit']['id']))
         
            
def _process_record(rec):
    #rec is dict representing 1 record
    #from json donwloaded from b2share_v1 API
    result = {}
    generic_keys = ['title'
        ,'description'
        ,'open_access'
        ,'resource_type'
        ,'contact_email'
        ,'contributors'
        ]
    for k in generic_keys:
        result[k] = rec[k]
    #make keywords unique
    seen = set()
    result['keywords'] = \
        [k for k in rec['keywords'] if k not in seen and not seen.add(k)]
    #fetch community
    comms = Community.get_all(0,1,name=rec['domain'])
    #TODO match generic and linguistics domains to communities
    if comms:
        community = comms[0]
        result['community']=str(community.id)
    elif rec['domain']=='generic':
        community = Community.get(name='EUDAT')
        result['community']=str(community.id)
    elif rec['domain']=='linguistics':
        community = Community.get(name='CLARIN')
        result['community']=str(community.id)
    else:
        return None
    if 'PID' in rec.keys():
        result['alternate_identifier'] = rec['PID']
    #TODO fetch domain_metadata and translate to community specific metadata
    #assume the current community specific block schema for metadata format
    return result
    
def _process_files(deposit, r, download, download_dir):
    if not(r['files']=='RESTRICTED'):
        for file_dict in r['files']:
            if download:
                try:
                    if 'name' in file_dict.keys():
                        #only for gangsters - bypass HTTPS verification see
                        #http://stackoverflow.com/
                        #questions/27835619/ssl-certificate-verify-failed-error
                        _save_file(file_dict['url']
                            , download_dir 
                            , file_dict['name'])
                except:
                    current_app.logger.error("something went wrong when trying to download file %s" % file_dict['name'])    
            try:
                f = open(os.path.join(download_dir, file_dict['name']),'r+b')
                ObjectVersion.create(deposit.files.bucket, file_dict['name'],
                    stream=BytesIO(f.read()))
            except:
                current_app.logger.error("Something wrong when trying to load %s" % file_dict['name'])
            
def _save_file(url, download_dir, filename):
    current_app.logger.debug("Downloading %s" % url)
    gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
    finished = False
    f = open(os.path.join(download_dir,filename),'wb')
    u = urlopen(url, context=gcontext)
    counter = 0
    while not finished:
        try:
            f.write(u.read())
            finished = True
        except IncompleteRead:
            current_app.logger.debug("IncompleteRead %d" % counter)
            counter += counter
        