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
import requests
import click

from pprint import pprint
from b2share.modules.communities import Community

from .helpers import resolve_block_schema_id



URL_SEARCH_NEW = "https://b2share.eudat.eu/api/records/"
URL_SEARCH_OLD = "https://eudatis.csc.fi/api/records"

TOKEN_NEW = None
TOKEN_OLD = None

MAX_PAGE = 8


def main_diff():
    assert TOKEN_NEW and TOKEN_OLD
    # v2_index = {}
    v2_index = make_v2_index()
    for record in search_v1():
        test_record(record, v2_index)


def make_v2_index():
    click.secho('*** Making v2 index')
    v2_index = {}
    for page in range(1, MAX_PAGE):
        click.secho('    page {}'.format(page))
        params = {'page': page, 'size': 100, 'access_token': TOKEN_NEW}
        r = requests.get(URL_SEARCH_NEW, params=params, verify=False)
        r.raise_for_status()
        search = json.loads(r.text)
        for record in search.get('hits', {}).get('hits', []):
            # click.secho('    record {}'.format(record.get('id')))
            md = record.get('metadata')
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


def search_v1():
    click.secho('*** Diffing')
    for page in range(0, MAX_PAGE-1):
        click.secho('Page {}'.format(page))
        params = {'page_offset': page, 'page_size': 100, 'access_token': TOKEN_OLD}
        r = requests.get(URL_SEARCH_OLD, params=params, verify=False)
        r.raise_for_status()
        search = json.loads(r.text).get('records')
        if len(search) == 0:
            return # no more records
        for record in search:
            yield record


def test_record(old_record, v2_index):
    recid = str(old_record.get('record_id'))
    click.secho('Test record {}'.format(recid))

    if not old_record.get('domain'):
        click.secho('    Record has no domain', fg='red')

    if not v2_index.get(recid):
        click.secho('    Record not migrated to v2', fg='red')
        return

    new_record = v2_index.get(recid)
    new_md = new_record.get('metadata')
    conv_record = convert_old_record_to_new(old_record)

    for key in ['alternate_identifiers', 'community', 'community_specific', 'contact_email',
                'contributors', 'creators', 'descriptions', 'keywords', 'language', 'license',
                'open_access', 'publication_date', 'publisher', 'resource_types', 'titles']:
        old_entry = conv_record.get(key)
        new_entry = new_md.get(key)
        if old_entry != new_entry:
            try:
                if set(old_entry) == set(new_entry):
                    click.secho('   "{}" items have different order'.format(key), fg='red')
            except:
                click.secho('   "{}" items differ or have different order'.format(key), fg='red')
                # pprint(old_entry)
                # pprint(new_entry)

    for oldfile in old_record.get('files', []):
        if not oldfile.get('name'):
            click.secho('    File with no name "{}"'.format(oldfile.get('url')), fg='red')
        else:
            newfile = one_or_none([f for f in new_record.get('files', [])
                                   if f.get('key') == oldfile.get('name')])
            if not newfile:
                click.secho('    File missing in new record "{}"'.format(oldfile.get('name')),
                            fg='red')
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


def convert_old_record_to_new(rec):
    #rec is dict representing 1 record
    #from json donwloaded from b2share_v1 API
    result = {}
    for k in ['open_access', 'contact_email', 'publication_date']:
        result[k] = rec[k]

    result['license'] = {'license': rec['licence']}

    result['titles'] = [{'title':rec['title']}]

    result['descriptions'] = [{'description_type': 'Abstract',
                               'description': rec['description']}]

    result['contributors'] = [{'contributor_type': "Other", 'contributor_name': c}
                              for c in list(set(rec['contributors']))]

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

    alternate_id = {'alternate_identifier_type':'B2SHARE_V1_ID',
                    'alternate_identifier': str(rec['record_id'])}
    result['alternate_identifiers'] = [alternate_id]

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
        resource_types = list(set([translate[r] for r in rec['resource_type']]))
        result['resource_types'] = []
        for rt in resource_types:
            element = {'resource_type_general':rt}
            result['resource_types'].append(element)

    if not result['resource_types']:
        result['resource_types'] = [{'resource_type_general': "Other"}]

    result['community_specific'] = {}
    if 'domain_metadata' in rec.keys():
        result.update(_match_community_specific_metadata(rec, community))
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


def one_or_none(lst):
    assert len(lst) <= 1
    return lst[0] if len(lst) == 1 else None
