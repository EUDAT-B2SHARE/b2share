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

"""PID providers."""

from __future__ import absolute_import, print_function

import uuid

from invenio_pidstore.providers.base import BaseProvider
from invenio_pidstore.models import PIDStatus


class DepositUUIDProvider(BaseProvider):
    """Deposit identifier provider."""

    pid_type = 'b2dep'
    """Type of persistent identifier."""

    pid_provider = None
    """Provider name.

    The provider name is not recorded in the PID since the provider does not
    provide any additional features besides creation of record ids.
    """

    default_status = PIDStatus.REGISTERED
    """Deposit UUIDs are registered immediately."""

    @classmethod
    def create(cls, object_type=None, object_uuid=None, **kwargs):
        """Create a new record identifier."""
        if 'pid_value' not in kwargs:
            kwargs.setdefault('pid_value', uuid.uuid4().hex)
        kwargs.setdefault('status', cls.default_status)
        return super(DepositUUIDProvider, cls).create(
            object_type=object_type, object_uuid=object_uuid, **kwargs)
