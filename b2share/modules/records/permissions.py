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
from flask_principal import UserNeed

from invenio_access.permissions import superuser_access, \
    ParameterizedActionNeed

from b2share.modules.access.permissions import StrictDynamicPermission


def _record_need_factory(name, **kwargs):
    from invenio_access.permissions import ParameterizedActionNeed

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


# actions to be registered by invenio_actions, see setup.py
update_record_metadata_need = update_record_metadata_need_factory(None)


class UpdateRecordPermission(StrictDynamicPermission):
    """Record update permission."""

    def __init__(self, record):
        super(UpdateRecordPermission, self).__init__()
        # Owners are allowed to update
        for owner_id in record['_deposit']['owners']:
            self.explicit_needs.add(UserNeed(owner_id))

        # authorize depending on the community
        self.explicit_needs.add(
            update_record_metadata_need_factory(
                community=record['community'],
            )
        )


class DeleteRecordPermission(StrictDynamicPermission):
    """Record delete permission."""

    def __init__(self, record):
        from invenio_access.permissions import superuser_access
        super(DeleteRecordPermission, self).__init__(superuser_access)
