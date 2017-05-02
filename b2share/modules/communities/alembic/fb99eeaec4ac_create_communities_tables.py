"""Create communities tables.

Revision ID: fb99eeaec4ac
Revises: ec77f5a034d1
Create Date: 2017-04-25 17:45:13.538252

"""
import uuid

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import expression
from sqlalchemy.types import TIMESTAMP
from sqlalchemy_utils.types import UUIDType


# revision identifiers, used by Alembic.
revision = 'fb99eeaec4ac'
down_revision = 'ec77f5a034d1'  # communities-create-branch
branch_labels = ()
depends_on = None


def upgrade():
    op.create_table(
        'b2share_community',
        sa.Column('created', TIMESTAMP, nullable=False),
        sa.Column('updated', TIMESTAMP, nullable=False),
        sa.Column('id', UUIDType, default=uuid.uuid4, nullable=False),
        sa.Column('name', sa.String(80), unique=True, nullable=False),
        sa.Column('description', sa.String(2000), nullable=False),
        sa.Column('logo', sa.String(300), nullable=True),
        sa.Column('deleted', sa.Boolean, nullable=False,
                  server_default=expression.false()),
        sa.Column('publication_workflow', sa.String(80), nullable=False,
                  default='direct_publish'),
        sa.Column('restricted_submission', sa.Boolean, nullable=False,
                  server_default=expression.false(), default=False),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('b2share_community')
