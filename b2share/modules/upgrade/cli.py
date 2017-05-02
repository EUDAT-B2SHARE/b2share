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

"""B2Share cli commands for upgrades."""


from __future__ import absolute_import, print_function

import re

import click
from flask.cli import with_appcontext
from b2share.version import __version__
from flask import current_app
from invenio_db import db

from .models import Migration
from .api import UpgradeRecipe


@click.group()
def upgrade():
    """B2SHARE upgrade commands."""


@upgrade.command()
@with_appcontext
@click.option('-v', '--verbose', is_flag=True, default=False)
def run(verbose):
    """Upgrade the database and reindex the records."""
    alembic = current_app.extensions['invenio-db'].alembic
    # Remove ".dev" from the version to simplify the upgrade
    last_version = __version__.split('.dev')[0]

    last_failure = None
    # detect data current version. Special case for version 2.0.0 as there was
    # no alembic recipe at that time.
    if db.engine.dialect.has_table(db.engine, 'transaction'):
        if not db.engine.dialect.has_table(db.engine, 'alembic_version'):
            current_version = '2.0.0'
        else:
            all_migrations = Migration.query.order_by(
                Migration.updated.desc()).all()
            last_migration = all_migrations[-1]
            if last_migration.success:
                if last_migration.version == last_version:
                    click.secho('Already up to date.')
                    return

            last_success = next(mig for mig in all_migrations if mig.success)
            current_version = last_success.version
    else:
        current_version = 'init'

    upgrades = UpgradeRecipe.build_upgrade_path(current_version,
                                                last_version)
    for upgrade in upgrades:
        upgrade.run(failed_migration=last_failure, verbose=verbose)
