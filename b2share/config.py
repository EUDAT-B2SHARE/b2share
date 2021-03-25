# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 EUDAT.
#
# B2SHARE is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""Default configuration for B2SHARE.

You overwrite and set instance-specific configuration by either:

- Configuration file: ``<virtualenv prefix>/var/instance/invenio.cfg``
- Environment variables: ``APP_<variable name>``
"""

from __future__ import absolute_import, print_function

import os
from datetime import timedelta

from b2share.modules.access.permissions import admin_only, authenticated_only
from celery.schedules import crontab
from flask import request

from invenio_app.config import APP_DEFAULT_SECURE_HEADERS
# from invenio_previewer.config import PREVIEWER_PREFERENCE as BASE_PREFERENCE
from invenio_records_rest.utils import deny_all, allow_all

from b2share.modules.oauthclient.b2access import make_b2access_remote_app
from b2share.modules.records.search import B2ShareRecordsSearch
from b2share.modules.records.permissions import (
    UpdateRecordPermission, DeleteRecordPermission
)
from b2share.modules.deposit.permissions import (
    CreateDepositPermission, ReadDepositPermission,
    UpdateDepositPermission, DeleteDepositPermission,
)
from b2share.modules.deposit.loaders import deposit_patch_input_loader
from b2share.modules.records.loaders import record_patch_input_loader
from b2share.modules.users.loaders import (
    account_json_loader, account_json_patch_loader,
)

from invenio_search.config import SEARCH_ELASTIC_HOSTS

SEARCH_ELASTIC_HOSTS = []

for elastic_host in os.environ.get("ELASTIC_HOSTS", "localhost:9200").split(','):
    try:
        (host, port) = elastic_host.split(':')
    except:
        host = elastic_host
        port = 9200

    SEARCH_ELASTIC_HOSTS.append(dict(host=host, port=port, use_ssl=False, ssl_show_warn=False))

def _(x):
    """Identity function used to trigger string extraction."""
    return x

# Rate limiting
# =============
#: Storage for ratelimiter.
RATELIMIT_STORAGE_URL = os.environ.get("INVENIO_RATELIMIT_STORAGE_URL", 'redis://localhost:6379/3')

# I18N
# ====
#: Default language
BABEL_DEFAULT_LANGUAGE = 'en'
#: Default time zone
BABEL_DEFAULT_TIMEZONE = 'Europe/Zurich'
#: Other supported languages (do not include the default language in list).
I18N_LANGUAGES = [
    # ('fr', _('French'))
]

# Base templates
# ==============
#: Global base template.
BASE_TEMPLATE = 'b2share_main/base.html'
#: Cover page base template (used for e.g. login/sign-up).
COVER_TEMPLATE = 'invenio_theme/page_cover.html'
#: Footer base template.
MAIN_TEMPLATE = 'invenio_theme/footer.html'
#: Header base template.
HEADER_TEMPLATE = 'invenio_theme/header.html'
#: Settings base template.
SETTINGS_TEMPLATE = 'invenio_theme/page_settings.html'

# Theme configuration
# ===================
#: Site name
THEME_SITENAME = _('B2SHARE')
#: Use default frontpage.
THEME_FRONTPAGE = True
#: Frontpage title.
THEME_FRONTPAGE_TITLE = _('B2SHARE')
#: Frontpage template.
THEME_FRONTPAGE_TEMPLATE = 'b2share_main/page.html'

# Email configuration
# ===================
#: Email address for support.
SUPPORT_EMAIL = "info@eudat.eu"
#: Disable email sending by default.
MAIL_SUPPRESS_SEND = True

# Assets
# ======
#: Static files collection method (defaults to copying files).
COLLECT_STORAGE = 'flask_collect.storage.file'

# Accounts
# ========
#: Email address used as sender of account registration emails.
SECURITY_EMAIL_SENDER = SUPPORT_EMAIL
#: Email subject for account registration emails.
SECURITY_EMAIL_SUBJECT_REGISTER = _(
    "Welcome to B2SHARE!")
#: Redis session storage URL.
CACHE_REDIS_URL=os.environ.get("INVENIO_CACHE_REDIS_URL", 'redis://localhost:6379/0')
ACCOUNTS_SESSION_REDIS_URL = os.environ.get("INVENIO_ACCOUNTS_SESSION_REDIS_URL", 'redis://localhost:6379/1')
#: Enable session/user id request tracing. This feature will add X-Session-ID
#: and X-User-ID headers to HTTP response. You MUST ensure that NGINX (or other
#: proxies) removes these headers again before sending the response to the
#: client. Set to False, in case of doubt.
ACCOUNTS_USERINFO_HEADERS = True

# Database
# ========
#: Database URI including user and password
SQLALCHEMY_DATABASE_URI = os.environ.get("INVENIO_SQLALCHEMY_DATABASE_URI", \
    'postgresql+psycopg2://b2share:b2share@localhost/b2share')

# JSONSchemas
# ===========
#: Hostname used in URLs for local JSONSchemas.
JSONSCHEMAS_HOST = os.environ.get("JSONSCHEMAS_HOST", 'b2share.eudat.eu')

# APPLICATION ROOT
APPLICATION_ROOT = os.environ.get("APPLICATION_ROOT", '')

# Flask configuration
# ===================
# See details on
# http://flask.pocoo.org/docs/0.12/config/#builtin-configuration-values

#: Secret key - each installation (dev, production, ...) needs a separate key.
#: It should be changed before deploying.
SECRET_KEY = 'CHANGE_ME'
#: Max upload size for form data via application/mulitpart-formdata.
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100 MiB
#: Sets cookie with the secure flag by default
SESSION_COOKIE_SECURE = (os.environ.get('SESSION_COOKIE_SECURE', "True").upper() == "True".upper())
#: Since HAProxy and Nginx route all requests no matter the host header
#: provided, the allowed hosts variable is set to localhost. In production it
#: should be set to the correct host and it is strongly recommended to only
#: route correct hosts to the application.
APP_ALLOWED_HOSTS = [ os.environ.get("SERVER_NAME", 'localhost'), os.environ.get("SERVER_INTERNAL_IP", '127.0.0.1') ]
APP_ALLOWED_HOSTS = None
# OAI-PMH
# =======
OAISERVER_ID_PREFIX = 'oai:b2share.eudat.eu:'

# Previewers
# ==========
#: Include IIIF preview for images.
# PREVIEWER_PREFERENCE = ['iiif_image'] + BASE_PREFERENCE

# Debug
# =====
# Flask-DebugToolbar is by default enabled when the application is running in
# debug mode. More configuration options are available at
# https://flask-debugtoolbar.readthedocs.io/en/latest/#configuration

#: Switches off incept of redirects by Flask-DebugToolbar.
DEBUG_TB_INTERCEPT_REDIRECTS = False

# Configures Content Security Policy for PDF Previewer
# Remove it if you are not using PDF Previewer
APP_DEFAULT_SECURE_HEADERS['content_security_policy'] = {
    'default-src': ["'self'", "'unsafe-inline'"],
    'object-src': ["'none'"],
    'script-src': ["'self'", "'unsafe-inline'", "'unsafe-eval'"],
    'style-src': ["'self'", "'unsafe-inline'", "data:", "https://fonts.googleapis.com/css"],
    'img-src': ["'self'", "data: blob:;"],
    'font-src': ["'self'", "data:", "https://fonts.gstatic.com", "https://fonts.googleapis.com"],
}

# ADDED:

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



SUPPORT_EMAIL = None # must be setup in the local instances
MAIL_SUPPRESS_SEND = True # this should be removed on a real instance
MIGRATION_LOGFILE = '/tmp/migration.log' #to log migration exceptions

# Default language and timezone
BABEL_DEFAULT_LANGUAGE = 'en'
BABEL_DEFAULT_TIMEZONE = 'Europe/Zurich'
I18N_LANGUAGES = [
]

# Records
# =======

RECORDS_REST_ENDPOINTS={} # We disable all endpoints as we will define our own custom REST API
#: Records REST API endpoints.
B2SHARE_RECORDS_REST_ENDPOINTS = dict(
    b2rec=dict(
        pid_type='b2rec',
        pid_minter='b2dep',
        pid_fetcher='b2rec',
        record_class='b2share.modules.records.api:B2ShareRecord',
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
            'application/json-patch+json': record_patch_input_loader,
            'application/json':
            # FIXME: create a loader so that only allowed fields can be set
            lambda: request.get_json(),
            # 'b2share.modules.deposit.loaders:deposit_record_loader'
        },
        default_media_type='application/json',
        list_route='/records/',
        item_route='/records/<pid(b2rec,record_class="b2share.modules.records.api:B2ShareRecord"):pid_value>',
        create_permission_factory_imp=CreateDepositPermission,
        read_permission_factory_imp=allow_all,
        update_permission_factory_imp=UpdateRecordPermission,
        delete_permission_factory_imp=DeleteRecordPermission,
    ),
)


#: Endpoint for uploading files.
DEPOSIT_FILES_API = u'/api/files'
#: Template for deposit list view.
DEPOSIT_SEARCH_API = '/api/deposit/depositions'
#: Template for deposit records API.
DEPOSIT_RECORDS_API = '/api/deposit/depositions/{pid_value}'
#: Records REST API endpoints.
RECORDS_API = '/api/records/{pid_value}'
#: Default API endpoint for search UI.
SEARCH_UI_SEARCH_API = "/api/records/"

DEPOSIT_REST_ENDPOINTS={} # We disable all endpoints as we will define our own custom REST API
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
            'application/json-patch+json': deposit_patch_input_loader,
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

#: URL template for generating URLs outside the application/request context
FILES_REST_ENDPOINT = '{scheme}://{host}/api/files/{bucket}/{key}'

#: Files REST permission factory
FILES_REST_PERMISSION_FACTORY = \
    'b2share.modules.files.permissions:files_permission_factory'

FILES_REST_STORAGE_FACTORY = \
    'b2share.modules.files.storage.b2share_storage_factory'

FILES_REST_STORAGE_CLASS_LIST = dict(
    B='B2SafePid',
    S='Standard',
    A='Archived'
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
            fields=['-_score'],
            title='Best match',
            default_order='desc',
            order=1,
        ),
        mostrecent=dict(
            fields=['-_created'],
            title='Most recent',
            default_order='desc',
            order=2,
        ),
    ),
    deposits=dict(
        bestmatch=dict(
            fields=['-_score'],
            title='Best match',
            default_order='desc',
            order=1,
        ),
        mostrecent=dict(
            fields=['-_created'],
            title='Most recent',
            default_order='desc',
            order=2,
        ),
    )
)

RECORDS_REST_DEFAULT_CREATE_PERMISSION_FACTORY = None
RECORDS_REST_DEFAULT_READ_PERMISSION_FACTORY = None
RECORDS_REST_DEFAULT_UPDATE_PERMISSION_FACTORY = None
RECORDS_REST_DEFAULT_DELETE_PERMISSION_FACTORY = \
    'b2share.modules.records.permissions:DeleteRecordPermission'

B2ACCESS_APP_CREDENTIALS = dict(
    # B2ACCESS authentication key and secret
    consumer_key=os.environ.get("B2ACCESS_CONSUMER_KEY", '*** CONSUMER KEY ***'),
    consumer_secret=os.environ.get("B2ACCESS_SECRET_KEY", '*** SECRET KEY ***'),
)

B2ACCESS_BASE_URL = 'https://b2access.eudat.eu/'
if os.environ.get("USE_STAGING_B2ACCESS"):
    B2ACCESS_BASE_URL = 'https://unity.eudat-aai.fz-juelich.de/'

OAUTHCLIENT_REMOTE_APPS = dict(
    b2access=make_b2access_remote_app(B2ACCESS_BASE_URL)
)

# Don't let Invenio Accounts register Flask Security
ACCOUNTS_REGISTER_BLUEPRINT = False


ACCOUNTS_REST_ASSIGN_ROLE_PERMISSION_FACTORY = \
    'b2share.modules.users.permissions:RoleAssignPermission'
ACCOUNTS_REST_UNASSIGN_ROLE_PERMISSION_FACTORY = \
    'b2share.modules.users.permissions:RoleAssignPermission'
ACCOUNTS_REST_READ_ROLE_PERMISSION_FACTORY = authenticated_only
ACCOUNTS_REST_READ_ROLES_LIST_PERMISSION_FACTORY = authenticated_only

ACCOUNTS_REST_UPDATE_ROLE_PERMISSION_FACTORY = admin_only
ACCOUNTS_REST_DELETE_ROLE_PERMISSION_FACTORY = admin_only
ACCOUNTS_REST_CREATE_ROLE_PERMISSION_FACTORY = admin_only

# permission to list all the users having the specific role
ACCOUNTS_REST_READ_ROLE_USERS_LIST_PERMISSION_FACTORY = allow_all

# permission to list/search users
ACCOUNTS_REST_READ_USERS_LIST_PERMISSION_FACTORY = \
    'b2share.modules.users.permissions:AccountSearchPermission'

# permission to read user properties
ACCOUNTS_REST_READ_USER_PROPERTIES_PERMISSION_FACTORY = \
    'b2share.modules.users.permissions:AccountReadPermission'

# permission to update user properties
ACCOUNTS_REST_UPDATE_USER_PROPERTIES_PERMISSION_FACTORY = \
    'b2share.modules.users.permissions:AccountUpdatePermission'

# permission to list a user's roles
ACCOUNTS_REST_READ_USER_ROLES_LIST_PERMISSION_FACTORY = authenticated_only

ACCOUNTS_REST_ACCOUNT_LOADERS = dict(
    PATCH={
        'application/json': account_json_loader,
        'application/json-patch+json': account_json_patch_loader,
    }
)

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

# Cache
# =====
CACHE_TYPE='redis'

# Celery
# ======
#: Default broker (RabbitMQ on locahost).
BROKER_URL = os.environ.get("INVENIO_CELERY_BROKER_URL", "amqp://guest:guest@localhost:5672//")
#: Default Celery result backend.
CELERY_RESULT_BACKEND = os.environ.get("INVENIO_ACCOUNTS_SESSION_REDIS_URL", "redis://localhost:6379/1")
#: Accepted content types for Celery.
CELERY_ACCEPT_CONTENT = ['json', 'msgpack', 'yaml']
#: Beat schedule
CELERY_BEAT_SCHEDULE = {
    'embargo-updater': {
        'task': 'b2share.modules.records.tasks.update_expired_embargoes',
        'schedule': crontab(minute=2, hour=0),
    },
    'indexer': {
        'task': 'invenio_indexer.tasks.process_bulk_queue',
        'schedule': timedelta(minutes=5),
    },
    'process-file-downloads': {
        'task': 'invenio_stats.tasks.process_events',
        'schedule': timedelta(minutes=5),
        'args': [['file-download']]
    },
    'aggregate-daily-file-downloads': {
        'task': 'invenio_stats.tasks.aggregate_events',
        'schedule': timedelta(minutes=15),
        'args': [['file-download-agg']]
    },
    # Check file checksums
    'file-checks': {
        'task': 'invenio_files_rest.tasks.schedule_checksum_verification',
        'schedule': timedelta(hours=1),
        'kwargs': {
            # Manually check and calculate checksums of files biannually
            'frequency': {'days': 180},
            'batch_interval': {'hours': 1},
            # Split batches based on max number of files
            'max_count': 0,
            # Split batches based on total files size
            'max_size': 0,
        },
    },
    # Check file checksums which have previously failed the scan
    'file-checks-failed': {
        'task': 'b2share.modules.files.tasks.schedule_failed_checksum_files',
        'schedule': timedelta(hours=1),
        'kwargs': {
            # Manually check and calculate checksums of files biannually
            'frequency': {'days': 7},
            'batch_interval': {'hours': 1},
            # Split batches based on max number of files
            'max_count': 0,
            # Split batches based on total files size
            'max_size': 0,
        },
    },
}


# ePIC PID config
# ===============

CFG_HANDLE_SYSTEM_BASEURL = 'http://hdl.handle.net'
CFG_FAIL_ON_MISSING_PID = False
CFG_FAIL_ON_MISSING_FILE_PID = False

## uncomment and configure PID_HANDLE_CREDENTIALS for Handle servers v8 or above
# PID_HANDLE_CREDENTIALS = {
#   "handle_server_url": "https://fqdn:<port>",
#   "private_key": "/<path>/<index>_<prefix>_ADMIN_privkey.pem",
#   "certificate_only": "/<path>/<index>_<prefix>_ADMIN_certificate_only.pem",
#   "prefix": "<prefix>",
#   "handleowner": "200:0.NA/<prefix>",
#   "reverse_username": "<prefix>",
#   "reverse_password": "<password>",
#   "HTTPS_verify": "True"
# }

## uncomment and configure the following for Handle servers supporting the ePIC API
# CFG_EPIC_USERNAME = 0000
# CFG_EPIC_PASSWORD = ''
# CFG_EPIC_BASEURL = 'https://epic4.storage.surfsara.nl/v2_A/handles/'
# CFG_EPIC_PREFIX = 0000

# for manual testing purposes, FAKE_EPIC_PID can be set to True
# in which case a fake epic pid will be generated for records
# FAKE_EPIC_PID = False


# DOI config
# ==========
RECORDS_FILES_REST_ENDPOINTS= {}
AUTOMATICALLY_ASSIGN_DOI = False
DOI_IDENTIFIER_FORMAT = 'b2share.{recid}'
CFG_FAIL_ON_MISSING_DOI = False

PIDSTORE_DATACITE_TESTMODE = False
PIDSTORE_DATACITE_DOI_PREFIX = "XXXX"
PIDSTORE_DATACITE_USERNAME = "XXXX"
PIDSTORE_DATACITE_PASSWORD = "XXXX"

# for manual testing purposes, FAKE_DOI can be set to True
# in which case a fake DOI will be generated for records
# FAKE_DOI = False


B2DROP_SERVER = {
    'host': 'b2drop.eudat.eu',
    'protocol': 'https',
    'path': '/remote.php/webdav/',
}


# comment B2NOTE_URL to hide b2note buttons
B2NOTE_URL = 'https://b2note.bsc.es'

# displayed in the UI
TERMS_OF_USE_LINK = 'http://hdl.handle.net/11304/e43b2e3f-83c5-4e3f-b8b7-18d38d37a6cd'
HELP_LINKS = {
    'b2note': 'https://b2note.eudat.eu/',
    'issues': 'https://github.com/EUDAT-B2SHARE/b2share/issues',
    'rest-api': 'https://eudat.eu/services/userdoc/b2share-http-rest-api',
    'search': 'https://eudat.eu/services/userdoc/b2share-advanced-search',
    'user-guide': 'https://eudat.eu/services/userdoc/b2share-usage'
}

# By default we suppose there is one proxy in front of B2Share
WSGI_PROXIES = 1
PREFERRED_URL_SCHEME = 'http'

FILES_REST_DEFAULT_MAX_FILE_SIZE = 10 * 1024 * 1024 * 1024 # 10 GB per file
"""Maximum file size for the files in a record"""

FILES_REST_DEFAULT_QUOTA_SIZE = 20 * 1024 * 1024 * 1024 # 20 GB per record
"""Quota size for the files in a record"""

# prominently displayed on the front page, except when set to "production"
# and also returned by the REST API when querying http://<HOSTNAME>/api
SITE_FUNCTION = 'demo' # set to "production" on production instances

# if the TRAINING_SITE_LINK parameter is not empty, a message will show up
# on the front page redirecting the testers to this link
TRAINING_SITE_LINK = ""


# Invenio Stats
# ==============

STATS_EVENTS = {
    'file-download': dict(
        templates='invenio_stats.contrib.file_download',
        signal='invenio_files_rest.signals.file_downloaded',
        event_builders=[
            'invenio_stats.contrib.event_builders.file_download_event_builder'
        ],
        processor_config=dict(
            preprocessors=[
                'b2share.modules.stats.processors:skip_deposit',
                'invenio_stats.processors:flag_robots',
                'invenio_stats.processors:anonymize_user',
                'invenio_stats.contrib.event_builders:build_file_unique_id',
            ],
            # Keep only 1 file download for each file and user every 30 sec
            double_click_window=30,
            # Create one index per month which will store file download events
            suffix='%Y-%m'
        ))
}

from invenio_stats.aggregations import StatAggregator

STATS_AGGREGATIONS = {
    'file-download-agg': dict(
        templates='invenio_stats.contrib.aggregations.aggr_file_download',
        cls=StatAggregator,
        params=dict(
            event='file-download',
            field='unique_id',
            interval='day',
            index_interval='month',
            copy_fields=dict(
                file_key='file_key',
                bucket_id='bucket_id',
                file_id='file_id',
            ),
            metric_fields={
                'unique_count': (
                    'cardinality', 'unique_session_id',
                    {'precision_threshold': 1000},
                ),
                'volume': ('sum', 'size', {}),
            },
        )
    ),
}

STATS_QUERIES = {
    'bucket-file-download-total': {},
}

# Flask-Security
# ==============
#: As we use B2Access, don't ask users to confirm their accounts.
SECURITY_CONFIRMABLE=False
#: Don't send emails when users register
SECURITY_SEND_REGISTER_EMAIL=False
#: There is no password so don't send password change emails
SECURITY_SEND_PASSWORD_CHANGE_EMAIL=False
SECURITY_SEND_PASSWORD_RESET_NOTICE_EMAIL=False

# Extra (Harry Kodden)
# When testing in HTTP, both cookie secure and CSRF enforcement is switched off
APP_ENABLE_SECURE_HEADERS = (os.environ.get('SESSION_COOKIE_SECURE', "True").upper() == "True".upper())

SESSION_COOKIE_PATH="/"
SESSION_COOKIE_SAMESITE="Lax"

APP_THEME = ['semantic-ui']
SECURITY_CHANGEABLE = False
