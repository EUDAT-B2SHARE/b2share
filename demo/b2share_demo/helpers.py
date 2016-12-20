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
from uuid import UUID
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
    base_url = urlunsplit((
        current_app.config.get('PREFERRED_URL_SCHEME', 'http'),
        # current_app.config['SERVER_NAME'],
        current_app.config['JSONSCHEMAS_HOST'],
        current_app.config.get('APPLICATION_ROOT') or '', '', ''
    ))
    with db.session.begin_nested():
        user_info = _create_user(verbose)
        # Define the base url used for the request context. This is useful
        # for generated URLs which will use the provided url "scheme".
        with current_app.test_request_context('/', base_url=base_url):
            current_app.login_manager.reload_user(user_info['user'])
            communities = _create_communities(path, verbose)
            _create_block_schemas(communities, verbose)
            _create_community_schemas(communities, verbose)
            _create_records(path, verbose)


DemoCommunity = namedtuple('DemoCommunity', ['ref', 'config'])


def _create_user(verbose, email=None):
    """Create demo user."""
    if verbose:
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


def download_v1_data(token, target_dir, logfile, limit=None, verbose=False):
    """
    Download the data from B2SHARE V1 records using token in to target_dir .
    """
    V1_URL_BASE = current_app.config.get('V1_URL_BASE')
    url = "%srecords" % V1_URL_BASE
    params = {}
    params['access_token'] = token
    params['page_size'] = 100
    counter = 0
    page_counter = 0
    os.chdir(target_dir)
    while True:
        click.secho("Download counter is now: %d" % counter)
        params['page_offset'] = page_counter
        click.secho("Params to download: %s" % str(params))
        r = requests.get(url, params=params, verify=False)
        r.raise_for_status()
        recs = json.loads(r.text)['records']
        if len(recs) == 0:
            return # no more records
        for record in recs:
            if record.get('files') == 'RESTRICTED':
                if verbose:
                    click.secho('Ignore restricted record {}'.format(record.get('title')),
                                fg='red')
            else:
                counter = counter + 1
                os.mkdir(str(counter))
                download_v1_record(str(counter), record,
                     logfile, verbose )
                if not(limit is None) and counter >= limit:
                    return # limit reached
        page_counter = page_counter + 1


def download_v1_record(directory, record, logfile, verbose=False):
    if verbose:
        click.secho('Download record {} "{}"'.format(
            directory, record.get('title')))
    target_file = os.path.join(directory, '___record___.json')
    with open(target_file, 'w') as f:
        f.write(json.dumps(record))
    for index, file_dict in enumerate(record.get('files', [])):
        if not file_dict.get('name'):
            click.secho('    Ignore file with no name "{}"'.format(file_dict.get('url')),
                        fg='red')
        else:
            if verbose:
                click.secho('    Download file "{}"'.format(file_dict.get('name')))
            filepath = os.path.join(directory, 'file_{}'.format(index))
            _save_file(logfile, file_dict['url'], filepath)
            if int(os.path.getsize(filepath)) != int(file_dict.get('size')):
                logfile.write("********************")
                logfile.write(traceback.format_exc())
                logfile.write("ERROR: downloaded file size differs for file {}".format(filepath))
                logfile.write("        {} instead of {}".format(os.path.getsize(filepath), file_dict.get('size')))
                logfile.write("********************")


def get_or_create_user(verbose, email):
    result_set = User.query.filter(User.email==email)
    if result_set.count():
        result = result_set.one()
    else:
        user_info = _create_user(verbose, email)
        result = user_info['user']
    return result

def process_v1_record(directory, indexer, base_url, logfile, verbose=False):
    """
    Parse a downloaded file containing records
    """
    with open(os.path.join(directory, '___record___.json'),'r') as f:
        file_content = f.read()
    record_json = json.loads(file_content)
    if not record_json.get('domain'):
        click.secho('Record {} "{}" has no domain'.format(
                    directory, record_json.get('title')),
                    fg='red')
    if verbose:
        click.secho('Processing record {} "{}"'.format(
                    directory, record_json.get('title')))
    record = _process_record(record_json)
    if record is not None:
        user = get_or_create_user(verbose, record_json['uploaded_by'])
        with current_app.test_request_context('/', base_url=base_url):
            current_app.login_manager.reload_user(user)
            try:
                deposit = Deposit.create(record)
                _create_bucket(deposit, record_json, directory, logfile, verbose)
                deposit.publish()
                pid, record = deposit.fetch_published()
                # index the record
                indexer.index(record)
                db.session.commit()
            except:
                logfile.write("********************")
                logfile.write(traceback.format_exc())
                logfile.write("ERROR in %s" % record_json['record_id'])
                logfile.write("********************")
    if verbose:
        click.secho("Finished processing {}".format(record['titles'][0]['title']))

def _create_bucket(deposit, record_json,directory, logfile, verbose):
    for index, file_dict in enumerate(record_json.get('files', [])):
        if not file_dict.get('name'):
            click.secho('    Ignore file with no name "{}"'.format(
                        file_dict.get('url')),
                    fg='red')
        else:
            if verbose:
                click.secho('    Load file "{}"'.format(
                    file_dict.get('name')))
            filepath = os.path.join(directory,
                'file_{}'.format(index))
            if int(os.path.getsize(filepath)) != int(file_dict.get('size')):
                logfile.write("***** downloaded file size differs, {} ******".format(filepath))
            else:
                with open(filepath, 'r+b') as f:
                    ObjectVersion.create(deposit.files.bucket,
                        file_dict['name'],
                        stream=BytesIO(f.read()))

def _process_record(rec):
    #rec is dict representing 1 record
    #from json donwloaded from b2share_v1 API
    result = {}
    generic_keys = [
        'open_access'
        ,'contact_email'
        ,'publication_date'
        ]
    for k in generic_keys:
        result[k] = rec[k]
    result['license'] = {'license': rec['licence']}
    result['titles'] = []
    result['titles'].append({'title':rec['title']})
    result['descriptions'] = []
    element = {}
    element['description_type'] = 'Abstract'
    element['description'] = rec['description']
    result['descriptions'].append(element)
    result['contributors'] = []
    contributors = list(set(rec['contributors']))
    for contributor in contributors:
        element = {}
        element['contributor_type'] = "Other"
        element['contributor_name'] = contributor
        result['contributors'].append(element)
    result['keywords'] = list(set(rec['keywords']))
    creators = list(set(rec['creator']))
    result['creators'] = []
    for creator in creators:
        result['creators'].append({'creator_name':creator})

    result['publisher'] = rec.get('publisher', "https://b2share.eudat.eu")
    if rec.get('discipline'):
        result['disciplines'] = list(set(rec.get('discipline')))
    if rec.get('language'):
        result['language'] = rec.get('language')
    if rec.get('version'):
        result['version'] = rec.get('version')
    if rec.get('embargo_date'):
        result['embargo_date'] = rec.get('embargo_date')

    #fetch community
    rec['domain'] = rec['domain'].upper()
    #hardcoded Aalto exception
    if rec['domain']=='AALTO':
        rec['domain'] = 'Aalto'
    comms = Community.get_all(0,1,name=rec['domain'])
    if comms:
        community = comms[0]
        result['community']=str(community.id)
    elif rec['domain']=='GENERIC':
        community = Community.get(name='EUDAT')
        result['community']=str(community.id)
    elif rec['domain']=='LINGUISTICS':
        community = Community.get(name='CLARIN')
        result['community']=str(community.id)
    else:
        raise Exception("Community not found for domain: `{}`".format(rec['domain']))
    result['alternate_identifiers'] = [
         {'alternate_identifier_type':'B2SHARE_V1_ID',
            'alternate_identifier': str(rec['record_id'])}
        ]
    if 'PID' in rec.keys():
        result['alternate_identifiers'].append(
            {'alternate_identifier_type':'ePIC_PID',
            'alternate_identifier': rec['PID']}
        )
    if 'resource_type' in rec.keys():
        translate = {
            'Audio': 'Audiovisual',
            'Video': 'Audiovisual',
            'Time-series': 'Dataset',
            'Text': 'Text',
            'Image': 'Image',
            'Other': 'Other',
            'treebank':'Other',
            'Time-Series':'Dataset'
        }
        resource_types= list(set([translate[r] for r in rec['resource_type']]))
        result['resource_types'] = []
        for rt in resource_types:
            element = {'resource_type_general':rt}
            result['resource_types'].append(element)
    if not result['resource_types']:
        result['resource_types'] = [{'resource_type_general': "Other"}]
    result['community_specific'] = {}
    if 'domain_metadata' in rec.keys():
        result.update(
            _match_community_specific_metadata(rec, community)
            )
    return result

def _match_community_specific_metadata(rec, community):
    cs_md_values_dict = rec['domain_metadata']
    convert_to_array = [
        'hasOntologyLanguage',
        'usedOntologyEngineeringTool',
    ]
    for key in convert_to_array:
        if key in cs_md_values_dict.keys():
            cs_md_values_dict[key] = [
                cs_md_values_dict[key]
            ]
    remove_integer_keys_with_empty_values = [
        'planned_sampled_individuals',
        'planned_total_individuals'
    ]
    for key in remove_integer_keys_with_empty_values:
        if key in cs_md_values_dict.keys():
            if cs_md_values_dict[key] == '':
                 cs_md_values_dict.pop(key)
            else:
                cs_md_values_dict[key] = int(cs_md_values_dict[key])
    result = {}
    result['community_specific'] = {}
    resolve_string = "$BLOCK_SCHEMA_ID[%s]" % community.name.lower()
    block_schema_id = resolve_block_schema_id(resolve_string)
    result['community_specific'][block_schema_id] = cs_md_values_dict
    return result

def _save_file(logfile, url, filename):
    CHUNK_SIZE = 16 * 1024 * 1024 #download 16MB at a time
    current_app.logger.debug("Downloading %s" % url)
    gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
    finished = False
    f = open(filename, 'wb')
    try:
        u = urlopen(url, context=gcontext)
    except:
        current_app.logger.error("TIMEOUT trying to download %s" % url)
        logfile.write("********************")
        logfile.write(traceback.format_exc())
        logfile.write("ERROR: cannot open file URL for download: {}".format(url))
        logfile.write("********************")

    while not finished:
        try:
            chunk = u.read(CHUNK_SIZE)
            if chunk:
                f.write(chunk)
            else:
                finished = True
        except:
            logfile.write("********************")
            logfile.write(traceback.format_exc())
            logfile.write("WARN: exception while reading file: {}".format(url))
            logfile.write("********************")
            finished = True
    f.close()
