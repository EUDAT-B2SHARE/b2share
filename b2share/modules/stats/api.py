# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2016 University of Tuebingen, CERN
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

"""Statistics methods for API."""

import os, shutil

from flask import current_app

from invenio_files_rest.models import Location
from invenio_accounts.models import User

def get_quota():
    total_quota = 0
    if Location:
        print(Location.all())
        for l in Location.all():
            path_parsed = None
            if '://' in l.uri:
                path_parsed = l.uri.split('://')[1]
            else:
                path_parsed = l.uri
            if path_parsed:
                path = os.path.realpath(path_parsed)
                total, used, free = shutil.disk_usage(path)
                total_quota += total
    current_app.logger.info("Stats-API: Collecting total quota -> {}".format(total_quota))
    return total_quota

def users_list():
    """List all known users"""
    userdata_query = User.query.order_by(User.id)
    userdata={u.id:{"email":u.email} for u in userdata_query}
    return userdata