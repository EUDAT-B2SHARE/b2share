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

"""Example Permissions for communities."""

from functools import partial

from invenio_access.permissions import Permission, \
    ParameterizedActionNeed

CommunityReadActionNeed = partial(ParameterizedActionNeed, 'communities-read')
"""Action need for reading a community."""

communities_read_all = CommunityReadActionNeed(None)
"""Read all communities action need."""

CommunityCreateActionNeed = partial(
    ParameterizedActionNeed, 'communities-create')
"""Action need for creating a community."""

communities_create_all = CommunityCreateActionNeed(None)
"""Create all communities action need."""

CommunityUpdateActionNeed = partial(
    ParameterizedActionNeed, 'communities-update')
"""Action need for updating a community."""

communities_update_all = CommunityUpdateActionNeed(None)
"""Update all communities action need."""

CommunityDeleteActionNeed = partial(
    ParameterizedActionNeed, 'communities-delete')
"""Action need for deleting a community."""

communities_delete_all = CommunityDeleteActionNeed(None)
"""Delete all communities action need."""

communities_create_all_permission = Permission(communities_create_all)


def read_permission_factory(community):
    """Factory for creating read permissions for communities."""
    return Permission(CommunityReadActionNeed(str(community.id)))


def update_permission_factory(community):
    """Factory for creating update permissions for communities."""
    return Permission(CommunityUpdateActionNeed(str(community.id)))


def delete_permission_factory(community):
    """Factory for creating delete permissions for communities."""
    return Permission(CommunityDeleteActionNeed(str(community.id)))
