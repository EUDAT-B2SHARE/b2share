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

import amqp
from flask import current_app
from invenio_search import current_search
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_indexer.api import RecordIndexer
from invenio_indexer.tasks import process_bulk_queue
from invenio_queues.proxies import current_queues
from celery.messaging import establish_connection
from b2share.modules.schemas.helpers import load_root_schemas


def elasticsearch_index_destroy(alembic, verbose):
    """Destroy the elasticsearch indices and indexing queue."""
    for _ in current_search.delete(ignore=[400, 404]):
        pass
    queue = current_app.config['INDEXER_MQ_QUEUE']
    with establish_connection() as c:
        q = queue(c)
        try:
            q.delete()
        except amqp.exceptions.NotFound:
            pass


def elasticsearch_index_init(alembic, verbose):
    """Initialize the elasticsearch indices and indexing queue."""
    for _ in current_search.create(ignore=[400]):
        pass
    for _ in current_search.put_templates(ignore=[400]):
        pass
    queue = current_app.config['INDEXER_MQ_QUEUE']
    with establish_connection() as c:
        q = queue(c)
        q.declare()


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


def queues_declare(alembic, verbose):
    """Declare queues, except for the indexing queue."""
    current_queues.declare()


def schemas_init(alembic, verbose):
    """Load root schemas."""
    load_root_schemas(cli=True, verbose=verbose)
