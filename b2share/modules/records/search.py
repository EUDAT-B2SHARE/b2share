# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2016 CERN.
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

"""Records search class and helpers."""

from elasticsearch_dsl.query import Bool, Q
from invenio_search.api import RecordsSearch
from flask_security import current_user


class B2ShareRecordsSearch(RecordsSearch):
    """Search class for records."""

    class Meta:
        """Default index and filter for record search."""

        index = 'records'

    def __init__(self, **kwargs):
        """Initialize instance."""
        super(B2ShareRecordsSearch, self).__init__(**kwargs)
        if current_user.is_authenticated:
            self.query = Q(
                'bool',
                must=self.query._proxied,
                should=[Q(
                    Bool(filter=[Q('term', open_access=True)])
                ),
                Q(
                    Bool(filter=[Q('term', owners=current_user.id)])
                )],
                minimum_should_match=1
            )
        else:
            self.query = Q(
                'bool',
                must=self.query._proxied,
                should=[Q(
                    Bool(filter=[Q('term', open_access=True)])
                )],
                minimum_should_match=1
            )
