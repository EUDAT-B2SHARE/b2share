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

"""Test user account REST API."""

from __future__ import absolute_import, print_function

import json

from flask import url_for
from invenio_accounts.models import User
from tests.b2share_unit_tests.helpers import create_user


def test_accounts_update(app, test_users, test_community,
                         login_user):
    """Test assigning community admin and member roles."""
    counter = [0]
    def account_update(field, value, expected_code):
        def account_update_sub(patch_content, content_type):
            with app.app_context():
                test_user = create_user('test_user{}'.format(counter[0]))
                counter[0] += 1
                url = url_for(
                    'invenio_accounts_rest.user',
                    user_id=test_user.id,
                )

                headers = [('Content-Type', content_type),
                           ('Accept', 'application/json')]

                with app.test_client() as client:
                    # send the request as global admin
                    login_user(test_users['admin'], client)
                    res = client.patch(url, headers=headers,
                                       data=json.dumps(patch_content))
                    assert res.status_code == expected_code
                    if expected_code == 200:
                        request_data = json.loads(
                            res.get_data(as_text=True))

                        assert request_data[field] == value
        # test with a simple JSON
        account_update_sub({field: value}, 'application/json')
        # test with a JSON patch
        account_update_sub([{
            'op': 'replace', 'path': '/{}'.format(field),'value': value
        }], 'application/json-patch+json')

    # try desactivating the user
    account_update('active', False, 200)
    # it should not be possible to change email address
    account_update('email', 'newemail@example.org', 400)
    # it should not be possible to set a password
    account_update('password', 'newpassword', 400)
    # test with an unknown field
    account_update('unknown_field', 'value', 400)
