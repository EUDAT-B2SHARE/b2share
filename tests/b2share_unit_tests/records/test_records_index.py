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
from invenio_records.api import Record
from b2share.modules.deposit.api import Deposit
from time import sleep

def test_record_indexing(app, test_users, test_records, script_info,
                           login_user):
    """Test record indexing and reindexing."""
    creator = test_users['deposits_creator']
    
    with app.app_context():
        # flush the indices so that indexed records are searchable
        current_search_client.indices.flush(index='_all', params= {'force':'true'})
        current_search_client.indices.refresh(index='_all')
        sleep(1)

    # records and deposits should be indexed
    subtest_record_search(app, creator, test_records, test_records, login_user)

    with app.app_context():
        current_search_client.indices.flush(index='_all', params= {'force':'true'})
        current_search_client.indices.refresh(index='_all')
        # delete all elasticsearch indices and recreate them
        for deleted in current_search.delete(ignore=[404]):
            pass
        for created in current_search.create(None):
            pass
        # flush the indices so that indexed records are searchable
        current_search_client.indices.flush(index='_all', params= {'force':'true'})
        current_search_client.indices.refresh(index='_all')
        sleep(1)
       
    # all records should have been deleted
    subtest_record_search(app, creator, [], [], login_user)

    with app.app_context():
        runner = CliRunner()
        # Initialize queue
        res = runner.invoke(cli.queue, ['init', 'purge'],
                            obj=script_info)
        assert 0 == res.exit_code
        # schedule a reindex task
        res = runner.invoke(cli.reindex, ['--yes-i-know', '-t', 'b2dep'], obj=script_info)
        assert 0 == res.exit_code
        res = runner.invoke(cli.reindex, ['--yes-i-know', '-t', 'b2rec'], obj=script_info)
        assert 0 == res.exit_code
        # execute scheduled tasks synchronously
        process_bulk_queue.delay()

        # flush the indices so that indexed records are searchable
        current_search_client.indices.flush(index='_all', params= {'force':'true'})
        current_search_client.indices.refresh(index='_all')
        sleep(1)

    # records and deposits should be indexed again
    subtest_record_search(app, creator, test_records, test_records, login_user)


def subtest_record_search(app, creator, test_records, test_deposits,
                          login_user):
    
    """Check that all expected published and deposit records are found."""
    with app.app_context():
        search_url = url_for('b2share_records_rest.b2rec_list')
        search_deposits_url = url_for('b2share_records_rest.b2rec_list',
                                      drafts=1)

    headers = [('Content-Type', 'application/json'),
               ('Accept', 'application/json')]

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
        expected_record_pids = [str(rec.pid) for rec in test_records]
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
        assert deposit_search_data['hits']['total'] == len(test_deposits)
        deposit_pids = [hit['id'] for hit
                       in deposit_search_data['hits']['hits']]
        expected_deposit_pids = [rec.deposit_id.hex for rec in test_deposits]
        deposit_pids.sort()
        expected_deposit_pids.sort()
        assert deposit_pids == expected_deposit_pids


def test_record_unindex(app, test_users, test_records, script_info,
                        login_user):
    """Check that deleting a record also removes it from the search index."""
    creator = test_users['deposits_creator']

    with app.app_context():
        Record.get_record(test_records[0].record_id).delete()
        # execute scheduled tasks synchronously
        process_bulk_queue.delay()
        # flush the indices so that indexed records are searchable
        current_search_client.indices.flush('*')
        sleep(1)

    # deleted record should not be searchable
    subtest_record_search(app, creator, test_records[1:], test_records,
                          login_user)


def test_unpublished_deposit_unindex(app, test_users, draft_deposits, script_info,
                        login_user):
    """Check that deleting an unpublished deposit also removes it from the search index."""
    creator = test_users['deposits_creator']

    with app.app_context():
        Deposit.get_record(draft_deposits[0].deposit_id).delete()
        # execute scheduled tasks synchronously
        process_bulk_queue.delay()
        # flush the indices so that indexed records are searchable
        current_search_client.indices.flush('*')
        sleep(1)

    # deleted record should not be searchable
    subtest_record_search(app, creator, [], draft_deposits[1:],
                          login_user)


def test_published_deposit_unindex(app, test_users, test_records, script_info,
                                   login_user):
    """Check that deleting a published deposit also removes it from the search index."""
    creator = test_users['deposits_creator']

    with app.app_context():
        Deposit.get_record(test_records[0].deposit_id).delete()
        # execute scheduled tasks synchronously
        process_bulk_queue.delay()
        # flush the indices so that indexed records are searchable
        current_search_client.indices.flush('*')
        sleep(1)
    # deleted record should not be searchable
    subtest_record_search(app, creator, test_records, test_records[1:],
                          login_user)


def test_record_index_after_update(app, test_users, test_records, script_info,
                                   login_user):
    """Check that updating a record also reindex it."""
    creator = test_users['deposits_creator']

    with app.app_context():
        rec = Record.get_record(test_records[0].record_id)
        pid = test_records[0].pid
        rec.update({'title': 'my modified title'})
        # execute scheduled tasks synchronously
        process_bulk_queue.delay()
        # flush the indices so that indexed records are searchable
        current_search_client.indices.flush('*')

        # HK: If i do not sleep a little, then ES is not flushed, and i do not get back
        # updated results inn next query. So there is an issue with 'flush' than needs
        # attention, for this test to pass, I just sleep 1 second...

        sleep(1)
        search_url = url_for('b2share_records_rest.b2rec_list')

    headers = [('Content-Type', 'application/json'),
               ('Accept', 'application/json')]

    with app.test_client() as client:
        record_search_res = client.get(
            search_url,
            data='',
            headers=headers)
        assert record_search_res.status_code == 200
        record_search_data = json.loads(
            record_search_res.get_data(as_text=True))
        assert record_search_data['hits']['total'] == len(test_records)
        found_rec = [rec for rec in record_search_data['hits']['hits']
                     if rec['id'] == pid][0]
        assert rec['title'] == 'my modified title'
