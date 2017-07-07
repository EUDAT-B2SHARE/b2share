"""Create schemas tables.

Revision ID: 35d7d8958395
Revises: 226892354af5
Create Date: 2017-04-25 18:03:15.919582

"""
from alembic import op
from datetime import datetime
import sqlalchemy as sa
import uuid

from sqlalchemy.types import TIMESTAMP
from sqlalchemy_utils.types import UUIDType
from sqlalchemy.engine.reflection import Inspector


# revision identifiers, used by Alembic.
revision = '35d7d8958395'
down_revision = '226892354af5'  # schemas-create-branch
branch_labels = ()
depends_on = None


def upgrade():
    """Upgrade Database."""
    op.create_table(
        'b2share_root_schema_version',
        sa.Column('version', sa.Integer, autoincrement=False),
        sa.Column('json_schema', sa.Text, nullable=False),
        sa.PrimaryKeyConstraint('version')
    )
    op.create_table(
        'b2share_block_schema',
        sa.Column('created', TIMESTAMP, nullable=False),
        sa.Column('updated', TIMESTAMP, nullable=False),
        sa.Column('id', UUIDType, default=uuid.uuid4),
        sa.Column('name', sa.String(200),
                  sa.CheckConstraint(
                      'LENGTH(name) > 2 AND LENGTH(name) <= 200',
                      name='name_length'),
                  nullable=False),
        sa.Column('deprecated', sa.Boolean, default=False, nullable=False),
        sa.Column('community', UUIDType, nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['community'], [u'b2share_community.id'],
                                name='fk_b2share_block_schema_community')
    )
    op.create_table(
        'b2share_block_schema_version',
        sa.Column('block_schema', UUIDType, nullable=False),
        sa.Column('version', sa.Integer, autoincrement=False),
        sa.Column('released', sa.DateTime, default=datetime.utcnow,
                  nullable=False),
        sa.Column('json_schema', sa.Text, nullable=True),
        sa.PrimaryKeyConstraint('block_schema', 'version'),
        sa.ForeignKeyConstraint(
            ['block_schema'], ['b2share_block_schema.id'],
            name='fk_b2share_block_schema_version_block_schema'
        )
    )
    op.create_table(
        'b2share_community_schema_version',
        sa.Column('community', UUIDType),
        sa.Column('version', sa.Integer, default=None, nullable=False,
                  autoincrement=False),
        sa.Column('released', sa.DateTime, default=datetime.utcnow,
                  nullable=False),
        sa.Column('root_schema', sa.Integer, nullable=False),
        sa.Column('community_schema', sa.String, default='{}', nullable=False),
        sa.PrimaryKeyConstraint('community', 'version'),
        sa.ForeignKeyConstraint(
            ['community'], [u'b2share_community.id'],
            name='fk_b2share_community_schema_version_community'
        ),
        sa.ForeignKeyConstraint(
            ['root_schema'], [u'b2share_root_schema_version.version'],
            name='fk_b2share_community_schema_version_root_schema'
        )
    )


def downgrade():
    """Downgrade database."""
    ctx = op.get_context()
    insp = Inspector.from_engine(ctx.connection.engine)

    for fk in insp.get_foreign_keys('b2share_block_schema'):
        if fk['referred_table'] == 'b2share_community':
            op.drop_constraint(
                op.f(fk['name']),
                'b2share_block_schema',
                type_='foreignkey'
            )

    op.drop_table('b2share_block_schema_version')

    for fk in insp.get_foreign_keys('b2share_community_schema_version'):
        if fk['referred_table'] == 'b2share_community':
            op.drop_constraint(
                op.f(fk['name']),
                'b2share_community_schema_version',
                type_='foreignkey'
            )

    op.drop_table('b2share_community_schema_version')
    op.drop_table('b2share_block_schema')
    op.drop_table('b2share_root_schema_version')
