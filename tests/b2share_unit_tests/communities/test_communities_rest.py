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
from b2share_unit_tests.communities.helpers import community_metadata, \
    community_patch, patched_community_metadata
from b2share_unit_tests.helpers import subtest_self_link, create_user
from invenio_db import db
from mock import patch

from b2share.modules.communities import Community
from b2share.modules.communities.errors import CommunityDeletedError
from b2share.modules.communities.models import Community as CommunityModel


# FIXME: Test is disabled for V2 as it is not used by the UI
# @community_with_and_without_access_control
# def test_valid_create(app, login_user,
#                       communities_permissions):
#     """Test VALID community creation request (POST .../communities/)."""
#     with app.app_context():
#         allowed_user = create_user('allowed')
#         communities_permissions(allowed_user.id).create_permission(True)
#         communities_permissions(allowed_user.id).read_permission(True)
#         db.session.commit()

#     with app.test_client() as client:
#         with app.app_context():
#             login_user(allowed_user, client)

#             headers = [('Content-Type', 'application/json'),
#                         ('Accept', 'application/json')]
#             res = client.post(url_for('b2share_communities.communities_list',
#                                       _external=False),
#                                 data=json.dumps(community_metadata),
#                                 headers=headers)
#             assert res.status_code == 201
#             # check that the returned community matches the given data
#             response_data = json.loads(res.get_data(as_text=True))
#             for field, value in community_metadata.items():
#                 assert response_data[field] == value

#             # check that an internal community returned id and that it contains
#             # the same data
#             assert 'id' in response_data.keys()
#             assert response_data['id'] == str(Community.get(
#                 name=community_metadata['name']).id)
#             headers = res.headers
#             community_id = response_data['id']

#     with app.app_context():
#         communities_permissions(
#             allowed_user.id).read_permission(True, community_id)
#         db.session.commit()

#     with app.app_context():
#         with app.test_client() as client:
#             login_user(allowed_user, client)
#             # check that the returned self link returns the same data
#             subtest_self_link(response_data, headers, client)
#             assert headers['Location'] == response_data['links']['self']
#         # check that one community has been created
#         assert len(CommunityModel.query.all()) == 1


# FIXME: Test is disabled for V2 as it is not used by the UI
# @community_with_and_without_access_control
# def test_invalid_create(app, login_user,
#                         communities_permissions):
#     """Test INVALID community creation request (POST .../communities/)."""
#     with app.app_context():
#         allowed_user = create_user('allowed')
#         communities_permissions(allowed_user.id).create_permission(True)
#         db.session.commit()

#     with app.app_context():
#         with app.test_client() as client:
#             login_user(allowed_user, client)
#             # check that creating with non accepted format will return 406
#             headers = [('Content-Type', 'application/json'),
#                        ('Accept', 'video/mp4')]
#             res = client.post(url_for('b2share_communities.communities_list'),
#                               data=json.dumps(community_metadata),
#                               headers=headers)
#             assert res.status_code == 406
#         # check that no community has been created
#         assert len(CommunityModel.query.all()) == 0

#     with app.app_context():
#         with app.test_client() as client:
#             login_user(allowed_user, client)
#             # Check that creating with non-json Content-Type will return 400
#             headers = [('Content-Type', 'video/mp4'),
#                        ('Accept', 'application/json')]
#             res = client.post(url_for('b2share_communities.communities_list'),
#                               data=json.dumps(community_metadata),
#                               headers=headers)
#             assert res.status_code == 415
#         # check that no community has been created
#         assert len(CommunityModel.query.all()) == 0

#     with app.app_context():
#         with app.test_client() as client:
#             login_user(allowed_user, client)
#             # check that creating with invalid json will return 400
#             headers = [('Content-Type', 'application/json'),
#                        ('Accept', 'application/json')]
#             res = client.post(url_for('b2share_communities.communities_list'),
#                               data='{fdssfd',
#                               headers=headers)
#             assert res.status_code == 400
#         # check that no community has been created
#         assert len(CommunityModel.query.all()) == 0

#     with app.app_context():
#         with app.test_client() as client:
#             login_user(allowed_user, client)
#             # check that creating with no content will return 400
#             headers = [('Content-Type', 'application/json'),
#                        ('Accept', 'application/json')]
#             res = client.post(url_for('b2share_communities.communities_list'),
#                               headers=headers)
#             assert res.status_code == 400

#             # Bad internal error:
#             with patch('b2share.modules.communities.views.db.session.commit') \
#                     as mock:
#                 mock.side_effect = Exception()

#                 headers = [('Content-Type', 'application/json'),
#                            ('Accept', 'application/json')]
#                 res = client.post(url_for('b2share_communities.communities_list'),
#                                   data=json.dumps(community_metadata),
#                                   headers=headers)
#                 assert res.status_code == 500
#         # check that no community has been created
#         assert len(CommunityModel.query.all()) == 0


def test_valid_get(app, login_user,
                   communities_permissions):
    """Test VALID community get request (GET .../communities/<id>)."""
    with app.app_context():
        # create community
        created_community = Community.create_community(**community_metadata)
        community_id = created_community.id
        # create allowed user
        allowed_user = create_user('allowed')
        communities_permissions(
            allowed_user.id).read_permission(True, community_id)
        db.session.commit()

    with app.app_context():
        with app.test_client() as client:
            login_user(allowed_user, client)

            headers = [('Content-Type', 'application/json'),
                       ('Accept', 'application/json')]
            res = client.get(url_for('b2share_communities.communities_item',
                                     community_id=community_id),
                             headers=headers)
            assert res.status_code == 200
            # check that the returned community matches the given data
            response_data = json.loads(res.get_data(as_text=True))
            for field, value in community_metadata.items():
                assert response_data[field] == value

            # check that an internal community returned id and that it contains
            # the same data
            assert 'id' in response_data.keys()
            assert response_data['id'] == str(Community.get(
                name=community_metadata['name']).id)
            headers = res.headers

    with app.app_context():
        with app.test_client() as client:
            login_user(allowed_user, client)
            # check that the returned self link returns the same data
            subtest_self_link(response_data, headers, client)


def test_invalid_get(app, login_user,
                     communities_permissions):
    """Test INVALID community get request (GET .../communities/<id>)."""
    with app.app_context():
        # create user allowed to GET all records
        allowed_user = create_user('allowed')
        communities_permissions(
            allowed_user.id).read_permission(True, None)
        db.session.commit()

    with app.app_context():
        with app.test_client() as client:
            login_user(allowed_user, client)
            unknown_uuid = uuid.uuid4().hex
            # check that GET with non existing id will return 404
            headers = [('Content-Type', 'application/json'),
                       ('Accept', 'application/json')]
            res = client.get(url_for('b2share_communities.communities_item',
                                     community_id=unknown_uuid),
                             headers=headers)
            assert res.status_code == 404
            # create community
            created_community = Community.create_community(
                **community_metadata)
            community_id = created_community.id
            db.session.commit()

            login_user(allowed_user, client)
            # check that GET with non accepted format will return 406
            headers = [('Accept', 'video/mp4')]
            res = client.get(url_for('b2share_communities.communities_item',
                                     community_id=community_id),
                             headers=headers)
            assert res.status_code == 406


# FIXME: Test is disabled for V2 as it is not used by the UI
# @community_with_and_without_access_control
# def test_valid_patch(app, login_user,
#                      communities_permissions, patch_community_function):
#     """Test VALID community patch request (PATCH .../communities/<id>)."""
#     with app.app_context():
#         # create community
#         created_community = Community.create_community(**community_metadata)
#         community_id = created_community.id
#         # create allowed user
#         allowed_user = create_user('allowed')
#         communities_permissions(
#             allowed_user.id).update_permission(True, community_id)
#         communities_permissions(
#             allowed_user.id).read_permission(True, community_id)
#         db.session.commit()

#     with app.app_context():
#         with app.test_client() as client:
#             login_user(allowed_user, client)
#             res = patch_community_function(community_id, client)
#             assert res.status_code == 200
#             # check that the returned community matches the given data
#             response_data = json.loads(res.get_data(as_text=True))
#             for field, value in patched_community_metadata.items():
#                 assert response_data[field] == value

#             # check that an internal community returned id and that it contains
#             # the same data
#             assert 'id' in response_data.keys()
#             assert response_data['id'] == str(Community.get(
#                 name=patched_community_metadata['name']).id)
#             headers = res.headers

#     with app.app_context():
#         with app.test_client() as client:
#             login_user(allowed_user, client)
#             # check that the returned self link returns the same data
#             subtest_self_link(response_data, headers, client)


# FIXME: Test is disabled for V2 as it is not used by the UI
# @community_with_and_without_access_control
# def test_invalid_patch(app, login_user,
#                        communities_permissions):
#     """Test INVALID community patch request (PATCH .../communities/<id>)."""
#     with app.app_context():
#         # create user allowed to update all records
#         allowed_user = create_user('allowed')
#         communities_permissions(
#             allowed_user.id).update_permission(True, None)
#         db.session.commit()

#         with app.test_client() as client:
#             login_user(allowed_user, client)
#             unknown_uuid = uuid.uuid4()
#             # check that PATCH with non existing id will return 404
#             headers = [('Content-Type', 'application/json-patch+json'),
#                        ('Accept', 'application/json')]
#             res = client.patch(url_for('b2share_communities.communities_item',
#                                        community_id=unknown_uuid),
#                                data=json.dumps(community_patch),
#                                headers=headers)
#             assert res.status_code == 404

#             # create community
#             created_community = Community.create_community(
#                 **community_metadata)
#             community_id = created_community.id
#             db.session.commit()

#             # check that PATCH with non accepted format will return 406
#             headers = [('Content-Type', 'application/json-patch+json'),
#                        ('Accept', 'video/mp4')]
#             res = client.patch(url_for('b2share_communities.communities_item',
#                                        community_id=community_id),
#                                data=json.dumps(community_patch),
#                                headers=headers)
#             assert res.status_code == 406

#             # check that PATCH with non-json Content-Type will return 415
#             headers = [('Content-Type', 'video/mp4'),
#                        ('Accept', 'application/json')]
#             res = client.patch(url_for('b2share_communities.communities_item',
#                                        community_id=community_id),
#                                data=json.dumps(community_patch),
#                                headers=headers)
#             assert res.status_code == 415

#             # check that PATCH with invalid json-patch will return 400
#             headers = [('Content-Type', 'application/json-patch+json'),
#                        ('Accept', 'application/json')]
#             res = client.patch(url_for('b2share_communities.communities_item',
#                                        community_id=community_id),
#                                data=json.dumps([
#                                    {'invalid': 'json-patch'}
#                                ]),
#                                headers=headers)
#             assert res.status_code == 400

#             # check that PATCH with invalid json will return 400
#             headers = [('Content-Type', 'application/json-patch+json'),
#                        ('Accept', 'application/json')]
#             res = client.patch(url_for('b2share_communities.communities_item',
#                                        community_id=community_id),
#                                data='{sdfsdf',
#                                headers=headers)
#             assert res.status_code == 400


# FIXME: Test is disabled for V2 as it is not used by the UI
# @community_with_and_without_access_control
# def test_valid_put(app, login_user,
#                    communities_permissions):
#     """Test VALID community put request (PUT .../communities/<id>)."""
#     with app.app_context():
#         # create community
#         created_community = Community.create_community(**community_metadata)
#         community_id = created_community.id
#         # create allowed user
#         allowed_user = create_user('allowed')
#         communities_permissions(
#             allowed_user.id).update_permission(True, community_id)
#         communities_permissions(
#             allowed_user.id).read_permission(True, community_id)
#         db.session.commit()

#     with app.app_context():
#         with app.test_client() as client:
#             login_user(allowed_user, client)

#             headers = [('Content-Type', 'application/json'),
#                        ('Accept', 'application/json')]
#             res = client.put(url_for('b2share_communities.communities_item',
#                                      community_id=community_id),
#                              data=json.dumps(patched_community_metadata),
#                              headers=headers)
#             assert res.status_code == 200
#             # check that the returned community matches the given data
#             response_data = json.loads(res.get_data(as_text=True))
#             for field, value in patched_community_metadata.items():
#                 assert response_data[field] == value

#             # check that an internal community returned id and that it contains
#             # the same data
#             assert 'id' in response_data.keys()
#             assert response_data['id'] == str(Community.get(
#                 name=patched_community_metadata['name']).id)
#             headers = res.headers

#     with app.app_context():
#         with app.test_client() as client:
#             login_user(allowed_user, client)
#             # check that the returned self link returns the same data
#             subtest_self_link(response_data, headers, client)


# FIXME: Test is disabled for V2 as it is not used by the UI
# @community_with_and_without_access_control
# def test_invalid_put(app, login_user,
#                      communities_permissions):
#     """Test INVALID community put request (PUT .../communities/<id>)."""
#     with app.app_context():
#         # create allowed user
#         allowed_user = create_user('allowed')
#         communities_permissions(
#             allowed_user.id).update_permission(True, None)
#         db.session.commit()

#         with app.test_client() as client:
#             login_user(allowed_user, client)
#             unknown_uuid = uuid.uuid4()
#             # check that PUT with non existing id will return 404
#             headers = [('Content-Type', 'application/json'),
#                        ('Accept', 'application/json')]
#             res = client.put(url_for('b2share_communities.communities_item',
#                                      community_id=unknown_uuid),
#                              data=json.dumps(patched_community_metadata),
#                              headers=headers)
#             assert res.status_code == 404

#             # create community
#             created_community = Community.create_community(
#                 **community_metadata)
#             community_id = created_community.id
#             db.session.commit()

#             # check that PUT with non accepted format will return 406
#             headers = [('Content-Type', 'application/json'),
#                        ('Accept', 'video/mp4')]
#             res = client.put(url_for('b2share_communities.communities_item',
#                                      community_id=community_id),
#                              data=json.dumps(patched_community_metadata),
#                              headers=headers)
#             assert res.status_code == 406

#             # check that PUT with non-json Content-Type will return 415
#             headers = [('Content-Type', 'video/mp4'),
#                        ('Accept', 'application/json')]
#             res = client.put(url_for('b2share_communities.communities_item',
#                                      community_id=community_id),
#                              data=json.dumps(patched_community_metadata),
#                              headers=headers)
#             assert res.status_code == 415

#             # check that PUT with invalid json will return 400
#             headers = [('Content-Type', 'application/json'),
#                        ('Accept', 'application/json')]
#             res = client.put(url_for('b2share_communities.communities_item',
#                                      community_id=community_id),
#                              data='{invalid-json',
#                              headers=headers)
#             assert res.status_code == 400


# FIXME: Test is disabled for V2 as it is not used by the UI
# @community_with_and_without_access_control
# def test_valid_delete(app, login_user,
#                       communities_permissions):
#     """Test VALID community delete request (DELETE .../communities/<id>)."""
#     with app.app_context():
#         # create community
#         created_community = Community.create_community(**community_metadata)
#         community_id = created_community.id
#         # create allowed user
#         allowed_user = create_user('allowed')
#         communities_permissions(
#             allowed_user.id).delete_permission(True, community_id)
#         db.session.commit()

#     with app.app_context():
#         with app.test_client() as client:
#             login_user(allowed_user, client)
#             headers = [('Content-Type', 'application/json'),
#                        ('Accept', 'application/json')]
#             res = client.delete(url_for('b2share_communities.communities_item',
#                                         community_id=community_id),
#                                 headers=headers)
#             assert res.status_code == 204

#     with app.app_context():
#         # check database state
#         with pytest.raises(CommunityDeletedError):
#             Community.get(community_id)
#         community = Community.get(community_id, with_deleted=True)
#         assert community.deleted
#         # check that one community has been created
#         assert len(CommunityModel.query.all()) == 1


# FIXME: Test is disabled for V2 as it is not used by the UI
# @community_with_and_without_access_control
# def test_invalid_delete(app, login_user,
#                         communities_permissions):
#     """Test INVALID community delete request (DELETE .../communities/<id>)."""
#     with app.app_context():
#         # create allowed user
#         allowed_user = create_user('allowed')
#         communities_permissions(
#             allowed_user.id).delete_permission(True, None)
#         db.session.commit()

#         with app.test_client() as client:
#             login_user(allowed_user, client)
#             unknown_uuid = uuid.uuid4()
#             # check that GET with non existing id will return 404
#             headers = [('Accept', 'application/json')]
#             res = client.delete(url_for('b2share_communities.communities_item',
#                                         community_id=unknown_uuid),
#                                 headers=headers)
#             assert res.status_code == 404


# FIXME: Test is disabled for V2 as it is not used by the UI
def test_action_on_deleted(app, login_user,
                           communities_permissions):
    """Test getting, deleting and updating a perviously deleted community."""
    with app.app_context():
        # create community
        created_community = Community.create_community(**community_metadata)
        community_id = created_community.id
        # create allowed user
        allowed_user = create_user('allowed')
        communities_permissions(
            allowed_user.id).delete_permission(True, community_id)
        db.session.commit()

    def assert_410_gone_result(res):
        """Check that the result is a 410 error with JSON message."""
        assert res.status_code == 410
        # check that the returned record matches the given data
        response_data = json.loads(res.get_data(as_text=True))
        assert response_data['status'] == 410

    with app.app_context():
        # delete the record
        Community.get(community_id).delete()
        with app.test_client() as client:
            login_user(allowed_user, client)
#             # try DELETE
#             headers = [('Content-Type', 'application/json'),
#                        ('Accept', 'application/json')]
#             res = client.delete(url_for('b2share_communities.communities_item',
#                                         community_id=community_id),
#                                 headers=headers)
#             assert_410_gone_result(res)
            # try GET
            headers = [('Content-Type', 'application/json'),
                       ('Accept', 'application/json')]
            res = client.get(url_for('b2share_communities.communities_item',
                                     community_id=community_id),
                             headers=headers)
            assert_410_gone_result(res)
#             # try PUT
#             headers = [('Content-Type', 'application/json'),
#                        ('Accept', 'application/json')]
#             res = client.put(url_for('b2share_communities.communities_item',
#                                      community_id=community_id),
#                              data=json.dumps(patched_community_metadata),
#                              headers=headers)
#             assert_410_gone_result(res)
#             # try PATCH
#             headers = [('Content-Type', 'application/json-patch+json'),
#                        ('Accept', 'application/json')]
#             res = client.patch(url_for('b2share_communities.communities_item',
#                                        community_id=community_id),
#                                data=json.dumps(community_patch),
#                                headers=headers)
#             assert_410_gone_result(res)

    # check that the record exist and is marked as deleted
    with app.app_context():
        # check database state
        with pytest.raises(CommunityDeletedError):
            Community.get(community_id)
        community = Community.get(community_id, with_deleted=True)
        assert community.deleted
        # check that one community has been created
        assert len(CommunityModel.query.all()) == 1
