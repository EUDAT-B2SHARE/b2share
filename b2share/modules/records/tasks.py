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

"""Celery background tasks."""

from __future__ import absolute_import, print_function

from datetime import datetime, timezone
from urllib.parse import urlunsplit

from flask import current_app
from celery import shared_task
from invenio_db import db
from invenio_indexer.api import RecordIndexer
from invenio_records_files.api import Record
from invenio_search import current_search_client

from .search import B2ShareRecordsSearch


@shared_task(ignore_result=True)
def update_expired_embargoes():
    """Release expired embargoes every midnight."""
    logger = current_app.logger
    base_url = urlunsplit((
        current_app.config.get('PREFERRED_URL_SCHEME', 'http'),
        current_app.config['JSONSCHEMAS_HOST'],
        current_app.config.get('APPLICATION_ROOT') or '', '', ''
    ))
    # The task needs to run in a request context as JSON Schema validation
    # will use url_for.
    with current_app.test_request_context('/', base_url=base_url):
        s = B2ShareRecordsSearch(
            using=current_search_client,
            index='records'
        ).query(
            'query_string',
            query='open_access:false AND embargo_date:{{* TO {0}}}'.format(
                datetime.now(timezone.utc).isoformat()
            ),
            allow_leading_wildcard=False
        ).fields([])
        record_ids = [hit.meta.id for hit in s.scan()]
        if record_ids:
            logger.info('Changing access of {} embargoed publications'
                        ' to public.'.format(len(record_ids)))
        for record in Record.get_records(record_ids):
            logger.debug('Making embargoed publication {} public'.format(
                record.id))
            record['open_access'] = True
            record.commit()
        db.session.commit()

        indexer = RecordIndexer()
        indexer.bulk_index(record_ids)
        indexer.process_bulk_queue()
