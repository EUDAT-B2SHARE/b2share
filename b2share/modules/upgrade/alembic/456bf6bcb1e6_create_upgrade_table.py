"""Create upgrade table.

Revision ID: 456bf6bcb1e6
Revises: 53b6e1711607
Create Date: 2017-05-04 11:51:49.599966

"""
from alembic import op
import sqlalchemy as sa
import uuid

from b2share.version import __version__
from sqlalchemy_utils.types import JSONType, UUIDType
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '456bf6bcb1e6'
down_revision = '53b6e1711607'
branch_labels = (u'b2share_upgrade',)
depends_on = None


def upgrade():
    op.create_table(
        'b2share_migrations',
        sa.Column('created', sa.DateTime(), nullable=False),
        sa.Column('updated', sa.DateTime(), nullable=False),
        sa.Column('id', UUIDType, default=uuid.uuid4, nullable=False),
        sa.Column('version', sa.String(80), default=__version__,
                  nullable=False),
        sa.Column('data', JSONType().with_variant(
                  postgresql.JSON(none_as_null=True),
                  'postgresql'),
                  default=lambda: dict(),
                  nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('b2share_migrations')
