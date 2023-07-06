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
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Function registering signal events"""

from invenio_records.signals import before_record_insert
from invenio_accounts.models import User
from flask import current_app
from sqlalchemy import func

@before_record_insert.connect
def add_ownership_automatically(sender, **kwargs):
    for email in current_app.config.get('DEFAULT_OWNERSHIP', []):
        user = User.query.filter(func.lower(User.email) == email.lower()).one_or_none()
        if user == None:
            current_app.logger.error(f"User not found: {email}")
            continue
        print(f"Adding ownership to a new record for user: {user.id}")
        if user.id not in sender['_deposit']['owners']:
            sender['_deposit']['owners'].append(user.id)
