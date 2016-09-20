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

"""Test record indexing."""

import json

from flask import url_for
from click.testing import CliRunner
from invenio_search import current_search_client, current_search
from invenio_indexer import cli
from invenio_indexer.tasks import process_bulk_queue
from invenio_indexer.api import RecordIndexer


def test_record_indexing(app, test_users, test_records, script_info,
                         login_user):
    """Test record indexing."""

    creator = test_users['deposits_creator']

    with app.app_context():
        current_search_client.indices.flush('*')
        # delete all elasticsearch indices
        res = current_search_client.search(index="records",
                                           body={"query": {"match_all": {}}})

    with app.app_context():
        # delete all elasticsearch indices and recreate them
        for deleted in current_search.delete(ignore=[404]):
            pass
        for created in current_search.create(None):
            pass

        runner = CliRunner()
        # Initialize queue
        res = runner.invoke(cli.queue, ['init', 'purge'],
                            obj=script_info)
        assert 0 == res.exit_code
        # schedule a reindex task
        res = runner.invoke(cli.reindex, ['--yes-i-know'], obj=script_info)
        assert 0 == res.exit_code
        # execute scheduled tasks synchronously
        process_bulk_queue.delay()
        # flush the indices so that indexed records are searchable
        current_search_client.indices.flush('*')

        search_url = url_for('b2share_records_rest.b2share_record_list')
        search_deposits_url = url_for('b2share_records_rest.b2share_record_list',
                                      drafts=1)

    headers = [('Content-Type', 'application/json'),
               ('Accept', 'application/json')]


    with app.app_context():
        # delete all elasticsearch indices
        res = current_search_client.search(index="records",
                                           body={"query": {"match_all": {}}})
        pass

    # search for published records
    with app.test_client() as client:
        record_search_res = client.get(
            search_url,
            data='',
            headers=headers)
        assert record_search_res.status_code == 200
        record_search_data = json.loads(
            record_search_res.get_data(as_text=True))
        assert record_search_data['hits']['total'] == len(test_records)
        record_pids = [hit['id'] for hit
                       in record_search_data['hits']['hits']]
        expected_record_pids = [str(rec[1]) for rec in test_records]
        record_pids.sort()
        expected_record_pids.sort()
        assert record_pids == expected_record_pids

    # search for draft records
    with app.test_client() as client:
        login_user(creator, client)
        deposit_search_res = client.get(
            search_deposits_url,
            data='',
            headers=headers)
        assert deposit_search_res.status_code == 200
        deposit_search_data = json.loads(
            deposit_search_res.get_data(as_text=True))
        assert deposit_search_data['hits']['total'] == len(test_records)
        deposit_pids = [hit['id'] for hit
                       in deposit_search_data['hits']['hits']]
        expected_deposit_pids = [rec[0].hex for rec in test_records]
        deposit_pids.sort()
        expected_deposit_pids.sort()
        assert deposit_pids == expected_deposit_pids
