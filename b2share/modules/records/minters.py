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

from flask import current_app, url_for

from invenio_oaiserver.provider import OAIIDProvider
from invenio_oaiserver.utils import datetime_to_datestamp

from datacite.errors import DataCiteError

from .providers import RecordUUIDProvider
from .errors import EpicPIDError
from .b2share_epic import createHandle


def b2share_record_uuid_minter(record_uuid, data):
    """Use record's UUID as unique identifier."""
    provider = RecordUUIDProvider.create(
        object_type='rec', object_uuid=record_uuid,
        pid_value=data['_deposit']['id']
    )
    if '_pid' not in data:
        data['_pid'] = []
    data['_pid'].append({
        'value': provider.pid.pid_value,
        'type': provider.pid.pid_type,
    })

    b2share_oaiid_minter(record_uuid, data)
    b2share_pid_minter(record_uuid, data)
    b2share_doi_minter(record_uuid, data)

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


def b2share_pid_minter(record_uuid, data):
    """Mint EPIC PID for published record."""
    epic_pids = [p for p in data['_pid'] if p.get('type') == 'ePIC_PID']
    assert len(epic_pids) == 0

    url = make_record_url(record_uuid)
    throw_on_failure = current_app.config.get('CFG_FAIL_ON_MISSING_PID', True)

    try:
        pid = createHandle(url)
        if pid is None:
            raise EpicPIDError("EPIC PID allocation failed")
        data['_pid'].append({
            'value': pid,
            'type': 'ePIC_PID',
        })
    except EpicPIDError as e:
        if throw_on_failure:
            raise e
        else:
            current_app.logger.warning(e)


def b2share_doi_minter(record_uuid, data):
    from invenio_pidstore.models import PIDStatus, PersistentIdentifier
    from invenio_pidstore.providers.datacite import DataCiteProvider
    from .serializers import datacite_v31

    def filter_out_reserved_dois(data):
        ret = [d for d in data['_pid'] if d.get('type') != 'DOI_RESERVED']
        data['_pid'] = ret

    doi_list = [d for d in data['_pid'] if d.get('type') == 'DOI']
    if len(doi_list) > 0:
        return

    doi = generate_doi(record_uuid)
    url = make_record_url(record_uuid)

    filter_out_reserved_dois(data)
    data['_pid'].append({
        'value': doi,
        'type': 'DOI_RESERVED',
    })

    throw_on_failure = current_app.config.get('CFG_FAIL_ON_MISSING_DOI', True)
    try:
        dcp = DataCiteProvider.create(doi,
                                      object_type='rec',
                                      object_uuid=record_uuid,
                                      status=PIDStatus.RESERVED)
        doc = datacite_v31.serialize(dcp.pid, data)
        dcp.register(url=url, doc=doc)
        filter_out_reserved_dois(data)
        data['_pid'].append({
            'value': doi,
            'type': 'DOI',
        })
    except DataCiteError as e:
        if throw_on_failure:
            raise e
        else:
            current_app.logger.warning(e)



def make_record_url(recid):
    endpoint = 'b2share_records_rest.b2rec_item'
    url = url_for(endpoint, pid_value=recid, _external=True)
    url = url.replace('/api/records/', '/records/')
    return url


def generate_doi(recid):
    prefix = current_app.config['PIDSTORE_DATACITE_DOI_PREFIX']
    doi_format = current_app.config['DOI_IDENTIFIER_FORMAT']
    local_part = doi_format.format(recid=recid)
    return '{prefix}/{local_part}'.format(prefix=prefix, local_part=local_part)
