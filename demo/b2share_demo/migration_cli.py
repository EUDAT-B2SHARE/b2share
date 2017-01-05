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
import requests
from urllib.parse import urljoin

import click
from flask_cli import with_appcontext
from flask import current_app
from invenio_db import db
from invenio_files_rest.models import Location
from invenio_indexer.api import RecordIndexer
from invenio_records.api import Record


@click.group()
def migrate():
    """Migration commands. WARNING csc only."""

@migrate.command()
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
            found = found and found_v1_id
            if not found:
                error_msg = """***** INFO - this record does not have ePIC_PID 
                    in _pid or alternate_identifiers or does not have a 
                    B2SHARE_V1_ID in alternate_identifiers"""
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
