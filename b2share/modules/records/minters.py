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

"""PID minters."""

from __future__ import absolute_import, print_function

from datetime import datetime

from flask import current_app

from invenio_oaiserver.provider import OAIIDProvider
from invenio_oaiserver.utils import datetime_to_datestamp

from .providers import RecordUUIDProvider


def b2share_record_uuid_minter(record_uuid, data):
    """Use record's UUID as unique identifier."""
    provider = RecordUUIDProvider.create(
        object_type='rec', object_uuid=record_uuid,
        pid_value=data['_deposit']['id']
    )
    if not '_pid' in data:
        data['_pid'] = []
    data['_pid'].append({
        'value': provider.pid.pid_value,
        'type': provider.pid.pid_type,
    })

    b2share_oaiid_minter(record_uuid, data)

    return provider.pid


def b2share_oaiid_minter(record_uuid, data):
    """Mint record identifiers."""
    pid_value = data.get('_oai', {}).get('id')
    if pid_value is None:
        assert '_deposit' in data and 'id' in data['_deposit']
        id_ = str(data['_deposit']['id'])
        pid_value = current_app.config.get('OAISERVER_ID_PREFIX', '') + id_
    provider = OAIIDProvider.create(
        object_type='rec', object_uuid=record_uuid,
        pid_value=str(pid_value)
    )
    data.setdefault('_oai', {})
    data['_oai'].update({
        'id': provider.pid.pid_value,
        'sets': [],
        'updated': datetime_to_datestamp(datetime.utcnow()),
    })
    return provider.pid
