# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2016 University of Tuebingen, CERN.
# Copyright (C) 2015 University of Tuebingen.
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

"""B2share communities extension"""

from __future__ import absolute_import, print_function

from werkzeug.utils import cached_property

from . import config
from .views import blueprint

from .cli import communities as communities_cmd


class _B2ShareCommunitiesState(object):
    """B2Share communities extension state."""

    def __init__(self, app):
        """Constructor.

        Args:
            app: the Flask application.
        """
        self.app = app
        self._rest_access_control_disabled = None

    @cached_property
    def rest_access_control_disabled(self):
        """Load the REST API access control disabling flag from app config.

        Returns:
            bool: True if B2SHARE_COMMUNITIES_REST_ACCESS_CONTROL_DISABLED is
                set to True in the application configuration, else False.
        """
        if self._rest_access_control_disabled is None:
            self._rest_access_control_disabled = self.app.config.get(
                'B2SHARE_COMMUNITIES_REST_ACCESS_CONTROL_DISABLED')
        return (self._rest_access_control_disabled if
                self._rest_access_control_disabled is not None else False)


class B2ShareCommunities(object):
    """B2Share Communities extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
        app.register_blueprint(blueprint)
        app.cli.add_command(communities_cmd)
        app.extensions['b2share-communities'] = _B2ShareCommunitiesState(app)

    def init_config(self, app):
        """Initialize configuration."""
        for k in dir(config):
            if k.startswith('B2SHARE_COMMUNITIES_'):
                app.config.setdefault(k, getattr(config, k))
