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

"""Test roles REST API permissions."""

from __future__ import absolute_import, print_function

import json

import pytest
from b2share.modules.communities.api import Community
from invenio_accounts.models import User, Role
from tests.b2share_unit_tests.helpers import create_user, create_role
from flask import url_for
from invenio_db import db


def test_assign_roles_permissions(app, test_users, custom_role,
                                  test_community, login_user):
    """Test permissions for assigning roles."""
    headers = [('Content-Type', 'application/json'),
               ('Accept', 'application/json')]
    counter = [0]
    def assign_role(role_id, user=None, expected_status_code=200):
        """Test assigning a role to a user.
        Args:
            - role_id: id of the role to assign.
            - user: user whose identity will be used when assigning the role.
            - expected_status_code: expected status code of the request.
        """
        with app.app_context():
            test_user = create_user('test_user{}'.format(counter[0]))
            counter[0] += 1
            db.session.commit()
            url = url_for(
                'invenio_accounts_rest.assign_role',
                user_id=test_user.id,
                role_id=role_id,
            )

        with app.test_client() as client:
            if user is not None:
                login_user(user, client)
            res = client.put(url, headers=headers)
            assert res.status_code == expected_status_code

        # check that the user roles didn't change
        if expected_status_code != 200:
            with app.app_context():
                user_roles = User.query.get(test_user.id).roles
                assert role_id not in [role.id for role in user_roles]


    # annonymous user shouldn't be able to assign community admin or member
    assign_role(test_community.admin_role_id, None, 401)
    assign_role(test_community.member_role_id, None, 401)
    assign_role(custom_role, None, 401)

    # normal users shouldn't be able to assign community admin or member
    assign_role(test_community.admin_role_id, test_users['normal'], 403)
    assign_role(test_community.member_role_id, test_users['normal'], 403)
    assign_role(custom_role, test_users['normal'], 403)

    # community admins can assign other community admin or member
    assign_role(test_community.admin_role_id, test_community.member, 403)
    assign_role(test_community.member_role_id, test_community.member, 403)
    assign_role(custom_role, test_community.member, 403)

    # community admins can assign other community admin or member
    assign_role(test_community.admin_role_id, test_community.admin, 200)
    assign_role(test_community.member_role_id, test_community.admin, 200)
    assign_role(custom_role, test_community.admin, 403)

    # global admin can assign community admins
    assign_role(test_community.admin_role_id, test_users['admin'], 200)
    assign_role(test_community.member_role_id, test_users['admin'], 200)
    assign_role(custom_role, test_users['admin'], 200)


def test_unassign_roles_permissions(app, test_users, test_community,
                                    custom_role, login_user):
    """Test access control of roles unassignment."""
    headers = [('Content-Type', 'application/json'),
               ('Accept', 'application/json')]
    counter = [0]
    def unassign_role(role_id, user=None, expected_status_code=200):
        """Test assigning a role to a user.
        Args:
            - role_id: id of the role to unassign.
            - user: user whose identity will be used when unassigning the role.
            - expected_status_code: expected status code of the request.
        """
        with app.app_context():
            role = Role.query.filter(Role.id==role_id).one()
            test_user = create_user('test_user{}'.format(counter[0]),
                                roles=[role])
            counter[0] += 1
            db.session.commit()

            url = url_for(
                'invenio_accounts_rest.assign_role',
                user_id=test_user.id,
                role_id=role_id,
            )

        with app.test_client() as client:
            if user is not None:
                login_user(user, client)
            res = client.delete(url, headers=headers)
            assert res.status_code == expected_status_code

        # check that the user roles didn't change
        if expected_status_code != 204:
            with app.app_context():
                user_roles = User.query.get(test_user.id).roles
                assert role_id in [role.id for role in user_roles]


    # annonymous user shouldn't be able to unassign community admin or member
    unassign_role(test_community.admin_role_id, None, 401)
    unassign_role(test_community.member_role_id, None, 401)
    unassign_role(custom_role, None, 401)

    # normal users shouldn't be able to unassign community admin or member
    unassign_role(test_community.admin_role_id, test_users['normal'], 403)
    unassign_role(test_community.member_role_id, test_users['normal'], 403)
    unassign_role(custom_role, test_users['normal'], 403)

    # community admins can unassign other community admin or member
    unassign_role(test_community.admin_role_id, test_community.member, 403)
    unassign_role(test_community.member_role_id, test_community.member, 403)
    unassign_role(custom_role, test_community.member, 403)

    # community admins can unassign other community admin or member
    unassign_role(test_community.admin_role_id, test_community.admin, 204)
    unassign_role(test_community.member_role_id, test_community.admin, 204)
    unassign_role(custom_role, test_community.admin, 403)

    # global admin can unassign community admins
    unassign_role(test_community.admin_role_id, test_users['admin'], 204)
    unassign_role(test_community.member_role_id, test_users['admin'], 204)
    unassign_role(custom_role, test_users['admin'], 204)


def test_update_roles_permissions(app, test_users, test_community,
                                  custom_role, login_user):
    """Test access control of roles update."""
    headers = [('Content-Type', 'application/json-patch+json'),
               ('Accept', 'application/json')]
    def update_role(role_id, user, expected_status_code=200):
        """Test assigning a role to a user.
        Args:
            - role_id: id of the role to update.
            - user: user whose identity will be used when updating the role.
            - expected_status_code: expected status code of the request.
        """
        with app.app_context():
            url = url_for(
                'invenio_accounts_rest.role',
                role_id=role_id,
            )

        with app.test_client() as client:
            if user is not None:
                login_user(user, client)
            res = client.patch(url, headers=headers, data=json.dumps([
                {'op': 'replace', 'path': '/description',
                 'value': 'new_description'}
            ]))
            assert res.status_code == expected_status_code

    # annonymous user shouldn't be able to update
    update_role(custom_role, None, 401)

    # normal users shouldn't be able to update
    update_role(custom_role, test_users['normal'], 403)

    # community admins cannot update
    update_role(custom_role, test_community.member, 403)

    # community admins cannot update
    update_role(custom_role, test_community.admin, 403)

    # super admin can update any role
    update_role(custom_role, test_users['admin'], 200)


def test_delete_roles_permissions(app, test_users, test_community,
                                  login_user):
    """Test access control of roles delete."""
    headers = [('Content-Type', 'application/json'),
               ('Accept', 'application/json')]
    counter = [0]
    def delete_role(user, expected_status_code=200):
        """Test assigning a role to a user.
        Args:
            - role_id: id of the role to delete.
            - user: user whose identity will be used when updating the role.
            - expected_status_code: expected status code of the request.
        """
        with app.app_context():
            role = create_role('some_custom_role{}'.format(counter[0]))
            db.session.commit()
            counter[0] += 1
            role_id = role.id
            url = url_for(
                'invenio_accounts_rest.role',
                role_id=role_id,
            )

        with app.test_client() as client:
            if user is not None:
                login_user(user, client)
            res = client.delete(url, headers=headers)
            assert res.status_code == expected_status_code

    # annonymous user shouldn't be able to delete
    delete_role(None, 401)

    # normal users shouldn't be able to delete
    delete_role(test_users['normal'], 403)

    # community admins cannot delete
    delete_role(test_community.member, 403)

    # community admins cannot delete
    delete_role(test_community.admin, 403)

    # super admin can delete any role
    delete_role(test_users['admin'], 204)
