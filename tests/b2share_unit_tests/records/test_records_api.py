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

"""Test Record's programmatic API."""


import uuid

import pytest
from jsonschema.exceptions import ValidationError
from b2share.modules.records.errors import AlteredRecordError
from invenio_records import Record
from b2share.modules.deposit.api import Deposit


def test_change_record_schema_fails(app, test_records):
    """Test updating the $schema field fails."""
    with app.app_context():
        record = Record.get_record(test_records[0].record_id)
        del record['$schema']
        with pytest.raises(AlteredRecordError):
            record.commit()


def test_change_record_community(app, test_records):
    """Test updating the community field fails."""
    with app.app_context():
        record = Record.get_record(test_records[0].record_id)
        del record['community']
        with pytest.raises(AlteredRecordError):
            record.commit()

    with app.app_context():
        record = Record.get_record(test_records[0].record_id)
        record['community'] = str(uuid.uuid4())
        with pytest.raises(AlteredRecordError):
            record.commit()


def test_record_add_unknown_fields(app, test_records):
    """Test adding unknown fields in a record. It should fail."""
    for path in [
        # all the following paths point to "object" fields in
        # in the root JSON Schema
        '/new_field',
        '/community_specific/new_field',
        '/creators/0/new_field',
        '/titles/0/new_field',
        '/contributors/0/new_field',
        '/resource_types/0/new_field',
        '/alternate_identifiers/0/new_field',
        '/descriptions/0/new_field',
        '/license/new_field',
    ]:
        with app.app_context():
            record = Record.get_record(test_records[0].record_id)
            record = record.patch([
                {'op': 'add', 'path': path, 'value': 'any value'}
            ])
            with pytest.raises(ValidationError):
                record.commit()


def test_record_commit_with_incomplete_metadata(app,
                                                test_incomplete_records_data):
    """Test commit of an incomplete record fails."""
    for data in test_incomplete_records_data:
        with app.app_context():
            deposit = Deposit.create(data.complete_data)
            deposit.submit()
            deposit.publish()
            deposit.commit()
            pid, record = deposit.fetch_published()
            # make the data incomplete
            record = record.patch(data.patch)
            with pytest.raises(ValidationError):
                record.commit()
