"""Upgrade recipe migrating B2SHARE from version 2.3.1 to 2.3.2."""


from __future__ import absolute_import, print_function

import pkg_resources

from .common import elasticsearch_index_init

from ..api import UpgradeRecipe


migrate_2_3_1_to_2_3_2 = UpgradeRecipe('2.3.1', '2.3.2')

# There are no ES mapping updates

# There are no changes to the db schema, so no other updates are necessary
