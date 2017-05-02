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

"""Upgrade recipemigrating B2SHARE from version 2.0.0 to 2.0.2."""


from __future__ import absolute_import, print_function

import pkg_resources

from invenio_db import db

from ..api import UpgradeRecipe, alembic_stamp, alembic_upgrade
from .common import elasticsearch_index_destroy, elasticsearch_index_init, \
    elasticsearch_index_reindex


migrate_2_0_0_to_2_0_2 = UpgradeRecipe('2.0.0', '2.0.2')

@migrate_2_0_0_to_2_0_2.step(
    lambda alembic, *args:
    not db.engine.dialect.has_table(db.engine, 'alembic_version')
)
def alembic_upgrade_to_2_0_2(alembic, verbose):
    """Migrate the database from the v2.0.0 schema to the 2.0.2 schema."""
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
        # Upgrade alembic recipes for B2SHARE 2.0.2.
        for revision in [
            '456bf6bcb1e6',  # b2share-upgrade
            'e12419831262'  # invenio-accounts
        ]:
            alembic_upgrade(revision)
    db.session.commit()


for step in [elasticsearch_index_destroy, elasticsearch_index_init,
             elasticsearch_index_reindex]:
    migrate_2_0_0_to_2_0_2.step()(step)
