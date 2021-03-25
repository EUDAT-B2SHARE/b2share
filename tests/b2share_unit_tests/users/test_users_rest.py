# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2016, University of Tuebingen.
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

"""Test B2Share users module's REST API."""

import json

from flask import url_for
from tests.b2share_unit_tests.helpers import create_user, create_role


def test_users_get(app, test_users, login_user):
    headers = [('Content-Type', 'application/json'),
               ('Accept', 'application/json')]

    def get_user():
        req = client.get(url_for('b2share_users.current_user'), headers=headers)
        assert req.status_code == 200
        return json.loads(req.get_data(as_text=True))

    with app.app_context():
        with app.test_client() as client:
            # test get info of anonymous user
            user_info = get_user()
            assert user_info == {}

            # test getting info for logged in user
            user = test_users['normal']
            login_user(user, client)
            user_info = get_user()
            expected = {
                'email': user.email,
                'id': user.id,
                'name': user.email,
                'roles': []
            }
            assert user_info == expected

    with app.app_context():
        with app.test_client() as client:
            # test getting info for logged in user with roles
            some_role = create_role('some_role')
            user_with_role = create_user('user_with_role', roles=[some_role])
            login_user(user_with_role, client)
            user_info = get_user()
            expected = {
                'email': user_with_role.email,
                'id': user_with_role.id,
                'name': user_with_role.email,
                'roles': [{
                    'id': some_role.id,
                    'description': some_role.description,
                    'name': some_role.name,
                }]
            }
            assert user_info == expected


def test_users_tokens(app, test_users, login_user):
    headers = [('Content-Type', 'application/json'),
               ('Accept', 'application/json')]

    def assert_user_token_list(names, expected_code=200):
        req = client.get(url_for('b2share_users.user_token_list'),
                         headers=headers)
        assert req.status_code == expected_code
        if req.status_code == 200:
            hits = json.loads(req.get_data(as_text=True))['hits']
            assert hits['total'] == len(names)
            assert set([h['name'] for h in hits['hits']]) == set(names)

    def get_user_token(token_id, expected_code=200):
        url = url_for('b2share_users.user_token_item', token_id=token_id)
        req = client.get(url, headers=headers)
        assert req.status_code == expected_code
        return json.loads(req.get_data(as_text=True))

    def create_user_token_request(token_name):
        return client.post(url_for('b2share_users.user_token_list'),
                           data=json.dumps({'token_name':token_name}),
                           headers=headers)

    def create_user_token(token_name):
        req = create_user_token_request(token_name)
        assert req.status_code == 201
        token = json.loads(req.get_data(as_text=True))

        token_noaccess = get_user_token(token['id'])

        assert 'access_token' in token and 'access_token' not in token_noaccess
        assert token['id'] == token_noaccess['id']
        assert token['name'] == token_noaccess['name']
        return token

    def delete_user_token(token_id):
        url = url_for('b2share_users.user_token_item', token_id=token_id)
        req = client.delete(url, headers=headers)
        assert req.status_code == 200
        assert json.loads(req.get_data(as_text=True)) == {}

    with app.app_context():
        with app.test_client() as client:
            # test get tokens of anonymous user
            assert_user_token_list([], expected_code=401)
            assert_user_token_list([], expected_code=401)

            # test tokens for logged in user
            user = test_users['normal']
            login_user(user, client)
            assert_user_token_list([])

            # test bad token requests
            get_user_token(42, expected_code=404)

            bad_create_token_request = create_user_token_request(None)
            assert bad_create_token_request.status_code == 400

            # test create and list tokens
            token1 = create_user_token('test42')
            assert token1['name'] == 'test42'
            assert_user_token_list(['test42'])

            token2 = create_user_token('test42+1')
            assert token2['name'] == 'test42+1'
            assert_user_token_list(['test42', 'test42+1'])

            delete_user_token(token1['id'])
            assert_user_token_list(['test42+1'])

            delete_user_token(token2['id'])
            assert_user_token_list([])
