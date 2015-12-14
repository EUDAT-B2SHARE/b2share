# -*- coding: utf-8 -*-
# B2SHARE2

"""B2share schemas extension"""

from __future__ import absolute_import, print_function

from .restful import blueprint


class B2ShareSchemas(object):
    """B2Share Schemas extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
        app.extensions['b2share-schemas'] = self
        app.register_blueprint(blueprint)

    def init_config(self, app):
        """Initialize configuration."""
        pass
