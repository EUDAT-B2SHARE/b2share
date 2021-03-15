# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2015, 2016, University of Tuebingen, CERN.
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

"""B2Share generic permissions."""

import json

from flask_principal import Permission, Need
from invenio_access.permissions import (
    Permission, ParameterizedActionNeed,
)


AllowAllPermission = type('Allow', (), {
    'can': lambda self: True,
    'allows': lambda *args: True,
})()
"""Permission that always allow an access."""


DenyAllPermission = type('Deny', (), {
    'can': lambda self: False,
    'allows': lambda *args: False,
})()
"""Permission that always deny an access."""


def admin_only(*args, **kwargs):
    """Return permission that allows access to super-admin only.

    :returns: a permission allowing only super-admin.
    """
    return StrictDynamicPermission()
"""Permission allowing only access to super administrator."""


AuthenticatedNeed = Need('authenticated', True)
"""Need provided by any authenticated user."""


def authenticated_only(*args, **kwargs):
    """Return a permission allowing access to admin and authenticated users.

    :returns: a permission allowing only super-admin.
    """
    return StrictDynamicPermission(AuthenticatedNeed)
"""Permission allowing only access to super administrator
   and authenticated users.
"""

class StrictDynamicPermission(Permission):
    """Stricter DynamicPermission.

    It adds the given needs to the returned needs instead of using only
    those found in the database.
    This has two effects:
        - Identities can also provide a need without using the database.
        - The permission is not given even if there are no needs in the
            database. Thus the action is not allowed by default.
    """
    def __init__(self, *needs):
        self.explicit_excludes = set()
        super(StrictDynamicPermission, self).__init__(*needs)

    @property
    def needs(self):
        needs = super(StrictDynamicPermission, self).needs
        needs.update(self.explicit_needs)
        return needs

    @property
    def excludes(self):
        excludes = super(StrictDynamicPermission, self).excludes
        excludes.update(self.explicit_excludes)
        return excludes


class PermissionSet(Permission):
    """Abstract permissions combining multiple permissions.

    Default Flask-Principal permissions just test the intersection of
    user Identity set of Needs and Permission set of Needs. The user is allowed
    to access as soon as one of the need is in both sets. This is enough in
    most cases but sometime we need to have more complex permissions where
    one intersection is not enough. This is why this class and its subclasses
    were created.
    """

    def __init__(self, *permissions, allow_if_no_permissions=False):
        """A set of set of permissions, all of which must be allow the
        identity to have access.
        """
        self.permissions = set(permissions)
        self.allow_if_no_permissions = allow_if_no_permissions

    def allows(self, identity):
        raise NotImplementedError()

    def reverse(self):
        raise NotImplementedError()

    def union(self):
        raise NotImplementedError()

    def difference(self):
        raise NotImplementedError()

    def issubset(self):
        raise NotImplementedError()

    def __repr__(self):
        return '<{0} {1} permissions={2}>'.format(
            self.__class__.__name__, self.action, self.permissions
        )


class AndPermissions(PermissionSet):
    """Represents a set of Permissions, all of which must be allowed to access
    a resource

    Args:
        permissions: a set of permissions.
    """
    action = 'AND'

    def allows(self, identity):
        """Whether the identity can access this permission.
        Args:
            identity: The identity
        """
        for permission in self.permissions:
            if not permission.allows(identity):
                return False
        return len(self.permissions) > 0 or self.allow_if_no_permissions


class OrPermissions(PermissionSet):
    """Represents a set of Permissions, any of which must be allowed to access
    a resource

    Args:
        permissions: a set of permissions.
    """

    action = 'OR'

    def allows(self, identity):
        """Whether the identity can access this permission.
        Args:
            identity: The identity
        """
        for permission in self.permissions:
            if permission.allows(identity):
                return True
        return len(self.permissions) == 0 and self.allow_if_no_permissions


def generic_need_factory(name, **kwargs):
    """Generic need factory using a JSON object as argument.

    Args:
        **kwargs: keywords which will be used in the JSON parameter.
    """
    if kwargs:
        for key, value in enumerate(kwargs):
            if value is None:
                del kwargs[key]

    if not kwargs:
        argument = None
    else:
        argument = json.dumps(kwargs, separators=(',', ':'), sort_keys=True)
    return ParameterizedActionNeed(name, argument)
