# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2017 CERN.
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

"""Access controls for users and roles."""

from __future__ import absolute_import, print_function

from functools import partial

from b2share.modules.access.permissions import (
    OrPermissions,
    StrictDynamicPermission,
    generic_need_factory,
)
from invenio_access.permissions import (
    ParameterizedActionNeed, superuser_access
)
from flask_principal import ActionNeed, UserNeed


search_accounts_need = ActionNeed('accounts-search')
"""Need enabling to list all user accounts."""


def assign_role_need_factory(role=None, community=None):
    """Create the need for assigning roles in a community.

    Args:
        - role (int): id of the role which is allowed to (un)assign.
        - community (uuid): id of the community whose roles can be assigned.
    """
    return generic_need_factory('assign_role',
                                 community=str(community),
                                 role=str(role))


# actions to be registered by invenio_actions, see setup.py
assign_role_need = assign_role_need_factory()
# search_accounts_need -- see above


class RoleAssignPermission(StrictDynamicPermission):
    """Role assignment permission."""

    def __init__(self, role, user) :
        """Constructor.

        Args:
            role: assigned role.
            user: user to whom the role is assigned.
        """
        from b2share.modules.communities.api import (
            get_role_community_id, is_community_role
        )

        super(RoleAssignPermission, self).__init__()
        # ask for the permission to assign this specific role
        self.explicit_needs.add(assign_role_need_factory(role=role.id))
        # ask for the permission to assign any role in this role's community
        if is_community_role(role):
            community_id = get_role_community_id(role)
            self.explicit_needs.add(
                assign_role_need_factory(community=community_id)
            )


class AccountSearchPermission(StrictDynamicPermission):
    """Permission enabling to list all users.

    We restrict for now the possibility to list all users' accounts in order
    to prevent email address harvesting.
    """

    def __init__(self) :
        """Constructor."""
        super(AccountSearchPermission, self).__init__(search_accounts_need)


class AccountReadPermission(StrictDynamicPermission):
    """Permission enabling to read a users's account.

    We restrict for now the possibility to read users' account in order to
    prevent email address harvesting.
    """

    def __init__(self, user) :
        """Constructor.

        Args:
            user: user whose account is read.
        """
        # users allowed to list all accounts are also allowed to read
        # one specific account. Users can see their own account.
        super(AccountReadPermission, self).__init__(search_accounts_need,
                                                    UserNeed(user.id))


class AccountUpdatePermission(StrictDynamicPermission):
    """User account permission giving access."""

    def __init__(self, user) :
        """Constructor.

        Args:
            user: user whose account is modified.
        """
        super(AccountUpdatePermission, self).__init__()
        # account owner can't update his account for now as we only allow
        # account acticate/deactivate operations. This can change later if
        # we allow custom user name or other properties.
