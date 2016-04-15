# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2015, 2016, University of Tuebingen, CERN.
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

"""B2Share base Invenio configuration."""

from __future__ import absolute_import, print_function

import os

from invenio_records_rest.utils import deny_all
from b2share.oauth import b2access

# Default language and timezone
BABEL_DEFAULT_LANGUAGE = 'en'
BABEL_DEFAULT_TIMEZONE = 'Europe/Zurich'
I18N_LANGUAGES = [
]

# FIXME disable authentication by default as B2Access integration is not yet
# done.
B2SHARE_COMMUNITIES_REST_ACCESS_CONTROL_DISABLED = True

# Records
# =======
#: Records REST API endpoints.
RECORDS_REST_ENDPOINTS = dict(
    recuuid=dict(
        pid_type='recuuid',
        pid_minter='b2share_record_uuid_minter',
        pid_fetcher='b2share_record_uuid_fetcher',
        list_route='/records/',
        item_route='/records/<pid_value>',
        search_index='records',
        search_type=None,
        record_serializers={
            'application/json': ('b2share.modules.records.serializers'
                                 ':json_v1_response'),
        },
        search_serializers={
            'application/json': ('b2share.modules.records.serializers'
                                 ':json_v1_search'),
        },
        default_media_type='application/json',
        query_factory_imp='invenio_records_rest.query.es_query_factory',
    ),
)

RECORDS_REST_DEFAULT_SORT = dict(
    records=dict(
        query='bestmatch',
        noquery='mostrecent',
    )
)

RECORDS_REST_SORT_OPTIONS = dict(
    records=dict(
        bestmatch=dict(
            fields=['_score'],
            title='Best match',
            default_order='desc',
            order=1,
        ),
        mostrecent=dict(
            fields=['_created'],
            title='Most recent',
            default_order='desc',
            order=2,
        ),
    )
)

RECORDS_REST_DEFAULT_CREATE_PERMISSION_FACTORY = None
RECORDS_REST_DEFAULT_READ_PERMISSION_FACTORY = None
RECORDS_REST_DEFAULT_UPDATE_PERMISSION_FACTORY = None
RECORDS_REST_DEFAULT_DELETE_PERMISSION_FACTORY = deny_all


B2ACCESS_APP_CREDENTIALS = dict(
    # B2ACCESS authentication key and secret
    consumer_key=os.environ.get("B2ACCESS_CONSUMER_KEY"),
    consumer_secret=os.environ.get("B2ACCESS_SECRET_KEY"),
)


OAUTHCLIENT_REMOTE_APPS=dict(
    b2access=b2access.REMOTE_APP,
)
