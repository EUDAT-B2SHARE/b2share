"""Upgrade recipe migrating B2SHARE from version 2.2.4 to 2.2.5."""


from __future__ import absolute_import, print_function

import pkg_resources

from .common import elasticsearch_index_init

from ..api import UpgradeRecipe


migrate_2_2_4_to_2_2_5 = UpgradeRecipe('2.2.4', '2.2.5')

# Update Elasticsearch mappings
for step in [elasticsearch_index_init]:
    migrate_2_2_4_to_2_2_5.step()(step)

# There are no changes to the db schema, so no other updates are necessary
