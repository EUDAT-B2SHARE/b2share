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

"""B2Share Records JSON schemas used for serialization."""

from flask import g, current_app
from invenio_rest.serializer import BaseSchema as Schema
from marshmallow import fields, pre_dump
from b2share.modules.access.policies import allow_public_file_metadata
from b2share.modules.files.permissions import files_permission_factory
from b2share.modules.records.utils import is_deposit
from b2share.modules.records.minters import generate_doi


DOI_URL_PREFIX = 'http://doi.org/'


class DraftSchemaJSONV1(Schema):
    """Schema for records v1 in JSON."""

    id = fields.String(attribute='pid.pid_value')
    metadata = fields.Raw()
    links = fields.Raw()
    created = fields.Str()
    updated = fields.Str()
    files = fields.Raw()

    @pre_dump
    def filter_internal(self, data, **kwargs):
        """Remove internal fields from the record metadata."""
        external_pids = []
        bucket = None
        record = None

        # differentiating between search results and
        # single record requests
        if hasattr(g, 'record'):
            record = g.record
            if record.files:
                bucket = record.files.bucket
            if is_deposit(record.model):
                from b2share.modules.deposit.api import generate_external_pids
                external_pids = generate_external_pids(record)
            # if it is a published record don't generate external pids
            # as they are immutable and stored in _deposit
            else:
                external_pids = record.model.json[
                    '_deposit'].get('external_pids')
            user_has_permission = \
                allow_public_file_metadata(data['metadata']) if bucket \
                is None else files_permission_factory(
                    bucket, 'bucket-read').can()
        elif hasattr(g, 'record_hit'):
            user_has_permission = allow_public_file_metadata(
                g.record_hit['_source'])

        if '_deposit' in data['metadata']:
            if hasattr(g, 'record') and is_deposit(record.model):# and current_app.config['AUTOMATICALLY_ASSIGN_DOI']:
                # add future DOI string
                data['b2share'] = {'future_doi': generate_doi(data['metadata']['_deposit']['id']) }

            data['metadata']['owners'] = data['metadata']['_deposit']['owners']

            # Add the external_pids only if the
            # user is allowed to read the bucket
            if external_pids and bucket and user_has_permission:
                data['metadata']['external_pids'] = external_pids
            del data['metadata']['_deposit']
        if '_files' in data['metadata']:
            # Also add the files field only if the user is allowed
            if user_has_permission:
                data['files'] = data['metadata']['_files']
                if external_pids and bucket:
                    external_dict = {x['key']: x['ePIC_PID']
                                     for x in external_pids}
                    for _file in data['files']:
                        if _file['key'] in external_dict:
                            _file['b2safe'] = True
                            _file['ePIC_PID'] = external_dict[_file['key']]
            del data['metadata']['_files']
        if '_pid' in data['metadata']:
            # move PIDs to metadata top level
            epic_pids = [p for p in data['metadata']['_pid']
                         if p.get('type') == 'ePIC_PID']
            dois = [p for p in data['metadata']['_pid']
                    if p.get('type') == 'DOI']
            if len(epic_pids) > 0:
                data['metadata']['ePIC_PID'] = epic_pids[0].get('value')
            if len(dois) > 0:
                data['metadata']['DOI'] = DOI_URL_PREFIX + dois[0].get('value')

            # add parent version pid
            # data['metadata']['parent_id'] = next(
            #     pid['value'] for pid in data['metadata']['_pid']
            #     if pid['type'] == RecordUUIDProvider.parent_pid_type
            # )
            del data['metadata']['_pid']
        if '_oai' in data['metadata']:
            del data['metadata']['_oai']
        if '_internal' in data['metadata']:
            del data['metadata']['_internal']
        if '_bucket' in data['metadata']:
            del data['metadata']['_bucket']
        return data


class RecordSchemaJSONV1(DraftSchemaJSONV1):
    """Schema for record v1 in JSON."""
