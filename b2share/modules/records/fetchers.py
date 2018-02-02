# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2016 University of Tuebingen, CERN.
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

"""PID Fetchers."""

from collections import namedtuple

from .providers import RecordUUIDProvider

FetchedPID = namedtuple('FetchedPID', ['provider', 'object_uuid',
                                       'pid_type', 'pid_value'])


def b2share_record_uuid_fetcher(record_uuid, data):
    """Fetch a record's identifiers."""
    return FetchedPID(
        provider=RecordUUIDProvider,
        object_uuid=record_uuid,
        pid_type=RecordUUIDProvider.pid_type,
        pid_value=str(next(pid['value'] for pid in data['_pid']
                           if pid['type'] == RecordUUIDProvider.pid_type)),
    )


def b2share_parent_pid_fetcher(record_uuid, data):
    """Fetch record's parent version persistent identifier."""
    return FetchedPID(
        provider=RecordUUIDProvider,
        # The record_uuid is not relevant for the parent pids
        # but it is added in the signature for consistency.
        object_uuid=None,
        pid_type=RecordUUIDProvider.pid_type,
        pid_value=next(pid['value'] for pid in data['_pid']
                       if pid['type'] == RecordUUIDProvider.parent_pid_type)
    )
