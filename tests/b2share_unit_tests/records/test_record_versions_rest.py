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

"""Test B2Share versioning REST API."""

from types import SimpleNamespace
import json
import time
from flask import url_for

from invenio_search.proxies import current_search_client
from b2share.modules.deposit.api import PublicationStates


headers = [('Content-Type', 'application/json'),
           ('Accept', 'application/json')]
patch_headers = [('Content-Type', 'application/json-patch+json'),
                 ('Accept', 'application/json')]


def test_get_and_search_versions(app, test_records_data, test_users, login_user):
    """Test search of records with versions."""

    login = SimpleNamespace()
    login.normal = lambda client: login_user(test_users['normal'], client)
    login.owner = lambda c: login_user(test_users['deposits_creator'], c)
    login.admin = lambda client: login_user(test_users['admin'], client)

    data = test_records_data

    with app.app_context():
        # create and publish some records in a version chain
        chain_list = []
        for _ in range(3):
            chain = []
            chain.append(make_record(app, login, data[0]))
            chain.append(make_record(app, login, data[1], version_of=chain[0]))
            chain.append(make_record(app, login, data[2], version_of=chain[1]))
            chain.append(make_record(app, login, data[0], version_of=chain[2]))
            chain.append(make_record(app, login, data[1], version_of=chain[3]))
            chain.append(make_record(app, login, data[2], version_of=chain[4]))
            chain_list.append(chain)
        
        # Test GET /api/records/<ID>/versions/

        for chain in chain_list:
            rec0 = get_record(app, chain[0])
            versions0 = get_request(app, rec0['links']['versions'])['versions']
            assert [(v['id']) for v in versions0] == [(r['id']) for r in chain]
            
            for r in chain[1:]:
                rec = get_record(app, r)
                versions = get_request(app, rec['links']['versions'])['versions']
                assert versions0 == versions
        current_search_client.indices.refresh()
        
        # Test search
        search_res = search(app, login, 'bbmri')
        hits = search_res['hits']['hits']
        # we only want one hit per version chain (aggregation)
        assert len(hits) == len(chain_list)


def search(app, login, query):
    """Search all records."""
    url = url_for('b2share_records_rest.b2rec_list')
    if query:
        url += "?q="+query
    with app.test_client() as client:
        res = client.get(url, headers=headers)
        assert res.status_code == 200
        search_json = json.loads(res.get_data(as_text=True))
        return search_json


def get_record(app, rec):
    """Retrieve a record via the REST API."""
    url = url_for('b2share_records_rest.b2rec_item', pid_value=rec['id'])
    with app.test_client() as client:
        res = client.get(url, headers=headers)
        assert res.status_code == 200
        res_json = json.loads(res.get_data(as_text=True))
        links = res_json['links']
        return res_json

def get_request(app, url):
    """Execute a get request."""
    with app.test_client() as client:
        res = client.get(url, headers=headers)
        assert res.status_code == 200
        return json.loads(res.get_data(as_text=True))


def make_record(app, login, data, version_of=None):
    """Create a record."""
    # TODO: replace this with the create_record helper. We don't need to create
    # the record via the REST API for this test.
    with app.test_client() as client:
        # Create the record draft
        login.owner(client)
        url = url_for('b2share_records_rest.b2rec_list')
        if version_of:
            url += "?version_of="+version_of['id']
        res = client.post(url, data=json.dumps(data), headers=headers)
        res_json = json.loads(res.get_data(as_text=True))
        assert res.status_code == 201
        if version_of:
            assert 'versions' in res_json['links']
        draft_url = res_json['links']['self']

    # submits the record
    with app.test_client() as client:
        login.owner(client)
        patch = [{
            "op": "replace", "path": "/publication_state",
            "value": PublicationStates.submitted.name,
        }]
        res = client.patch(draft_url, data=json.dumps(patch), headers=patch_headers)
        assert 200 <= res.status_code <= 201

    # publish the record
    with app.test_client() as client:
        login.admin(client)
        patch[0]['value'] = PublicationStates.published.name
        res = client.patch(draft_url, data=json.dumps(patch), headers=patch_headers)
        assert 200 <= res.status_code <= 201
        deposit_json_data = json.loads(res.get_data(as_text=True))
        if version_of:
            assert 'versions' in deposit_json_data['links']

    # Test retrieving the record
    url = url_for('b2share_records_rest.b2rec_item', pid_value=deposit_json_data['id'])
    with app.test_client() as client:
        login.normal(client)
        res = client.get(url, headers=headers)
        assert res.status_code == 200
        res_json = json.loads(res.get_data(as_text=True))
        if version_of:
            assert 'versions' in res_json['links']
        return res_json
