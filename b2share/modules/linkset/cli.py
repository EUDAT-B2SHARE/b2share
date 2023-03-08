# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2016 University of Tuebingen.
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

"""B2Share cli commands for Singposting feature."""


from __future__ import absolute_import, print_function
from urllib.parse import urlunsplit
import click

from flask.cli import with_appcontext
from flask import current_app, url_for

from b2share.modules.records.api import B2ShareRecord
from b2share.modules.records.utils import list_db_published_records

def get_base_url():
    return urlunsplit((
        current_app.config.get('PREFERRED_URL_SCHEME', 'http'),
        current_app.config['JSONSCHEMAS_HOST'], '', '', ''
    ))


def generate_linkset(record):
    pids = {x.get('type'):x.get('value') for x in record.get('_pid')}
    linkset_url = url_for('b2share_linkset.linkset', record_id=pids.get('b2rec'), _external=True)
    return {"pid":pids.get('b2rec'),"linkset_url":linkset_url}

def generate_multiple_linksets(records_list):
    data=[]
    for record in records_list:
        data.append(generate_linkset(record))
    return data

def check_linkset(client,linksets_list):
    err=0
    headers = [('Accept', 'application/json')]
    for record in linksets_list:
            record_get_res = client.get(record.get("linkset_url"), data='', headers=headers) 
            if record_get_res.status_code != 200:
                click.secho('---------------')
                click.secho("            PID: {}".format(record.get("pid")))
                click.secho("RESPONSE STATUS: {}".format(record_get_res.status_code))
                click.secho("    LINKSET URL: {}".format(record.get("linkset_url")))
                err+=1
    click.secho("  TOTAL:{}".format(len(linksets_list)))
    click.secho("  ERROR:{}".format(err))
    click.secho("CORRECT:{}".format(len(linksets_list)-err))


@click.group()
def linkset():
    """linkset commands."""


@linkset.command('check')
@with_appcontext
@click.argument('record-pid', required=False, type=str)
@click.option('--all','-a', required=False, is_flag=True, default=False)
def check(record_pid=None,all=False):
    """ Check if the Linkset is created and a json file is returned.

    :params record-pid: record id
    """
    if all:
        records_list=list_db_published_records()
    else:
        if record_pid is None:
           raise click.ClickException(
            "You need to provide a record id or set the flag to --all.")
        else:
            records_list=[B2ShareRecord.get_record(record_pid)]

    with current_app.test_request_context('/', base_url=get_base_url()+current_app.config.get('APPLICATION_ROOT')):
        linksets_list = generate_multiple_linksets(records_list)
    
    with current_app.test_client() as client:
        check_linkset(client,linksets_list)

@linkset.command('generate')
@with_appcontext
@click.argument('record-pid', required=True, type=str)
def generate(record_pid):
    """ Generate Linkset url given the record_id.

    :params record-pid: record id
    """
    with current_app.test_request_context('/', base_url=get_base_url()+current_app.config.get('APPLICATION_ROOT')):
        record=B2ShareRecord.get_record(record_pid)
        linkset_dict=generate_linkset(record)
        click.secho("\n".join(["{key} = {value}".format(key=k,value=val) for (k, val) in linkset_dict.items()]))
