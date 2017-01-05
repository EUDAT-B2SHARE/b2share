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

from .helpers import resolve_block_schema_id, _match_community_specific_metadata
from .helpers import _process_record as convert_old_record_to_new



URL_SEARCH_NEW = "https://b2share.eudat.eu/api/records/"
URL_SEARCH_OLD = "https://eudatis.csc.fi/api/records"

TOKEN_NEW = None
TOKEN_OLD = None

MAX_PAGE = 8


def main_diff():
    assert TOKEN_NEW and TOKEN_OLD
    # v2_index = {}
    v2_index = make_v2_index(TOKEN_NEW)
    for record in search_v1(TOKEN_OLD):
        test_record(record, v2_index)


def make_v2_index(v2_access_token):
    click.secho('*** Making v2 index')
    v2_index = {}
    for page in range(1, MAX_PAGE):
        click.secho('    page {}'.format(page))
        params = {'page': page, 'size': 100, 'access_token': v2_access_token}
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


def search_v1(v1_access_token):
    click.secho('*** Diffing')
    for page in range(0, MAX_PAGE-1):
        click.secho('Page {}'.format(page))
        params = {'page_offset': page, 'page_size': 100, 'access_token': v1_access_token}
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

def one_or_none(lst):
    assert len(lst) <= 1
    return lst[0] if len(lst) == 1 else None
