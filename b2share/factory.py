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

"""Application factory creating the B2SHARE application.

This module is the starting point of a B2SHARE service.

The real B2SHARE application is the HTTP REST API application created by
:py:func:`~.create_api`. However the UI files (ReactJS) also need to be served
to the users' browser.
It would be better to serve it via NGINX but up to now we chose to serve it
via another top Flask application. The requests are dispatched between this
UI application and the REST API application depending on the request URL. Any
request whose endpoint starts with ``/api`` will be redirected to the REST API
application.

.. graphviz::

    digraph G {
    rankdir=TB;

    web [
        label="WEB",
        width=3,
        height=1.5,
        fixedsize=true,
        shape=rectangle
        color=grey,
        style=filled,
    ];
    web -> dispatcher [label="request"];

    subgraph cluster_invenio_stats {
        rank=same;
        fontsize = 20;
        label = "B2SHARE";
        style = "solid";

        dispatcher [label="DispatcherMiddleware", shape="parallelogram"]
        app [label="Top Flask\\napplication", shape="Mcircle"];
        rest_app [label="REST API\\nApplication", shape="Mcircle"]
        ui_files [label="UI Files", shape="folder"]
        communities_views [label="b2share.modules.communities.views", shape="rectangle"]
        schemas_views [label="b2share.modules.schemas.views", shape="rectangle"]
        other_views [label="...", shape="rectangle"]
    }
    dispatcher -> app [label="endpoint != '/api/*'"];
    app -> ui_files [label="serves"];
    dispatcher -> rest_app [label="endpoint == '/api/*'"];
    rest_app -> communities_views [label="endpoint in\\n['/api/communities/*', ...]"]
    rest_app -> schemas_views [label="endpoint in\\n['/api/communities/<ID>/schemas/*', ...]"]
    rest_app -> other_views [label="endpoint == '...'"]
    }

See Invenio and invenio_base module for more information regarding how Invenio
applications are created. The *"UI Application"* in our case is a custom
one, it does not match *"Invenio UI application"* which serves default
Invenio UI.

The ``*\*.views*`` are the ``views.py`` modules included in modules which
contain the REST API definition. The requests are dispatched to the right
view class using the Flask endpoints matching rules.

**TODO**: Note that Invenio has evolved since :py:func:`~.create_app` was
created. It will be necessary at some point to refactor it.
"""

import os
import sys

from flask import Flask
from invenio_base.app import create_app_factory
from invenio_config import create_conf_loader
from werkzeug.wsgi import DispatcherMiddleware
from werkzeug.contrib.fixers import ProxyFix

from . import config

env_prefix = 'B2SHARE'

try:
    from b2share.admin import b2share_config_loader
    config_loader=b2share_config_loader
except (ModuleNotFoundError,ImportError):
    # Error handling
    config_loader = create_conf_loader(config=config, env_prefix=env_prefix)
    pass

instance_path = os.getenv(env_prefix + '_INSTANCE_PATH') or \
    os.path.join(sys.prefix, 'var', 'b2share-instance')
"""Instance path for B2Share."""


def create_api(*args, **kwargs):
    """Create Flask application providing B2SHARE REST API."""
    app = create_app_factory(
        'b2share',
        config_loader=config_loader,
        extension_entry_points=['invenio_base.api_apps'],
        blueprint_entry_points=['invenio_base.api_blueprints'],
        converter_entry_points=['invenio_base.api_converters'],
        instance_path=instance_path,
    )(*args, **kwargs)
    return app


def create_app(**kwargs):
    """Create Flask application providing B2SHARE UI and REST API.abs

    The REST API is provided by redirecting any request to another Flask
    application created with :func:`~.create_api`.
    """
    # Create the REST API Flask application
    api = create_api(**kwargs)
    api.config.update(
        APPLICATION_ROOT='/api'
    )
    app_ui = Flask(__name__,
                   static_folder=os.environ.get(
                       'B2SHARE_UI_PATH',
                       os.path.join(api.instance_path, 'static')),
                   static_url_path='',
                   instance_path=api.instance_path)

    add_routes(app_ui)

    api.wsgi_app = DispatcherMiddleware(app_ui.wsgi_app, {
        '/api': api.wsgi_app
    })
    if api.config.get('WSGI_PROXIES'):
        wsgi_proxies = api.config.get('WSGI_PROXIES')
        assert(wsgi_proxies > 0)
        api.wsgi_app = ProxyFix(api.wsgi_app,
                                num_proxies=api.config['WSGI_PROXIES'])

    check_configuration(api.config, api.logger)

    return api


def add_routes(app_ui):
    @app_ui.route('/')
    def root():
        return app_ui.send_static_file('index.html')

    @app_ui.route('/help', defaults={'path': ''})
    @app_ui.route('/help/', defaults={'path': ''})
    @app_ui.route('/help/<path:path>')
    def serve_help(path):
        return app_ui.send_static_file('index.html')

    @app_ui.route('/communities', defaults={'path': ''})
    @app_ui.route('/communities/', defaults={'path': ''})
    @app_ui.route('/communities/<path:path>')
    def serve_communities(path):
        return app_ui.send_static_file('index.html')

    @app_ui.route('/user', defaults={'path': ''})
    @app_ui.route('/user/', defaults={'path': ''})
    @app_ui.route('/user/<path:path>')
    def serve_user(path):
        return app_ui.send_static_file('index.html')

    @app_ui.route('/records', defaults={'path': ''})
    @app_ui.route('/records/', defaults={'path': ''})
    @app_ui.route('/records/<path:path>')
    def serve_records(path):
        return app_ui.send_static_file('index.html')

    @app_ui.route('/search', defaults={'path': ''})
    @app_ui.route('/search/', defaults={'path': ''})
    @app_ui.route('/search/<path:path>')
    def serve_search(path):
        return app_ui.send_static_file('index.html')


def check_configuration(config, logger):
    errors_found = False
    def error(msg):
        nonlocal errors_found
        errors_found = True
        logger.error(msg)

    def check(var_name):
        if not config.get(var_name):
            error("Configuration variable expected: {}".format(var_name))

    if not os.environ.get('B2SHARE_SECRET_KEY') and check('B2SHARE_SECRET_KEY'):
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
