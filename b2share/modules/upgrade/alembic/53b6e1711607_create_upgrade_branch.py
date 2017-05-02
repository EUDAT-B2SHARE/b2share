"""Create upgrade branch.

Revision ID: 53b6e1711607
Revises:
Create Date: 2017-05-04 11:51:11.157763

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '53b6e1711607'
down_revision = None
branch_labels = ()
depends_on = (
    '35c1075e6360',  # invenio-db force_naming_convention
)


def upgrade():
    pass


def downgrade():
    pass
