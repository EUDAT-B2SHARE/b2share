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

"""B2SHARE specific configuration loader."""

from invenio_config import create_conf_loader as create_invenio_conf_loader

from b2share.modules.configloader.vaultloader import (
    load_vault_secrets, 
    load_vault_certificates
    )
from b2share.modules.configloader.features import load_features

def create_b2share_config_loader(config=None, env_prefix="B2SHARE"):

    def _b2share_config_loader(app, **kwargs_config):
        """B2SHARE specific configuration loader

        1. Loads config(s) as invenio_config would load them.
        2. Loads additional config from from Hashicorp Vault instance.
        3. Loads additional functionality defined by feature flags.
        """
        # Get instance of invenio config loader
        invenio_config_loader = create_invenio_conf_loader(
            config=config, 
            env_prefix=env_prefix
            )
        
        # Execute invenio config loader.
        # Load configuration from invenio_config.module entry point group.
        # Load configuration from config module if provided as argument.
        # Load configuration from the instance folder: 
        # <app.instance_path>/<app.name>.cfg.
        # Load configuration keyword arguments provided.
        # Load configuration from environment variables with
        # the prefix env_prefix.
        invenio_config_loader(app, **kwargs_config)

        ## TODO: Update README.md

        # Configure Flask default loggers for specified log level.
        # Handlers need to configured as well.
        # Invenio-Logging has not loaded its handlers yet, 
        # so we need to override Flask default handlers.
        app.logger.setLevel(app.config.get('LOGGING_LEVEL'))
        for h in app.logger.handlers:
            h.setLevel(app.config.get('LOGGING_LEVEL'))

        if app.config.get('CONFIG_USE_VAULT_AGENT'):
            app.logger.info("Loading secrets.")
            load_vault_secrets(app, env_prefix="B2SHARE")

            app.logger.info("Loading certificates.")
            load_vault_certificates(app)

        app.logger.info("Loading feature configuration.")
        load_features(app)

    return _b2share_config_loader
