# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2017 CERN.
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

"""B2Share utility functions."""

import copy
import uuid

from itertools import groupby
from urllib.parse import urlunsplit
from tabulate import tabulate


from sqlalchemy import UniqueConstraint, PrimaryKeyConstraint

from flask import current_app, jsonify, request

from elasticsearch_dsl.query import QueryString

from invenio_search import RecordsSearch, current_search
from invenio_accounts.models import User
from invenio_db import db


def add_to_db(instance, skip_if_exists=False, **fields):
    """Add a row to the database, optionally skip if it already exist.

    :param instance: the row to add to the database.
    :param skip_if_exists: if true, check if the row exists before
        inserting it.
    :param fields: override fields during comparison. Some fields might be null
        if the session is not flushed yet.
    """
    if not skip_if_exists:
        db.session.add(instance)
        return instance
    # Add only if the row does not already exist
    clazz = instance.__class__
    table = instance.__table__
    cols = None
    # Try retrieving the row using the first unique constraint
    unique_constraints = [
        cst for cst in table.constraints if cst.__class__ == UniqueConstraint
    ]
    if unique_constraints:
        cols = unique_constraints[0].columns
    else:
        # Otherwise use the first primary key constraint
        primary_constraints = [
            cst for cst in table.constraints
            if cst.__class__ == PrimaryKeyConstraint
        ]
        cols = primary_constraints[0].columns
    # Retrieve the row
    existing = db.session.query(clazz).filter(
        *[getattr(clazz, col.name) == (fields.get(col.name) or
                                       getattr(instance, col.name))
          for col in cols]
    ).one_or_none()

    if existing is not None:
        return existing

    # Add the row if it does not already exist
    db.session.add(instance)
    return instance


def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False


def get_base_url():
    return urlunsplit((
        current_app.config.get('PREFERRED_URL_SCHEME', 'http'),
        current_app.config['JSONSCHEMAS_HOST'],
        current_app.config.get('APPLICATION_ROOT') or '', '', ''
    ))


def jsonify_keeporder(json_schema):
    dosort = current_app.config['JSON_SORT_KEYS']
    current_app.config['JSON_SORT_KEYS'] = False
    res = jsonify(json_schema)
    current_app.config['JSON_SORT_KEYS'] = dosort
    return res


class ESSearch():
    """
    Class to search for deposit and drafts using invenio_search.
    """

    def __init__(self, app=current_app):
        self.app = app
        self.query = ''
        self.raw_results = {}
        self.results = []
        self.index = ['*']

    def _reset_(self):
        self.query = ''
        self.raw_results = {}
        self.results = []
        self.index = ['*']
        # if we do not flush and refresh we get cached data for the next query
        search = current_search
        search.flush_and_refresh("_all")


    def search(self, query, index=None):
        '''
        query: Querystring object (elasticsearch_dsl.query)
        index: ['records', 'deposits']
        '''
        self._reset_()
        index = index or self.index
        # check both deposits and records
        with current_app.app_context():
            search = RecordsSearch()
            # record -> owners , deposit -> _deposit.owners
            search = search.query(QueryString(query=query))
            results = search.execute().to_dict()
            self.raw_results = results.get('hits')
        self._process_results()

    def _process_results(self):
        '''
        extract hits from search results
        '''
        self.results = []
        for search_hits in self.raw_results.get('hits'):
            pid_dic = copy.deepcopy(search_hits)
            pid_dic['publication_state'] = search_hits.get(
                '_source').get('publication_state')
            pid_dic['b2rec'] = 'not published'
            for e in search_hits.get('_source').get('_pid'):
                pid_dic[e.get('type')] = e.get('value')
            self.results.append(pid_dic)

    def __str__(self):
        string = ""
        if self.raw_results['total'] > 0:
            INFO = sorted(self.results, key=lambda x: x['b2rec'])
            headers = ["vb2rec", "b2rec2", "id", "type", "publication state"]
            val = []
            for k, v in groupby(INFO, key=lambda x: (x['vb2rec'], x['b2rec'])):
                for i in list(v):
                    val.append([i.get('vb2rec'), i.get('b2rec'), i.get(
                        '_id'), i.get('_type'), i.get('publication_state')])
            string = str(tabulate(val, headers=headers))
        return string

    def matches(self):
        '''
        returns True is search has found something in the db
        '''
        return self.raw_results['total'] > 0

    def get_ownership_info(self):
        '''
        returns ownership info about deposits/records
        '''
        info = dict()
        if self.raw_results['total'] > 0:
            INFO = sorted(self.results, key=lambda x: (
                x['vb2rec'], x['b2rec']))
            for k, v in groupby(INFO, key=lambda x: (x['vb2rec'], x['b2rec'])):
                for i in list(v):
                    owners = i.get('_source').get('_deposit').get('owners') if i.get(
                        '_type') == 'deposit' else i.get('_source').get('owners')
                    owners_emails = [User.query.filter(
                        User.id.in_([w])).one_or_none() for w in owners]
                    info[i.get('_id')] = {'id': i.get('_id'), 'vb2rec': i.get('vb2rec'), 'b2rec': i.get('b2rec'), 'type': i.get('_type'), 'publication_state': i.get(
                        'publication_state'), 'owners': "\n".join([str(_) for _ in owners]), "owners_emails": "\n".join([e.email if e is not None else "Unknown user" for e in owners_emails])}
        return info

    def get_record_info(self):
        '''
        returns main info about deposits/records
        '''
        info = dict()
        if self.raw_results['total'] > 0:
            INFO = sorted(self.results, key=lambda x: (
                x['vb2rec'], x['b2rec']))
            for k, v in groupby(INFO, key=lambda x: (x['vb2rec'], x['b2rec'])):
                for i in list(v):
                    info[i.get('_id')] = {'id': i.get('_id'), 'vb2rec': i.get('vb2rec'), 'b2rec': i.get(
                        'b2rec'), 'type': i.get('_type'), 'publication_state': i.get('publication_state')}
        return info

    def get_all_info(self):
        '''
        returns all record/deposit info
        '''
        info = dict()
        if self.raw_results['total'] > 0:
            INFO = sorted(self.results, key=lambda x: (
                x['vb2rec'], x['b2rec']))
            for k, v in groupby(INFO, key=lambda x: (x['vb2rec'], x['b2rec'])):
                for i in list(v):
                    info[i.get('_id')] = i
        return info


def to_tabulate(input_dict):
    headers = list(input_dict[list(input_dict.keys())[0]].keys())
    val = []
    for keys in input_dict:
        val.append([input_dict[keys][t] for t in input_dict[keys].keys()])
    return str(tabulate(val, headers=headers))
