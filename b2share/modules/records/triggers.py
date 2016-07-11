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

"""B2share records triggers."""

from __future__ import absolute_import, print_function

import pytz

from invenio_records.signals import before_record_update

from invenio_search import current_search_client
from invenio_rest.errors import FieldError

from .errors import AlteredRecordError


def register_triggers(app):
    # TODO(edima): replace this check with explicit permissions
    before_record_update.connect(check_record_immutable_fields)


# def on_create_record(record):
#     record_with_pid = assign_pid_and_commit(record)
#     index_record(record_with_pid)


# def assign_pid_and_commit(record):
#     from .handle import register_pid
#     from invenio_db import db
#     from sqlalchemy.orm.attributes import flag_modified

#     with db.session.begin_nested():
#         record['PID'] = register_pid(record, record.model.id)
#         record.validate()

#         record.model.json = dict(record)
#         flag_modified(record.model, 'json')
#         db.session.merge(record.model)

#     return record


def index_record(record):
    """Index the given record."""
    metadata = record.dumps()
    metadata['_created'] = pytz.utc.localize(record.created).isoformat()
    metadata['_updated'] = pytz.utc.localize(record.updated).isoformat()
    current_search_client.index(
        index='records',
        doc_type='record',
        id=record.id,
        body=metadata,
        version=record.revision_id,
        version_type='external_gte',
    )


# TODO(edima): replace this check with explicit permissions
def check_record_immutable_fields(record):
    """Checks that the previous community and owner fields are preserved"""
    previous_md = record.model.json
    if previous_md.get('owner') != record.get('owner'):
        raise AlteredRecordError(errors=[
            FieldError('owner', 'The owner field cannot be changed.')
        ])
    if previous_md.get('community') != record.get('community'):
        raise AlteredRecordError(errors=[
            FieldError('community', 'The community field cannot be changed.')
        ])
    if previous_md.get('PID') != record.get('PID'):
        raise AlteredRecordError(errors=[
            FieldError('PID', 'The PID field cannot be changed.')
        ])
