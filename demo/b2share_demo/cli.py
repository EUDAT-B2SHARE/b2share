# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2016 CERN.
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

"""B2Share demo command line interface."""

from __future__ import absolute_import, print_function

import click

from flask_cli import with_appcontext
from invenio_db import db


@click.group(chain=True)
def demo():
    """Demonstration commands."""


@demo.command()
@with_appcontext
@click.option('-v', '--verbose', is_flag=True, default=False)
def load(verbose):
    """Load demonstration data."""
    _create_records()


def _create_records():
    """Create demo records."""
    import uuid
    from invenio_records.api import Record
    from invenio_pidstore.models import PersistentIdentifier, PIDStatus

    click.secho('Creating records', fg='yellow', bold=True)
    # Record 1 - Live record
    with db.session.begin_nested():
        rec_uuid = uuid.uuid4()
        PersistentIdentifier.create(
            'recid', '1', object_type='rec', object_uuid=rec_uuid,
            status=PIDStatus.REGISTERED)
        Record.create({'title': 'Registered '}, id_=rec_uuid)
    db.session.commit()
    click.secho('Created all records!', fg='green')
