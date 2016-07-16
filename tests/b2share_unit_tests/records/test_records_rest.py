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

from flask import url_for
from b2share_unit_tests.helpers import create_record, generate_record_data
from jsonpatch import apply_patch


######################
#  Test permissions  #
######################

def test_record_read_permissions(app, test_communities,
                                 create_user, login_user, admin):
    """Test record read with HTTP GET."""
    with app.app_context():
        creator = create_user('creator')
        non_creator = create_user('non-creator')

        open_record_data = generate_record_data(open_access=True)
        _, open_record_pid, open_record = create_record(open_record_data, creator)

        closed_record_data = generate_record_data(open_access=False)
        _, closed_record_pid, closed_record = create_record(closed_record_data, creator)

        def test_get(pid, status, user=None):
            with app.test_client() as client:
                if user is not None:
                    login_user(user, client)
                headers = [('Accept', 'application/json')]
                request_res = client.get(
                    url_for('b2share_records_rest.b2share_record_item',
                            pid_value=pid.pid_value),
                    headers=headers)
                assert request_res.status_code == status
        # test with anonymous user
        test_get(open_record_pid, 200)
        test_get(closed_record_pid, 401)

        test_get(open_record_pid, 200, non_creator)
        test_get(closed_record_pid, 403, non_creator)

        test_get(open_record_pid, 200, creator)
        test_get(closed_record_pid, 200, creator)

        test_get(open_record_pid, 200, admin)
        test_get(closed_record_pid, 200, admin)


def test_modify_published_record_permissions(app, test_communities,
                                             create_user, login_user, admin):
    """Test record read with HTTP GET."""
    with app.app_context():
        creator = create_user('creator')
        non_creator = create_user('non-creator')

        record_data = generate_record_data(open_access=True)

        def test_modify(status, user=None):
            patch = [{
                "op": "replace", "path": "/title",
                "value": 'newtitle'
            }]
            with app.test_client() as client:
                _, record_pid, record = create_record(record_data, creator)
                if user is not None:
                    login_user(user, client)
                # test patching the document
                headers = [('Content-Type', 'application/json-patch+json'),
                           ('Accept', 'application/json')]
                request_res = client.patch(
                    url_for('b2share_records_rest.b2share_record_item',
                            pid_value=record_pid.pid_value),
                    data=json.dumps(patch),
                    headers=headers)
                assert request_res.status_code == status

                _, record_pid, record = create_record(record_data, creator)
                # test putting the document
                data = dict(record)
                apply_patch(data, patch)
                headers = [('Content-Type', 'application/json'),
                           ('Accept', 'application/json')]
                request_res = client.put(
                    url_for('b2share_records_rest.b2share_record_item',
                            pid_value=record_pid.pid_value),
                    data=json.dumps(data),
                    headers=headers)
                assert request_res.status_code == status

        # test with anonymous user
        test_modify(401)
        test_modify(403, non_creator)
        test_modify(403, creator)
        test_modify(200, admin)
