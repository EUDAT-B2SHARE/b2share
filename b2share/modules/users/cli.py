# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2017 University of Tübingen, CERN
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

"""B2Share cli commands for records."""


from __future__ import absolute_import, print_function

import click
from flask.cli import with_appcontext
import requests

from invenio_accounts.cli import users
from invenio_accounts.models import User

@users.command('list')
@with_appcontext
def users_list():
    """List all known users"""

    userdata = User.query.order_by(User.id)

    click.secho("ID\tACTIVE\tEMAIL\t\t\t\t\tROLES")
    for u in userdata:
        click.secho("%s\t%s\t%s\t\t\t%s" % (
            u.id,
            u.active,
            u.email,
            u.roles if len(u.roles) else 'None'
        ))
