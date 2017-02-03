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

"""Access controls for records."""

from __future__ import absolute_import, print_function

import json
from jsonpatch import apply_patch, JsonPatchException
from copy import deepcopy
from flask import request, abort
from flask_principal import UserNeed

from invenio_access.permissions import (
    superuser_access, ParameterizedActionNeed, DynamicPermission
)
from b2share.modules.access.permissions import (
    StrictDynamicPermission, OrPermissions
)
from .loaders import record_patch_input_loader


def _record_need_factory(name, **kwargs):
    if kwargs:
        for key, value in enumerate(kwargs):
            if value is None:
                del kwargs[key]

    if not kwargs:
        argument = None
    else:
        argument = json.dumps(kwargs, separators=(',', ':'), sort_keys=True)
    return ParameterizedActionNeed(name, argument)


def update_record_metadata_need_factory(community):
    return _record_need_factory('update-record-metadata', community=community)


class RecordPermission(OrPermissions):
    """Generic record permission."""

    def __init__(self, record):
        """Constructor.

        Args:
            record: record to which access is requested.
        """
        super(RecordPermission, self).__init__()
        # superuser can always do everything
        self.permissions.add(StrictDynamicPermission(superuser_access))
        self.record = record
        self._load_additional_permissions()

    def _load_additional_permissions(self):
        """Create additional permission."""
        pass


class UpdateRecordMetadataPermission(StrictDynamicPermission):
    """Permission to update a record's metadata fields."""

    def __init__(self, record):
        """Constructor

        Args:
            record (Record): record which is modified.
        """
        super(UpdateRecordMetadataPermission, self).__init__()
        # Owners are allowed to update
        for owner_id in record['_deposit']['owners']:
            self.explicit_needs.add(UserNeed(owner_id))

        # authorize if the user can modify metadata in the old
        # publication state
        self.explicit_needs.add(
            update_record_metadata_need_factory(
                community=record['community'],
            )
        )


class UpdateRecordPermission(RecordPermission):
    """Record update permission."""
    def _load_additional_permissions(self):
        permissions = []
        new_record = None
        # Check submit/publish actions
        if (request.method == 'PATCH' and
            request.content_type == 'application/json-patch+json'):
            # FIXME: optimise on Invenio side. We are applying the patch twice
            # see also the UpdateDepositPermission
            patch = record_patch_input_loader(self.record)
            new_record = deepcopy(self.record)
            try:
                apply_patch(new_record, patch, in_place=True)
            except JsonPatchException:
                abort(400)
        else:
            abort(400)

        # Create permission for updating generic metadata fields.
        # Only superadmin can modify published draft.
        permissions.append(
            UpdateRecordMetadataPermission(self.record)
        )

        if len(permissions) > 1:
            self.permissions.add(AndPermissions(*permissions))
        elif len(permissions) == 1:
            self.permissions.add(permissions[0])


class DeleteRecordPermission(RecordPermission):
    """Record delete permission."""
