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
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""B2share records extension"""

from __future__ import absolute_import, print_function

from invenio_records_rest.utils import PIDConverter

from .triggers import register_triggers
from .errors import register_error_handlers
from .views import create_blueprint
from .handle import init_handle_client


class B2ShareRecords(object):
    """B2Share Records extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
        app.extensions['b2share-records'] = self
        register_triggers(app)
        register_error_handlers(app)
        # Register records API blueprints
        app.register_blueprint(
            create_blueprint(app.config['B2SHARE_RECORDS_REST_ENDPOINTS'])
        )
        init_handle_client(app)
        app.url_map.converters['pid'] = PIDConverter

    def init_config(self, app):
        """Initialize configuration."""
        pass
