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

import pytest
from .helpers import patch_with_json_diff, patch_with_json_patch
from invenio_access.models import ActionUsers
from invenio_db import db

from b2share.modules.communities.permissions import communities_create_all, \
    communities_delete_all, communities_read_all, communities_update_all


@pytest.fixture(scope='function')
def communities_permissions(app):
    accounts = app.extensions['invenio-accounts']

    class UserPermissionsFactory(object):

        def __init__(self, user_id):
            self.user_id = user_id

        def create_permission(self, allow):
            with db.session.begin_nested():
                user = accounts.datastore.get_user(self.user_id)
                # only add the access rights if the access control is enabled
                db.session.add(ActionUsers(
                    action=communities_create_all.value, argument=None,
                    user=user, exclude=not allow))

        def read_permission(self, allow, community_id=None):
            with db.session.begin_nested():
                user = accounts.datastore.get_user(self.user_id)
                # only add the access rights if the access control is enabled
                db.session.add(ActionUsers(
                    action=communities_read_all.value,
                    argument=str(community_id),
                    user=user, exclude=not allow))

        def update_permission(self, allow, community_id=None):
            with db.session.begin_nested():
                user = accounts.datastore.get_user(self.user_id)
                # only add the access rights if the access control is enabled
                db.session.add(ActionUsers(
                    action=communities_update_all.value,
                    argument=str(community_id),
                    user=user, exclude=not allow))

        def delete_permission(self, allow, community_id=None):
            with db.session.begin_nested():
                user = accounts.datastore.get_user(self.user_id)
                # only add the access rights if the access control is enabled
                db.session.add(ActionUsers(
                    action=communities_delete_all.value,
                    argument=str(community_id),
                    user=user, exclude=not allow))

    return UserPermissionsFactory


@pytest.fixture(params=[patch_with_json_patch, patch_with_json_diff])
def patch_community_function(request):
    """Fixture used to test both way of patching a record."""
    return request.param
