"""Upgrade recipe migrating B2SHARE from version 2.4.1 to 2.4.2"""


from __future__ import absolute_import, print_function

import pkg_resources

from .common import elasticsearch_index_init

from ..api import UpgradeRecipe


migrate_2_4_1_to_2_4_2 = UpgradeRecipe('2.4.1', '2.4.2')

# There are no ES mapping updates

# There are no changes to the db schema, so no other updates are necessary
