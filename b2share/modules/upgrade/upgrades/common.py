# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2017 CERN.
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

"""B2Share common upgrade recipes."""

from __future__ import absolute_import, print_function

from invenio_search import current_search
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_indexer.api import RecordIndexer
from invenio_indexer.tasks import process_bulk_queue


def elasticsearch_index_destroy(alembic, verbose):
    """Destroy the elasticsearch indices."""
    current_search.delete(ignore=[400, 404])


def elasticsearch_index_init(alembic, verbose):
    """Initialize the elasticsearch indices."""
    current_search.create(ignore=[400])


def elasticsearch_index_reindex(alembic, verbose):
    """Reindex records."""
    query = (x[0] for x in PersistentIdentifier.query.filter_by(
            object_type='rec', status=PIDStatus.REGISTERED
        ).filter(
            PersistentIdentifier.pid_type.in_(['b2rec', 'b2dep'])
        ).values(
            PersistentIdentifier.object_uuid
        ))
    RecordIndexer().bulk_index(query)
    process_bulk_queue.delay()
