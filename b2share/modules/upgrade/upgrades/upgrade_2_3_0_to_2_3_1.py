"""Upgrade recipe migrating B2SHARE from version 2.3.0 to 2.3.1."""


from __future__ import absolute_import, print_function

import pkg_resources

from .common import elasticsearch_index_init

from ..api import UpgradeRecipe


migrate_2_3_0_to_2_3_1 = UpgradeRecipe('2.3.0', '2.3.1')

# There are no ES mapping updates

# There are no changes to the db schema, so no other updates are necessary
