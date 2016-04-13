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

"""PID providers."""

from __future__ import absolute_import, print_function

from invenio_pidstore.providers.base import BaseProvider
from invenio_pidstore.models import PIDStatus


class RecordUUIDProvider(BaseProvider):
    """Record identifier provider.

    The sole purpose of this model is to generate Persistent Identifiers from
    record's UUID.
    """

    pid_type = 'recuuid'
    """Type of persistent identifier."""

    pid_provider = None
    """Provider name.

    The provider name is not recorded in the PID since the provider does not
    provide any additional features besides creation of record ids.
    """

    default_status = PIDStatus.RESERVED
    """Record IDs are by default registered immediately."""

    @classmethod
    def create(cls, object_type=None, object_uuid=None, **kwargs):
        """Create a new record identifier."""
        # Request next integer in recid sequence.
        assert 'pid_value' not in kwargs
        assert object_uuid
        kwargs['pid_value'] = str(object_uuid)
        kwargs.setdefault('status', cls.default_status)
        if object_type and object_uuid:
            kwargs['status'] = PIDStatus.REGISTERED
        return super(RecordUUIDProvider, cls).create(
            object_type=object_type, object_uuid=object_uuid, **kwargs)
