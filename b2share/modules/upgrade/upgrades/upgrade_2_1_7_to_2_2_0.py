# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2018 CERN.
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

"""Upgrade recipe migrating B2SHARE from version 2.1.0 to 2.1.1."""


from __future__ import absolute_import, print_function

import pkg_resources

from ..api import UpgradeRecipe
from .common import schemas_init, elasticsearch_index_destroy, elasticsearch_index_init, \
    elasticsearch_index_reindex, queues_declare, fix_communities
from b2share.modules.schemas.cli import update_or_set_community_root_schema
from b2share.modules.communities.api import Community
from b2share.modules.communities.models import create_roles_and_permissions, \
    create_community_oaiset, Community

migrate_2_1_7_to_2_2_0 = UpgradeRecipe('2.1.7', '2.2.0')

def upgrade_community_root_schemas(alembic, verbose):
    for community in Community.query.all():
        update_or_set_community_root_schema(community.id, 1)

for step in [schemas_init,
             upgrade_community_root_schemas,
             elasticsearch_index_destroy,
             elasticsearch_index_init,
             elasticsearch_index_reindex,
             queues_declare]:
    migrate_2_1_7_to_2_2_0.step()(step)