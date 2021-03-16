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

"""Pytest configuration for b2share communities."""

import json

import pytest
from flask import url_for
from .helpers import community_metadata
from invenio_db import db

from b2share.modules.communities import B2ShareCommunities
from b2share.modules.communities.models import Community as CommunityModel
from b2share_unit_tests.helpers import create_user


# FIXME: Test is disabled for V2 as it is not used by the UI
# @pytest.mark.parametrize('app', [({
#     'extensions': [B2ShareCommunities],
#     'config': {'B2SHARE_COMMUNITIES_REST_ACCESS_CONTROL_DISABLED': False}
# })],
#     indirect=['app'])
# def test_create_access_control(app, login_user, communities_permissions):
#     """Test community creation with differnet access rights."""
#     with app.app_context():
#         allowed_user = create_user('allowed')
#         not_allowed_user = create_user('not allowed')
#         communities_permissions(allowed_user.id).create_permission(True)
#         db.session.commit()

#     # test without login
#     with app.app_context():
#         with app.test_client() as client:
#             headers = [('Content-Type', 'application/json'),
#                        ('Accept', 'application/json')]
#             res = client.post(url_for('b2share_communities.communities_list'),
#                               data=json.dumps(community_metadata),
#                               headers=headers)
#             assert res.status_code == 401
#         assert len(CommunityModel.query.all()) == 0

#     # test not allowed user
#     with app.app_context():
#         with app.test_client() as client:
#             login_user(not_allowed_user, client)

#             headers = [('Content-Type', 'application/json'),
#                        ('Accept', 'application/json')]
#             res = client.post(url_for('b2share_communities.communities_list'),
#                               data=json.dumps(community_metadata),
#                               headers=headers)
#             assert res.status_code == 403
#         assert len(CommunityModel.query.all()) == 0

#     # test allowed user
#     with app.app_context():
#         with app.test_client() as client:
#             login_user(allowed_user, client)

#             headers = [('Content-Type', 'application/json'),
#                        ('Accept', 'application/json')]
#             res = client.post(url_for('b2share_communities.communities_list'),
#                               data=json.dumps(community_metadata),
#                               headers=headers)
#             assert res.status_code == 201
#         assert len(CommunityModel.query.all()) == 1


# FIXME: Test is disabled for V2 as it is not used by the UI
# @pytest.mark.parametrize('app', [({
#     'extensions': [B2ShareCommunities],
#     'config': {'B2SHARE_COMMUNITIES_REST_ACCESS_CONTROL_DISABLED': True}
# })],
#     indirect=['app'])
# def test_create_unlogged_disabled_access_control(app, login_user,
#                                                  communities_permissions):
#     """Test community creation with ACL disabled and unlogged user."""
#     with app.app_context():
#         with app.test_client() as client:
#             headers = [('Content-Type', 'application/json'),
#                        ('Accept', 'application/json')]
#             res = client.post(url_for('b2share_communities.communities_list'),
#                               data=json.dumps(community_metadata),
#                               headers=headers)
#             assert res.status_code == 201
#         assert len(CommunityModel.query.all()) == 1


# FIXME: Test is disabled for V2 as it is not used by the UI
# @pytest.mark.parametrize('app', [({
#     'extensions': [B2ShareCommunities],
#     'config': {'B2SHARE_COMMUNITIES_REST_ACCESS_CONTROL_DISABLED': True}
# })],
#     indirect=['app'])
# def test_create_not_allowed_disabled_access_control(app, login_user,
#                                                     communities_permissions):
#     """Test community creation with ACL disabled and not allowed user."""
#     with app.app_context():
#         not_allowed_user = create_user('not allowed')
#         db.session.commit()

#     # test not allowed user
#     with app.app_context():
#         with app.test_client() as client:
#             login_user(not_allowed_user, client)

#             headers = [('Content-Type', 'application/json'),
#                        ('Accept', 'application/json')]
#             res = client.post(url_for('b2share_communities.communities_list'),
#                               data=json.dumps(community_metadata),
#                               headers=headers)
#             assert res.status_code == 201
#         assert len(CommunityModel.query.all()) == 1
