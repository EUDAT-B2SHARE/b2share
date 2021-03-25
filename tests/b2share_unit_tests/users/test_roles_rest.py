# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2017 University of Tuebingen, CERN, CSC, KTH.
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

"""Test roles REST API."""

from __future__ import absolute_import, print_function

import json

import pytest
from b2share.modules.communities.api import Community
from invenio_accounts.models import User
from tests.b2share_unit_tests.helpers import create_user
from flask import url_for
from invenio_db import db


def test_assign_community_roles(app, test_users, test_community,
                                login_user):
    """Test assigning community admin and member roles."""
    def assign_role(role_id):
        with app.app_context():
            test_user = create_user('test_user{}'.format(role_id))
            url = url_for(
                'invenio_accounts_rest.assign_role',
                user_id=test_user.id,
                role_id=role_id,
            )

            headers = [('Content-Type', 'application/json'),
                    ('Accept', 'application/json')]

            with app.test_client() as client:
                # send the request as global admin
                login_user(test_users['admin'], client)
                res = client.put(url, headers=headers)
                assert res.status_code == 200

        with app.app_context():
            user_roles = User.query.get(test_user.id).roles
            assert role_id in [role.id for role in user_roles]

    assign_role(test_community.admin_role_id)
    assign_role(test_community.member_role_id)


def test_unassign_community_roles(app, test_users, test_community,
                                  login_user):
    with app.app_context():
        community = Community.get(id=test_community.id)
        com_admin = create_user('test_community_admin',
                                roles=[community.admin_role])
        db.session.commit()

    headers = [('Content-Type', 'application/json'),
               ('Accept', 'application/json')]

    with app.app_context():
        with app.test_client() as client:
            # send the request as global admin
            login_user(test_users['admin'], client)
            res = client.delete(
                url_for(
                    'invenio_accounts_rest.assign_role',
                    user_id=com_admin.id,
                    role_id=test_community.admin_role_id,
                ),
                headers=headers
            )
            assert res.status_code == 204

    with app.app_context():
        user_roles = User.query.get(com_admin.id).roles
        assert test_community.admin_role_id \
            not in [role.id for role in user_roles]
