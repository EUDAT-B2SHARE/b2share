# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2016 University of Tuebingen, CERN.
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

"""Test Invenio integration with submission tests."""

from __future__ import absolute_import, print_function

import json
from copy import deepcopy

import pytest

from flask import url_for
from invenio_db import db
from b2share.modules.b2share_demo.helpers import resolve_community_id, resolve_block_schema_id
from tests.b2share_unit_tests.helpers import create_user


json_headers = [('Content-Type', 'application/json'),
                ('Accept', 'application/json')]

jsonpatch_headers = [('Content-Type', 'application/json-patch+json'),
                     ('Accept', 'application/json')]


def make_record_json():
    record_data = {
        'owner': '',
        'titles': [{'title':'My Errorneous BBMRI record'}],
        'community': '$COMMUNITY_ID[MyTestCommunity1]',
        'open_access': True,
        'creators': [{'creator_name':'Anonymous'}],
        'community_specific': {
            '$BLOCK_SCHEMA_ID[MyTestSchema]': {
                'study_design': ['Case-control']
            }
        }
    }
    record_str = json.dumps(record_data)
    record_str = resolve_community_id(record_str)
    record_str = resolve_block_schema_id(record_str)
    return json.loads(record_str)


record_list_url = (lambda **kwargs:
                   url_for('b2share_records_rest.b2rec_list',
                           **kwargs))


def test_submission_error(app, test_communities, login_user):
    with app.app_context():
        # FIXME test permissions
        with app.test_client() as client:
            the_owner = create_user('TheOwner')
            db.session.commit()
            login_user(the_owner, client)

            record_json = make_record_json()
            # FIXME: fix these tests. #userforumrush
            # _test_deposition_error(client, record_json)

            # record_url, record_data = post_record(client, record_json)
            # _test_patch_error(client, record_url, record_data)
            # _test_put_error(client, record_url, record_data)


def _test_deposition_error(client, record_json_):
    record_json = deepcopy(record_json_)
    record_json = record_json_.copy()
    del record_json['titles']
    record_create_res = client.post(record_list_url(),
                                    data=json.dumps(record_json),
                                    headers=json_headers)
    assert record_create_res.status_code == 400
    error = json.loads(record_create_res.get_data(as_text=True))
    assert len(error['errors']) == 1 and error['errors'][0]['field'] == 'titles'


def post_record(client, record_json):
    record_create_res = client.post(record_list_url(),
                                    data=json.dumps(record_json),
                                    headers=json_headers)
    assert record_create_res.status_code == 201
    record_create_data = json.loads(record_create_res.get_data(as_text=True))
    record_url = url_for('b2share_records_rest.b2rec_item',
                         pid_value=record_create_data['id'])
    return (record_url, record_create_data)


def _test_patch_error(client, record_url, record_data):
    _test_patch_error_1(client, record_url,
                        [{
                            'op': 'replace',
                            'path': '/titles',
                            'value': True
                        }])
    _test_patch_error_1(client, record_url,
                        [{
                            'op': 'remove',
                            'path': '/open_access'
                        }])
    _test_patch_error_1(client, record_url,
                        [{
                            'op': 'add',
                            'path': '/invented_field',
                            'value': 'oh yes'
                        }])
    _test_patch_error_1(client, record_url,
                        [{
                            'op': 'add',
                            'path': '/embargo_date',
                            'value': True
                        }])
    _test_get_record_returns_original(client, record_url, record_data)

def _test_patch_error_1(client, record_url, patch):
    record_patch_res = client.patch(record_url,
                                    data=json.dumps(patch),
                                    headers=jsonpatch_headers)
    assert record_patch_res.status_code == 400
    error = json.loads(record_patch_res.get_data(as_text=True))
    assert len(error['errors']) == 1 and error['errors'][0]['field'] == patch[0]['path'][1:]



def _test_put_error(client, record_url, record_data):
    record_err_data = deepcopy(record_data['metadata'])
    record_err_data.update({'open_access': "oh no"})
    _test_put_error_1(client, record_url, 'open_access', record_err_data)

    record_err_data = deepcopy(record_data['metadata'])
    record_err_data.update({'embargo_date': 15})
    _test_put_error_1(client, record_url, 'embargo_date', record_err_data)

    record_err_data = deepcopy(record_data['metadata'])
    record_err_data.update({'invented_field': "oh yes"})
    _test_put_error_1(client, record_url, 'invented_field', record_err_data)

    record_err_data = deepcopy(record_data['metadata'])
    del record_err_data['titles']
    _test_put_error_1(client, record_url, 'titles', record_err_data)

    _test_get_record_returns_original(client, record_url, record_data)

def _test_put_error_1(client, record_url, field, record_err_data):
    record_put_res = client.put(record_url,
                                data=json.dumps(record_err_data),
                                headers=json_headers)
    assert record_put_res.status_code == 400
    error = json.loads(record_put_res.get_data(as_text=True))
    assert len(error['errors']) == 1 and error['errors'][0]['field'] == field


def _test_get_record_returns_original(client, record_url, record_expected_data):
    record_get_res = client.get(record_url, headers=json_headers)
    assert record_get_res.status_code == 200
    record_get_data = json.loads(
        record_get_res.get_data(as_text=True))
    assert '_internal' not in record_get_data['metadata']
    assert record_get_data == record_expected_data
