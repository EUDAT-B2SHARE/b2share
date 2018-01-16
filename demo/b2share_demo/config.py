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
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Demonstration configuration, to be changed by the site administrator"""

from __future__ import absolute_import, print_function
from b2share.modules.oauthclient.b2access import make_b2access_remote_app


SITE_FUNCTION = 'demo' # set to "production" on production instances
# it is prominently displayed on the front page, except when set to "production"
# and also returned by the REST API when querying http://<HOSTNAME>/api

#: In order to modify this variable B2SHARE_SQLALCHEMY_DATABASE_URI
#: needs to be removed from docker-compose.yml
#: Change this parameter to use an external database, e.g.:
# SQLALCHEMY_DATABASE_URI = "postgresql://db_username:db_password@db_host/db_name"


# email notifications
# ===================

SUPPORT_EMAIL = None      # must be setup in the local instances
# (e.g. 'b2share-admin@b2share.eudat.eu')

MAIL_SUPPRESS_SEND = True # this should be set to False on a real instance

OAISERVER_ADMIN_EMAILS = [SUPPORT_EMAIL]
# this will make the SUPPORT_EMAIL show up on the oai-pmh identify page
# if this is undesirable, set it to [], or to ['some_other_email@example.com']


# B2ACCESS
# ========
#: To change the B2ACCESS instance, uncomment and set B2ACCESS_BASE_URL
#:     and also make sure to uncomment OAUTHCLIENT_REMOTE_APPS
# B2ACCESS_BASE_URL = 'https://b2access.eudat.eu/'
# OAUTHCLIENT_REMOTE_APPS = dict(
#     b2access=make_b2access_remote_app(B2ACCESS_BASE_URL)
# )


# file and record quotas
# ======================

FILES_REST_DEFAULT_MAX_FILE_SIZE = 10 * 1024 * 1024 * 1024 # 10 GB per file
"""Maximum file size for the files in a record"""

FILES_REST_DEFAULT_QUOTA_SIZE = 20 * 1024 * 1024 * 1024 # 20 GB per record
"""Quota size for the files in a record"""



# ePIC PID config
# ===============

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

## uncomment and configure the following Handle servers supporting the ePIC API
# CFG_EPIC_USERNAME = 0000
# CFG_EPIC_PASSWORD = ''
# CFG_EPIC_BASEURL = 'https://epic4.storage.surfsara.nl/v2_A/handles/'
# CFG_EPIC_PREFIX = 0000

# for manual testing purposes, FAKE_EPIC_PID can be set to True
# in which case a fake epic pid will be generated for records
# FAKE_EPIC_PID = False



# DOI config
# ==========

AUTOMATICALLY_ASSIGN_DOI = False # change to True to have DOIs allocated on publish
CFG_FAIL_ON_MISSING_DOI = False

PIDSTORE_DATACITE_TESTMODE = False
PIDSTORE_DATACITE_DOI_PREFIX = "XXXX"
PIDSTORE_DATACITE_USERNAME = "XXXX"
PIDSTORE_DATACITE_PASSWORD = "XXXX"

# for manual testing purposes, FAKE_DOI can be set to True
# in which case a fake DOI will be generated for records
# FAKE_DOI = False



# Other
# ==========

# if the TRAINING_SITE_LINK parameter is not empty, a message will show up
# on the front page redirecting the testers to this link
TRAINING_SITE_LINK = ""

# comment B2NOTE_URL to hide b2note buttons
B2NOTE_URL = 'https://b2note.bsc.es/interface_main.html'

# displayed in the UI
TERMS_OF_USE_LINK = 'http://hdl.handle.net/11304/e43b2e3f-83c5-4e3f-b8b7-18d38d37a6cd'


# Cache
# =====
#: In order to modify this variable B2SHARE_CACHE_REDIS_HOST
#: needs to be removed from docker-compose.yml
# CACHE_REDIS_HOST='redis'

#: In order to modify this variable B2SHARE_CACHE_REDIS_URL
#: needs to be removed from docker-compose.yml
# CACHE_REDIS_URL='redis://redis:6379/0'

# Session
# =======
#: In order to modify this variable B2SHARE_ACCOUNTS_SESSION_REDIS_URL
#: needs to be removed from docker-compose.yml
# ACCOUNTS_SESSION_REDIS_URL='redis://redis:6379/1'

# Celery
# ======
#: In order to modify this variable B2SHARE_BROKER_URL needs to be
#: removed from docker-compose.yml
# BROKER_URL='amqp://guest:guest@mq:5672//'

#: In order to modify this variable B2SHARE_CELERY_RESULT_BACKEND needs to be
#: removed from docker-compose.yml
# CELERY_RESULT_BACKEND='redis://redis:6379/2'

# Elasticsearch
# =============
#: In order to modify this variable B2SHARE_SEARCH_ELASTIC_HOSTS needs to be
#: removed from docker-compose.yml
# SEARCH_ELASTIC_HOSTS=['elasticsearch']

