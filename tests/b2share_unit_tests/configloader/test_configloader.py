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

"""Tests for B2Share config loader."""

import responses
import os
import pytest

from b2share.modules.configloader.vaultloader import (
    load_vault_secrets, 
    load_vault_certificates
)

from b2share.modules.configloader.features import load_features

@responses.activate
def test_loading_vault_secrets(mocked_app, vault_secrets_response):
    """."""
    # Test loading vault secrets
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            "http://agent:8100/v1/secret/data/b2share/dev/application",
            body=vault_secrets_response,
            status=200,
            content_type="application/json",
        )

        mocked_app.config['CONFIG_VAULT_ENTITY'] = 'dev'
        mocked_app.config['CONFIG_VAULT_AGENT_ADDR'] = 'http://agent:8100'
        mocked_app.config['LOGGING_LEVEL'] = 'DEBUG'
        mocked_app.config['CONFIG_OUTPUT_SECRETS'] = True

        load_vault_secrets(mocked_app)
        assert mocked_app.config.get("SECRET_KEY") == "abcxyz"
        assert mocked_app.config.get("B2ACCESS_CONSUMER_KEY") == "b2share_inar"
        assert mocked_app.config.get("PID_HANDLE_CREDENTIALS", {}).get("prefix") == "12345"

def test_loading_vault_certificates(mocked_app, vault_certificate_response):
    """."""
    # Test loading vault certificates
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            "http://agent:8100/v1/secret/data/b2share/dev/certificates",
            body=vault_certificate_response,
            status=200,
            content_type="application/json",
        )

        mocked_app.config['CONFIG_VAULT_ENTITY'] = 'dev'
        mocked_app.config['CONFIG_VAULT_AGENT_ADDR'] = 'http://agent:8100'

        load_vault_certificates(mocked_app)

        assert os.path.isfile(f'{mocked_app.instance_path}/my_mocked_test_cert.pem')

def test_loading_vault_secrets_fail(mocked_app, vault_secrets_response, capsys):
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            "http://agent:8100/v1/secret/data/b2share/dev/application",
            status=404,
            content_type="application/json",
        )
        mocked_app.config = {}
        with pytest.raises(Exception):
            load_vault_secrets(mocked_app)

        mocked_app.config['CONFIG_VAULT_ENTITY'] = 'dev'
        mocked_app.config['CONFIG_VAULT_AGENT_ADDR'] = 'http://agent:8100'

        load_vault_secrets(mocked_app)
        captured = capsys.readouterr()
        assert '404' in captured.out

    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            "http://agent:8100/v1/secret/data/b2share/dev/application",
            json={},
            status=200,
            content_type="application/json",
        )
        with pytest.raises(Exception):
            load_vault_secrets(mocked_app)

def test_loading_vault_certificates_fail(mocked_app, vault_certificate_response, capsys):

    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            "http://agent:8100/v1/secret/data/b2share/dev/certificates",
            status=403,
            content_type="application/json",
        )
        mocked_app.config = {}
        with pytest.raises(Exception):
            load_vault_certificates(mocked_app)

        mocked_app.config['CONFIG_VAULT_ENTITY'] = 'dev'
        mocked_app.config['CONFIG_VAULT_AGENT_ADDR'] = 'http://agent:8100'

        load_vault_certificates(mocked_app)
        captured = capsys.readouterr()
        assert '403' in captured.out

def test_feature_b2access(mocked_app):
    mocked_app.config = {}
    load_features(mocked_app)
    assert mocked_app.config['OAUTHCLIENT_REMOTE_APPS'] == {}


    # Test for missing required config
    mocked_app.config['CONFIG_ENABLE_B2ACCESS'] = True
    with pytest.raises(Exception):
        load_features(mocked_app)

    # Test for missing optional config
    mocked_app.config['B2ACCESS_CONSUMER_KEY'] = 'abcxyz'
    mocked_app.config['B2ACCESS_SECRET_KEY'] = 'xyzabc'
    load_features(mocked_app)
    assert mocked_app.config['OAUTHCLIENT_REMOTE_APPS'].get('b2access').get('registration_url') == 'https://b2access.eudat.eu/'

    # Test for b2access integration

    mocked_app.config['USE_STAGING_B2ACCESS'] = True
    load_features(mocked_app)
    assert mocked_app.config['OAUTHCLIENT_REMOTE_APPS'].get('b2access').get('registration_url') == 'https://b2access-integration.fz-juelich.de'

def test_feature_cscaai(mocked_app):
    mocked_app.config = {}
    load_features(mocked_app)
    assert mocked_app.config['OAUTHCLIENT_REMOTE_APPS'] == {}


    # Test for missing required config
    mocked_app.config['CONFIG_ENABLE_CSCAAI'] = True
    with pytest.raises(Exception):
        load_features(mocked_app)

    # Test for missing optional config
    mocked_app.config['CSCAAI_CONSUMER_KEY'] = 'abcxyz'
    mocked_app.config['CSCAAI_SECRET_KEY'] = 'xyzabc'
    mocked_app.config['CSCAAI_ALLOWED_ORGANIZATIONS'] = ['csc']
    load_features(mocked_app)
    assert mocked_app.config['OAUTHCLIENT_REMOTE_APPS'].get('cscaai').get('registration_url') == 'https://user-auth.csc.fi/LoginHaka'

    # Test for cscaai test

    mocked_app.config['USE_STAGING_CSCAAI'] = True
    load_features(mocked_app)
    assert mocked_app.config['OAUTHCLIENT_REMOTE_APPS'].get('cscaai').get('registration_url') == 'https://test-user-auth.csc.fi/LoginHaka'
