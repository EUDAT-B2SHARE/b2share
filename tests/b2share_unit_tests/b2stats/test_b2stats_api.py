# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2023 CSC - IT Center for Science Ltd.
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

"""Test B2Share Statistics Collection Endpoint."""

from flask import url_for    


def test_b2share_stats_permissions(app, login_user, test_users):
    """Test B2shareStatistics API collection point authorization."""

    with app.app_context():
        b2stats_url = url_for('b2share_statistics.b2share_statistics')

        def test_access(status, user=None):
            with app.test_client() as client:
                if user is not None:
                    login_user(user, client)
                # try accessing the record
                request_res = client.get(b2stats_url, query_string="query=quota", data="{}")
                print(request_res)
                assert request_res.status_code == status
        
        user = test_users['normal']
        admin = test_users['admin']
        
        test_access(403)  # anonymous user
        test_access(403,user) 
        test_access(200,admin) 
