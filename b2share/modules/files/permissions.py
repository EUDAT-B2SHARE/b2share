#

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

"""Access controls for files."""

from functools import partial

from invenio_access.permissions import (
    superuser_access, ParameterizedActionNeed
)
from invenio_db import db
from invenio_files_rest.models import Bucket, MultipartObject, ObjectVersion
from invenio_records.api import Record
from invenio_records_files.api import FileObject
from invenio_records_files.models import RecordsBuckets
from b2share.modules.access.permissions import (
    DenyAllPermission, StrictDynamicPermission, OrPermissions, DynamicPermission
)
from flask_principal import Permission, UserNeed

from b2share.modules.records.utils import is_publication, is_deposit


read_restricted_files = partial(ParameterizedActionNeed,
                                'read-restricted-files')
"""Need required to read fiels of a restricted access record."""


# Actions requiring read access
_read_actions = set([
    'bucket-read',
    'object-read',
    'bucket-listmultiparts',
])


# Actions requiring update access
_update_actions = _read_actions.union([
    'bucket-update',  # upload or complete a new file
    'object-delete',
    'multipart-delete',
])


def files_permission_factory(obj, action=None):
    """Permission for files are always based on the type of record.

    Record bucket: Read access only with open access.
    Deposit bucket: Read/update with restricted access.
    """
    # Extract bucket id
    bucket_id = None
    if isinstance(obj, Bucket):
        bucket_id = str(obj.id)
    elif isinstance(obj, ObjectVersion):
        bucket_id = str(obj.bucket_id)
    elif isinstance(obj, MultipartObject):
        bucket_id = str(obj.bucket_id)
    elif isinstance(obj, FileObject):
        bucket_id = str(obj.bucket_id)

    # Retrieve record
    if bucket_id is not None:
        # Record or deposit bucket
        rb = RecordsBuckets.query.filter_by(bucket_id=bucket_id).one_or_none()
        if rb is not None:
            record = Record.get_record(rb.record_id)
            if is_publication(record.model):
                return PublicationFilesPermission(record, action)
            elif is_deposit(record.model):
                return DepositFilesPermission(record, action)

    return DynamicPermission(superuser_access)


class RecordFilesPermission(OrPermissions):
    """Generic record files permission."""

    def __init__(self, record, action):
        """Constructor.

        Args:
            record: record to which access is requested.
            action: the action performed on the deposit.
        """
        super(RecordFilesPermission, self).__init__()
        # superuser can always do everything
        self.permissions.add(StrictDynamicPermission())
        self.record = record
        self.action = action
        self._load_additional_permissions()

    def _load_additional_permissions(self):
        """Create additional permission."""
        pass


class DepositFilesPermission(RecordFilesPermission):
    """Permission checked for acting on deposit records."""

    def _load_additional_permissions(self):
        """Create additional permission."""
        from b2share.modules.deposit.api import PublicationStates

        if self.record['publication_state'] == \
                PublicationStates.published.name:
            # Nobody can access published deposit files, for now at least
            self.permissions.clear()
            self.permissions.add(DenyAllPermission)
        else:
            from b2share.modules.deposit.permissions import (
                ReadDepositPermission, UpdateDepositMetadataPermission
            )
            # all actions are granted to the owner
            if self.action in {'bucket-read', 'object-read'}:
                # A user can read the files if he can read the deposit
                self.permissions.add(
                    ReadDepositPermission(self.record)
                )
            if self.action in {'bucket-update', 'object-delete'}:
                # A user can modify the files if he can modify the metadata
                self.permissions.add(
                    UpdateDepositMetadataPermission(self.record)
                )


class PublicationFilesPermission(RecordFilesPermission):
    """Permission checked for acting on published records."""

    def _load_additional_permissions(self):
        """Create additional permission."""
        if self.action in _read_actions:
            if self.record['open_access']:
                # allow everybody to see open_access records
                self.permissions.clear()
                self.permissions.add(Permission())
            else:
                needs = set()
                needs.add(read_restricted_files(self.record['community']))
                needs.add(read_restricted_files(None))
                # all actions are granted to the owner
                for owner_id in self.record['_deposit']['owners']:
                    needs.add(UserNeed(owner_id))
                self.permissions.add(StrictDynamicPermission(*needs))
        else:
            # Nobody can change the files of a published record.
            self.permissions.clear()
            self.permissions.add(DenyAllPermission)
