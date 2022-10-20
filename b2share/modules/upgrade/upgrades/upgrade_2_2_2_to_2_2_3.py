"""Upgrade recipe migrating B2SHARE from version 2.2.2 to 2.2.3."""


from __future__ import absolute_import, print_function

import pkg_resources

from ..api import UpgradeRecipe


migrate_2_2_2_to_2_2_3 = UpgradeRecipe('2.2.2', '2.2.3')

# No changes to Elasticsearch mappings

# There are no changes to the db schema, so no other updates are necessary
