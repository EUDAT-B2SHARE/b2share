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

"""Record utils."""
from flask import abort

from invenio_records.models import RecordMetadata
from invenio_records_files.api import Record
from invenio_pidstore.resolver import Resolver
from invenio_indexer.api import RecordIndexer
from invenio_pidstore.models import PersistentIdentifier
from invenio_files_rest.models import Bucket
from elasticsearch.exceptions import NotFoundError

from invenio_pidstore.models import PIDStatus
from invenio_pidrelations.contrib.versioning import PIDVersioning
from invenio_pidstore.errors import PIDDoesNotExistError
    

def is_publication(record):
    """Check if a given record is a published record.

    Returns:
        bool: True if the record is a published record, else False.
    """
    return record.json['$schema'].endswith('#/json_schema')


def is_deposit(record):
    """Check if a given record is a deposit record.

    Returns:
        bool: True if the record is a deposit record, else False.
    """
    return record.json['$schema'].endswith('#/draft_json_schema')


def list_db_published_records():
    """A generator for all the published records"""
    query = RecordMetadata.query.filter(RecordMetadata.json is not None)
    for obj in query.all():
        record = Record(obj.json, model=obj)
        if record.model.json and is_publication(record.model):
            yield record


def get_parent_ownership(pid):
    """ Retrieve the Ownerships of a record given the record PID"""
    version_master = find_version_master(pid)
    record=Record.get_record(version_master.children.first().object_uuid)
    return record['_deposit']['owners']


def find_version_master(pid):
    """Retrieve the PIDVersioning of a record PID.

    :params pid: record PID.
    """
    from b2share.modules.deposit.errors import RecordNotFoundVersioningError
    from b2share.modules.records.providers import RecordUUIDProvider
    try:
        child_pid = RecordUUIDProvider.get(pid).pid
        if child_pid.status == PIDStatus.DELETED:
            raise RecordNotFoundVersioningError()
    except PIDDoesNotExistError as e:
        raise RecordNotFoundVersioningError() from e

    return PIDVersioning(child=child_pid)
