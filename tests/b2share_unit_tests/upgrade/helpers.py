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
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Upgrade test Helpers."""

import json
import os

import pytest
from click.testing import CliRunner
from flask.cli import ScriptInfo
from invenio_db import db
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy_utils.functions import create_database, drop_database

from b2share.modules.upgrade.models import Migration
from b2share.modules.upgrade.cli import run
from invenio_accounts.models import User
from invenio_records_files.api import Record
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_pidrelations.contrib.versioning import PIDVersioning
from b2share.modules.records.fetchers import b2share_parent_pid_fetcher, \
    b2share_record_uuid_fetcher
from b2share.modules.records.providers import RecordUUIDProvider
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_accounts.models import Role
from invenio_access.models import ActionRoles


def upgrade_run(app):
    """Run the "b2share upgrade" command."""
    # unset SERVER_NAME as we want to check that it is not needed.
    server_name = app.config['SERVER_NAME']
    app.config.update(dict(SERVER_NAME=None))
    # Upgrade B2SHARE with `b2share upgrade run`
    runner = CliRunner()
    script_info = ScriptInfo(create_app=lambda info: app)
    result = runner.invoke(run, ['-v'], obj=script_info)
    ## Uncomment this in order to test without Click. ##
    # from b2share.modules.upgrade.api import upgrade_to_last_version
    # with app.app_context():
    #     upgrade_to_last_version(False)

    # Set the SERVER_NAME to its previous value
    app.config.update(dict(SERVER_NAME=server_name))
    return result


def repeat_upgrade(app, alembic, expected_migrations=1):
    """Repeat the upgrade just to make sure that everything is done well."""
    # Make sure that alembic upgrades can be run now
    alembic.upgrade()

    # Try rerunning the upgrade
    result = upgrade_run(app)
    assert result.exit_code == 0
    # no migration should have been performed
    migrations = Migration.query.all();
    assert len(migrations) == expected_migrations
    assert result.output == 'Already up to date.\n'


def _load_json(filename):
    """Load a local JSON file."""
    path = os.path.join(os.path.dirname(__file__), filename)
    with open(path) as data_file:
        return json.load(data_file)


def check_records_migration(app):
    """Check that a set of records have been migrated."""
    expected_records = _load_json('expected_records.json')
    for exp_record in expected_records:
        db_record = Record.get_record(exp_record['id'], with_deleted=True)
        assert str(db_record.created) == exp_record['created']
        # If the record is deleted there is no metadata to check
        if db_record.model.json is None:
            continue
        # Check that the parent pid is minted properly
        parent_pid = b2share_parent_pid_fetcher(exp_record['id'],
                                                db_record)
        fetched_pid = b2share_record_uuid_fetcher(exp_record['id'], db_record)
        record_pid = PersistentIdentifier.get(fetched_pid.pid_type,
                                              fetched_pid.pid_value)
        assert PIDVersioning(record_pid).parent.pid_value == parent_pid.pid_value
        # Remove the parent pid as it has been added by the migration
        db_record['_pid'].remove({
            'type': RecordUUIDProvider.parent_pid_type,
            'value': parent_pid.pid_value,
        })
        # The OAI-PMH identifier has been modified by the migration
        if db_record.get('_oai'):
            oai_prefix = app.config.get('OAISERVER_ID_PREFIX', 'oai:')
            record_id = exp_record['metadata']['_deposit']['id']
            assert db_record['_oai']['id'] == str(oai_prefix) + record_id
            exp_record['metadata']['_oai']['id'] = db_record['_oai']['id']
        assert db_record == exp_record['metadata']


def check_pids_migration():
    """Check that the persistent identifiers have been migrated."""
    expected_pids = _load_json('expected_pids.json')
    # Check unchanging properties
    for exp_pid in expected_pids:
        db_pid = PersistentIdentifier.get(exp_pid['pid_type'],
                                          exp_pid['pid_value'])
        for key, value in exp_pid.items():
            if key != 'updated':
                assert str(getattr(db_pid, key)) == str(value)

        # check that deleted PID's records are (soft or hard) deleted
        if exp_pid['status'] == PIDStatus.DELETED.value:
            metadata = None
            try:
                record = Record.get_record(exp_pid['pid_value'],
                                           with_deleted=True)
                # Soft deleted record
                metadata = record.model.json
            except NoResultFound:
                # Hard deleted record
                pass
            assert metadata is None

        # Check versioning relations and PIDs
        if exp_pid['pid_type'] == 'b2dep':
            try:
                rec_pid = PersistentIdentifier.get('b2rec',
                                                    exp_pid['pid_value'])
                # if the deposit is deleted, either the record PID was reserved
                # and has been deleted, or it still exists.
                if db_pid.status == PIDStatus.DELETED:
                    assert rec_pid.status != PIDStatus.RESERVED
            except PIDDoesNotExistError:
                # The record PID was only reserved and has been deleted
                # with the deposit PID.
                assert db_pid.status == PIDStatus.DELETED
                continue

            # Check that a parent pid has been created
            versioning = PIDVersioning(child=rec_pid)
            parent = versioning.parent
            assert rec_pid.status in [PIDStatus.RESERVED, PIDStatus.REGISTERED]
            if rec_pid.status == PIDStatus.RESERVED:
                assert parent.status == PIDStatus.RESERVED
            else:
                assert parent.status == PIDStatus.REDIRECTED
                assert parent.get_redirect() == rec_pid


def check_communities():
    """Check that the missing community permissions have been fixed.

    See the commented rows of Role and ActionRole in b2share_db_load_data.sql.
    These are recreated by the upgrade.
    """
    role = Role.query.filter(
        Role.name == 'com:99916f6f9a2c4feba3426552ac7f1529:member'
    ).one_or_none()
    assert role is not None
    action = ActionRoles.query.filter(
        ActionRoles.argument == '{"community":"99916f6f-9a2c-4feb-a342-6552ac7f1529","publication_state":"draft"}',
        ActionRoles.action == 'create-deposit',
        ActionRoles.role_id == role.id
    ).one_or_none()
    assert action is not None


def validate_loaded_data(app, alembic):
    """Checks that the loaded data is still there and valid."""
    with app.app_context():
        # Check the demo user
        users = User.query.all()
        assert len(users) == 1
        assert users[0].email == 'firstuser@example.com'

        check_records_migration(app)
        check_pids_migration()
        check_communities()


def validate_database_schema(app, alembic):
    """Check that the database schema is as expected after a full migration."""
    # Check that the resulting state is in sync with sqlalchemy's MetaData
    assert not alembic.compare_metadata()

    # list all existing constraints
    current_constraints = get_all_constraints(app)
    current_constraint_names = [x[1] for x in current_constraints]

    # Recreate the database with alembic only (without migrating)
    db.session.remove()
    drop_database(db.engine.url)
    db.engine.dispose()
    create_database(db.engine.url)

    alembic.upgrade()

    # Check that the constraints are the same. This is needed because
    # alembic.compare_metadata does not check all constraints.
    expected_constraints = get_all_constraints(app)
    expected_constraint_names = [x[1] for x in expected_constraints]
    assert set(current_constraint_names) == set(expected_constraint_names)


def get_all_constraints(app):
    """List all constraints existing in the database."""
    pks = get_constraints_of_type(app, 'p')  # PRIMARY KEY
    fks = get_constraints_of_type(app, 'f')  # FOREIGN KEY
    uqs = get_constraints_of_type(app, 'u')  # UNIQUE
    cks = get_constraints_of_type(app, 'c')  # CHECK
    all_constraints = pks + fks + uqs + cks
    sorted_constraints = sorted(all_constraints,
                                key=lambda element: (element[1], element[2]))
    return sorted_constraints


def get_constraints_of_type(app, constraint_type):
    """Get all constraint names of a type."""
    with app.app_context():
        result = []
        for table in db.metadata.sorted_tables:
            query = 'select conrelid::regclass AS table_from, conname, ' \
                'pg_get_constraintdef(c.oid), contype from pg_constraint ' \
                'c join pg_namespace n ON n.oid = c.connamespace where ' \
                'conrelid::regclass = \'{0}\'::regclass and contype = ' \
                '\'{1}\' order by conname'.format(table.name, constraint_type)
            query_result = db.engine.execute(query)
            constraints = query_result.fetchall()
            if constraints:
                result += constraints
    return result
