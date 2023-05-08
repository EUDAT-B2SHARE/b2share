# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2023 CSC, EUDAT ltd.
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

"""Test B2Share Ownership receivers module."""

from b2share_unit_tests.helpers import create_user, create_deposit

from b2share.modules.management.ownership.receivers import add_ownership_automatically

def test_record_ownership_added(app, test_records_data):
    with app.app_context():
        curator = create_user('curator')
        app.config['DEFAULT_OWNERSHIP'] = ['curator@example.org']
        r1 = test_records_data[0]
        rec = create_deposit(r1)
        assert len(rec['_deposit']['owners']) == 1
        assert rec['_deposit']['owners'][0] == curator.id

def test_record_ownership_faulty_emails(app, test_records_data):
    with app.app_context():
        app.config['DEFAULT_OWNERSHIP'] = ['curator@organization.org']
        r1 = test_records_data[0]
        rec = create_deposit(r1)
        assert len(rec['_deposit']['owners']) == 0
