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

from invenio_search import current_search_client
from invenio_stats.aggregations import StatAggregator

"""Statistics aggregations."""

def register_aggregations():
    """Register additional stats aggregations."""
    return [dict(
        aggregation_name='record-view-agg',
        templates='contrib/aggregations/aggr_record_view/v2',
        aggregator_class=StatAggregator,
        aggregator_config=dict(
            client=current_search_client,
            event='record-view',
            aggregation_field='unique_id',
            aggregation_interval='day',
            copy_fields=dict(
                record_id='record_id',
                pid_type='pid_type',
                pid_value='pid_value',
                community='community'
            )
        ))]