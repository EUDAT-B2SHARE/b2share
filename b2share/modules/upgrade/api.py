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

"""B2Share upgrade api."""

import re
import traceback
import warnings
import click

from collections import namedtuple
from queue import Queue
from urllib.parse import urlunsplit
from functools import wraps
from flask import current_app

from invenio_db import db

from sqlalchemy.orm.attributes import flag_modified
from b2share.version import __version__

from .errors import MigrationFromUnknownVersionError
from .models import Migration


def with_request_context(f):
    """Runs the decorated function in a request context."""
    @wraps(f)
    def decorator(*args, **kwargs):
        base_url = urlunsplit((
            current_app.config.get('PREFERRED_URL_SCHEME', 'http'),
            current_app.config['JSONSCHEMAS_HOST'],
            current_app.config.get('APPLICATION_ROOT') or '', '', ''
        ))
        with current_app.test_request_context('/', base_url=base_url):
            f(*args, **kwargs)
    return decorator


def upgrade_to_last_version(verbose):
    """Upgrade the database to the last version and reindex the records."""
    alembic = current_app.extensions['invenio-db'].alembic
    # Remove ".dev*", "rc*", ... from the version to simplify the upgrade
    last_version = re.match(r'^\d+\.\d+\.\d+', __version__).group(0)

    last_failure = None
    # detect data current version. Special case for version 2.0.0 as there was
    # no alembic recipe at that time.
    if db.engine.dialect.has_table(db.engine, 'transaction'):
        if not db.engine.dialect.has_table(db.engine, 'alembic_version'):
            current_version = '2.0.0'
        else:
            all_migrations = Migration.query.order_by(
                Migration.updated.desc()).all()
            
            last_migration = all_migrations[0]
            if last_migration.success:
                if last_migration.version == last_version:
                    click.secho('Already up to date.')
                    return
            else:
                last_failure = last_migration
            try:
                last_success = next(mig for mig in all_migrations
                                    if mig.success)
                current_version = last_success.version
            except StopIteration:
                current_version = '2.0.0'
    else:
        current_version = 'init'

    upgrades = UpgradeRecipe.build_upgrade_path(current_version,
                                                last_version)
    for upgrade in upgrades:
        upgrade.run(failed_migration=last_failure, verbose=verbose)


Step = namedtuple('Step', ['condition', 'run'])


def default_step_condition_factory(target_version, step_name):
    """Create a default condition used by upgrade steps.

    The created condition checks if the step was already successfully ran
    and skip it if it is the case.
    """
    def default_step_condition(alembic, failed_migration, *args):
        if failed_migration and failed_migration.version == target_version:
            try:
                step = next(step for step in failed_migration.data['steps']
                            if step['name'] == step_name)
                # skip the step if it already ran successfully
                if step['status'] in {'success', 'skip'}:
                    return False
            except StopIteration:
                # The step was not run at all.
                pass
        return True
    return default_step_condition


class UpgradeRecipe(object):
    """A B2SHARE upgrade which migrates from one B2SHARE version to another.

    An upgrade is composed of Steps which are run sequentially.
    Every Step is a function which is replayable if it fails but cannot be
    rollbacked once it succeeds.
    A failed upgrade can be rerun.
    """
    # dict of all upgrades. src_version -> dst_version -> upgrade
    upgrades = dict()

    loaded = False
    """Flag signaling if the upgrade recipes have been loaded yet."""

    def __init__(self, src_version, dst_version):
        """Constructor

        Args:
            src_version: origin version required to run this upgrade.
            dst_version: new B2SHARE version once this upgrade has ran.
        """
        self.src_version = src_version
        self.dst_version = dst_version
        # upgrade step. Each step is a unit which is replayable if it failed.
        self.steps = []
        self._step_names = set()

        # register the new upgrade
        src_upgrades = self.upgrades.setdefault(src_version, dict())
        assert dst_version not in src_upgrades
        src_upgrades[dst_version] = self

    def step(self, condition=None):
        """Function decorator registering a step of the upgrade.

        Args:
            condition: a callable which, if it returns False, makes upgrade.run
            skip the step.
        """
        def decorator(step_func):
            # docstring is mandatory
            assert step_func.__doc__ is not None
            # check for duplicate step names
            assert step_func.__name__ not in self._step_names
            final_condition = condition
            # Use the default condition if none is provided
            if condition is None:
                final_condition = default_step_condition_factory(
                    self.dst_version, step_func.__name__
                )
            self.steps.append(
                Step(condition=final_condition, run=step_func)
            )
            self._step_names.add(step_func.__name__)
            return step_func
        return decorator

    def remove_step(self, step_func):
        """Remove a step from the list of upgrade steps."""
        self.steps = filter(lambda step: step.run != step_func, self.steps)
        self._step_names.remove(step_func.__name__)


    @classmethod
    def load(cls):
        """Load all upgrade recipes."""
        import pkgutil
        import b2share.modules.upgrade.upgrades as upgrades
        for importer, modname, ispkg in pkgutil.walk_packages(
                path=upgrades.__path__,
                prefix=upgrades.__name__+'.',
                onerror=lambda x: None):
            __import__(modname)
        cls.loaded = True


    @with_request_context
    def run(self, failed_migration=None, verbose=None):
        """Run the upgrade."""
        if not self.loaded:
            self.load()
        alembic = current_app.extensions['invenio-db'].alembic
        migration = Migration(
            version = self.dst_version,
            data = dict(steps=[], error=None, status='start')
        )
        # save the migration state
        if db.engine.dialect.has_table(db.engine, 'b2share_migrations'):
            db.session.add(migration)
            db.session.commit()
        for step in self.steps:
            step_log = dict(
                name=step.run.__name__,
                status='start'
            )
            migration.data['steps'].append(step_log)
            try:
                alembic.migration_context.bind.close()
                if step.condition is None or step.condition(alembic,
                                                            failed_migration):
                    if verbose:
                        click.secho(step.run.__doc__, fg='green')
                    step.run(alembic, verbose)
                    step_log['status'] = 'success'
                else:
                    step_log['status'] = 'skip'
            except BaseException as e:
                db.session.rollback()
                migration.data['steps'].append(dict(
                    name=step.run.__name__,
                    status='error'
                ))
                migration.data['error'] = traceback.format_exc()
                migration.data['status'] = 'error'
                if not db.engine.dialect.has_table(db.engine,
                                                   'b2share_migrations'):
                    click.secho(
                        'Failed to upgrade while running upgrade {0} -> {1}. '
                        'Step {2}.\nTraceback:\n{3}'.format(
                            self.src_version, self.dst_version,
                            step.run.__name__, traceback.format_exc())
                    )
                raise e
            finally:
                # save the migration state
                if db.engine.dialect.has_table(db.engine,
                                               'b2share_migrations'):
                    flag_modified(migration, 'data')
                    db.session.add(migration)
                    db.session.commit()
        # mark the migration as successful and save it
        migration.data['status'] = 'success'
        db.session.add(migration)
        flag_modified(migration, 'data')
        db.session.commit()

    @classmethod
    def build_upgrade_path(cls, src_version, dst_version):
        """Build the upgrade path from src_version to dst_version.

        The idea is that we might have migrations with different possible
        paths.

        Example:
            v1.0.0 -> v1.0.1 -> v1.0.2
                |       |         |
                ----> v1.1.0 <-----

        Thus we have to find the shortest path from the current version
        to the one we target.

        Returns:
            the list of upgrade to run to migrate from version src_version
            to dst_version.
        """
        if not cls.loaded:
            cls.load()
        if src_version == dst_version:
            return []
        # stop the migration if the current version is unknown.
        if src_version not in cls.upgrades:
            raise MigrationFromUnknownVersionError(src_version, dst_version)
        Branch = namedtuple('branch', ['version', 'upgrades'])
        queue = Queue()
        branch = Branch(src_version, [])
        queue.put(branch)
        while not queue.empty():
            branch = queue.get()
            for new_version in cls.upgrades[branch.version]:
                upgrades = branch.upgrades + \
                    [cls.upgrades[branch.version][new_version]]
                if new_version == dst_version:
                    return upgrades
                queue.put(Branch(new_version, upgrades))


def alembic_upgrade(target='heads'):
    """Upgrade the database using alembic.

    We use this instead of flask-alembic because this is currently the only
    way to use the same connection as our flask-sqlalchemy session. This
    enables us to run everything in the same transaction.

    This code is inspired from flask-alembic code.
    """
    alembic = current_app.extensions['invenio-db'].alembic
    env = alembic.environment_context

    def do_upgrade(revision, context):
        return alembic.script_directory._upgrade_revs(target, revision)
    env.configure(
        connection=db.session.connection(), target_metadata=db.metadata,
        fn=do_upgrade, **current_app.config['ALEMBIC_CONTEXT']
    )
    with warnings.catch_warnings():
        # Ignore the warning comming from invenio-db naming convention recipe
        warnings.filterwarnings("ignore",
                                message='Update \\w* CHECK \\w* manually')
        env.run_migrations()


def alembic_stamp(target='heads'):
    """Stamp the database using alembic.

    We use this instead of flask-alembic because this is currently the only
    way to use the same connection as our flask-sqlalchemy session. This
    enables us to run everything in the same transaction.

    This code is inspired from flask-alembic code.
    """
    alembic = current_app.extensions['invenio-db'].alembic
    env = alembic.environment_context

    def do_stamp(revision, context):
        return alembic.script_directory._stamp_revs(target, revision)
    env.configure(
        connection=db.session.connection(), target_metadata=db.metadata,
        fn=do_stamp, **current_app.config['ALEMBIC_CONTEXT']
    )
    env.run_migrations()
