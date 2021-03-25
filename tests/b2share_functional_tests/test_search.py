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

"""Test for specific issues."""

from __future__ import absolute_import, print_function

import json
import pytest
from b2share.modules.deposit.api import PublicationStates
from invenio_search import current_search
from flask import url_for as flask_url_for
from invenio_db import db
from b2share.modules.communities.api import Community
from tests.b2share_unit_tests.helpers import (
    create_user, generate_record_data
)


def test_make_record_with_no_file_and_search(app, test_communities,
                                             login_user):
    '''Test for issue https://github.com/EUDAT-B2SHARE/b2share/issues/1073'''
    def url_for(*args, **kwargs):
        with app.app_context():
            return flask_url_for(*args, **kwargs)

    with app.app_context():
        community_name = 'MyTestCommunity1'
        record_data = generate_record_data(community=community_name)

        allowed_user = create_user('allowed')
        community = Community.get(name=community_name)
        com_admin = create_user('com_admin', roles=[community.admin_role])
        db.session.commit()

    with app.test_client() as client:
        login_user(allowed_user, client)
        headers = [('Content-Type', 'application/json'),
                   ('Accept', 'application/json')]
        patch_headers = [('Content-Type', 'application/json-patch+json'),
                         ('Accept', 'application/json')]

        # create record without files
        draft_create_res = client.post(
            url_for('b2share_records_rest.b2rec_list'),
            data=json.dumps(record_data), headers=headers)
        assert draft_create_res.status_code == 201
        draft_create_data = json.loads(
            draft_create_res.get_data(as_text=True))

        # submit the record
        draft_submit_res = client.patch(
            url_for('b2share_deposit_rest.b2dep_item',
                    pid_value=draft_create_data['id']),
            data=json.dumps([{
                "op": "replace", "path": "/publication_state",
                "value": PublicationStates.submitted.name
            }]),
            headers=patch_headers)
        assert draft_submit_res.status_code == 200

    with app.test_client() as client:
        login_user(com_admin, client)
        # publish record
        draft_publish_res = client.patch(
            url_for('b2share_deposit_rest.b2dep_item',
                    pid_value=draft_create_data['id']),
            data=json.dumps([{
                "op": "replace", "path": "/publication_state",
                "value": PublicationStates.published.name
            }]),
            headers=patch_headers)
        assert draft_publish_res.status_code == 200
        draft_publish_data = json.loads(
            draft_publish_res.get_data(as_text=True))

        # get record
        record_get_res = client.get(
            url_for('b2share_records_rest.b2rec_item',
                    pid_value=draft_publish_data['id']),
            headers=headers)
        assert record_get_res.status_code == 200
        record_get_data = json.loads(
            record_get_res.get_data(as_text=True))

    with app.test_client() as client:
        # refresh index to make records searchable
        with app.app_context():
            current_search._client.indices.refresh()

    with app.test_client() as client:
        # test search, for crashes
        record_search_res = client.get(
            url_for('b2share_records_rest.b2rec_list'),
            data='',
            headers=headers)
        assert record_search_res.status_code == 200
        record_search_data = json.loads(
            record_search_res.get_data(as_text=True))
        assert len(record_search_data['hits']['hits']) == 1
        record_hit = record_search_data['hits']['hits'][0]

        # TODO: the following assert should work:
        # assert record_hit == record_get_data
        # -- but currently it doesn't because records with no files
        #    do not have a 'files' link

        assert record_hit['metadata'] == record_get_data['metadata']
