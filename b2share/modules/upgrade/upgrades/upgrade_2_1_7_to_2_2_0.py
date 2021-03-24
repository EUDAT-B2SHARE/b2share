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

"""Upgrade recipe migrating B2SHARE from version 2.1.7 to 2.2.0"""


from __future__ import absolute_import, print_function

import pkg_resources

from ..api import UpgradeRecipe
from .common import schemas_init, elasticsearch_index_init

migrate_2_1_7_to_2_2_0 = UpgradeRecipe('2.1.7', '2.2.0')

def delete_indices():
    """delete deposit and record indices"""
    from invenio_search.proxies import current_search_client
    current_search_client.indices.delete(index='deposits')
    current_search_client.indices.delete(index='records')

def reindex_records():
    """reindex records"""
    from invenio_indexer.api import RecordIndexer
    from invenio_records.models import RecordMetadata
    def records():
        """Record iterator."""
        for record in RecordMetadata.query.values(RecordMetadata.id):
            yield record[0]
    RecordIndexer().bulk_index(records())
    RecordIndexer().process_bulk_queue()


for step in [schemas_init, delete_indices, elasticsearch_index_init, reindex_records]:
    migrate_2_1_7_to_2_2_0.step()(step)