# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2017 CERN.
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

from elasticsearch.exceptions import NotFoundError

from invenio_indexer.tasks import delete_record, index_record
from invenio_records.signals import (
    after_record_insert, after_record_update, before_record_delete,
    before_record_update,
)
from invenio_indexer.api import RecordIndexer
from invenio_rest.errors import FieldError

from .errors import AlteredRecordError
from .indexer import is_publication


def register_triggers(app):
    # TODO(edima): replace this check with explicit permissions
    before_record_update.connect(check_record_immutable_fields)
    before_record_delete.connect(unindex_record_trigger)
    after_record_update.connect(index_record_trigger)
    after_record_insert.connect(index_record_trigger)


# TODO(edima): replace this check with explicit permissions
def check_record_immutable_fields(sender, *args, **kwargs):
    """Checks that the previous community and owner fields are preserved"""

    record = kwargs['record']

    previous_md = record.model.json
    for field in ['community', '$schema']:
        if previous_md.get(field) != record.get(field):
            raise AlteredRecordError(errors=[
                FieldError(field,
                           'The {} field cannot be changed.'.format(field))
            ])


def index_record_trigger(sender, *args, **kwargs):
    """Index the given record if it is a publication."""

    record = kwargs['record']
    
    if is_publication(record.model):
        # index the record synchronously as an asynchronous task will not
        # find the record if it runs before this transaction's commit.
        RecordIndexer().index(record)


def unindex_record_trigger(sender, *args, **kwargs):
    """Unindex the given record if it is a publication."""

    record = kwargs['record']

    if is_publication(record.model):
        # The indexer requires that the record still exists in the database
        # when it is removed from the search index. Thus we have to unindex it
        # synchonously.
        try:
            RecordIndexer().delete(record)
        except NotFoundError:
            pass
