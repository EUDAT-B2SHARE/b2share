# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2016 University of Tuebingen, CERN.
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

"""B2SHARE deposit module.

Invenio deposits are also known in B2SHARE as **draft records**. They are
the first stage of the record publication workflow. The name **deposit** comes
from the import Invenio-Deposit module it is based on.

Deposits are separate from published records. They have their own internal
Persistent Identifier with type ``b2dep``. Once a deposit is published its
metadata are duplicated in a published record, but the deposit continues to
exist.

Use cases
^^^^^^^^^

The need for a deposit comes from different use cases:

* Draft work: a researcher wants to work on a draft for some time, potentially
  logging out in-between, before publishiing his dataset.
* Filtering: some communities want to filter what is published in their
  communities. The deposit can be submitted by the author and then accepted
  by the community administrator.
* Curation: a curator can modify the deposit before it is published.
* Validation: many communities have the use case where they would like to
  perform some automatic validation on the dataset before they are published.
  The deposit is the right stage at which this validation should be done.

Not all these use cases are currently supported but they have been taken into
account during the design of draft records.

When a user calls ``POST /api/records`` a deposit is created. This deposit has
metadata and files which can both be modified. The deposit has a ``publication
state`` which can be either **draft**, **submitted** or **published**. The
publication state is registered within the deposit's metadata in the
``publication_state`` field.


Workflow
^^^^^^^^

Deposits have threee publication states, but not all of them are always used.
A community can define the workflow it wants for its records
(``publication_workflow`` in the
:py:class:``b2share.modules.communities.models.Community`` database model).
Currently there are two existing workflows:

* :py:func:`b2share.modules.communities.wokflows.review_and_publish_workflow`
  When the deposit owner sets ``publication_state`` to ``submitted``, the
  community administrator can either set it to ``published`` (and thus publish
  the deposit) or to ``draft``. The owner can also set it back to draft.
* :py:func:`b2share.modules.communities.wokflows.direct_publish_workflow`
  When the deposit owner sets ``publication_state`` to ``submitted``, the
  workflow automatically sets it to ``published``.

Access control
^^^^^^^^^^^^^^

**Combining permissions**

As the publication state is part of the metadata, sending a PATCH request
via the REST API on a deposit can do multiple actions:

* modify the deposit metadata.
* change the publication state of the deposit.

The permissions for both actions are different. Thus multiple permissions need
to be checked at the same time on a single request. If either of those
actions is forbidden, the request should be fully aborted.

This is possible thanks to the
:py:class:`b2share.modules.access.permissions.AndPermissions` class which
enables to combine multiple permissions. It is used by
:py:class:`~.permissions.UpdateDepositPermission` to check both permissions
during a deposit PATCH.

**Permissions and publication state**

The access control is different depending on the publication state of the
deposit:

* draft: the owner of the deposit can modify it as he wants. He can also
  modify the publication_state field.
* submitted: the owner cannot modify the metadata nor the files. The community
  administrator can modify both. The owner and the community adminisrator can
  set publication_state back to *draft*. The community administrator can also
  set it to *published*.
* published: files cannot be changed as a published record was created.

The deposit can always be deleted for any reason by its owner or the
superuser.

We could have hardcoded those permissions but we chose instead to use
the ``invenio-access`` module which enables to create generic permissions. We
hacked a little the :py:class:`invenio_access.models.ActionNeedMixin` model
by putting JSON inside the ``argument`` field. This enables to use custom
filters like "the user can modify the record if the record belong to community
A and is in *submitted* publication_state". The JSON arguments are always
generated the same way (sorted keys, not space) so that the output string
can be compared. See ``b2share.modules.deposit.permissions``.


Files
^^^^^

The published record uses a snapshot of the deposit's bucket. Thus the
FileInstances are the same and the files are not duplicated.
"""

from __future__ import absolute_import, print_function

from .ext import B2ShareDeposit

__all__ = ('B2ShareDeposit')
