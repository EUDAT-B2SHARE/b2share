# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.

import os
import sys

from flask import Flask
from invenio_base.app import create_app_factory
from invenio_config import create_conf_loader
from werkzeug.wsgi import DispatcherMiddleware

from . import config

env_prefix = 'B2SHARE'

config_loader = create_conf_loader(config=config, env_prefix=env_prefix)

instance_path = os.getenv(env_prefix + '_INSTANCE_PATH') or \
    os.path.join(sys.prefix, 'var', 'b2share-instance')
"""Instance path for B2Share."""

create_api = create_app_factory(
    'b2share',
    config_loader=config_loader,
    extension_entry_points=['invenio_base.api_apps'],
    instance_path=instance_path,
)


def create_app(**kwargs):
    api = create_api(**kwargs)
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
