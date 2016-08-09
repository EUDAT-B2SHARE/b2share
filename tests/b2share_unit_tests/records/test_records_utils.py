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

"""Test B2Share record module utils."""

from b2share_unit_tests.helpers import create_deposit
from b2share.modules.records.utils import is_publication, is_deposit


def test_records_type_helpers(app, test_records_data, create_user):
    """Test record util functions retrieving the record type."""
    with app.app_context():
        creator = create_user('creator')
        deposit = create_deposit(test_records_data[0], creator)
        deposit.submit()
        deposit.publish()
        _, record = deposit.fetch_published()
        assert is_deposit(deposit)
        assert not is_deposit(record)
        assert is_publication(record)
        assert not is_publication(deposit)
