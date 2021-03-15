# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2017 CERN, SurfsSara
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

"""B2Share migration command line interface.
These commands were designed only for the migration of data from
the instance hosted by CSC on https://b2share.eudat.eu .
WARNING - Operating these commands on local instances may severely impact data
integrity and/or lead to dysfunctional behaviour."""

import logging
import os
import requests
import traceback
from urllib.parse import urlunsplit, urljoin, urlsplit

import click
from flask.cli import with_appcontext
from flask import current_app
from invenio_db import db
from invenio_indexer.api import RecordIndexer
from invenio_records.api import Record

from .migration import (download_v1_data, process_v1_record, main_diff,
                        make_v2_index, records_endpoint, directly_list_v2_record_ids)

from b2share.modules.records.indexer import record_to_index

@click.group()
def migrate():
    """Migration commands. WARNING csc only."""



@migrate.command()
@with_appcontext
@click.option('-v', '--verbose', count=True)
@click.option('-d', '--download', is_flag=True, default=False)
@click.option('-l', '--limit', default=None)
@click.argument('token')
@click.argument('download_directory')
def import_v1_data(verbose, download, token, download_directory,limit):
    click.secho("Importing data to the current instance")
    logger = logging.getLogger("sqlalchemy.engine")
    logger.setLevel(logging.ERROR)

    logfile = open(current_app.config.get('MIGRATION_LOGFILE'), 'a')
    logfile.write("\n\n\n~~~ Starting import task download={} limit={}"
                  .format(download, limit))
    if os.path.isdir(download_directory):
        os.chdir(download_directory)
    else:
        raise click.ClickException("%s does not exist or is not a directory. If you want to import "
                                   "records specify an empty, existing directory."
                                   % download_directory)
    if limit and not download:
        raise click.ClickException("Limit can only be set with download")

    if download:
        filelist = os.listdir('.')
        if len(filelist) > 0:
            click.secho("!!! Downloading data into existing directory, "
                        "overwriting previous data", fg='red')
        click.secho("----------")
        click.secho("Downloading data into directory %s" % download_directory)
        if limit is not None:
            limit = int(limit)
            click.secho("Limiting to %d records for debug purposes" % limit)
        download_v1_data(token, download_directory, logfile, limit)
    
    indexer = RecordIndexer(record_to_index=record_to_index)
    dirlist = os.listdir('.')

    click.secho("-----------")
    click.secho("Processing %d downloaded records" % (len(dirlist)))
    base_url = urlunsplit((
        current_app.config.get('PREFERRED_URL_SCHEME', 'http'),
        # current_app.config['SERVER_NAME'],
        current_app.config['JSONSCHEMAS_HOST'],
        current_app.config.get('APPLICATION_ROOT') or '', '', ''
    ))
    for d in dirlist:
        try:
            process_v1_record(d, indexer, base_url, logfile)
        except:
            logfile.write("\n********************")
            logfile.write("\nERROR: exception while processing record /{}/___record.json___\n"
                          .format(d))
            logfile.write(traceback.format_exc())
            logfile.write("\n********************")

    logfile.close()


@migrate.command()
@with_appcontext
@click.option('-u', '--update', is_flag=True, default=False)
@click.argument('base_url')
def check_pids(update, base_url):
    """ Checks and optionally fixes ePIC PIDs from records in the `base_url`.

        The ePIC PIDs in the first 1000 records of the `base_url` B2SHARE site
        are checked. The PIDs are extracted from the main ePIC_PID field and
        the alternative_identifiers fields (based on the type being equal to
        'ePIC_PID'). Only the PIDs starting with the configured ePIC prefix are
        considered. If the PID does not point to the record it's contained in,
        then an error message is generated. When the `-u` argument is used, the
        current configuration variables are used to update the PID with the
        correct target URL.
    """
    epic_base_url = str(current_app.config.get('CFG_EPIC_BASEURL'))
    epic_username = str(current_app.config.get('CFG_EPIC_USERNAME'))
    epic_password = str(current_app.config.get('CFG_EPIC_PASSWORD'))
    epic_prefix = str(current_app.config.get('CFG_EPIC_PREFIX'))

    click.secho('Checking epic pids for all records')
    record_search = requests.get(urljoin(base_url, "api/records"),
                                 {'size': 1000, 'page': 1},
                                 verify=False)
    records = record_search.json()['hits']['hits']
    for rec in records:
        recid = str(rec['id'])
        click.secho('\n--- Checking epic pids for record {}'.format(recid))
        rec_url = rec['links']['self'].replace("/api/records/", "/records/")
        metadata = rec['metadata']
        epic_list = [aid['alternate_identifier']
                     for aid in metadata.get('alternate_identifiers', [])
                     if aid['alternate_identifier_type'] == 'ePIC_PID']
        if metadata.get('ePIC_PID'):
            epic_list.append(metadata.get('ePIC_PID'))
        for epic_url in epic_list:
            pid = urlsplit(epic_url).path.strip('/')
            if not pid.startswith(epic_prefix):
                continue # is not one of our pids
            click.secho('    {}'.format(pid))
            target_request = requests.get(epic_url, allow_redirects=False)
            if target_request.status_code < 300 or target_request.status_code >= 400:
                click.secho('Record {}: error retrieving epic pid information: {}'
                            .format(recid, epic_url),
                            fg='yellow', bold=True)
                continue
            target_url = target_request.headers.get('Location')
            if is_same_url(target_url, rec_url):
                continue

            click.secho('Record {}: error: bad epic pid: {}'.format(recid, epic_url),
                        fg='red', bold=True)
            if update:
                change_req = requests.put(urljoin(epic_base_url, pid),
                                          json=[{'type': 'URL', 'parsed_data': rec_url}],
                                          auth=(epic_username, epic_password),
                                          headers={'Content-Type': 'application/json',
                                                   'Accept': 'application/json'})
                if change_req.status_code >= 300:
                    click.secho('Record {}: error setting epic pid target url: {}, error code {}'
                                .format(recid, epic_url, change_req.status_code),
                                fg='red', bold=True)
                else:
                    click.secho('Record {}: fixed epic pid target url: {}'
                                .format(recid, epic_url),
                                fg='green', bold=True)


def is_same_url(url1, url2):
    u1 = urlsplit(url1)
    u2 = urlsplit(url2)
    return u1.scheme == u2.scheme and u1.netloc == u2.netloc and \
        u1.path == u2.path and u1.query == u2.query


@migrate.command()
@click.argument('v1_api_url')
@click.argument('v1_access_token')
@click.argument('v2_api_url')
@click.argument('v2_access_token')
@with_appcontext
def diff_sites(v1_api_url, v1_access_token, v2_api_url, v2_access_token):
    main_diff(v1_api_url, v1_access_token, v2_api_url, v2_access_token)


@migrate.command()
@with_appcontext
def swap_pids():
    """ Fix the invalid creation of new ePIC_PIDs for migrated files. Swaps
    with the old b2share v1 PID that we stored in alternate_identifiers and
    puts the wrongly created ePIC_PID in alternate_identifiers. Note this
    creates a new version of the invenio record (at the time of writing we do
    not show the latest version of invenio record objects)
    """
    for search_record in directly_list_v2_record_ids():
        recid = search_record.get('_id')
        inv_record = Record.get_record(recid)
        if inv_record.revision_id >= 1:
            print ("Skipping record {}: too many revisions ({}), "
                   "may have been already updated".format(
                    recid, inv_record.revision_id))
            continue
        aids = None
        if 'alternate_identifiers' in inv_record.keys():
            aids = inv_record['alternate_identifiers']
            found = False
            found_v1_id = False
            for aid in aids:
                if aid['alternate_identifier_type']=='B2SHARE_V1_ID':
                    found_v1_id = True
                if aid['alternate_identifier_type']=='ePIC_PID':
                    new_pid = aid['alternate_identifier']
                    _pid = inv_record['_pid']
                    for pid in _pid:
                        if pid['type']=='ePIC_PID':
                            old_pid = pid['value']
                            found = True
                            break
                    break
            found = found and found_v1_id
            if not found:
                error_msg = """***** INFO - this record does not have ePIC_PID
                    in _pid or alternate_identifiers or does not have a
                    B2SHARE_V1_ID in alternate_identifiers"""
                print(error_msg)
                print(inv_record['titles'])
                print(recid)
                print("********")
            else:
                print("SWAPPING %s %s" % (old_pid, new_pid))
                for pid in inv_record['_pid']:
                    if pid['type']=='ePIC_PID':
                        pid['value']=new_pid
                        break
                for aid in inv_record['alternate_identifiers']:
                    if aid['alternate_identifier_type']=='ePIC_PID':
                        aid['alternate_identifier']=old_pid
                        break
                inv_record.commit()
                db.session.commit()


@migrate.command()
@with_appcontext
@click.argument('v1_api_url')
@click.argument('v1_access_token')
@click.argument('v2_api_url')
@click.argument('v2_access_token')
def extract_alternate_identifiers(v1_api_url, v1_access_token, v2_api_url, v2_access_token):
    """Extracting alternate identifiers from v1 records"""
    v2_index = make_v2_index(v2_api_url, v2_access_token)

    click.secho('Extracting alternate identifiers from v1 records')
    params = {'access_token': v1_access_token, 'page_size': 100}
    for page in range(0, 7):
        params['page_offset'] = page
        req = requests.get(records_endpoint(v1_api_url), params=params, verify=False)
        req.raise_for_status()
        recs = req.json().get('records')
        for record in recs:
            recid = str(record.get('record_id'))
            alternate_identifier = str(record.get('alternate_identifier'))
            if not alternate_identifier:
                continue
            click.secho("alternate_identifier: {}".format(alternate_identifier))
            click.secho("    domain: {}".format(record.get('domain')))
            click.secho("    old record ID: {}".format(recid))
            v2 = v2_index.get(recid)
            if v2:
                click.secho("    new record ID: {}".format(v2.get('id')))
                click.secho("    new record URL: {}".format(v2.get('links', {}).get('self')))
                click.secho("    new record PID: {}".format(v2.get('metadata', {}).get('ePIC_PID')))


@migrate.command()
@with_appcontext
@click.argument('v1_api_url')
@click.argument('v1_access_token')
# @click.argument('v2_api_url')
def add_missing_alternate_identifiers(v1_api_url, v1_access_token):
    """Add missing alternate identifiers from v1 records to the published v2
       records in the current instance"""
    v2_index = make_v2_index(None, None) # make index of current site
    # v2_index = make_v2_index(v2_api_url, None)

    click.secho('Adding missing alternate identifiers from v1 records')
    params = {'access_token': v1_access_token, 'page_size': 100}
    for page in range(0, 7):
        params['page_offset'] = page
        req = requests.get(records_endpoint(v1_api_url), params=params, verify=False)
        req.raise_for_status()
        for v1_record in req.json().get('records'):
            v1_recid = str(v1_record.get('record_id'))
            alternate_identifier = str(v1_record.get('alternate_identifier', '')).strip()
            if not alternate_identifier:
                continue
            ai_type = guess_alternate_identifier_type(alternate_identifier)
            click.secho("alternate_identifier: {}"
                        "\n\told id: {}\n\taltid type: {}".format(
                            alternate_identifier, v1_recid, ai_type))

            if not v2_index.get(v1_recid):
                click.secho("\tcannot find recid {}".format(v1_recid), fg='red')
                continue
            record_search = v2_index.get(v1_recid)
            v2_recid = record_search.get('id') or record_search.get('_id')
            record = Record.get_record(v2_recid)
            # record = v2_index.get(v1_recid).get('metadata')
            exists = [ai for ai in record.get('alternate_identifiers', [])
                      if ai.get('alternate_identifier') == alternate_identifier]
            if exists:
                click.secho("\talready present in record: {}".format(v2_recid))
            else:
                ais = record.get('alternate_identifiers', [])
                new_ai = {'alternate_identifier': alternate_identifier,
                          'alternate_identifier_type': ai_type}
                ais.insert(0, new_ai)
                record['alternate_identifiers'] = ais
                record.commit()
                click.secho("\tupdated new record: {}".format(v2_recid))
        db.session.commit()


def guess_alternate_identifier_type(aid):
    for x in ['http://dx.doi.org/', 'http://doi.org/', 'doi.org', 'dx.doi.org', 'doi.', '10.']:
        if aid.startswith(x):
            return 'DOI'
    if aid.startswith('URN:'):
        return 'URN'
    if aid.startswith('http://') or aid.startswith('https://'):
        return 'URL'
    return 'Other'
