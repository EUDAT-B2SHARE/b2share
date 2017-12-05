# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2017 CERN, University of Tübingen.
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

"""B2SHARE's Handle module extension"""

from __future__ import absolute_import, print_function

from b2handle.handleclient import EUDATHandleClient
from flask import current_app

from .api import create_handle


class _B2ShareHandleState(object):
    """B2Share Handle extension.

    An instance of this class is accessible via
    :py:func:`b2share.modules.handle.proxies.current_handle` or
    `current_app.extensions['b2share-handle']`.
    """

    def __init__(self, credentials=None):
        """Constructor.

        :param credentials: B2Handle credentials.
        """
        self.credentials = credentials
        self.handle_prefix = None
        self.handle_client = None
        if credentials:
            self.handle_prefix = credentials.get('prefix')
            self.handle_client = EUDATHandleClient(**credentials)
        # otherwise assume EPIC API
        # TODO: load EPIC config variables

    def create_handle(self, location, checksum=None, fixed=False,
                      fake=None):
        """Create a new handle for a file, using the B2HANDLE library."""
        if fake is None:
            fake = current_app.config.get('TESTING', False) \
                or current_app.config.get('FAKE_EPIC_PID', False)
        create_handle(self.handle_client, self.handle_prefix,
                      location, checksum, fixed, fake=fake)

    def check_eudat_entries_in_handle_pid(self, update, verbose):
        """Checks and update the mandatory EUDAT entries in a Handle PID."""
        check_eudat_entries_in_handle_pid(self.handle_client,
                                          self.handle_prefix, update)


class B2ShareHandle(object):
    """B2Share Handle extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
        app.extensions['b2share-handle'] = _B2ShareHandleState(
            app.config.get('PID_HANDLE_CREDENTIALS')
        )

    def init_config(self, app):
        """Initialize configuration."""
        pass
