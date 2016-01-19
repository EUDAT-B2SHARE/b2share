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

"""Pytest configuration."""

from __future__ import absolute_import, print_function

import os

import pytest
from flask import Flask
from flask_cli import FlaskCLI
from invenio_db import InvenioDB, db
from invenio_records import InvenioRecords
from invenio_records_rest import InvenioRecordsREST
from sqlalchemy_utils.functions import create_database, drop_database


@pytest.fixture(scope='function')
def app(request):
    """Flask application fixture."""
    app = Flask('testapp')
    app.config.update(
        TESTING=True,
        SERVER_NAME='localhost:5000',
        SQLALCHEMY_DATABASE_URI=os.environ.get(
            'SQLALCHEMY_DATABASE_URI', 'sqlite:///test.db'
        )
    )
    FlaskCLI(app)
    InvenioDB(app)
    InvenioRecords(app)
    InvenioRecordsREST(app)

    with app.app_context():
        if app.config['SQLALCHEMY_DATABASE_URI'] != 'sqlite://':
            create_database(db.engine.url)
        db.create_all()

    def finalize():
        with app.app_context():
            db.drop_all()
            if app.config['SQLALCHEMY_DATABASE_URI'] != 'sqlite://':
                drop_database(db.engine.url)

    request.addfinalizer(finalize)
    return app
