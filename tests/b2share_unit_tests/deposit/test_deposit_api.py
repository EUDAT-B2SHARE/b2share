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

import pytest
from b2share.modules.deposit.api import Deposit, PublicationStates
from b2share.modules.communities.errors import InvalidPublicationStateError


def test_deposit_create(app, draft_deposits):
    """Test deposit creation."""
    with app.app_context():
        deposit = Deposit.get_record(draft_deposits[0].id)
        assert (deposit['publication_state']
                == PublicationStates.draft.name)
        assert (deposit['_deposit']['status'] == 'draft')


def test_deposit_submit(app, draft_deposits):
    """Test deposit submission."""
    with app.app_context():
        deposit = Deposit.get_record(draft_deposits[0].id)
        deposit.submit()
        assert (deposit['publication_state']
                == PublicationStates.submitted.name)
        assert (deposit['_deposit']['status'] == 'draft')


def test_deposit_update_and_submit(app, draft_deposits):
    """Test deposit submission by updating the "publication_state" field."""
    with app.app_context():
        deposit = Deposit.get_record(draft_deposits[0].id)
        deposit.update({'publication_state':
                        PublicationStates.submitted.name})
        deposit.commit()
        assert (deposit['publication_state']
                == PublicationStates.submitted.name)
        assert (deposit['_deposit']['status'] == 'draft')


def test_deposit_publish(app, draft_deposits):
    """Test deposit submission by updating the "publication_state" field."""
    with app.app_context():
        deposit = Deposit.get_record(draft_deposits[0].id)
        deposit.submit()
        deposit.publish()
        assert (deposit['publication_state']
                == PublicationStates.published.name)
        assert (deposit['_deposit']['status'] == 'published')


def test_deposit_update_and_publish(app, draft_deposits):
    """Test deposit submission by updating the "publication_state" field."""
    with app.app_context():
        deposit = Deposit.get_record(draft_deposits[0].id)
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
        deposit = Deposit.get_record(draft_deposits[0].id)
        deposit.update({'publication_state':
                        'invalid_state'})
        with pytest.raises(InvalidPublicationStateError):
            deposit.commit()


# def test_direct_publish_workflow(app, draft_deposits, draft_community):
#     """Test deposit submission with "direct_publish" workflow"""
#     test_communities

#     with app.app_context():
#         deposit = Deposit.get_record(draft_deposits[0].id)
#         deposit.update({'publication_state':
#                         'invalid_state'})
#         with pytest.raises(ValidationError):
#             deposit.commit()
