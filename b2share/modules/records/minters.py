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
from invenio_pidstore.models import PIDStatus

from datacite.errors import DataCiteError

from .providers import RecordUUIDProvider


def b2share_record_uuid_minter(record_uuid, data):
    """Use record's UUID as unique identifier."""
    # register the existing record PID
    rec_pid = RecordUUIDProvider.get(data['_deposit']['id']).pid
    rec_pid.assign('rec', record_uuid)
    rec_pid.register()

    if '_pid' not in data:
        data['_pid'] = []
    data['_pid'].append({
        'value': rec_pid.pid_value,
        'type': rec_pid.pid_type,
    })

    b2share_oaiid_minter(rec_pid, data)
    b2share_pid_minter(rec_pid, data)
    if current_app.config.get('TESTING', False) or current_app.config.get('FAKE_DOI', False):
        b2share_doi_minter(rec_pid, data, fake_it=True)
    elif current_app.config.get('AUTOMATICALLY_ASSIGN_DOI'):
        b2share_doi_minter(rec_pid, data)

    return rec_pid


def b2share_oaiid_minter(rec_pid, data):
    """Mint record identifiers."""
    oai_pid_value = data.get('_oai', {}).get('id')
    if oai_pid_value is None:
        oai_prefix = current_app.config.get('OAISERVER_ID_PREFIX', 'oai:')
        oai_pid_value = str(oai_prefix) + str(rec_pid.pid_value)
    provider = OAIIDProvider.create(
        object_type='rec',
        object_uuid=rec_pid.object_uuid,
        pid_value=oai_pid_value
    )
    data.setdefault('_oai', {})
    data['_oai'].update({
        'id': oai_pid_value,
        'sets': [data.get('community')], # community_id == setSpec
        'updated': datetime_to_datestamp(datetime.utcnow()),
    })
    return provider.pid


def b2share_pid_minter(rec_pid, data):
    """Mint EPIC PID for published record."""

    from b2share.modules.handle.errors import EpicPIDError
    from b2share.modules.handle.proxies import current_handle

    epic_pids = [p for p in data['_pid'] if p.get('type') == 'ePIC_PID']
    assert len(epic_pids) == 0

    url = make_record_url(rec_pid.pid_value)
    throw_on_failure = current_app.config.get('CFG_FAIL_ON_MISSING_PID', True)

    try:
        pid = current_handle.create_handle(url)
        if pid is None:
            raise EpicPIDError("EPIC PID allocation failed")
        data['_pid'].append({'value': pid, 'type': 'ePIC_PID'})
    except EpicPIDError as e:
        if throw_on_failure:
            raise e
        else:
            current_app.logger.warning(e)


def b2share_doi_minter(rec_pid, data, fake_it=False):
    from invenio_pidstore.models import PIDStatus, PersistentIdentifier
    from invenio_pidstore.providers.datacite import DataCiteProvider
    from .serializers import datacite_v31

    def select_doi(metadata, status):
        doi_list = [DataCiteProvider.get(d.get('value'))
                    for d in metadata['_pid']
                    if d.get('type') == 'DOI']
        return [d for d in doi_list
                if d and d.pid and d.pid.status == status]

    if select_doi(data, PIDStatus.REGISTERED):
        return # DOI already allocated

    url = make_record_url(rec_pid.pid_value)

    reserved_doi = select_doi(data, PIDStatus.RESERVED)
    if reserved_doi:
        doi = reserved_doi[0]
    else:
        doi_id = generate_doi(rec_pid.pid_value)
        doi = DataCiteProvider.create(doi_id,
                                      object_type='rec',
                                      object_uuid=rec_pid.object_uuid,
                                      status=PIDStatus.RESERVED)
        data['_pid'].append({'value': doi_id, 'type': 'DOI'})

    throw_on_failure = current_app.config.get('CFG_FAIL_ON_MISSING_DOI', True)
    try:
        doc = datacite_v31.serialize(doi.pid, data)
        if fake_it: # don't actually register DOI, just pretend to do so
            doi.pid.register()
        else:
            doi.register(url=url, doc=doc)
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
