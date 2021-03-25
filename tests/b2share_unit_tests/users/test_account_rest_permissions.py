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

"""Test permissions of user account REST API."""

import json

from invenio_db import db
from flask import url_for
from invenio_accounts.models import User
from invenio_oauth2server.models import Token
from invenio_oauth2server import current_oauth2server
from tests.b2share_unit_tests.helpers import create_user


def test_accounts_search_permission(app, test_users, test_community,
                                    login_user):
    """Test permission of listing user accounts."""
    def account_search(user, expected_code):
        headers = [('Content-Type', 'application/json'),
                   ('Accept', 'application/json')]
        with app.app_context():
            url = url_for('invenio_accounts_rest.users_list')
            if user:
                scopes = current_oauth2server.scope_choices()
                allowed_token = Token.create_personal(
                    'allowed_token', user.id,
                    scopes=[s[0] for s in scopes]
                )
                # application authentication token header
                headers.append(('Authorization',
                                'Bearer {}'.format(allowed_token.access_token)))

        with app.test_client() as client:
            if user is not None:
                login_user(user, client)
            res = client.get(url, headers=headers)
            assert res.status_code == expected_code

    # anonymous users can't list accounts
    account_search(None, 401)
    # authenticated users can't list other users' account
    account_search(test_users['normal'], 403)
    # community members cannot list all users' accounts
    account_search(test_community.member, 403)
    # community admins can list all users
    account_search(test_community.admin, 200)
    # admin is allowed to list all accounts
    account_search(test_users['admin'], 200)


def test_account_read_permission(app, test_users, test_community,
                                 login_user):
    """Test permission of listing user accounts."""
    with app.app_context():
        read_user = create_user('read_user')
        url = url_for('invenio_accounts_rest.user',
                      user_id=read_user.id)
        db.session.commit()

    headers = [('Content-Type', 'application/json'),
                ('Accept', 'application/json')]

    def account_read(user, expected_code):
        with app.test_client() as client:
            if user is not None:
                login_user(user, client)
            res = client.get(url, headers=headers)
            assert res.status_code == expected_code

    # anonymous users can't read accounts
    account_read(None, 401)
    # authenticated users can't read other users' account
    account_read(test_users['normal'], 403)
    # community members cannot read other users' account
    account_read(test_community.member, 403)
    # users can read their own account
    account_read(read_user, 200)
    # community admins can list all users
    account_read(test_community.admin, 200)
    # admin is allowed to read all accounts
    account_read(test_users['admin'], 200)


def test_account_activation_permission(app, test_users, test_community,
                                       login_user):
    """Test deactivating a user account."""
    counter = [0]
    def account_update(user, expected_code, modified_user=None):
        def account_update_sub(patch_content, content_type):
            with app.app_context():
                if modified_user is None:
                    test_user = create_user(
                        'test_user{}'.format(counter[0]))
                else:
                    test_user = modified_user
                counter[0] += 1
                url = url_for(
                    'invenio_accounts_rest.user',
                    user_id=test_user.id,
                )
                db.session.commit()

            headers = [('Content-Type', content_type),
                        ('Accept', 'application/json')]

            with app.test_client() as client:
                if user is not None:
                    login_user(user, client)
                res = client.patch(url, headers=headers,
                                    data=json.dumps(patch_content))
                assert res.status_code == expected_code
        # test with a simple JSON
        account_update_sub({'active': False}, 'application/json')
        # test with a JSON patch
        account_update_sub([{
            'op': 'replace', 'path': '/active','value': False
        }], 'application/json-patch+json')

    # anonymous users can't activate/deactivate accounts
    account_update(None, 401)
    # authenticated users can't activate/deactivate other users' account
    account_update(test_users['normal'], 403)
    # users can't deactivate their own accounts
    account_update(test_users['normal'], 403, test_users['normal'])
    # admin is allowed to activate/deactivate accounts
    account_update(test_users['admin'], 200)


def test_account_roles_search_permission(app, test_users, test_community,
                                         login_user):
    """Test permission of listing user accounts."""
    with app.app_context():
        read_user = create_user('read_user')
        url = url_for('invenio_accounts_rest.user_roles_list',
                      user_id=read_user.id)
        db.session.commit()

    headers = [('Content-Type', 'application/json'),
                ('Accept', 'application/json')]

    def roles_read(user, expected_code):
        with app.test_client() as client:
            if user is not None:
                login_user(user, client)
            res = client.get(url, headers=headers)
            assert res.status_code == expected_code

    # anonymous users can't read other users' roles
    roles_read(None, 401)
    # any authenticated user can read other users' roles
    roles_read(test_users['normal'], 200)
