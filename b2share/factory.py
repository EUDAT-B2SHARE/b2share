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

"""Application factory creating the b2share application."""

import os
import sys

from flask import Flask
from invenio_base.app import create_app_factory
from invenio_config import create_conf_loader
from werkzeug.wsgi import DispatcherMiddleware
from werkzeug.contrib.fixers import ProxyFix

from . import config

env_prefix = 'B2SHARE'

config_loader = create_conf_loader(config=config, env_prefix=env_prefix)

instance_path = os.getenv(env_prefix + '_INSTANCE_PATH') or \
    os.path.join(sys.prefix, 'var', 'b2share-instance')
"""Instance path for B2Share."""


def create_api(*args, **kwargs):
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
