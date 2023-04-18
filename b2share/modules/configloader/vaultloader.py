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

"""B2SHARE specific secrets loader."""

import json
import requests

from .utils import _check_config_exists

BASE_PATH = '/v1/secret/data/b2share/'
APP_SECRETS_PATH = '/application'
CERTIFICATES_PATH = '/certificates'


def _load_from_vault(
    app, 
    secrets=False, 
    certificates=False, 
    env_prefix="B2SHARE"
    ):
    
    vaultloader_required_conf_vars = [
        'CONFIG_VAULT_ENTITY',
        'CONFIG_VAULT_AGENT_ADDR'
    ]

    vaultloader_optional_conf_vars = [
        'CONFIG_OUTPUT_SECRETS'
    ]

    if not _check_config_exists(
        app,
        vaultloader_required_conf_vars,
        vaultloader_optional_conf_vars
        ):
        raise Exception('Required config vars not provided')

    # Vault always responds with permission denied error.
    # E.g. if value of CONFIG_VAULT_ENTITY is configured
    # wrong Vault will return just permission denied error.
    CONFIG_VAULT_ENTITY = app.config.get('CONFIG_VAULT_ENTITY', 'dev')
    CONFIG_VAULT_AGENT_ADDR = app.config.get('CONFIG_VAULT_AGENT_ADDR', '')
    
    r = None

    try:
        if secrets:
            vault_url = (
                CONFIG_VAULT_AGENT_ADDR + 
                BASE_PATH + 
                CONFIG_VAULT_ENTITY + 
                APP_SECRETS_PATH
                )
            r = requests.get(vault_url)
            r.raise_for_status()
            # Request secrets
            secrets = r.json()['data']['data']
            for key in secrets.keys():
                if secrets[key] in ("", [], None):
                    app.logger.warning(f"{key} has an empty value")
                # Require that all keys have the env_prefix.
                # if not varname.startswith(env_prefix):
                #     continue
                else:
                    if app.config.get("CONFIG_OUTPUT_SECRETS"):
                        if app.config.get('LOGGING_LEVEL') != 'DEBUG':
                            app.logger.warning(
                                "Secrets will be outputted only " +
                                "with logging level DEBUG.")
                        else:
                            app.logger.debug("Loading {} with value {}".format(
                                key[len(env_prefix)+1:], secrets[key]))
                    # PID_HANDLE_CREDENTIALS is json. needs special handling
                    # 'key[len(env_prefix):]' removes 'env_prefix'
                    # e.g. B2SHARE_LOGGING_LEVEL -> LOGGING_LEVEL
                    if key == env_prefix + "_" + "PID_HANDLE_CREDENTIALS":
                        tmp_dict = {
                            key[len(env_prefix)+1:] : secrets[key]
                            }
                    else:
                        tmp_dict = {key[len(env_prefix)+1:] : secrets[key]}

                    # Update app config with secret
                    app.config.update(tmp_dict)

        elif certificates:
            # Request certificates
            vault_url = (
                CONFIG_VAULT_AGENT_ADDR + 
                BASE_PATH + 
                CONFIG_VAULT_ENTITY + 
                CERTIFICATES_PATH
                )
            r = requests.get(vault_url)
            r.raise_for_status()
            certs = r.json()['data']['data']
            certs = json.dumps(r.json()['data']['data'], indent = 2)
            certs_dict = json.loads(certs)
            if certs_dict is not None:
                for var, val in certs_dict.items():
                    with open(f'{app.instance_path}/{var}', 'w') as out_file:
                        out_file.write(f"{val}")

        else:
            # Nothing to load
            pass
    except requests.exceptions.HTTPError as ex:
        app.logger.warning(f'HTTP Exception: {ex}')
    except Exception as e:
        # TODO: Add specific Exception(s) and not catch all.
        app.logger.warning("Secrets loading failed.")
        app.logger.error(e, exc_info=True)
        raise Exception(f'Something went wrong: {e}')


def load_vault_secrets(app, env_prefix="B2SHARE"):
    """Load secrets and add them to app.config ."""
    
    _load_from_vault(app, secrets=True, env_prefix="B2SHARE")
    

def load_vault_certificates(app):
    """Load certificates and add them app instance folder"""

    _load_from_vault(app, certificates=True, env_prefix="B2SHARE")

