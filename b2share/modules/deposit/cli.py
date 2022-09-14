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

"""B2Share cli commands for deposits."""


from __future__ import absolute_import, print_function

import click
from flask.cli import with_appcontext
from flask import current_app
import requests

from invenio_db import db
from invenio_deposit.cli import deposit

from b2share.modules.deposit.utils import delete_deposit


@deposit.command('delete')
@with_appcontext
@click.argument('deposit-pid', required=True, type=str)
def delete(deposit_pid):
    """ Delete unpublished deposit given the deposit id.

    :params deposit-pid: deposit id
    """
    try:
        delete_deposit(deposit_pid)
        db.session.commit()
        click.secho("deposit <{}> deleted from db".format(deposit_pid))
    except:
        raise click.ClickException("It is not possible to delete deposit_pid: {}".format(deposit_pid))

   
        