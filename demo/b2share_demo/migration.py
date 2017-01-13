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
import traceback
import ssl
from pprint import pprint
from flask import current_app
import click
import requests
from six import BytesIO
from urllib.parse import urljoin

from invenio_db import db
from invenio_search.api import RecordsSearch
from invenio_accounts.models import User
from invenio_files_rest.models import ObjectVersion
from b2share.modules.deposit.api import Deposit
from b2share.modules.communities import Community

from .helpers import resolve_block_schema_id, _create_user


MAX_PAGE = 8



def download_v1_data(token, target_dir, logfile, limit=None):
    """
    Download the data from B2SHARE V1 records using token in to target_dir .
    """
    V1_URL_BASE = current_app.config.get('V1_URL_BASE')
    url = "%srecords" % V1_URL_BASE
    params = {}
    params['access_token'] = token
    params['page_size'] = 100
    page_counter = 0
    os.chdir(target_dir)
    while True:
        params['page_offset'] = page_counter
        click.secho("Params to download: %s" % str(params))
        r = requests.get(url, params=params, verify=False)
        r.raise_for_status()
        recs = json.loads(r.text)['records']
        if len(recs) == 0:
            return # no more records
        for record in recs:
            recid = str(record.get('record_id'))
            click.secho("Download record : %s" % recid)
            if not os.path.exists(recid):
                os.mkdir(recid)
            download_v1_record(recid, record, logfile)
            if (limit is not None) and int(recid) >= limit:
                return # limit reached
        page_counter = page_counter + 1


def download_v1_record(recid, record, logfile):
    click.secho('Download record {} "{}"'.format(recid, record.get('title')))
    directory = recid
    target_file = os.path.join(directory, '___record___.json')
    with open(target_file, 'w') as f:
        f.write(json.dumps(record))
    for index, file_dict in enumerate(record.get('files', [])):
        click.secho('    Download file "{}"'.format(file_dict.get('name')))
        filepath = os.path.join(directory, 'file_{}'.format(index))
        if not os.path.exists(filepath) or int(os.path.getsize(filepath)) != int(file_dict.get('size')):
            _save_file(logfile, file_dict['url'], filepath)
        if int(os.path.getsize(filepath)) != int(file_dict.get('size')):
            logfile.write("\n********************\n")
            logfile.write("\nERROR: downloaded file size differs for file {}\n".format(filepath))
            logfile.write("        {} instead of {}\n".format(
                os.path.getsize(filepath), file_dict.get('size')))
            logfile.write("\n********************\n")


def get_or_create_user(email):
    result_set = User.query.filter(User.email==email)
    if result_set.count():
        result = result_set.one()
    else:
        user_info = _create_user(email)
        result = user_info['user']
    return result

def process_v1_record(directory, indexer, base_url, logfile):
    """
    Parse a downloaded file containing records
    """
    with open(os.path.join(directory, '___record___.json'), 'r') as f:
        file_content = f.read()
    record_json = json.loads(file_content)
    recid = str(record_json.get('record_id'))
    if not record_json.get('domain'):
        click.secho('Record {} "{}" has no domain, '.format(recid, record_json.get('title')),
                    fg='red')
        logfile.write("\n********************\n")
        logfile.write("\nERROR: record {} has no domain, is in limbo\n".format(recid))
        logfile.write("\n********************\n")
    click.secho('Processing record {} "{}"'.format(recid, record_json.get('title')))
    record = _process_record(record_json)
    if record is not None:
        user = get_or_create_user(record_json['uploaded_by'])
        with current_app.test_request_context('/', base_url=base_url):
            current_app.login_manager.reload_user(user)
            try:
                deposit = Deposit.create(record)
                _create_bucket(deposit, record_json, directory, logfile)
                deposit.publish()
                _, record = deposit.fetch_published()
                # index the record
                indexer.index(record)
                db.session.commit()
            except:
                logfile.write("\n********************")
                logfile.write("\nERROR while creating record {}\n".format(recid))
                logfile.write(traceback.format_exc())
                logfile.write("\n********************")
    click.secho("Finished processing {}".format(record['titles'][0]['title']))


def _create_bucket(deposit, record_json, directory, logfile):
    for index, file_dict in enumerate(record_json.get('files', [])):
        click.secho('    Load file "{}"'.format(file_dict.get('name')))
        filepath = os.path.join(directory, 'file_{}'.format(index))
        if int(os.path.getsize(filepath)) != int(file_dict.get('size')):
            logfile.write("\n********************")
            logfile.write("\nERROR: downloaded file size differs for file {}: {} instead of {}"
                          .format(filepath, os.path.getsize(filepath), file_dict.get('size')))
            logfile.write("\n********************")
        else:
            with open(filepath, 'r+b') as f:
                ObjectVersion.create(deposit.files.bucket, file_dict['name'],
                                     stream=BytesIO(f.read()))

def _process_record(rec):
    #rec is dict representing 1 record
    #from json donwloaded from b2share_v1 API
    result = {}
    generic_keys = ['open_access', 'contact_email', 'publication_date']
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
    contributors = unique(rec['contributors'])
    contributors = unique(rec['contributors'])
    for contributor in contributors:
        element = {}
        element['contributor_type'] = "Other"
        element['contributor_name'] = contributor
        result['contributors'].append(element)
    result['keywords'] = unique(rec['keywords'])
    creators = unique(rec['creator'])
    result['creators'] = []
    for creator in creators:
        result['creators'].append({'creator_name':creator})

    result['publisher'] = rec.get('publisher', "https://b2share.eudat.eu")
    if rec.get('discipline'):
        result['disciplines'] = unique(rec.get('discipline'))
    if rec.get('language'):
        result['language'] = rec.get('language')
    if rec.get('version'):
        result['version'] = rec.get('version')
    if rec.get('embargo_date'):
        result['embargo_date'] = rec.get('embargo_date')

    #fetch community
    rec['domain'] = rec['domain'].upper()
    #hardcoded Aalto exception
    if rec['domain'] == 'AALTO':
        rec['domain'] = 'Aalto'
    comms = Community.get_all(0, 1, name=rec['domain'])
    if comms:
        community = comms[0]
        result['community'] = str(community.id)
    elif rec['domain'] == 'GENERIC':
        community = Community.get(name='EUDAT')
        result['community'] = str(community.id)
    elif rec['domain'] == 'LINGUISTICS':
        community = Community.get(name='CLARIN')
        result['community'] = str(community.id)
    else:
        raise Exception("Community not found for domain: `{}`".format(rec['domain']))
    result['alternate_identifiers'] = [{
        'alternate_identifier_type':'B2SHARE_V1_ID',
        'alternate_identifier': str(rec['record_id'])
    }]
    if 'PID' in rec.keys():
        result['alternate_identifiers'].append({
            'alternate_identifier_type':'ePIC_PID',
            'alternate_identifier': rec['PID']
        })
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
        resource_types = unique([translate[r] for r in rec['resource_type']])
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

def _save_file(logfile, old_url, filename):
    V1_URL_BASE = current_app.config.get('V1_URL_BASE')
    url1 = old_url.replace('https://b2share.eudat.eu/', V1_URL_BASE)
    url = url1.replace('/api/record/', '/record/')

    CHUNK_SIZE = 16 * 1024 * 1024 #download 16MB at a time
    current_app.logger.debug("Downloading %s" % url)
    gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
    finished = False
    f = open(filename, 'wb')
    try:
        u = urlopen(url, context=gcontext)
    except:
        current_app.logger.error("TIMEOUT trying to download %s" % url)
        logfile.write("\n********************")
        logfile.write("\nERROR: cannot open file URL for download: {}\n".format(url))
        logfile.write(traceback.format_exc())
        logfile.write("\n********************")
        return

    while not finished:
        try:
            chunk = u.read(CHUNK_SIZE)
            if chunk:
                f.write(chunk)
            else:
                finished = True
        except:
            logfile.write("\n********************")
            logfile.write("\nWARN: exception while reading file: {}\n".format(url))
            logfile.write(traceback.format_exc())
            logfile.write("\n********************")
            finished = True
    f.close()



def unique(lst):
    ret = []
    o = {}
    for l in lst:
        if l not in o:
            ret.append(l)
            o[l] = True
    return ret

assert unique([1, 1, 1, "a", 2, 2, "b", 3, "b", "a", 3]) == [1, "a", 2, "b", 3]
assert unique([1, 2, 1, 1, 3, "a", 2, 2, "b", "b", "a"]) == [1, 2, 3, "a", "b"]


def records_endpoint(x):
    x = x.rstrip('/')
    if x.endswith('/api/records'):
        return x
    if x.endswith('/api'):
        return urljoin(x, 'records')
    return urljoin(x, '/api/records')


def main_diff(v1_api_url, v1_access_token, v2_api_url, v2_access_token):
    v2_index = make_v2_index(v2_api_url, v2_access_token)
    for record in search_v1(v1_api_url, v1_access_token):
        test_record(record, v2_index)


def directly_list_v2_record_ids():
    size = 100
    page = 1
    while True:
        search = RecordsSearch().params(version=True)
        search = search[(page - 1) * size:page * size]
        search_result = search.execute()
        for record in search_result.hits.hits:
            if record.get('_index') == 'records-records':
                yield record
        if size * page < search_result.hits.total:
            page += 1
        else:
            break


def api_list_v2_record_ids(v2_api_url, v2_access_token):
    for page in range(1, MAX_PAGE):
        click.secho('    page {}'.format(page))
        params = {'page': page, 'size': 100}
        if v2_access_token:
            params['access_token'] = v2_access_token
        r = requests.get(records_endpoint(v2_api_url), params=params, verify=False)
        r.raise_for_status()
        search = json.loads(r.text)
        for record in search.get('hits', {}).get('hits', []):
            yield record


def make_v2_index(v2_api_url, v2_access_token):
    click.secho('*** Making v2 index')
    v2_index = {}
    records_generator = api_list_v2_record_ids(v2_api_url, v2_access_token) \
                        if v2_api_url else directly_list_v2_record_ids()
    for record in records_generator:
        # click.secho('    record {}'.format(record.get('id')))
        md = record.get('metadata') or record.get('_source')
        old_id = one_or_none(
            [x.get('alternate_identifier')
             for x in md.get('alternate_identifiers', {})
             if x.get('alternate_identifier_type') == 'B2SHARE_V1_ID'])
        if old_id:
            if v2_index.get(old_id):
                raise Exception("duplicated old id", record)
            v2_index[str(old_id)] = record
        else:
            click.secho('    nouveau', fg='yellow')

    click.secho('    v2 index ready, {} records'.format(len(v2_index)), fg='green')
    return v2_index


def search_v1(v1_api_url, v1_access_token):
    for page in range(0, MAX_PAGE-1):
        click.secho('Search v1 page {}'.format(page))
        params = {'page_offset': page, 'page_size': 100, 'access_token': v1_access_token}
        r = requests.get(records_endpoint(v1_api_url), params=params, verify=False)
        r.raise_for_status()
        search = json.loads(r.text).get('records')
        if len(search) == 0:
            return # no more records
        for record in search:
            yield record


def test_record(old_record, v2_index):
    recid = str(old_record.get('record_id'))

    if not v2_index.get(recid):
        click.secho('Record {} not migrated to v2'.format(recid), fg='red')
        return

    new_record = v2_index.get(recid)
    new_recid = new_record.get('id') or new_record.get('_id')
    click.secho('Diff record {} {}'.format(recid, new_recid))
    if not old_record.get('domain'):
        click.secho('    Record has no domain', fg='red')

    new_md = new_record.get('metadata') or new_record.get('_source')
    conv_record = _process_record(old_record)

    for key in ['alternate_identifiers', 'community', 'community_specific', 'contact_email',
                'contributors', 'creators', 'descriptions', 'keywords', 'language', 'license',
                'open_access', 'publication_date', 'publisher', 'resource_types', 'titles']:
        old_entry = conv_record.get(key)
        new_entry = new_md.get(key)
        if old_entry != new_entry and key != 'alternate_identifiers':
            try:
                if set(old_entry) == set(new_entry):
                    click.secho('   "{}" items have different order'.format(key), fg='red')
            except:
                click.secho('   "{}" items differ or have different order'.format(key), fg='red')
                print ("----")
                print ("v1: ")
                pprint(old_entry)
                print ("v2: ")
                pprint(new_entry)
                print ("----")
    open_access = conv_record.get('open_access')

    for oldfile in old_record.get('files', []):
        if not oldfile.get('name'):
            click.secho('    File with no name "{}"'.format(oldfile.get('url')), fg='red')
        else:
            newfile = one_or_none([f for f in new_record.get('files', [])
                                   if f.get('key') == oldfile.get('name')])
            if not newfile:
                click.secho('    File missing in new record "{}"'.format(oldfile.get('name')),
                            fg='red')
                if not open_access:
                    click.secho('        [object is private]')
            elif int(newfile.get('size')) != int(oldfile.get('size')):
                click.secho('    Different file sizes for "{}": old={} != new={}'
                            .format(oldfile.get('name'), oldfile.get('size'), newfile.get('size')),
                            fg='red')
    for newfile in new_record.get('files', []):
        oldfile = one_or_none([f for f in old_record.get('files', [])
                               if f.get('name') == newfile.get('key')])
        if not oldfile:
            click.secho('    File missing in new record "{}"'.format(oldfile.get('name')),
                        fg='red')
        elif int(newfile.get('size')) != int(oldfile.get('size')):
            click.secho('    Different file sizes for "{}": old={} != new={}'
                        .format(oldfile.get('name'), oldfile.get('size'), newfile.get('size')),
                        fg='red')

def one_or_none(lst):
    assert len(lst) <= 1
    return lst[0] if len(lst) == 1 else None
