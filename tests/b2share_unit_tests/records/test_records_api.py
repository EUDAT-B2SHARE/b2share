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
