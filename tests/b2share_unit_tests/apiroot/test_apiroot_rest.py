# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2016, University of Tuebingen.
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

"""Test B2Share apiroot module."""

import json

from flask import url_for
from b2share import __version__


def test_info_get(app):
    headers = [('Content-Type', 'application/json'),
               ('Accept', 'application/json')]

    def get_info():
        req = client.get(url_for('b2share_apiroot.info'), headers=headers)
        assert req.status_code == 200
        return json.loads(req.get_data(as_text=True))

    with app.app_context():
        with app.test_client() as client:
            info = get_info()
            assert info['site_function'] == app.config.get("SITE_FUNCTION")
            assert info['training_site_link'] == app.config.get("TRAINING_SITE_LINK")
            assert info['version'] == __version__
