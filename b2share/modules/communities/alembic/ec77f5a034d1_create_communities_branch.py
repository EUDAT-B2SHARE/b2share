"""Create communities branch.

Revision ID: ec77f5a034d1
Revises:
Create Date: 2017-04-25 17:45:07.928254

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ec77f5a034d1'
down_revision = None
branch_labels = (u'b2share_communities',)
depends_on = 'dbdbc1b19cf2'  # in invenio-db


def upgrade():
    pass


def downgrade():
    pass
