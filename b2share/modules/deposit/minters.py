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

"""PID minters."""

from __future__ import absolute_import, print_function

import uuid

from .providers import DepositUUIDProvider
from b2share.modules.records.providers import RecordUUIDProvider


def b2share_deposit_uuid_minter(record_uuid, data):
    """Mint deposit's PID."""
    dep_pid = DepositUUIDProvider.create(
        object_type='rec', object_uuid=record_uuid,
        # we reuse the deposit UUID as PID value. This makes the demo easier.
        pid_value=record_uuid.hex
    )

    data['_deposit'] = {
        'id': dep_pid.pid.pid_value,
        # FIXME: do not set the status once it is done by invenio-deposit API
        'status': 'draft',
    }

    # reserve the record PID
    RecordUUIDProvider.create(
        object_type='rec',
        pid_value=dep_pid.pid.pid_value
    )

    return dep_pid.pid
