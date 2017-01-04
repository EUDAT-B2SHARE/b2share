# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2016 CERN, SurfsSara
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

"""B2Share demo command line interface."""

from __future__ import absolute_import, print_function

import json
import logging
import os
import traceback
from shutil import rmtree
import pathlib
import requests
from urllib.parse import urlunsplit, urljoin, urlsplit
from shutil import copyfile

import click
from flask_cli import with_appcontext
from flask import current_app
from invenio_db import db
from invenio_files_rest.models import Location
from invenio_indexer.api import RecordIndexer
from invenio_records.api import Record

from .helpers import load_demo_data, download_v1_data, process_v1_record
from . import config as demo_config


@click.group(chain=True)
def demo():
    """Demonstration commands."""


@demo.command()
@with_appcontext
@click.option('-v', '--verbose', count=True)
def load_data(verbose):
    """Load demonstration data."""
    # add files location
    files_path = os.path.join(current_app.instance_path, 'files')
    if os.path.exists(files_path):
        rmtree(files_path)
    os.mkdir(files_path)
    with db.session.begin_nested():
        db.session.add(Location(name='local',
                                uri=pathlib.Path(files_path).as_uri(),
                                default=True))
        # load the demo
        load_demo_data(
            os.path.join(os.path.dirname(os.path.realpath(__file__)),
                         'data'),
            verbose=verbose)
    db.session.commit()


@demo.command()
@with_appcontext
@click.option('-v', '--verbose', count=True)
@click.option('-f', '--force', is_flag=True, default=False,
              help='Overwrite the current configuration if it exists.')
def load_config(verbose, force):
    """Copy the demo configuration to the application instance directory."""
    if verbose > 0:
        click.secho('Loading demo configuration.', fg='yellow', bold=True)
    instance_config_path = os.path.join(
        '{}'.format(current_app.instance_path),
        '{}.cfg'.format(current_app.name))
    if os.path.exists(instance_config_path):
        if not force:
            raise click.ClickException(
                'Application configuration file "{}" already exists. Use '
                'the -f option to overwrite it.'.format(
                    instance_config_path))
        elif verbose > 0:
            click.secho('Configuration file exists. Overriding it!',
                        fg='red', bold=True)
    demo_config_path = os.path.join(os.path.dirname(__file__), 'config.py')
    copyfile(demo_config_path, instance_config_path)
    if verbose > 0:
        click.secho('Configuration file "{}" created.'.format(
            instance_config_path), fg='green')


@demo.command()
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
    indexer = RecordIndexer(record_to_index=lambda record: ('records', 'record'))
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

@demo.command()
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


@demo.command()
@with_appcontext
@click.option('-u', '--update', is_flag=True, default=False)
@click.argument('base_url')
def swap_pids(update, base_url):
    """ Fix the invalid creation of new ePIC_PIDs for migrated files. Swaps with the old b2share v1 PID that we stored in alternate_identifiers and puts the wrongly created ePIC_PID in alternate_identifiers. Note this creates a new version of the invenio record (at the time of writing we do not show the latest version of invenio record objects)
    """
    record_search = requests.get(urljoin(base_url, "api/records"),
                                 {'size': 1000, 'page': 1},
                                 verify=False)
    records = record_search.json()['hits']['hits']
    for rec in records:
        inv_record = Record.get_record(rec['id'])
        aids = None
        if 'alternate_identifiers' in inv_record.keys():
            aids = inv_record['alternate_identifiers']
            found = False
            for aid in aids:
                if aid['alternate_identifier_type']=='ePIC_PID':
                    new_pid = aid['alternate_identifier']
                    _pid = inv_record['_pid']
                    for pid in _pid:
                        if pid['type']=='ePIC_PID':
                            old_pid = pid['value']
                            found = True
            if not found:
                error_msg = """***** ERROR - this record does not have ePIC_PID 
                    in alternate_identifiers"""
                print(error_msg)
                print(inv_record['titles'])
                print(rec['id'])
                print("********")
            else:
                print("SWAPPING %s %s" % (old_pid, new_pid))
                for pid in inv_record['_pid']:
                    if pid['type']=='ePIC_PID':
                        pid['value']=new_pid
                for aid in inv_record['alternate_identifiers']:
                    if aid['alternate_identifier_type']=='ePIC_PID':
                        aid['alternate_identifier']=old_pid
                inv_record.commit()
                db.session.commit()
        

@demo.command()
@with_appcontext
def diff_sites():
    from .migration import main_diff
    main_diff()
