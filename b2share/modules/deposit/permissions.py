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

import json
from copy import deepcopy
from collections import namedtuple
from itertools import chain
from functools import partial

from jsonpatch import apply_patch
from flask_principal import UserNeed
from invenio_access.permissions import (
    superuser_access, ParameterizedActionNeed
)
from invenio_access.models import ActionUsers, ActionRoles
from flask_security import current_user
from invenio_accounts.models import userrole

from flask import request, abort
from b2share.modules.access.permissions import (AuthenticatedNeed,
                                                OrPermissions, AndPermissions, DynamicPermission,
                                                StrictDynamicPermission)
from invenio_db import db

from .loaders import deposit_patch_input_loader


def _deposit_need_factory(name, **kwargs):
    """Generate a JSON argument string from the given keyword arguments.

    The JSON string is always generated the same way so that the resulting Need
    is equal to any other Need generated with the same name and kwargs.
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


def create_deposit_need_factory(community=None, publication_state='draft'):
    """Create the need needed to create a deposit."""
    # FIXME: check that the community_id and publication_state exist
    return _deposit_need_factory('create-deposit',
                                 community=community,
                                 publication_state=publication_state)


def read_deposit_need_factory(community, publication_state):
    """Create the need needed to read a deposit."""
    # FIXME: check that the community_id and publication_state exist
    return _deposit_need_factory('read-deposit',
                                 community=community,
                                 publication_state=publication_state)


def update_deposit_publication_state_need_factory(community, old_state,
                                                  new_state):
    """Create the need needed to change the publication_state of a deposit."""
    # FIXME: check that the community_id and publication states exist
    return _deposit_need_factory('update-deposit-publication-state',
                                 community=community,
                                 old_state=old_state,
                                 new_state=new_state)


def update_deposit_metadata_need_factory(community, publication_state):
    """Create the need needed to change the metadata of a deposit."""
    # FIXME: check that the community_id and publication state exist
    return _deposit_need_factory('update-deposit-metadata',
                                 community=community,
                                 publication_state=publication_state)


# actions to be registered by invenio_actions, see setup.py
create_deposit_need = create_deposit_need_factory()
read_deposit_need = read_deposit_need_factory(None, None)
update_deposit_publication_state_need = update_deposit_publication_state_need_factory(
    None, None, None)
update_deposit_metadata_need = update_deposit_metadata_need_factory(None, None)


ReadableCommunities = namedtuple('ReadableCommunities', ['all', 'communities'])


def list_readable_communities(user_id):
    """List all communities whose records can be read by the given user.

    Args:
        user_id: id of the user which has read access to the retured
        communities.

    Returns:
        ReadableCommunities: list of communities which can be read by the
        given user with the publication_states limitation when the access
        is restricted to some states.
    """
    result = ReadableCommunities(set(), {})
    roles_needs = db.session.query(ActionRoles).join(
        userrole, ActionRoles.role_id == userrole.columns['role_id']
    ).filter(
        userrole.columns['user_id'] == user_id,
        ActionRoles.action == 'read-deposit',
    ).all()
    user_needs = ActionUsers.query.filter(
        ActionUsers.user_id == user_id,
        ActionUsers.action == 'read-deposit',
    ).all()

    for need in chain(roles_needs, user_needs):
        argument = json.loads(need.argument)
        result.communities.setdefault(argument['community'], set()).add(
            argument['publication_state'])
    return result


class CreateDepositPermission(AndPermissions):
    """Deposit create permission."""

    def __init__(self, record=None, previous_record=None):
        """Constructor.

        Args:
            record: data submitted for the new deposit
        """
        super(CreateDepositPermission, self).__init__()
        self.record = record
        if record is not None:
            needs = set()

            from b2share.modules.communities.api import Community

            community = Community.get(record['community'])
            publication_state = record.get('publication_state', 'draft')
            if publication_state != 'draft' or community.restricted_submission:
                needs.add(create_deposit_need_factory())
                needs.add(create_deposit_need_factory(
                    community=record['community'],
                    publication_state=publication_state,
                ))
            elif not community.restricted_submission:
                needs.add(AuthenticatedNeed)

            self.permissions.add(StrictDynamicPermission(*needs))
            if previous_record:
                # we allow only the owner of a record to
                # create a new version of it.
                needs = set()
                for owner_id in previous_record['_deposit']['owners']:
                    needs.add(UserNeed(owner_id))
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
        # owners of the deposit are allowed to read the deposit.
        needs = set(UserNeed(owner_id)
                 for owner_id in self.deposit['_deposit']['owners'])
        # add specific permission to read deposits of this community
        # in this publication state
        needs.add(read_deposit_need_factory(
            community=self.deposit['community'],
            publication_state=self.deposit['publication_state'],
        ))
        permission = DynamicPermission(*needs)
        self.permissions.add(permission)


class UpdateDepositMetadataPermission(StrictDynamicPermission):
    """Permission to update a deposit's metadata fields."""

    def __init__(self, deposit, new_state=None):
        """Constructor

        Args:
            deposit (Deposit): deposit which is modified.
            new_state (str): new publication state of the deposit
                if applicable.
        """
        super(UpdateDepositMetadataPermission, self).__init__()
        # Owners are allowed to update
        for owner_id in deposit['_deposit']['owners']:
            self.explicit_needs.add(UserNeed(owner_id))

        # authorize if the user can modify metadata in the old
        # publication state
        self.explicit_needs.add(
            update_deposit_metadata_need_factory(
                community=deposit['community'],
                publication_state=deposit['publication_state']
            )
        )
        # authorize if the user can modify metadata in the new
        # publication state
        if new_state != deposit['publication_state']:
            self.explicit_needs.add(
                update_deposit_metadata_need_factory(
                    community=deposit['community'],
                    publication_state=new_state
                )
            )


class UpdateDepositPermission(DepositPermission):
    """Deposit update permission."""

    def _load_additional_permissions(self):

        from b2share.modules.deposit.api import generate_external_pids, PublicationStates

        permissions = []
        new_deposit = None
        # Check submit/publish actions
        if (request.method == 'PATCH' and
            request.content_type == 'application/json-patch+json'):

            # FIXME: need some optimization on Invenio side. We are applying
            # the patch twice
            patch = deposit_patch_input_loader(self.deposit)
            new_deposit = deepcopy(self.deposit)
            # Generate 'external_pids' field in order to give
            # the illusion that this field actually exist.
            external_pids = generate_external_pids(self.deposit)
            if external_pids:
                new_deposit['external_pids'] = deepcopy(external_pids)
            apply_patch(new_deposit, patch, in_place=True)
            external_pids_changed = False
            if external_pids:
                external_pids_changed = (
                    external_pids != new_deposit['external_pids']
                )
                del new_deposit['external_pids']
        else:
            abort(400)

        # Create permission for updating the state_field
        if (new_deposit is not None and new_deposit['publication_state']
                != self.deposit['publication_state']):
            state_permission = StrictDynamicPermission()
            state_permission.explicit_needs.add(
                update_deposit_publication_state_need_factory(
                    community=self.deposit['community'],
                    old_state=self.deposit['publication_state'],
                    new_state=new_deposit['publication_state']
                )
            )

            # Owners of a record can always "submit" it.
            if (self.deposit['publication_state'] == PublicationStates.draft.name and
                new_deposit['publication_state'] == PublicationStates.submitted.name or
                # Owners have also the right to move the record from submitted
                # to draft again.
                self.deposit['publication_state'] == PublicationStates.submitted.name and
                new_deposit['publication_state'] == PublicationStates.draft.name):
                # Owners are allowed to update
                for owner_id in self.deposit['_deposit']['owners']:
                    state_permission.explicit_needs.add(UserNeed(owner_id))
            permissions.append(state_permission)

        # Create permission for updating generic metadata fields.
        # Only superadmin can modify published draft.
        if self.deposit['publication_state'] != 'published':
            new_state = new_deposit['publication_state']
            # Check if any metadata has been changed
            del new_deposit['publication_state']
            original_metadata = deepcopy(self.deposit)
            del original_metadata['publication_state']
            if original_metadata != new_deposit:
                permissions.append(
                    UpdateDepositMetadataPermission(self.deposit, new_state)
                )

            if external_pids_changed:
                from b2share.modules.files.permissions import DepositFilesPermission

                permissions.append(
                    DepositFilesPermission(self.deposit, 'bucket-update')
                )

        if len(permissions) > 1:
            self.permissions.add(AndPermissions(*permissions))
        elif len(permissions) == 1:
            self.permissions.add(permissions[0])
        elif len(permissions) == 0:
            # Avoid forbidding requests doing nothing. This can be useful if
            # a script replays an action.
            self.permissions.add(
                UpdateDepositMetadataPermission(
                    self.deposit, new_deposit['publication_state']
                )
            )


class DeleteDepositPermission(DepositPermission):
    """Deposit delete permission."""

    def _load_additional_permissions(self):
        permission = StrictDynamicPermission()
        # owners can delete the deposit if it is not published
        if not 'pid' in self.deposit['_deposit']:
            needs = set()
            for owner_id in self.deposit['_deposit']['owners']:
                needs.add(UserNeed(owner_id))
                self.permissions.add(StrictDynamicPermission(*needs))
        self.permissions.add(permission)
