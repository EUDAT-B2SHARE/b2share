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

"""B2SHARE upgrade module.

This module makes it easy to upgrade a B2SHARE instance in a one line
command. It is required because:

* Invenio alpha modules are unstable and the alembic recipes can change after
  a release (beta modules are deemed stable). Thus it is sometime not possible
  to just ask alembic to upgrade.
* A B2SHARE upgrade can require more than database changes.
* If an upgrade fail (ex: because of a DB connection) it should just require
  to run the same command again in order to fix and finish the upgrade.
* Each upgrade should be logged in the Database so that information is
  available in case of a repeated failed upgrade.

Command-line interface
^^^^^^^^^^^^^^^^^^^^^^

The upgrade module provides a Command Line Interface which enables
administrators to migrate an existing B2Share deployment from one version
of B2Share to another.
The alembic database migration tool is incorporated to provide this
functionality. Alembic works with recipes which define database schema changes
needed to go from one version to another. Each B2Share and Invenio module
containing models, provides recipes which create a branch of changes.
The branches depend either on invenio-db, which is the root, or other modules
as in the case of b2share communities and schemas, where the dependency is the
following:

- x  : revision
- \\. : down-revision relation
- \\..: depends-on relation

.. code-block:: python

               b2share_communities
                ____x--x--x--x..   b2share_schemas
  invenio-db ../                \\_____x--x--x--x
  x--x--x--x ..      invenio-*
               \\____x--x--x--x

More information on alembic can be found at http://alembic.zzzcomputing.com/
and http://flask-alembic.readthedocs.io/en/latest/.

In order to upgrade a B2Share deployment call the command:

.. code-block:: console

  $ b2share upgrade run

**Warning**: Alembic Command Line Interface should not be used directly except
when advised by EUDAT support.

B2Share v2.0.1 Specifics
^^^^^^^^^^^^^^^^^^^^^^^^

As B2Share v2.0.1 and earlier didn't include alembic recipes the transition to
v2.1.0 is special.
It bridges this gap by:

1. Creating the alembic_version table in the db

The following alembic recipes correspond to the B2Share v2.0.1 state.

+-----------------+---------------------------+
| **version_num** | **corresponding module**  |
|=================|===========================|
| 1ba76da94103    | invenio-records-files     |
+-----------------+---------------------------+
| 12a88921ada2    | invenio-oauth2server      |
+-----------------+---------------------------+
| 97bbc733896c    | invenio-oauthclient       |
+-----------------+---------------------------+
| 2f63be7b7572    | invenio-access            |
+-----------------+---------------------------+
| e655021de0de    | invenio-oaiserver         |
+-----------------+---------------------------+
| 999c62899c20    | invenio-pidstore          |
+-----------------+---------------------------+
| 35d7d8958395    | b2share-schemas           |
+-----------------+---------------------------+

Note that alembic does not list the following versions because they are
already included as dependencies of the ones above. See the documentation on
the alembic_version table for more information.

+-----------------+---------------------------+
| **version_num** | **corresponding module**  |
|=================|===========================|
| dbdbc1b19cf2    | invenio-db                |
+-----------------+---------------------------+
| 2e97565eba72    | invenio-files-rest        |
+-----------------+---------------------------+
| 862037093962    | invenio-records           |
+-----------------+---------------------------+
| 9848d0149abd    | invenio-accounts          |
+-----------------+---------------------------+
| fb99eeaec4ac    | b2share-communities       |
+-----------------+---------------------------+

Schemas and communities don't have alembic recipes in v2.0.1 but as the models
did not change we can safely add them in the alembic_version table.

2. Renaming constraints to account so that they match the new alembic
   naming conventions.

3. Using alembic to upgrade the new recipes.

4. Destroying and reindexing elasticsearch indices


Database model
^^^^^^^^^^^^^^

All previously ran migrations are saved, including failed migration, except
for failed 2.0.0->2.0.1 migrations because the upgrade database model did
not exist yet.
"""

from __future__ import absolute_import, print_function

from .ext import B2ShareUpgrade


__all__ = ('B2ShareUpgrade')
