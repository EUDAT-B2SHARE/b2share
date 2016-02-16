# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2016 University of Tuebingen, CERN.
# Copyright (C) 2015 University of Tuebingen.
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

"""Community module signals."""

from blinker import Namespace

_signals = Namespace()

before_community_insert = _signals.signal('before-community-insert')
"""Signal is sent before a community is inserted.

Example subscriber

.. code-block:: python

    def listener(sender, *args, **kwargs):
        sender['key'] = sum(args)

    from invenio_communities.signals import before_community_insert
    before_community_insert.connect(listener)
"""

after_community_insert = _signals.signal('after-community-insert')
"""Signal sent after a community is inserted."""

before_community_update = _signals.signal('before-community-update')
"""Signal is sent before a community is update."""

after_community_update = _signals.signal('after-community-update')
"""Signal sent after a community is updated."""

before_community_delete = _signals.signal('before-community-delete')
"""Signal is sent before a community is delete."""

after_community_delete = _signals.signal('after-community-delete')
"""Signal sent after a community is delete."""
