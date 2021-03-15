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

"""B2Share Schema models."""

import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy_utils.models import Timestamp
from sqlalchemy_utils.models import Timestamp
from sqlalchemy_utils.types import UUIDType

from invenio_db import db


class RootSchemaVersion(db.Model):
    """Represent a version of the B2Share root metadata schema in the database.
    """

    __tablename__ = 'b2share_root_schema_version'

    version = db.Column(db.Integer, primary_key=True, autoincrement=False)
    """Schema identifier."""

    json_schema = db.Column(db.Text, nullable=False)
    """JSON Schema."""


class BlockSchema(db.Model, Timestamp):
    """Represent one of the community's metadata block schema in the database.

    Every schema is versioned. Previous versions can always be accessible.
    These versions are represented as BlockSchemaVersion.

    Additionally it contains two columns ``created`` and ``updated``
    with automatically managed timestamps.
    """

    from b2share.modules.communities.models import Community

    __tablename__ = 'b2share_block_schema'

    id = db.Column(
        UUIDType,
        default=uuid.uuid4,
        primary_key=True,
    )
    """Schema identifier."""

    name = db.Column(db.String(200),
                     sa.CheckConstraint('LENGTH(name) > 2 AND '
                                        'LENGTH(name) <= 200',
                                        name='name_length'),
                     nullable=False,

                     )
    """Name of the schema."""

    deprecated = db.Column(db.Boolean, default=False, nullable=False)
    """True if the schema is not maintained anymore."""

    community = db.Column(
        UUIDType,
        db.ForeignKey(Community.id,
                      name='fk_b2share_block_schema_community'),
        nullable=False
    )
    """Community owning and maintaining this schema."""


class BlockSchemaVersion(db.Model):
    """Represent one version of a "Block Schema" in the database.

    Every version of a schema MUST be backward compatible with all its previous
    versions, i.e. no previously existing field can have its type changed.
    Fields can be added or removed and the required fields can change.
    This enables to search and analyze records in a consistent way.
    """

    __tablename__ = 'b2share_block_schema_version'

    block_schema = db.Column(
        UUIDType, db.ForeignKey(
            BlockSchema.id,
            name='fk_b2share_block_schema_version_block_schema'
        ),
        primary_key=True
    )
    """ID of the parent block schema."""

    version = db.Column(db.Integer, primary_key=True, autoincrement=False)
    """Version number of this schema."""

    released = sa.Column(sa.DateTime, default=datetime.utcnow, nullable=False)
    """Schema release date."""

    json_schema = db.Column(db.Text, nullable=True)
    """JSON Schema."""


class CommunitySchemaVersion(db.Model):
    """Represent a version of a community's schema in the database.

    Each Community has only one schema, which can have multiple versions. All
    released community schemas are immutable.

    The last released Community schema is used to validate all the new records
    submitted to this Community.
    """

    from b2share.modules.communities.models import Community

    __tablename__ = 'b2share_community_schema_version'

    community = db.Column(
        UUIDType,
        db.ForeignKey(
            Community.id,
            name='fk_b2share_community_schema_version_community'
        ),
        primary_key=True
    )
    """Community accepting this schema."""

    version = db.Column(db.Integer, primary_key=True, default=None,
                        nullable=False, autoincrement=False)
    "Schema version."

    released = sa.Column(sa.DateTime, default=datetime.utcnow, nullable=False)
    """Schema release date."""

    root_schema = db.Column(
        db.Integer,
        db.ForeignKey(
            RootSchemaVersion.version,
            name='fk_b2share_community_schema_version_root_schema'
        ),
        nullable=False
    )
    """Root schema used by this community."""

    community_schema = db.Column(db.String, nullable=False, default="{}")
