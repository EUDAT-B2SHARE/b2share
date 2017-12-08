# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2017 CERN.
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

"""B2SHARE Handle API tests."""

from mock import patch
from flask import Flask

from b2share.modules.handle.proxies import current_handle
from b2handle.handleclient import EUDATHandleClient
from b2share.modules.handle.ext import B2ShareHandle
from unittest.mock import ANY


def test_b2handle_pid_creation():
    """Test the creatio of B2Handle PID."""
    app = Flask(__name__)
    app.config.update(dict(
        PID_HANDLE_CREDENTIALS=dict(prefix='myprefix')
    ))
    with app.app_context():
        with patch.object(EUDATHandleClient,
                          'generate_and_register_handle') as mock_register:
            B2ShareHandle(app)

            assert current_handle.handle_client is not None
            assert current_handle.handle_prefix == 'myprefix'

            current_handle.create_handle(
                location='mylocation', checksum='mychecksum', fixed=True
            )
            entries = {
                'EUDAT/FIXED_CONTENT': 'True',
                'EUDAT/PROFILE_VERSION': '1',
                'EUDAT/CHECKSUM_TIMESTAMP': ANY,
                'EUDAT/CHECKSUM': 'mychecksum'
            }
            mock_register.assert_called_with(
                location='mylocation', checksum='mychecksum',
                prefix='myprefix', **entries
            )
