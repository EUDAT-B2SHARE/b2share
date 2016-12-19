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
from datetime import timedelta

from celery.schedules import crontab
from flask import request
from invenio_records_rest.utils import deny_all, allow_all
from b2share.modules.oauthclient import b2access
from b2share.modules.records.search import B2ShareRecordsSearch
from b2share.modules.records.permissions import (
    UpdateRecordPermission, DeleteRecordPermission
)
from b2share.modules.deposit.permissions import (
    CreateDepositPermission, ReadDepositPermission,
    UpdateDepositPermission, DeleteDepositPermission,
)
from b2share.modules.deposit.loaders import patch_input_loader


SUPPORT_EMAIL = None # must be setup in the local instances
MAIL_SUPPRESS_SEND = True # this should be removed on a real instance
MIGRATION_LOGFILE = '/tmp/migration.log' #to log migration exceptions

# Default language and timezone
BABEL_DEFAULT_LANGUAGE = 'en'
BABEL_DEFAULT_TIMEZONE = 'Europe/Zurich'
I18N_LANGUAGES = [
]

# FIXME disable authentication by default as B2Access integration is not yet
# done.
B2SHARE_COMMUNITIES_REST_ACCESS_CONTROL_DISABLED = False

# Records
# =======

RECORDS_REST_ENDPOINTS={}
#: Records REST API endpoints.
B2SHARE_RECORDS_REST_ENDPOINTS = dict(
    b2rec=dict(
        pid_type='b2rec',
        pid_minter='b2dep',
        pid_fetcher='b2rec',
        record_class='invenio_records_files.api:Record',
        search_class=B2ShareRecordsSearch,
        record_serializers={
            'application/json': ('b2share.modules.records.serializers'
                                 ':json_v1_response'),
        },
        search_serializers={
            'application/json': ('b2share.modules.records.serializers'
                                 ':json_v1_search'),
        },
        links_factory_imp=('b2share.modules.records.links'
                           ':record_links_factory'),
        record_loaders={
            'application/json-patch+json': patch_input_loader,
            'application/json':
            # FIXME: create a loader so that only allowed fields can be set
            lambda: request.get_json(),
            # 'b2share.modules.deposit.loaders:deposit_record_loader'
        },
        default_media_type='application/json',
        list_route='/records/',
        item_route='/records/<pid(b2rec,record_class="invenio_records_files.api:Record"):pid_value>',
        create_permission_factory_imp=CreateDepositPermission,
        read_permission_factory_imp=allow_all,
        update_permission_factory_imp=UpdateRecordPermission,
        delete_permission_factory_imp=DeleteRecordPermission,
    ),
)


DEPOSIT_REST_ENDPOINTS={}
#: REST API configuration.
DEPOSIT_PID = 'pid(b2dep,record_class="b2share.modules.deposit.api:Deposit")'
DEPOSIT_PID_MINTER='b2rec'
B2SHARE_DEPOSIT_REST_ENDPOINTS = dict(
    b2dep=dict(
        pid_type='b2dep',
        pid_minter='b2dep',
        pid_fetcher='b2dep',
        record_class='b2share.modules.deposit.api:Deposit',
        max_result_window=10000,
        default_media_type='application/json',
        record_serializers={
            'application/json': ('b2share.modules.deposit.serializers'
                                 ':json_v1_response'),
        },
        search_serializers={
            'application/json': (
                'b2share.modules.records.serializers:json_v1_search'),
        },
        links_factory_imp='b2share.modules.deposit.links:deposit_links_factory',
        record_loaders={
            'application/json-patch+json': patch_input_loader,
            'application/json':
            lambda: request.get_json(),
            # FIXME: create a loader so that only allowed fields can be set
            # lambda: request.get_json(),
            # 'b2share.modules.deposit.loaders:deposit_record_loader'
        },
        item_route='/records/<{0}:pid_value>/draft'.format(DEPOSIT_PID),
        create_permission_factory_imp=deny_all,
        read_permission_factory_imp=ReadDepositPermission,
        update_permission_factory_imp=UpdateDepositPermission,
        delete_permission_factory_imp=DeleteDepositPermission,
    ),
)

INDEXER_RECORD_TO_INDEX='b2share.modules.records.indexer:record_to_index'

#: Files REST permission factory
FILES_REST_PERMISSION_FACTORY = \
    'b2share.modules.files.permissions:files_permission_factory'

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


OAUTHCLIENT_REMOTE_APPS = dict(
    b2access=b2access.REMOTE_APP,
)

# Let Invenio Accounts register Flask Security
ACCOUNTS_REGISTER_BLUEPRINT = True


# OAI-PMH
OAISERVER_RECORD_INDEX = 'records'
OAISERVER_ID_PREFIX = 'oai:b2share.eudat.eu:b2rec/'
OAISERVER_PAGE_SIZE = 25
OAISERVER_ADMIN_EMAILS = [SUPPORT_EMAIL]
OAISERVER_REGISTER_RECORD_SIGNALS = False
OAISERVER_METADATA_FORMATS = {
    'oai_dc': {
        'namespace': 'http://www.openarchives.org/OAI/2.0/oai_dc/',
        'schema': 'http://www.openarchives.org/OAI/2.0/oai_dc.xsd',
        'serializer': 'b2share.modules.records.serializers.oaipmh_oai_dc',
    },
    'marcxml': {
        'namespace': 'http://www.loc.gov/MARC21/slim',
        'schema': 'http://www.loc.gov/standards/marcxml/schema/MARC21slim.xsd',
        'serializer': 'b2share.modules.records.serializers.oaipmh_marc21_v1',
    },
}

# Celery
# ======
#: Default broker (RabbitMQ on locahost).
BROKER_URL = "amqp://guest:guest@localhost:5672//"
#: Default Celery result backend.
CELERY_RESULT_BACKEND = "redis://localhost:6379/1"
#: Accepted content types for Celery.
CELERY_ACCEPT_CONTENT = ['json', 'msgpack', 'yaml']
#: Beat schedule
CELERYBEAT_SCHEDULE = {
    'embargo-updater': {
        'task': 'b2share.modules.records.tasks.update_expired_embargos',
        'schedule': crontab(minute=2, hour=0),
    },
    'indexer': {
        'task': 'invenio_indexer.tasks.process_bulk_queue',
        'schedule': timedelta(minutes=5),
    },
}


# ePIC PID config
# ===============

CFG_HANDLE_SYSTEM_BASEURL = 'http://hdl.handle.net'
CFG_FAIL_ON_MISSING_PID = False
CFG_FAIL_ON_MISSING_FILE_PID = False

# CFG_EPIC_USERNAME = 0000
# CFG_EPIC_PASSWORD = ''
# CFG_EPIC_BASEURL = 'https://epic4.storage.surfsara.nl/v2_A/handles/'
# CFG_EPIC_PREFIX = 0000

# DOI config
# ==========

DOI_IDENTIFIER_FORMAT = 'b2share.{recid}'
CFG_FAIL_ON_MISSING_DOI = False

PIDSTORE_DATACITE_TESTMODE = False
PIDSTORE_DATACITE_DOI_PREFIX = "XXXX"
PIDSTORE_DATACITE_USERNAME = "XXXX"
PIDSTORE_DATACITE_PASSWORD = "XXXX"

V1_URL_BASE = 'https://b2share.eudat.eu/api/'

B2DROP_SERVER = {
    'host': 'b2drop.eudat.eu',
    'protocol': 'https',
    'path': '/remote.php/webdav/',
}

# By default we suppose there is one proxy in front of B2Share
WSGI_PROXIES = 1
PREFERRED_URL_SCHEME = 'http'

FILES_REST_DEFAULT_MAX_FILE_SIZE = 1000 * 1024 * 1024 # 1 GB by default for RC4

# prominently displayed on the front page, except when set to "production"
# and also returned by the REST API when querying http://<HOSTNAME>/api
SITE_FUNCTION = 'demo' # set to "production" on production instances

# if the TRAINING_SITE_LINK parameter is not empty, a message will show up
# on the front page redirecting the testers to this link
TRAINING_SITE_LINK = ""
