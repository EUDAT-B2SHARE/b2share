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

"""Upgrade recipe initializing B2SHARE from a clean database."""

from __future__ import absolute_import, print_function

import re

from invenio_db import db
from b2share.version import __version__

from ..models import Migration
from ..api import UpgradeRecipe, alembic_stamp, alembic_upgrade
from .common import elasticsearch_index_destroy, elasticsearch_index_init, \
    queues_declare, schemas_init



simple_init = UpgradeRecipe(
    'init',
    re.match(r'^\d+\.\d+\.\d+', __version__).group(0)
)

@simple_init.step()
def alembic_upgrade_heads(alembic, verbose):
    """Run all alembic upgrade recipes."""
    # Force our sqlalchemy session connection to use flask-alembic
    # connection so that they are in the same transaction
    # db.session.connection(bind=alembic.migration_context.bind)
    with db.session.begin_nested():
        db.metadata.create_all(db.session.connection())
        alembic_stamp('heads')
    db.session.commit()


for step in [elasticsearch_index_destroy, elasticsearch_index_init,
             queues_declare, schemas_init]:
    simple_init.step()(step)
