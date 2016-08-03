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

from b2share.modules.access.permissions import OrPermissions
from invenio_access.permissions import superuser_access

from b2share.modules.access.permissions import StrictDynamicPermission


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


class UpdateRecordPermission(RecordPermission):
    """Record update permission."""


class DeleteRecordPermission(RecordPermission):
    """Record delete permission."""
