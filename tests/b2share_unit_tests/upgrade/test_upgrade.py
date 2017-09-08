# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2017 CERN.
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

"""Test db alembic functionality."""

import click
import pytest
import re
import sqlalchemy as sa
from invenio_db import InvenioDB, db
from b2share.version import __version__
from sqlalchemy_utils.functions import create_database, drop_database
from b2share.modules.upgrade.cli import run
from b2share.modules.upgrade.models import Migration
from b2share_unit_tests.helpers import db_create_v2_0_1, \
    remove_alembic_version_table
from sqlalchemy.engine.reflection import Inspector
from subprocess import call

from b2share.modules.upgrade.errors import MigrationFromUnknownVersionError

from b2share_unit_tests.upgrade.helpers import upgrade_run, repeat_upgrade, \
    validate_metadata, get_all_constraints

current_migration_version = re.match(r'^\d+\.\d+\.\d+', __version__).group(0)

def test_alembic(clean_app):
    """Test alembic recipes upgrade and downgrade."""
    with clean_app.app_context():
        ext = clean_app.extensions['invenio-db']
        if db.engine.name == 'sqlite':
            raise pytest.skip('Upgrades are not supported on SQLite.')
        db.drop_all()
        remove_alembic_version_table()

        ext.alembic.upgrade()

        # downgrade to root revision which is in invenio-db
        ext.alembic.downgrade(target='96e796392533')

        insp = Inspector.from_engine(db.engine)
        remaining_table = insp.get_table_names()
        assert remaining_table == ['alembic_version']
        remove_alembic_version_table()
        insp = Inspector.from_engine(db.engine)
        assert not insp.get_table_names()


def test_alembic_and_db_create_match(clean_app):
    """Check that alembic recipes and alembic models are in sync."""
    with clean_app.app_context():
        ext = clean_app.extensions['invenio-db']
        if db.engine.name == 'sqlite':
            raise pytest.skip('Upgrades are not supported on SQLite.')

        # Make sure that alembic upgrades can be run now
        ext.alembic.upgrade()
        constraints = get_all_constraints(clean_app)
        alembic_constraint_names = [x[0] for x in constraints]

        # Recreate the database with alembic only (without migrating)
        db.session.remove()
        drop_database(db.engine.url)
        db.engine.dispose()
        create_database(db.engine.url)
        db.create_all()

        # Check that the resulting state is in sync with alembic metaData
        assert not ext.alembic.compare_metadata()

        # Check that the constraints are the same. This is needed because
        # alembic.compare_metadata does not check all constraints.
        constraints = get_all_constraints(clean_app)
        db_create_constraint_names = [x[0] for x in constraints]
        assert set(alembic_constraint_names) == set(db_create_constraint_names)


def test_upgrade_from_unknown_version(app):
    """Test upgrade from an unknown B2SHARE version."""
    with app.app_context():
        ext = app.extensions['invenio-db']
        if db.engine.name == 'sqlite':
            raise pytest.skip('upgrades are not supported on sqlite.')

        migration = Migration(
            version = 'unknown.version',
            data = dict(steps=[], error=None, status='success')
        )
        db.session.add(migration)
        db.session.commit()

        # Upgrade B2SHARE with `b2share upgrade run`
        result = upgrade_run(app)
        assert result.exit_code == MigrationFromUnknownVersionError.exit_code

        # check that the migration information have been saved
        migrations = Migration.query.all();
        assert len(migrations) == 1


# TODO: add a test checking that the Migration error is correctly saved if
# it fails.

# TODO: add a test checking that the records are correctly reindexed


def test_init_upgrade(clean_app):
    """Test database upgrade from a clean state."""
    with clean_app.app_context():
        ext = clean_app.extensions['invenio-db']
        if db.engine.name == 'sqlite':
            raise pytest.skip('upgrades are not supported on sqlite.')

        result = upgrade_run(clean_app)
        assert result.exit_code == 0

        # check that the migration information have been saved
        migrations = Migration.query.all();
        assert len(migrations) == 1
        mig = migrations[0]
        assert mig.version == current_migration_version
        assert mig.success

        repeat_upgrade(clean_app, ext.alembic)

        validate_metadata(clean_app, ext.alembic)


def test_init_fail_and_retry(clean_app):
    """Test replay first database init after a failure."""
    with clean_app.app_context():
        ext = clean_app.extensions['invenio-db']
        if db.engine.name == 'sqlite':
            raise pytest.skip('upgrades are not supported on sqlite.')

        # create a conflicting table.
        db.engine.execute('CREATE table b2share_community (wrong int);')
        result = upgrade_run(clean_app)
        assert result.exit_code == -1

        # remove the problematic table
        db.engine.execute('DROP table b2share_community;')
        result = upgrade_run(clean_app)
        assert result.exit_code == 0

        # check that the migration information have been saved
        migrations = Migration.query.all();
        assert len(migrations) == 1
        mig = migrations[0]
        assert mig.version == current_migration_version
        assert mig.success

        repeat_upgrade(clean_app, ext.alembic)

        validate_metadata(clean_app, ext.alembic)


def test_upgrade_from_v2_0_0(clean_app):
    """Test upgrading B2Share from version 2.0.0."""
    with clean_app.app_context():
        ext = clean_app.extensions['invenio-db']
        if db.engine.name == 'sqlite':
            raise pytest.skip('upgrades are not supported on sqlite.')
        # bring db to v2.0.1 state
        db_create_v2_0_1()

        # Upgrade B2SHARE with `b2share upgrade run`
        result = upgrade_run(clean_app)
        assert result.exit_code == 0

        repeat_upgrade(clean_app, ext.alembic)

        # check that the migration information have been saved
        migrations = Migration.query.all();
        assert len(migrations) == 1
        mig = migrations[0]
        assert mig.version == current_migration_version
        for step in mig.data['steps']:
            assert step['status'] == 'success'
        assert mig.data['error'] is None

        validate_metadata(clean_app, ext.alembic)


def test_failed_and_repair_upgrade_from_v2_0_0(clean_app):
    """Test upgrade from an unknown B2SHARE version."""
    with clean_app.app_context():
        ext = clean_app.extensions['invenio-db']
        if db.engine.name == 'sqlite':
            raise pytest.skip('upgrades are not supported on sqlite.')

        # bring db to v2.0.1 state
        db_create_v2_0_1()
        Migration.__table__.create(db.engine)
        db.session.commit()
        result = upgrade_run(clean_app)
        assert result.exception.__class__ == sa.exc.ProgrammingError

        Migration.__table__.drop(db.engine)

        result = upgrade_run(clean_app)
        assert result.exit_code == 0
        # Check that the resulting state is in sync with sqlalchemy's MetaData
        assert not ext.alembic.compare_metadata()

        # check that the migration information have been saved
        migrations = Migration.query.all();
        assert len(migrations) == 1
        mig = migrations[0]
        assert mig.version == current_migration_version
        assert mig.success

        repeat_upgrade(clean_app, ext.alembic)

        validate_metadata(clean_app, ext.alembic)
