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

"""Upgrade recipemigrating B2SHARE from version 2.0.0 to 2.1.0."""


from __future__ import absolute_import, print_function

import pkg_resources
import click

from flask import current_app

from invenio_db import db
from invenio_pidrelations.contrib.versioning import PIDVersioning
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_pidstore.errors import PIDDoesNotExistError
from sqlalchemy.orm.exc import NoResultFound

from ..api import UpgradeRecipe, alembic_stamp, alembic_upgrade
from .common import elasticsearch_index_destroy, elasticsearch_index_init, \
    elasticsearch_index_reindex, queues_declare, schemas_init, fix_communities
from b2share.modules.records.providers import RecordUUIDProvider
from b2share.modules.deposit.providers import DepositUUIDProvider
from b2share.modules.deposit.api import Deposit
from invenio_records_files.api import Record
from b2share.modules.deposit.api import PublicationStates


migrate_2_0_0_to_2_1_0 = UpgradeRecipe('2.0.0', '2.1.0')

@migrate_2_0_0_to_2_1_0.step(
    lambda alembic, *args:
    not db.engine.dialect.has_table(db.engine, 'alembic_version')
)
def alembic_upgrade_database_schema(alembic, verbose):
    """Migrate the database from the v2.0.0 schema to the 2.1.0 schema."""
    # This also fixes the B2SHARE 2.0.0 database so that it matches alembic
    # recipes.


    # As B2SHARE 2.0.0 and 2.0.1 are based on Invenio 3 alpha and beta modules
    # when there was not yet any upgrade procedure we need to do some hacks:
    #     - Alembic was not yet used at that time, thus we need to create the
    #     alembic_version table as if we used it in the first place.
    #     - A new naming convention has been enforced and we need to fix the
    #     corresponding constraints and indices.

    # This whole recipe is ran in a transaction, thus it will rollback in
    # case of any error.

    # Make sure alembic version table exists in the db
    with db.session.begin_nested():
        # alembic_version state of B2Share v2.0.0 and v2.0.1
        heads_v2_0_0 = [
            '35c1075e6360',
            '999c62899c20',
            '1ba76da94103',
            '12a88921ada2',
            '97bbc733896c',
            '2f63be7b7572',
            'e655021de0de',
            'fb99eeaec4ac',
            '35d7d8958395',
        ]
        # Populate it as if alembic upgrade heads had ran
        for revision in heads_v2_0_0:
            alembic_stamp(revision)
        with pkg_resources.resource_stream(
                'b2share.modules.upgrade',
                'alembic_renaming_script.sql') as stream:
            script_str = stream.read().decode().strip()
            db.session.execute(script_str)
        # Upgrade alembic recipes for B2SHARE 2.1.0.
        for revision in [
            '456bf6bcb1e6',  # b2share-upgrade
            'e12419831262',  # invenio-accounts
            'f741aa746a7d',  # invenio-files-rest
            '1d4e361b7586',  # invenio-pidrelations
        ]:
            alembic_upgrade(revision)
    db.session.commit()


@migrate_2_0_0_to_2_1_0.step()
def alembic_upgrade_database_data(alembic, verbose):
    """Migrate the database data from v2.0.0 to 2.1.0."""
    ### Add versioning PIDs ###
    # Reserve the record PID and versioning PID for unpublished deposits

    # Hack: disable record indexing during record migration
    from invenio_indexer.api import RecordIndexer
    old_index_fn = RecordIndexer.index
    RecordIndexer.index = lambda s, record: None

    if verbose:
        click.secho('migrating deposits and records...')
    with db.session.begin_nested():
        # Migrate published records
        records_pids = PersistentIdentifier.query.filter(
            PersistentIdentifier.pid_type == RecordUUIDProvider.pid_type,
            PersistentIdentifier.status == PIDStatus.REGISTERED,
        ).all()
        for rec_pid in records_pids:
            if verbose:
                click.secho('    record {}'.format(rec_pid.pid_value))
            try:
                record = Record.get_record(rec_pid.object_uuid)
            except NoResultFound:
                # The record is deleted but not the PID. Fix it.
                rec_pid.status = PIDStatus.DELETED
                continue
            # Create parent version PID
            parent_pid = RecordUUIDProvider.create().pid
            version_master = PIDVersioning(parent=parent_pid)
            version_master.insert_draft_child(child=rec_pid)
            version_master.update_redirect()
            migrate_record_metadata(
                Record.get_record(rec_pid.object_uuid),
                parent_pid
            )

        # Migrate deposits
        deposit_pids = PersistentIdentifier.query.filter(
            PersistentIdentifier.pid_type == DepositUUIDProvider.pid_type,
            PersistentIdentifier.status == PIDStatus.REGISTERED,
        ).all()
        for dep_pid in deposit_pids:
            if verbose:
                click.secho('    deposit {}'.format(dep_pid.pid_value))
            try:
                deposit = Deposit.get_record(dep_pid.object_uuid)

                if deposit['publication_state'] != \
                        PublicationStates.published.name:
                    # The record is not published yet. Reserve the PID.
                    rec_pid = RecordUUIDProvider.create(
                        object_type='rec',
                        pid_value=dep_pid.pid_value,
                    ).pid
                    # Create parent version PID
                    parent_pid = RecordUUIDProvider.create().pid
                    assert parent_pid
                    version_master = PIDVersioning(parent=parent_pid)
                    version_master.insert_draft_child(child=rec_pid)
                else:
                    # Retrieve previously created version PID
                    rec_pid = RecordUUIDProvider.get(dep_pid.pid_value).pid
                    version_master = PIDVersioning(child=rec_pid)
                    parent_pid = version_master.parent
                    if not parent_pid:
                        click.secho('    record {} was deleted, but the deposit has not been removed'.format(rec_pid.pid_value), fg='red')

                if parent_pid:
                    migrate_record_metadata(
                        Deposit.get_record(dep_pid.object_uuid),
                        parent_pid
                    )
            except NoResultFound:
                # The deposit is deleted but not the PID. Fix it.
                dep_pid.status = PIDStatus.DELETED


    if verbose:
        click.secho('done migrating deposits.')
    RecordIndexer.index = old_index_fn


def migrate_record_metadata(record, parent_pid):
    """Migrate a record's metadata to 2.1.0 format."""
    # Fix bad OAI-PMH identifiers
    oai_prefix = current_app.config.get('OAISERVER_ID_PREFIX')
    if oai_prefix:
        oai_id = record.get('_oai', {}).get('id')
        if oai_id and not oai_id.startswith(oai_prefix):
            assert oai_id == record['_deposit']['id']
            record['_oai']['id'] = oai_prefix + oai_id

    # Mint the parent version Persistent Identifier. Every existing record
    # should be versioned.
    record['_pid'] = record.get('_pid', []) + [{
        'value': parent_pid.pid_value,
        'type': RecordUUIDProvider.parent_pid_type,
    }]
    record.commit()


migrate_2_0_0_to_2_1_0.step()(fix_communities)
