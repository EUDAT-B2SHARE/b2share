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

"""PID Fetchers."""

from collections import namedtuple

from .providers import DepositUUIDProvider


FetchedPID = namedtuple('FetchedPID', ['provider', 'object_uuid',
                                       'pid_type', 'pid_value'])


def b2share_deposit_uuid_fetcher(record_uuid, data):
    """Fetch a deposit's identifiers."""
    return FetchedPID(
        provider=DepositUUIDProvider,
        object_uuid=record_uuid,
        pid_type=DepositUUIDProvider.pid_type,
        pid_value=str(data['_deposit']['id']),
    )
