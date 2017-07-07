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

from click.testing import CliRunner
from flask.cli import ScriptInfo
from invenio_db import db
from sqlalchemy_utils.functions import create_database, drop_database

from b2share.modules.upgrade.models import Migration
from b2share.modules.upgrade.cli import run


def upgrade_run(app):
    """Run the "b2share upgrade" command."""
    # Upgrade B2SHARE with `b2share upgrade run`
    runner = CliRunner()
    script_info = ScriptInfo(create_app=lambda info: app)
    return runner.invoke(run, ['-v'], obj=script_info)


def repeat_upgrade(app, alembic):
    """Repeat the upgrade just to make sure that everything is done well."""
    # Make sure that alembic upgrades can be run now
    alembic.upgrade()

    # Try rerunning the upgrade
    result = upgrade_run(app)
    assert result.exit_code == 0
    # no migration should have been performed
    migrations = Migration.query.all();
    assert len(migrations) == 1
    assert result.output == 'Already up to date.\n'


def validate_metadata(app, alembic):
    """Check that the database is as expected after a full migration."""
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
