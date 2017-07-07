"""Create schemas branch.

Revision ID: 226892354af5
Revises:
Create Date: 2017-04-25 18:03:12.388159

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '226892354af5'
down_revision = None
branch_labels = (u'b2share_schemas',)
depends_on = (
    'dbdbc1b19cf2',  # in invenio-db
    'fb99eeaec4ac',  # in b2share communities
)


def upgrade():
    pass


def downgrade():
    pass
