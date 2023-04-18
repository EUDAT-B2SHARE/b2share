# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2022 CSC Ltd, EUDAT CDI.
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

import pytest
import json

@pytest.fixture(scope='function')
def mocked_app(config={}):
    """."""

    class _Logger(object):
        """Mocked logging class for Vault loader tests."""

        def __init__(self):
            """Constructor."""

        def warning(o, msg, *args, **kwargs):
            """Mock."""
            print(f'WARNING: {msg}\n')
            pass

        def info(o, msg, *args, **kwargs):
            """Mock."""
            print(f"INFO: {msg}\n")
            pass
        
        def error(o, msg, *args, **kwargs):
            """Mock."""
            print(f"ERROR: {msg}\n")
            pass
        
        def debug(o, msg, *args, **kwargs):
            """Debug."""
            print(f'DEBUG: {msg}\n')
            pass

    class _App(object):
        """Mocked App object for Vault loader."""

        config = dict()
        logger = _Logger()
        instance_path = ""

        def __init__(self, config):
            """Constructor."""

            self.config = config

    return _App(config)

@pytest.fixture(scope='function')
def vault_secrets_response():
    """Mocked HTTP response content for Vault loader tests."""

    secrets_response = {
        'request_id': '8d322e31-97f7-a68b-8d7a-b2b032580576',
        'lease_id': '',
        'renewable': False,
        'lease_duration': 0,
        'data': {
            'data': {
                'B2SHARE_B2ACCESS_CONSUMER_KEY': 'b2share_inar',
                'B2SHARE_B2ACCESS_SECRET_KEY': 'CHANGE_ME',
                'B2SHARE_BROKER_URL': 'amqp://invenio:invenio@mq:5672/',
                'B2SHARE_CELERY_BROKER_URL': 'amqp://invenio:invenio@mq:5672/',
                'B2SHARE_SECRET_KEY': 'abcxyz',
                'B2SHARE_PID_HANDLE_CREDENTIALS': {
                    "HTTPS_verify": "True",
                    "certificate_only": "certonlyfile.pem",
                    "handle_server_url": "handleurl.com",
                    "handleowner": "ow.ner",
                    "prefix": "12345",
                    "private_key": "privkey.pem",
                    "reverse_password": "<reverselookup_password>",
                    "reverselookup_username": "54321"
                },
                'emptyfield': ''
                },
            'metadata': {
                'created_time': '2022-02-30T00:00:00.000000001Z',
                'custom_metadata': None,
                'deletion_time': '',
                'destroyed': False,
                'version': 12
                }
        },
        'wrap_info': None,
        'warnings': None,
        'auth': None
    }
    
    return json.dumps(secrets_response)

@pytest.fixture(scope='function')
def vault_certificate_response():
    """Mocked HTTP response content for Vault loader tests."""
    
    certificate_response = {
        'request_id': 'd29f93aa-724c-75fe-5447-d618ad723e5a',
        'lease_id': '',
        'renewable': False,
        'lease_duration': 0,
        'data': {
            'data': {
                'my_mocked_test_cert.pem': 
                    '-----BEGIN CERTIFICATE-----\n-----END CERTIFICATE-----\n',
            },
            'metadata': {
                'created_time': '2022-02-30T00:00:00.000000001Z',
                'custom_metadata': None,
                'deletion_time': '',
                'destroyed': False,
                'version': 1
            }
        },
        'wrap_info': None,
        'warnings': None,
        'auth': None
    }
    
    return json.dumps(certificate_response)

