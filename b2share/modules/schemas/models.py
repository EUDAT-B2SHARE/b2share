"""Community models."""

import uuid

from invenio_db import db
from sqlalchemy.sql import expression
from sqlalchemy_utils.models import Timestamp
from sqlalchemy_utils.types import JSONType, UUIDType


class Schema(db.Model, Timestamp):
    """Represent a schema inside the SQL database.
    Additionally it contains two columns ``created`` and ``updated``
    with automatically managed timestamps.
    """

    __tablename__ = 'b2share_schema'

    id = db.Column(UUIDType, primary_key=True, default=uuid.uuid4)
    """Schema identifier."""  # noqa

    json = db.Column(JSONType, default=lambda: dict(), nullable=True)
    """Store metadata in JSON format."""


__all__ = (
    'Schema',
)
