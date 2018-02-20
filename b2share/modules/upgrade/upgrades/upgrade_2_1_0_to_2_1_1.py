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
from .common import elasticsearch_index_destroy, elasticsearch_index_init, \
    elasticsearch_index_reindex, queues_declare, fix_communities


migrate_2_1_0_to_2_1_1 = UpgradeRecipe('2.1.0', '2.1.1')

# We updated the elasticsearch mappings
for step in [elasticsearch_index_destroy,
             elasticsearch_index_init,
             elasticsearch_index_reindex,
             queues_declare]:
    migrate_2_1_0_to_2_1_1.step()(step)

# There are no changes to the db schema, so no other updates are necessary
