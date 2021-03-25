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

"""Test B2Share deposit module's versioning REST API."""

import json
import uuid
from flask import url_for

from b2share.modules.deposit.api import PublicationStates, \
    copy_data_from_previous
from b2share.modules.records.providers import RecordUUIDProvider

from invenio_pidstore.resolver import Resolver
from invenio_pidstore.models import PersistentIdentifier
from invenio_pidrelations.contrib.versioning import PIDVersioning

from b2share.modules.records.api import B2ShareRecord
from b2share.modules.deposit.api import Deposit

headers = [('Content-Type', 'application/json'),
           ('Accept', 'application/json')]
patch_headers = [('Content-Type', 'application/json-patch+json'),
                 ('Accept', 'application/json')]

def test_deposit_create_versions(app, test_records_data, test_users,
                                 login_user):
    """Test the creation of new record version draft."""
    # Use admin user in order to publish easily the records.
    login = lambda c: login_user(test_users['admin'], c)

    data = test_records_data

    # create and publish first record in a chain
    v1_draft = create_ok(app, login, data[0])
    assert 'versions' in v1_draft['links']
    check_links(app, v1_draft, [])

    v1_rec = publish(app, login, v1_draft)
    assert 'versions' in v1_rec['links']
    check_links(app, v1_rec, [v1_rec])

    # try to create a new version from an unknown pid
    res, json_data = create(app, login, data[1],
                            version_of=uuid.uuid4().hex)
    assert res.status_code == 400

    # try to create a new version from a parent pid
    with app.app_context():
        v1_pid = PersistentIdentifier.get(pid_value=v1_rec['id'], pid_type='b2rec')
        parent_pid = PIDVersioning(child=v1_pid).parent
    res, json_data = create(app, login, data[1],
                            version_of=parent_pid.pid_value)
    assert res.status_code == 400

    # create and publish second record in a chain
    v2_draft = create_ok(app, login, data[1], version_of=v1_rec['id'])
    check_links(app, v2_draft, [v1_rec])
    v2_rec = publish(app, login, v2_draft)
    check_links(app, v2_rec, [v1_rec, v2_rec])

    # test error if trying to create a non-linear version chain
    res, json_data = create(app, login, data[1], version_of=v1_rec['id'])
    assert res.status_code == 400
    assert json_data['use_record'] == v2_rec['id']

    # create third record draft in a chain
    v3_draft = create_ok(app, login, data[2], version_of=v2_rec['id'])
    check_links(app, v3_draft, [v1_rec, v2_rec])

    # test error when a draft already exists in a version chain
    res, json_data = create(app, login, data[1], version_of=v2_rec['id'])
    assert res.status_code == 400
    assert json_data['goto_draft'] == v3_draft['id']

    # publish third record in a chain
    v3_rec = publish(app, login, v3_draft)
    check_links(app, v3_rec, [v1_rec, v2_rec, v3_rec])

    # create a new version without data
    # assert that data is copied from the previous version
    v4_draft = create_ok(app, login, None, v3_rec['id'])
    with app.app_context():
        record_resolver = Resolver(
            pid_type='b2rec',
            object_type='rec',
            getter=B2ShareRecord.get_record,
        )
        deposit_resolver = Resolver(
            pid_type='b2dep',
            object_type='rec',
            getter=Deposit.get_record,
        )
        v4_metadata = deposit_resolver.resolve(v4_draft['id'])[1].model.json
        v3_metadata = record_resolver.resolve(v3_rec['id'])[1].model.json

        assert copy_data_from_previous(v4_metadata) == \
            copy_data_from_previous(v3_metadata)


def test_deposit_delete(app, test_records_data, test_users, login_user):
    """Test deposit deletion via the REST API."""
    with app.app_context():
        with app.test_client() as client:
            user = test_users['normal']
            login_user(user, client)
            # create the deposit
            record_data = test_records_data[0]
            draft_create_res = client.post(
                url_for('b2share_records_rest.b2rec_list'),
                data=json.dumps(record_data),
                headers=headers
            )
            assert draft_create_res.status_code == 201
            draft_create_data = json.loads(
                draft_create_res.get_data(as_text=True)
            )
            draft_pid_value = draft_create_data['id']
            dep_url = url_for('b2share_deposit_rest.b2dep_item',
                              pid_value=draft_pid_value)
            deposit_delete_res = client.delete(
                dep_url,
                headers=headers
            )
            assert deposit_delete_res.status_code == 204

            res = client.get(dep_url, headers=headers)
            assert res.status_code == 410


def check_links(app, json_data, expected_records):
    """Check that the record links behave as expected."""
    assert 'links' in json_data.keys()
    assert 'versions' in json_data['links']
    with app.test_client() as client:
        res = client.get(json_data['links']['versions'], headers=headers)
        versions = json.loads(res.get_data(as_text=True))
        assert 'versions' in versions
        versions = versions['versions']
        assert res.status_code == 200
        assert len(versions) == len(expected_records)
        for (i, v) in enumerate(versions):
            expected_id = expected_records[i]['id']
            expected_url = record_url(app, expected_id)
            assert v['url'] == expected_url


def create_ok(app, login, record_data, version_of=None):
    """Create a draft record."""
    res, json_data = create(app, login, record_data, version_of)
    assert res.status_code == 201
    res_md = json_data['metadata']
    if record_data is not None:
        for (k, v) in record_data.items():
            assert k in res_md
            assert v == res_md[k]
    return json_data


def create(app, login=None, record_data=None, version_of=None):
    """Create a draft record."""
    with app.test_client() as client:
        if login:
            login(client)
        url = url_for('b2share_records_rest.b2rec_list')
        if version_of:
            url += "?version_of="+version_of
        res = client.post(
            url,
            data=json.dumps(record_data) if record_data is not None else None,
            headers=headers
        )
        return res, json.loads(res.get_data(as_text=True))


def publish(app, login, rec):
    """Publish a draft record."""
    with app.test_client() as client:
        with app.app_context():
            url = url_for('b2share_deposit_rest.b2dep_item', pid_value=rec['id'])
        patch = [{
            "op": "replace", "path": "/publication_state",
            "value": PublicationStates.submitted.name,
        }]
        login(client)
        res = client.patch(url, data=json.dumps(patch), headers=patch_headers)
        assert 200 == res.status_code

        with app.app_context():
            url = url_for('b2share_deposit_rest.b2dep_item', pid_value=rec['id'])
        patch = [{
            "op": "replace", "path": "/publication_state",
            "value": PublicationStates.published.name,
        }]
        login(client)
        res = client.patch(url, data=json.dumps(patch), headers=patch_headers)
        assert 200 == res.status_code
        record_json_data = json.loads(res.get_data(as_text=True))
        return record_json_data


def record_url(app, record_id):
    """Generate the URL of a record."""
    record_endpoint = 'b2share_records_rest.{0}_item'.format(
        RecordUUIDProvider.pid_type
    )
    with app.app_context():
        return url_for(record_endpoint, pid_value=record_id, _external=True)
