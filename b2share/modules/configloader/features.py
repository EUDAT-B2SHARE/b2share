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

"""B2SHARE specific features loader."""

from .utils import _check_config_exists

def load_features(app):

    # Process feature flags

    ## Setup OAuthclient(s) configuration
    
    oauthclients = dict()

    ## Load B2ACCESS
    if app.config.get("CONFIG_ENABLE_B2ACCESS"):
        app.logger.info("Loading B2ACCESS...")
        try:
            from b2share.modules.oauthclient.b2access import make_b2access_remote_app
        except (ModuleNotFoundError, ImportError) as e:
            raise e
        
        b2access_required_conf_vars = [
            'B2ACCESS_CONSUMER_KEY',
            'B2ACCESS_SECRET_KEY'
            ]

        b2access_optional_conf_vars = [
            'USE_STAGING_B2ACCESS'
            ]

        if not _check_config_exists(
            app, 
            b2access_required_conf_vars, 
            b2access_optional_conf_vars
            ):
            raise Exception(f'Required config vars not provided: {b2access_required_conf_vars}')

        B2ACCESS_BASE_URL = 'https://b2access.eudat.eu/'
        
        if app.config.get("USE_STAGING_B2ACCESS"):
            B2ACCESS_BASE_URL = 'https://b2access-integration.fz-juelich.de'

        B2ACCESS_APP_CREDENTIALS = dict(
            consumer_key=app.config.get("B2ACCESS_CONSUMER_KEY"),
            consumer_secret=app.config.get("B2ACCESS_SECRET_KEY"),
        )
        app.config.update(
            {"B2ACCESS_APP_CREDENTIALS" : B2ACCESS_APP_CREDENTIALS}
            )

        oauthclients['b2access'] = make_b2access_remote_app(B2ACCESS_BASE_URL)

    else:
        app.logger.info("B2ACCESS is not loaded.")

    ## Load CSCAAI
    if app.config.get("CONFIG_ENABLE_CSCAAI"):
        app.logger.info("Loading CSCAAI...")
        try:
            from b2share.modules.oauthclient.cscaai import make_cscaai_remote_app
        except (ModuleNotFoundError, ImportError) as e:
            raise e

        cscaai_required_conf_vars = [
            'CSCAAI_CONSUMER_KEY',
            'CSCAAI_SECRET_KEY',
            'CSCAAI_ALLOWED_ORGANIZATIONS'
            ]

        cscaai_optional_conf_vars = [
            'USE_STAGING_CSCAAI'
            ]

        if not _check_config_exists(
            app, 
            cscaai_required_conf_vars, 
            cscaai_optional_conf_vars
            ):
            raise Exception(f'Required config vars not provided: {cscaai_required_conf_vars}')

        CSCAAI_BASE_URL = 'https://user-auth.csc.fi/LoginHaka'

        if app.config.get("USE_STAGING_CSCAAI"):
            CSCAAI_BASE_URL = 'https://test-user-auth.csc.fi/LoginHaka'

        CSCAAI_APP_CREDENTIALS = dict(
            consumer_key=app.config.get("CSCAAI_CONSUMER_KEY"),
            consumer_secret=app.config.get("CSCAAI_SECRET_KEY"),
        )
        app.config.update({"CSCAAI_APP_CREDENTIALS" : CSCAAI_APP_CREDENTIALS})

        oauthclients['cscaai'] = make_cscaai_remote_app(CSCAAI_BASE_URL)

    else:
        app.logger.info("CSCAAI is not loaded.")

    app.config.update(dict(
        OAUTHCLIENT_REMOTE_APPS = oauthclients
    ))
