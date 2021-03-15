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

"""B2Share utility functions."""

from sqlalchemy import UniqueConstraint, PrimaryKeyConstraint
from invenio_db import db
import uuid


def add_to_db(instance, skip_if_exists=False, **fields):
    """Add a row to the database, optionally skip if it already exist.

    :param instance: the row to add to the database.
    :param skip_if_exists: if true, check if the row exists before
        inserting it.
    :param fields: override fields during comparison. Some fields might be null
        if the session is not flushed yet.
    """
    if not skip_if_exists:
        db.session.add(instance)
        return instance
    # Add only if the row does not already exist
    clazz = instance.__class__
    table = instance.__table__
    cols = None
    # Try retrieving the row using the first unique constraint
    unique_constraints = [
        cst for cst in table.constraints if cst.__class__ == UniqueConstraint
    ]
    if unique_constraints:
        cols = unique_constraints[0].columns
    else:
        # Otherwise use the first primary key constraint
        primary_constraints = [
            cst for cst in table.constraints
            if cst.__class__ == PrimaryKeyConstraint
        ]
        cols = primary_constraints[0].columns
    # Retrieve the row
    existing = db.session.query(clazz).filter(
        *[getattr(clazz, col.name)==(fields.get(col.name) or
                                     getattr(instance, col.name))
        for col in cols]
    ).one_or_none()

    if existing is not None:
        return existing

    # Add the row if it does not already exist
    db.session.add(instance)
    return instance

def is_valid_uuid(val):
    """Validate uuid"""
    
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False
