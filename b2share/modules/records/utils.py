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
from b2share.modules.deposit.fetchers import b2share_deposit_uuid_fetcher
from invenio_pidstore.resolver import Resolver
from invenio_indexer.api import RecordIndexer
from invenio_pidstore.models import PersistentIdentifier
from invenio_files_rest.models import Bucket
from elasticsearch.exceptions import NotFoundError
from b2share.modules.deposit.api import Deposit


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
        if is_publication(record.model):
            yield record


def delete_record(pid, record):
    """Delete a published record."""
    # Fetch deposit id from record and resolve deposit record and pid.
    depid = b2share_deposit_uuid_fetcher(None, record)
    if not depid:
        abort(404)

    depid, deposit = Resolver(
        pid_type=depid.pid_type,
        object_type='rec',
        # Retrieve the deposit with the Record class on purpose as the current
        # Deposit api prevents the deletion of published deposits.
        getter=Record.get_record,
    ).resolve(depid.pid_value)

    # Note: the record is unindexed from Elasticsearch via the
    # signal handlers in triggers.py
    try:
        RecordIndexer().delete(deposit)
    except NotFoundError:
        pass

    # Mark connected buckets as DELETED
    record_bucket = record.files.bucket
    deposit_bucket = deposit.files.bucket
    Bucket.delete(deposit_bucket.id)
    Bucket.delete(record_bucket.id)

    # mark all PIDs as DELETED
    all_pids = PersistentIdentifier.query.filter(
        PersistentIdentifier.object_type == pid.object_type,
        PersistentIdentifier.object_uuid == pid.object_uuid,
    ).all()
    for rec_pid in all_pids:
        if not rec_pid.is_deleted():
            rec_pid.delete()
    depid.delete()

    # Mark the record and deposit as deleted
    record.delete()
    deposit.delete()
