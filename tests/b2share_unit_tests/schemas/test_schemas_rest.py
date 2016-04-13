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

"""Test Communities module's REST API."""

from __future__ import absolute_import

import json
import uuid

import pytest
from flask import url_for
from invenio_db import db
from mock import patch
from b2share.modules.schemas.api import CommunitySchema
from b2share_unit_tests.helpers import subtest_self_link

def test_valid_get(app, test_communities):
    """Test VALID community get request (GET .../communities/<id>)."""
    with app.app_context():
        community_id = '2b884138-898f-4651-bf82-34dea0e0e83f'
        with app.test_client() as client:
            for version in [0, 1, 'last']:
                headers = [('Content-Type', 'application/json'),
                        ('Accept', 'application/json')]
                res = client.get(
                    url_for('b2share_schemas.community_schema_item',
                            community_id=community_id,
                            schema_version_nb=str(version)),
                    headers=headers)
                assert res.status_code == 200
                # check that the returned community matches the given data
                response_data = json.loads(res.get_data(as_text=True))
                if isinstance(version, int):
                    expected = CommunitySchema.get_community_schema(
                        community_id, version)
                elif version == 'last':
                    expected = CommunitySchema.get_community_schema(
                        community_id)
                else:
                    raise NotImplementedError('Test not implemented')
                assert (expected.build_json_schema() ==
                        response_data['json_schema'])
                assert response_data['community'] == community_id
                assert response_data['version'] == expected.version

    with app.app_context():
        with app.test_client() as client:
            # check that the returned self link returns the same data
            subtest_self_link(response_data, res.headers, client)
