# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Flask application factories for Invenio flavours."""

from __future__ import absolute_import, print_function

import os
import sys

import pkg_resources

from flask import current_app

from invenio_base.app import create_app_factory
from invenio_base.wsgi import create_wsgi_factory, wsgi_proxyfix
from invenio_base.signals import app_created, app_loaded
from invenio_cache import BytecodeCache
from invenio_config import create_config_loader

from jinja2 import ChoiceLoader, FileSystemLoader

from . import config

env_prefix = 'B2SHARE'

invenio_config_loader = create_config_loader(
    config=config, env_prefix=env_prefix
)

@app_created.connect
def receiver_app_created(sender, app=None, **kwargs):
    app.logger.debug("Application created")

@app_loaded.connect
def receiver_app_loaded(sender, app=None, **kwargs):
    app.logger.debug("Application Loaded")
    app.logger.debug("Instance Path: {}".format(app.instance_path))
    check_configuration(app.config, app.logger)

def instance_path():
    """Instance path for Invenio.

    Defaults to ``<env_prefix>_INSTANCE_PATH``
     or if environment variable is not set ``<sys.prefix>/var/instance``.
    """
    return os.getenv(env_prefix + '_INSTANCE_PATH') or \
        os.path.join(sys.prefix, 'var', 'instance')


def static_folder():
    """Static folder path.

    Defaults to ``<env_prefix>_STATIC_FOLDER``
    or if environment variable is not set ``<sys.prefix>/var/instance/static``.
    """
    return os.getenv(env_prefix + '_STATIC_FOLDER') or \
        os.path.join(instance_path(), 'static')


def static_url_path():
    """Static url path.

    Defaults to ``<env_prefix>_STATIC_URL_PATH``
    or if environment variable is not set ``/static``.
    """
    return os.getenv(env_prefix + '_STATIC_URL_PATH') or '/static'


def config_loader(app, **kwargs_config):
    """Configuration loader.

    Adds support for loading templates from the Flask application's instance
    folder (``<instance_folder>/templates``).
    """
    # This is the only place customize the Flask application right after
    # it has been created, but before all extensions etc are loaded.
    local_templates_path = os.path.join(app.instance_path, 'theme/templates')
    if os.path.exists(local_templates_path):
        # Let's customize the template loader to look into packages
        # and application templates folders.
        app.jinja_loader = ChoiceLoader([
            FileSystemLoader(local_templates_path),
            app.jinja_loader,
        ])

    app.jinja_options = dict(
        app.jinja_options,
        cache_size=1000,
        bytecode_cache=BytecodeCache(app)
    )

    invenio_config_loader(app, **kwargs_config)


class TrustedHostsMixin(object):
    """Mixin for reading trusted hosts from application config."""

    @property
    def trusted_hosts(self):
        """Get list of trusted hosts."""
        if current_app:
            return current_app.config.get('APP_ALLOWED_HOSTS', None)


def app_class():
    """Create Flask application class.

    Invenio-Files-REST needs to patch the Werkzeug form parsing in order to
    support streaming large file uploads. This is done by subclassing the Flask
    application class.
    """
    try:
        pkg_resources.get_distribution('invenio-files-rest')
        from invenio_files_rest.app import Flask as FlaskBase
    except pkg_resources.DistributionNotFound:
        from flask import Flask as FlaskBase

    # Add Host header validation via APP_ALLOWED_HOSTS configuration variable.
    class Request(TrustedHostsMixin, FlaskBase.request_class):
        pass

    class Flask(FlaskBase):
        request_class = Request

    return Flask


create_api = create_app_factory(
    'invenio',
    config_loader=config_loader,
    blueprint_entry_points=['invenio_base.api_blueprints'],
    extension_entry_points=['invenio_base.api_apps'],
    converter_entry_points=['invenio_base.api_converters'],
    wsgi_factory=wsgi_proxyfix(),
    instance_path=instance_path,
    app_class=app_class(),
)
"""Flask application factory for Invenio REST API."""

#create_ui = create_app_factory(
#    'invenio',
#    config_loader=config_loader,
#    blueprint_entry_points=['invenio_base.blueprints'],
#    extension_entry_points=['invenio_base.apps'],
#    converter_entry_points=['invenio_base.converters'],
#    wsgi_factory=wsgi_proxyfix(),
#    instance_path=instance_path,
#    static_folder=static_folder,
#    static_url_path=static_url_path(),
#    app_class=app_class(),
#)
#"""Flask application factory for Invenio UI."""

create_app = create_app_factory(
    'invenio',
    config_loader=config_loader,
    blueprint_entry_points=['invenio_base.blueprints'],
    extension_entry_points=['invenio_base.apps'],
    converter_entry_points=['invenio_base.converters'],
    wsgi_factory=wsgi_proxyfix(create_wsgi_factory({'/api': create_api})),
    instance_path=instance_path,
    static_folder=static_folder,
    static_url_path=static_url_path(),
    app_class=app_class(),
)
"""Flask application factory used for CLI, UI and API for combined UI + REST API.

REST API is mounted under ``/api``.
"""

def check_configuration(config, logger):
    errors_found = False
    def error(msg):
        nonlocal errors_found
        errors_found = True
        logger.error(msg)

    def check(var_name):
        if not config.get(var_name):
            error("Configuration variable expected: {}".format(var_name))

    if not os.environ.get('B2SHARE_SECRET_KEY', '*** SECRET_KEY ***'):
        error("Environment variable not defined: B2SHARE_SECRET_KEY")

    check('SQLALCHEMY_DATABASE_URI')
    check('JSONSCHEMAS_HOST')
    check('PREFERRED_URL_SCHEME')

    check('B2ACCESS_APP_CREDENTIALS')
    if not config['B2ACCESS_APP_CREDENTIALS'].get('consumer_key'):
        error("Environment variable not defined: B2ACCESS_CONSUMER_KEY")
    if not config['B2ACCESS_APP_CREDENTIALS'].get('consumer_secret'):
        error("Environment variable not defined: B2ACCESS_SECRET_KEY")

    site_function = config.get('SITE_FUNCTION')
    if site_function and site_function != 'demo':
        if config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite'):
            error("SQLALCHEMY_DATABASE_URI cannot use sqlite database for a non-demo instance")

        check('SUPPORT_EMAIL')

    if site_function and site_function == 'production':
        if config['MAIL_SUPPRESS_SEND']:
            error("MAIL_SUPPRESS_SEND must be set to False for a production instance")

        if config.get('FAKE_EPIC_PID'):
            error("FAKE_EPIC_PID must be set to False for a production instance")

        if config.get('FAKE_DOI'):
            error("FAKE_DOI must be set to False for a production instance")

        if not (config.get('PID_HANDLE_CREDENTIALS') or
                (config.get('CFG_EPIC_USERNAME') and config.get('CFG_EPIC_PASSWORD') and
                 config.get('CFG_EPIC_BASEURL') and config.get('CFG_EPIC_PREFIX'))):
            logger.warning("Configuration variables for PID allocation are missing")

        if not (config['PIDSTORE_DATACITE_DOI_PREFIX'] and
                config['PIDSTORE_DATACITE_USERNAME'] and
                config['PIDSTORE_DATACITE_PASSWORD']):
            logger.warning("Configuration variables for DOI allocation are missing")

    if errors_found:
        print("Configuration errors found, exiting")
        sys.exit(1)
