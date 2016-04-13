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

"""B2Share demo command line interface."""

from __future__ import absolute_import, print_function

import os
from shutil import rmtree
import pathlib

import click
from flask_cli import with_appcontext
from flask import current_app
from invenio_db import db
from invenio_files_rest.models import Location

from .helpers import load_demo_data


@click.group(chain=True)
def demo():
    """Demonstration commands."""


@demo.command()
@with_appcontext
@click.option('-v', '--verbose', count=True)
def load(verbose):
    """Load demonstration data."""

    # add files location
    files_path = os.path.join(current_app.instance_path, 'files')
    if os.path.exists(files_path):
        rmtree(files_path)
    os.mkdir(files_path)
    with db.session.begin_nested():
        db.session.add(Location(name='local',
                                uri=pathlib.Path(files_path).as_uri(),
                                default=True))
        # load the demo
        load_demo_data(
            os.path.join(os.path.dirname(os.path.realpath(__file__)),
                         'data'),
            verbose=verbose)
    db.session.commit()
