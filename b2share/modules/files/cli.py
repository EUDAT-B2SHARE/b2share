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
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""B2Share Schemas module Command Line Interface."""

from __future__ import absolute_import

import json
import os
import sys

from sqlalchemy import exists, or_
import click
from flask.cli import with_appcontext
from invenio_db import db
from invenio_files_rest.models import Location


@click.group()
def files():
    """Files management commands."""

@files.command('add-location')
@with_appcontext
@click.argument('name')
@click.argument('uri')
@click.option('-d', '--default', is_flag=True, default=False,
              help='Use this location as the default location.')
def add_location(name, uri, default):
    """Add a file storage location.

    The URI should point to the location where the files will be stored. The
    NAME will be used to reference this location.
    """
    matching_locations = Location.query.filter(
        or_(Location.uri == uri, Location.name == name)).all()
    if len(matching_locations) > 0:
        if matching_locations[0].name == name:
            raise click.BadParameter(
                'Another location with the same name already exists.')
        else:
            raise click.BadParameter(
                'Existing location "{}" has the same uri.'.format(
                    matching_locations[0].name))
    if default:
        db.session.query(Location).filter(Location.default == True).update(
            {Location.default: False})
    location = Location(name=name, uri=uri, default=default)
    db.session.add(location)
    db.session.commit()


@files.command('set-default-location')
@with_appcontext
@click.argument('name')
def set_default_location(name):
    """Change the default file storage location.

    The NAME should point to an existing location.
    """
    location = Location.query.filter(Location.name == name).one()
    if location.default:
        return
    db.session.query(Location).filter(Location.default == True).update(
        {Location.default: False})
    location.default = True
    db.session.commit()


@files.command('list-locations')
@with_appcontext
def list_location():
    """List all file storage locations."""
    locations = Location.query.order_by(Location.default.desc(),
                                        Location.name).all()
    for location in locations:
        click.echo(json.dumps({c.name: str(getattr(location, c.name)) for c in
                    Location.__table__.columns}, sort_keys=True))
