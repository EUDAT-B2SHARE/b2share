
# -*- coding: utf-8 -*-

"""B2Share base Invenio configuration."""

from __future__ import absolute_import, print_function

from invenio_records_rest.utils import deny_all


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
