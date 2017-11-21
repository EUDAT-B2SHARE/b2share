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
from sqlalchemy.dialects import postgresql
from sqlalchemy_utils.models import Timestamp
from sqlalchemy_utils.types import JSONType, UUIDType


class Migration(db.Model, Timestamp):
    """Represent a community metadata inside the SQL database.
    Additionally it contains two columns ``created`` and ``updated``
    with automatically managed timestamps.
    """

    __tablename__ = 'b2share_migrations'

    id = db.Column(
        UUIDType,
        primary_key=True,
        default=uuid.uuid4,
    )

    # migration version
    version = db.Column(
        db.String(80), nullable=False)

    data = db.Column(
        JSONType().with_variant(
            postgresql.JSON(none_as_null=True),
            'postgresql',
        ),
        nullable=True
    )

    @property
    def success(self):
        """Returns the success or failure of the last migration."""
        return 'status' in self.data and self.data['status'] == 'success'


__all__ = (
    'Migration',
)
