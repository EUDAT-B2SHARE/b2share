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

"""Access controls for deposits."""

from copy import deepcopy
from collections import namedtuple
from itertools import chain

from jsonpatch import apply_patch, JsonPatchException
from flask_principal import UserNeed
from invenio_access.permissions import (
    superuser_access, ParameterizedActionNeed, DynamicPermission
)
from invenio_access.models import ActionUsers, ActionRoles
from invenio_accounts.models import userrole

from flask import request, abort
from b2share.modules.access.permissions import (OrPermissions, AndPermissions,
                                                StrictDynamicPermission)
from invenio_db import db

def list_readable_communities(user_id):
    result = namedtuple('ReadableCommunities', ['all', 'communities'])(
        set(), {})
    roles_needs = db.session.query(ActionRoles).join(
        userrole, ActionRoles.role_id == userrole.columns['role_id']
    ).filter(
        userrole.columns['user_id'] == user_id,
        ActionRoles.action.like('read-deposit-%')
    ).all()
    user_needs = ActionUsers.query.filter(
        ActionUsers.user_id == user_id,
        ActionRoles.action.like('read-deposit-%'),
    ).all()

    for need in chain(roles_needs, user_needs):
        publication_state = need.action[13:]
        community_id = need.argument
        if community_id is None:
            result.all.add(publication_state)
        else:
            result.communities.setdefault(community_id, set()).add(
                publication_state)
    return result

class CreateDepositPermission(OrPermissions):
    """Deposit read permission."""

    def __init__(self, record=None):
        """Constructor.

        Args:
            record: data submitted for the new deposit
        """
        super(CreateDepositPermission, self).__init__()
        self.record = record

        if record is not None:
            needs = set()
            needs.add(ParameterizedActionNeed(
                'create-deposit-{}'.format(
                    record.get('publication_state', 'draft')),
                record['community'])
            )
            needs.add(ParameterizedActionNeed(
                'create-deposit-{}'.format(
                    record.get('publication_state', 'draft')),
                None)
            )
            self.permissions.add(StrictDynamicPermission(*needs))

    def allows(self, *args, **kwargs):
        # allowed if the data is not loaded yet
        if self.record is None:
            return True
        return super(CreateDepositPermission, self).allows(*args, **kwargs)

    def can(self, *args, **kwargs):
        # allowed if the data is not loaded yet
        if self.record is None:
            return True
        return super(CreateDepositPermission, self).can(*args, **kwargs)


class DepositPermission(OrPermissions):
    """Generic deposit permission."""

    def __init__(self, record):
        """Constructor.

        Args:
            deposit: deposit to which access is requested.
        """
        super(DepositPermission, self).__init__()
        # superuser can always do everything
        self.permissions.add(StrictDynamicPermission(superuser_access))
        self.deposit = record
        self._load_additional_permissions()

    def _load_permissions(self):
        """Create additional permission."""
        raise NotImplementedError()


class ReadDepositPermission(DepositPermission):
    """Deposit read permission."""

    def _load_additional_permissions(self):
        permission = DynamicPermission()
        for owner_id in self.deposit['_deposit']['owners']:
            permission.needs.add(UserNeed(owner_id))
        permission.needs.add(ParameterizedActionNeed(
            'read-deposit-{}'.format(self.deposit['publication_state']),
            self.deposit['community'])
        )
        self.permissions.add(permission)


class UpdateDepositPermission(DepositPermission):
    """Deposit update permission."""

    def _load_additional_permissions(self):
        permissions = []
        new_deposit = None
        # Check submit/publish actions
        if (request.method == 'PATCH' and
                request.content_type == 'application/json-patch+json'):
            # FIXME: need some optimization on Invenio side. We are applying
            # the patch twice
            patch = request.get_json(force=True)
            if patch is None:
                abort(400)
            new_deposit = deepcopy(self.deposit)
            try:
                apply_patch(new_deposit, patch, in_place=True)
            except JsonPatchException:
                abort(400)
        elif (request.method == 'PUT' and
                request.content_type == 'application/json'):
            new_deposit = request.get_json()
            if new_deposit is None:
                abort(400)
        else:
            return

        # Create permission for updating the state_field
        if (new_deposit is not None and new_deposit['publication_state']
                != self.deposit['publication_state']):
            state_permission = StrictDynamicPermission()
            # state_permission.needs.add(ParameterizedActionNeed(
            #     'deposit-publication-state-transition-{0}-{1}'.format(
            #         self.deposit['publication_state'],
            #         new_deposit['publication_state'])
            #     , self.deposit['community'])
            # )
            # User can change the state
            # FIXME: Disable later user pulication when it is not allowed
            for owner_id in self.deposit['_deposit']['owners']:
                state_permission.needs.add(UserNeed(owner_id))
            permissions.append(state_permission)

        # Create permission for updating generic metadata fields.
        # Only superadmin can modify published draft.
        if self.deposit['publication_state'] != 'published':
            # Check if any metadata has been changed
            del new_deposit['publication_state']
            original_metadata = deepcopy(self.deposit)
            del original_metadata['publication_state']
            if original_metadata != new_deposit:
                metadata_permission = StrictDynamicPermission()
                # Owners are allowed to update
                for owner_id in self.deposit['_deposit']['owners']:
                    metadata_permission.needs.add(UserNeed(owner_id))
                # metadata_permission.needs.add(ParameterizedActionNeed(
                #     'update-deposit-{}'.format(
                #         self.deposit['publication_state'])
                #     , self.deposit['community'])
                # )
                permissions.append(metadata_permission)

        if len(permissions) > 1:
            self.permissions.add(AndPermissions(*permissions))
        elif len(permissions) == 1:
            self.permissions.add(permissions[0])


class DeleteDepositPermission(DepositPermission):
    """Deposit delete permission."""

    def _load_additional_permissions(self):
        permission = DynamicPermission()
        # owners can delete the deposit if it is not published
        if not 'pid' in self.deposit['_deposit']:
            for owner_id in self.deposit['_deposit']['owners']:
                permission.needs.add(UserNeed(owner_id))
        permission.needs.add(ParameterizedActionNeed(
            'delete-deposit-{}'.format(self.deposit['publication_state']),
            self.deposit['community'])
        )
        self.permissions.add(permission)
