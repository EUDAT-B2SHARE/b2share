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

"""B2share ownership extension"""

from __future__ import absolute_import, print_function

from werkzeug.utils import cached_property

from .views import blueprint

from .cli import ownership as ownership_cmd


class _B2ShareOwnership(object):
    """B2Share users extension state."""

    def __init__(self, app):
        """Constructor.

        Args:
            app: the Flask application.
        """
        self.app = app


class B2ShareOwnership(object):
    """B2Share Ownership extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
        app.cli.add_command(ownership_cmd)
        app.extensions['b2share-ownership'] = _B2ShareOwnership(app)
        app.register_blueprint(blueprint)

    def init_config(self, app):
        pass
