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

"""B2Share cli commands for upgrades."""


from __future__ import absolute_import, print_function

import click
from flask.cli import with_appcontext
from flask import current_app

from .api import upgrade_to_last_version

@click.group()
def upgrade():
    """B2SHARE upgrade commands."""


@upgrade.command()
@with_appcontext
@click.option('-v', '--verbose', is_flag=True, default=False)
def run(verbose):
    """Upgrade the database to the last version and reindex the records."""
    upgrade_to_last_version(verbose)
