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

"""Test B2Share deposit module's REST API."""

import json

import pytest
from flask import url_for
from b2share.modules.deposit.api import PublicationStates, Deposit
from copy import deepcopy
from b2share_unit_tests.helpers import subtest_self_link
from b2share.modules.records.providers import RecordUUIDProvider


def build_expected_metadata(record_data, state, owners=None):
    expected_metadata = deepcopy(record_data)
    expected_metadata['publication_state'] = state
    expected_metadata['$schema'] = '{}#/json_schema'.format(
        url_for('b2share_schemas.community_schema_item',
                community_id=record_data['community'],
                schema_version_nb=1,
                _external=True)
    )
    if owners is not None:
        expected_metadata['owners'] = owners
    return expected_metadata


@pytest.mark.parametrize('test_users', [({
    'users': ['myuser']
})], indirect=['test_users'])
def test_deposit_create(app, test_records_data, test_users, login_user):
    """Test record draft creation."""
    with app.app_context():
        with app.test_client() as client:
            user = test_users['myuser']
            login_user(user, client)
            # create the deposit
            headers = [('Content-Type', 'application/json'),
                       ('Accept', 'application/json')]
            for record_data in test_records_data:
                record_list_url = (
                    lambda **kwargs:
                    url_for('b2share_records_rest.b2share_record_list',
                            **kwargs))
                draft_create_res = client.post(record_list_url(),
                                               data=json.dumps(record_data),
                                               headers=headers)
                assert draft_create_res.status_code == 201
                draft_create_data = json.loads(
                    draft_create_res.get_data(as_text=True))
                expected_metadata = build_expected_metadata(
                    record_data,
                    PublicationStates.draft.name,
                    owners=[user.id],
                )
                assert expected_metadata == draft_create_data['metadata']
                subtest_self_link(draft_create_data,
                                  draft_create_res.headers,
                                  client)


@pytest.mark.parametrize('test_users, test_deposits', [({
    'users': ['myuser']
}, {
    'deposits_creator': 'myuser'
})], indirect=['test_users', 'test_deposits'])
def test_deposit_submit(app, test_records_data, test_deposits, test_users,
                        login_user):
    """Test record draft submit with HTTP PATCH."""
    with app.app_context():
        deposit = Deposit.get_record(test_deposits[0])
        record_data = test_records_data[0]
        with app.test_client() as client:
            user = test_users['myuser']
            login_user(user, client)

            headers = [('Content-Type', 'application/json-patch+json'),
                       ('Accept', 'application/json')]
            draft_patch_res = client.patch(
                url_for('b2share_deposit_rest.b2share_deposit_item',
                        pid_value=deposit.pid.pid_value),
                data=json.dumps([{
                    "op": "replace", "path": "/publication_state",
                    "value": PublicationStates.submitted.name
                }]),
                headers=headers)
            assert draft_patch_res.status_code == 200
            draft_patch_data = json.loads(
                draft_patch_res.get_data(as_text=True))
            expected_metadata = build_expected_metadata(
                record_data,
                PublicationStates.draft.name,
                owners=[user.id],
            )
    with app.app_context():
        deposit = Deposit.get_record(test_deposits[0])
        with app.test_client() as client:
            expected_metadata['publication_state'] = \
                PublicationStates.submitted.name
            assert expected_metadata == draft_patch_data['metadata']
            assert (deposit['publication_state']
                    == PublicationStates.submitted.name)
            subtest_self_link(draft_patch_data,
                              draft_patch_res.headers,
                              client)


@pytest.mark.parametrize('test_users, test_deposits', [({
    'users': ['myuser']
}, {
    'deposits_creator': 'myuser'
})], indirect=['test_users', 'test_deposits'])
def test_deposit_publish(app, test_records_data, test_deposits, test_users,
                         login_user):
    """Test record draft publication with HTTP PATCH."""
    record_data = test_records_data[0]
    with app.app_context():
        deposit = Deposit.get_record(test_deposits[0])
        with app.test_client() as client:
            user = test_users['myuser']
            login_user(user, client)

            headers = [('Content-Type', 'application/json-patch+json'),
                       ('Accept', 'application/json')]
            draft_patch_res = client.patch(
                url_for('b2share_deposit_rest.b2share_deposit_item',
                        pid_value=deposit.pid.pid_value),
                data=json.dumps([{
                    "op": "replace", "path": "/publication_state",
                    "value": PublicationStates.published.name
                }]),
                headers=headers)
            assert draft_patch_res.status_code == 200
            draft_patch_data = json.loads(
                draft_patch_res.get_data(as_text=True))
            expected_metadata = build_expected_metadata(
                record_data,
                PublicationStates.published.name,
                owners=[user.id],
            )

    with app.app_context():
        deposit = Deposit.get_record(test_deposits[0])
        with app.test_client() as client:
            assert expected_metadata == draft_patch_data['metadata']
            assert (deposit['publication_state']
                    == PublicationStates.published.name)
            subtest_self_link(draft_patch_data,
                              draft_patch_res.headers,
                              client)

            pid, published = deposit.fetch_published()
            # check that the published record and the deposit are equal
            assert dict(**published) == dict(**deposit)
            # check "published" link
            assert draft_patch_data['links']['publication'] == \
                url_for('b2share_records_rest.{0}_item'.format(
                    RecordUUIDProvider.pid_type
                ), pid_value=pid.pid_value, _external=True)
            # check that the published record content match the deposit
            headers = [('Accept', 'application/json')]
            self_response = client.get(
                draft_patch_data['links']['publication'],
                headers=headers
            )
            assert self_response.status_code == 200
            published_data = json.loads(self_response.get_data(
                as_text=True))
            # we don't want to compare the links and dates
            cleaned_published_data = deepcopy(published_data)
            cleaned_draft_data = deepcopy(draft_patch_data)
            for item in [cleaned_published_data, cleaned_draft_data]:
                del item['links']
                del item['created']
                del item['updated']
            assert cleaned_draft_data == cleaned_published_data