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

"""Test B2Share deposit module's programmatic API."""


import uuid
from copy import deepcopy

import pytest
from jsonschema.exceptions import ValidationError
from b2share.modules.deposit.api import Deposit, PublicationStates
from b2share.modules.deposit.errors import InvalidDepositError
from b2share.modules.communities.errors import InvalidPublicationStateError
from jsonschema.exceptions import ValidationError
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from b2share.modules.records.errors import AlteredRecordError
from b2share_unit_tests.helpers import assert_external_files, \
    create_deposit


def test_deposit_create(app, draft_deposits):
    """Test deposit creation."""
    with app.app_context():
        deposit = Deposit.get_record(draft_deposits[0].deposit_id)
        assert (deposit['publication_state']
                == PublicationStates.draft.name)
        assert (deposit['_deposit']['status'] == 'draft')


def test_deposit_submit(app, draft_deposits):
    """Test deposit submission."""
    with app.app_context():
        deposit = Deposit.get_record(draft_deposits[0].deposit_id)
        deposit.submit()
        assert (deposit['publication_state']
                == PublicationStates.submitted.name)
        assert (deposit['_deposit']['status'] == 'draft')


def test_deposit_update_and_submit(app, draft_deposits):
    """Test deposit submission by updating the "publication_state" field."""
    with app.app_context():
        deposit = Deposit.get_record(draft_deposits[0].deposit_id)
        deposit.update({'publication_state':
                        PublicationStates.submitted.name})
        deposit.commit()
        assert (deposit['publication_state']
                == PublicationStates.submitted.name)
        assert (deposit['_deposit']['status'] == 'draft')


def test_deposit_publish(app, draft_deposits):
    """Test deposit submission by updating the "publication_state" field."""
    with app.app_context():
        deposit = Deposit.get_record(draft_deposits[0].deposit_id)
        deposit.submit()
        deposit.publish()
        assert (deposit['publication_state']
                == PublicationStates.published.name)
        assert (deposit['_deposit']['status'] == 'published')


def test_deposit_update_and_publish(app, draft_deposits):
    """Test deposit submission by updating the "publication_state" field."""
    with app.app_context():
        deposit = Deposit.get_record(draft_deposits[0].deposit_id)
        deposit.submit()
        deposit.update({'publication_state':
                        PublicationStates.published.name})
        deposit.commit()
        assert (deposit['publication_state']
                == PublicationStates.published.name)
        assert (deposit['_deposit']['status'] == 'published')


def test_deposit_update_unknown_publication_state(app, draft_deposits):
    """Test deposit submission by updating the "publication_state" field."""
    with app.app_context():
        deposit = Deposit.get_record(draft_deposits[0].deposit_id)
        deposit.update({'publication_state':
                        'invalid_state'})
        with pytest.raises(InvalidPublicationStateError):
            deposit.commit()


def test_deposit_add_unknown_fields(app, draft_deposits):
    """Test adding unknown fields in deposit. It should fail."""
    for path in [
        # all the following paths point to "object" fields in
        # in the root JSON Schema
        '/new_field',
        '/community_specific/new_field',
        '/creators/0/new_field',
        '/titles/0/new_field',
        '/contributors/0/new_field',
        '/resource_types/0/new_field',
        '/alternate_identifiers/0/new_field',
        '/descriptions/0/new_field',
        '/license/new_field',
    ]:
        with app.app_context():
            deposit = Deposit.get_record(draft_deposits[0].deposit_id)
            deposit = deposit.patch([
                {'op': 'add', 'path': path, 'value': 'any value'}
            ])
            pytest.raises(ValidationError, deposit.commit)



def test_deposit_create_with_invalid_fields_fails(app, test_records_data):
    """Test deposit creation without or with an invalid field fails."""
    data = test_records_data[0]
    with app.app_context():
        data['publication_state'] = 'published'
        with pytest.raises(InvalidDepositError):
            deposit = create_deposit(data=data)

    with app.app_context():
        data['$schema'] = '__garbage__'
        with pytest.raises(InvalidDepositError):
            deposit = create_deposit(data=data)


def test_deposit_create_with_invalid_community_fails(app,
                                                     test_records_data):
    """Test deposit creation without or with an invalid community fails."""
    data = test_records_data[0]
    with app.app_context():
        # test with no community
        del data['community']
        with pytest.raises(ValidationError):
            deposit = create_deposit(data=data)

    with app.app_context():
        # test with an invalid community
        data['community'] = uuid.uuid4().hex
        with pytest.raises(InvalidDepositError):
            deposit = create_deposit(data=data)


def test_change_deposit_community(app, draft_deposits):
    """Test deposit creation without or with an invalid community fails."""
    with app.app_context():
        deposit = Deposit.get_record(draft_deposits[0].deposit_id)
        # test removing the community id
        del deposit['community']
        with pytest.raises(AlteredRecordError):
            deposit.commit()

    with app.app_context():
        deposit = Deposit.get_record(draft_deposits[0].deposit_id)
        # test changing the community id
        deposit['community'] = uuid.uuid4().hex
        with pytest.raises(InvalidDepositError):
            deposit.commit()


def test_deposit_create_with_incomplete_metadata(app,
                                                 test_incomplete_records_data):
    """Test deposit creation with incomplete metadata succeeds."""

            
    with app.app_context():
        for data in test_incomplete_records_data:
            deposit = create_deposit(data=data.incomplete_data)
            assert (deposit['publication_state']
                    == PublicationStates.draft.name)
            assert (deposit['_deposit']['status'] == 'draft')


def test_deposit_submit_with_incomplete_metadata(app,
                                                 test_incomplete_records_data):
    """Test deposit submission with incomplete metadata fails."""
    for data in test_incomplete_records_data:
        with app.app_context():
            deposit = create_deposit(data=data.complete_data)
            deposit.commit()
            # make the data incomplete
            deposit = deposit.patch(data.patch)
            with pytest.raises(ValidationError):
                deposit.submit()


def test_deposit_publish_with_incomplete_metadata(app,
                                                  test_incomplete_records_data):
    """Test publication of an incomplete deposit fails."""
    for data in test_incomplete_records_data:
        with app.app_context():
            deposit = create_deposit(data=data.complete_data)
            deposit.submit()
            deposit.commit()
            # make the data incomplete
            deposit = deposit.patch(data.patch)
            with pytest.raises(ValidationError):
                deposit.publish()


def test_change_deposit_schema_fails(app, draft_deposits):
    """Test updating the $schema field fails."""
    with app.app_context():
        deposit = Deposit.get_record(draft_deposits[0].deposit_id)
        del deposit['$schema']
        with pytest.raises(AlteredRecordError):
            deposit.commit()


def test_create_deposit_with_external_pids_errors(
        app, records_data_with_external_pids):
    """Test errors when a deposit is created with invalid external files."""
    data_without_pid = deepcopy(records_data_with_external_pids)
    del data_without_pid['external_pids'][0]['ePIC_PID']
    with app.app_context():
        with pytest.raises(ValidationError,
                           match="'ePIC_PID' is a required property.*"):
            create_deposit(data_without_pid)

    data_without_key = deepcopy(records_data_with_external_pids)
    del data_without_key['external_pids'][0]['key']
    with app.app_context():
        with pytest.raises(ValidationError,
                           match="'key' is a required property.*"):
            create_deposit(data_without_key)


    data_with_unknown_key = deepcopy(records_data_with_external_pids)
    data_with_unknown_key['external_pids'][0]['unknown'] = 'value'
    with app.app_context():
        with pytest.raises(ValidationError,
                           match="Additional properties are not allowed "
                           "\('unknown' was unexpected\).*"):
            create_deposit(data_with_unknown_key)


def test_patch_deposit_with_external_pids_errors(app,
                                                 deposit_with_external_pids):
    """Test errors when an invalid PATCH modifies the external files."""
    from jsonpatch import JsonPatchConflict
    with app.app_context():
        deposit = deposit_with_external_pids.get_deposit()
        with pytest.raises(JsonPatchConflict):
            deposit = deposit.patch([
                {
                    "op": "replace",
                    "path": "/external_pids",
                    "value": [{
                        "key":"file1.txt",
                    }]
                }
            ])
            deposit.commit()

        deposit = deposit_with_external_pids.get_deposit()
        with pytest.raises(JsonPatchConflict):
            deposit = deposit.patch([
                {
                    "op": "replace",
                    "path": "/external_pids",
                    "value": [{
                        "ePIC_PID": "http://hdl.handle.net/11304/0d8dbdec-74e4-4774-954e-1a98e5c0cfa3"
                    }]
                }
            ])
            deposit.commit()
        with pytest.raises(JsonPatchConflict):
            deposit = deposit.patch([
                {
                    "op": "replace",
                    "path": "/external_pids",
                    "value": [{
                        "ePIC_PID": "http://hdl.handle.net/11304/0d8dbdec-74e4-4774-954e-1a98e5c0cfa3",
                        "key":"file1.txt",
                        "unknown":"field",
                    }]
                }
            ])
            deposit.commit()
