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

"""Test helpers."""

import json
from copy import deepcopy
from contextlib import contextmanager

from flask import current_app
from six import string_types
from flask_login import login_user, logout_user
from invenio_accounts.models import User
from b2share.modules.deposit.api import Deposit
from b2share_demo.helpers import resolve_community_id, resolve_block_schema_id


def subtest_self_link(response_data, response_headers, client):
    """Check that the returned self link returns the same data.
    """
    assert 'links' in response_data.keys() \
        and isinstance(response_data['links'], dict)
    assert 'self' in response_data['links'].keys() \
        and isinstance(response_data['links']['self'], string_types)
    headers = [('Accept', 'application/json')]
    self_response = client.get(response_data['links']['self'],
                               headers=headers)

    assert self_response.status_code == 200
    self_data = json.loads(self_response.get_data(as_text=True))
    assert self_data == response_data
    if response_headers:
        assert response_headers['ETag'] == self_response.headers['ETag']


@contextmanager
def authenticated_user(userinfo):
    """Authentication context manager."""
    user = User.query.filter(User.id == userinfo.id).one()
    with current_app.test_request_context():
        login_user(user)
        try:
            yield
        finally:
            logout_user()


def create_deposit(data, creator):
    """Create a deposit with the given user as creator."""
    with authenticated_user(creator):
        deposit = Deposit.create(data=deepcopy(data))
    return deposit


def create_record(data, creator):
    """Create a deposit with the given user as creator."""
    deposit = create_deposit(data, creator)
    with authenticated_user(creator):
        deposit.submit()
        deposit.publish()
    published = deposit.fetch_published()
    return (deposit, published[0], published[1])  # deposit, pid, record


def resolve_record_data(data):
    """Resolve community and block schema IDs in the given record data."""
    return json.loads(
        resolve_block_schema_id(resolve_community_id(json.dumps(data)))
    )


def generate_record_data(title='My Test BBMRI Record', open_access=True,
                         community='MyTestCommunity',
                         block_schema='MyTestSchema',
                         block_schema_content=None):
    """Generate"""
    default_block_schema_content = {
        'study_design': ['Case-control']
    }
    data = {
        'title': title,
        'community': '$COMMUNITY_ID[{}]'.format(community),
        'open_access': open_access,
        'community_specific': {
            '$BLOCK_SCHEMA_ID[{}]'.format(block_schema): \
            default_block_schema_content if block_schema_content is None \
            else block_schema_content
        }
    }
    return resolve_record_data(data)
