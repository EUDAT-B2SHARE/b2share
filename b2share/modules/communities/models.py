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

"""Community models."""

import uuid

from invenio_db import db
from sqlalchemy.sql import expression
from sqlalchemy_utils.models import Timestamp
from sqlalchemy_utils.types import UUIDType


class Community(db.Model, Timestamp):
    """Represent a community metadata inside the SQL database.
    Additionally it contains two columns ``created`` and ``updated``
    with automatically managed timestamps.
    """

    __tablename__ = 'b2share_community'

    id = db.Column(
        UUIDType,
        primary_key=True,
        default=uuid.uuid4,
    )
    """Community identifier."""  # noqa

    # community name
    name = db.Column(
        db.String(80), unique=True, nullable=False)

    # community description
    description = db.Column(
        db.String(2000), nullable=False)

    # link to the logo
    logo = db.Column(
        db.String(300), nullable=True)

    # Flag marking the community as deleted
    deleted = db.Column(db.Boolean, nullable=False,
                        server_default=expression.false())


__all__ = (
    'Community',
)
