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
