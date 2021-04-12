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
from invenio_records.models import RecordMetadata
from b2share.modules.upgrade.api import UpgradeRecipe

from b2share.modules.upgrade.errors import MigrationFromUnknownVersionError

from b2share_unit_tests.upgrade.helpers import upgrade_run, repeat_upgrade, \
    validate_loaded_data, validate_database_schema, get_all_constraints

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

    with clean_app.app_context():
        repeat_upgrade(clean_app, ext.alembic)

    with clean_app.app_context():
        validate_database_schema(clean_app, ext.alembic)


def test_init_fail_and_retry(clean_app):
    """Test replay first database init after a failure."""
    with clean_app.app_context():
        ext = clean_app.extensions['invenio-db']
        if db.engine.name == 'sqlite':
            raise pytest.skip('upgrades are not supported on sqlite.')

        # create a conflicting table.
        db.engine.execute('CREATE table b2share_community (wrong int);')
        result = upgrade_run(clean_app)
        assert result.exit_code != 0

        # remove the problematic table
        db.engine.execute('DROP table b2share_community;')
        result = upgrade_run(clean_app)
        assert result.exit_code == 0

        # check that the migration information have been saved
        migrations = Migration.query.all()
        assert len(migrations) == 1
        mig = migrations[0]
        assert mig.version == current_migration_version
        assert mig.success

    with clean_app.app_context():
        repeat_upgrade(clean_app, ext.alembic)

    with clean_app.app_context():
        validate_database_schema(clean_app, ext.alembic)


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

        expected_migrations = UpgradeRecipe.build_upgrade_path(
            '2.0.0', current_migration_version)
        repeat_upgrade(clean_app, ext.alembic, len(expected_migrations))

        # check that the migration information have been saved
        migrations = Migration.query.order_by(Migration.created.asc()).all()
        assert len(migrations) == len(expected_migrations)
        assert migrations[-1].version == current_migration_version
        for mig in migrations:
            for step in mig.data['steps']:
                assert step['status'] == 'success'
            assert mig.data['error'] is None

    with clean_app.app_context():
        validate_loaded_data(clean_app, ext.alembic)
        # Check that it is possible to create a new record version after
        # the upgrade
        _create_new_record_version(clean_app)

        validate_database_schema(clean_app, ext.alembic)


def test_failed_and_repair_upgrade_from_v2_0_0(clean_app):
    """Test upgrade from an unknown B2SHARE version."""

    def failing_step(alembic, verbose):
        """Failing step used to make the upgrade fail."""
        raise Exception('This error is on purpose')

    with clean_app.app_context():
        expected_migrations = UpgradeRecipe.build_upgrade_path(
            '2.0.0', current_migration_version)
        ext = clean_app.extensions['invenio-db']
        if db.engine.name == 'sqlite':
            raise pytest.skip('upgrades are not supported on sqlite.')

        # bring db to v2.0.1 state
        db_create_v2_0_1()
        # Add a table which shouldn't exist in 2.0.1 version. This will
        # Make the 2.0.0->2.1.0 migration fail.

        Migration.__table__.create(db.engine)
        db.session.commit()
        result = upgrade_run(clean_app)
        assert result.exception.__class__ == sa.exc.ProgrammingError

        # Drop the problematic table
        Migration.__table__.drop(db.engine)

        # Fail every other migration one by one. Fixing the previous one at
        # each iteration.
        expected_number_of_migrations = 0
        first_loop = True
        for migration_idx  in range(len(expected_migrations)):
            migration = expected_migrations[migration_idx]
            # Add a failing step to the migration
            migration.step()(failing_step)
            # Run again a failing upgrade.
            result = upgrade_run(clean_app)
            assert result.exit_code == -1
            # This time the upgrade succeeded partially, the db schema is migrated
            # But not the records.
            migrations = Migration.query.order_by(
                Migration.updated.asc()).all()
            # The first failing migration is expected to save only one
            # "Migration" row in the database, every other migration should
            # have 2 migrations (the successful previous migration and the
            # next failing one).
            if first_loop:
                expected_number_of_migrations += 1
                first_loop = False
            else:
                expected_number_of_migrations += 2

            assert len(migrations) == expected_number_of_migrations
            number_of_migrations = len(migrations)
            last_migration = migrations[-1]
            assert last_migration.version == migration.dst_version
            assert not last_migration.success
            # Remove the failing migration step
            migration.remove_step(failing_step)
        # Migrate successfully
        result = upgrade_run(clean_app)
        assert result.exit_code == 0
        # Check that the resulting state is in sync with sqlalchemy's MetaData
        assert not ext.alembic.compare_metadata()

        # check that the migration information have been saved
        migrations = Migration.query.order_by(Migration.created.asc()).all()
        # Failed release + total succeeded releases
        expected_number_of_migrations += 1
        assert len(migrations) == expected_number_of_migrations
        # Check that every migration ran successfully
        assert [mig.version for mig in migrations if mig.success] == \
            [mig.dst_version for mig in expected_migrations]

    with clean_app.app_context():
        repeat_upgrade(clean_app, ext.alembic, expected_number_of_migrations)

    with clean_app.app_context():
        validate_loaded_data(clean_app, ext.alembic)
        # Check that it is possible to create a new record version after
        # the upgrade
        _create_new_record_version(clean_app)
        validate_database_schema(clean_app, ext.alembic)


def _create_new_record_version(app):
    """Create a new version of a record existing before the upgrade."""
    from invenio_accounts.models import User
    from flask_security import url_for_security
    from flask_security.utils import hash_password
    from flask import url_for
    from invenio_oauth2server.models import Token
    user = User.query.filter(User.email=='firstuser@example.com').one()
    user.password = hash_password('123')
    token = Token.create_personal(
        'other_token', user.id,
        scopes=[]
    )
    headers = [
        ('Authorization', 'Bearer {}'.format(token.access_token)),
        ('Content-type', 'application/json')
    ]
    db.session.commit()
    with app.test_request_context():
        login_url = url_for_security('login')
    with app.test_client() as client:
        res = client.post(login_url, data={
            'email': 'firstuser@example.com', 'password': '123'
        })
        assert res.status_code == 302
        url = url_for('b2share_records_rest.b2rec_list',
                      version_of='1033083fedf4408fb5611f23527a926d')
        res = client.post(url, headers=headers)
        assert res.status_code == 201
