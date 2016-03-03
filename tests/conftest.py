# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2016 University of Tuebingen, CERN.
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

"""Pytest configuration."""

from __future__ import absolute_import, print_function

import os
import re
from collections import namedtuple
from contextlib import contextmanager

import pytest
import responses
from flask import Flask
from flask_cli import FlaskCLI
from flask_security import url_for_security
from flask_security.utils import encrypt_password
from invenio_access import InvenioAccess
from invenio_accounts import InvenioAccounts
from invenio_db import InvenioDB, db
from invenio_records import InvenioRecords
from invenio_records_rest import InvenioRecordsREST
from invenio_rest import InvenioREST
from invenio_search import InvenioSearch
from sqlalchemy_utils.functions import create_database, drop_database


@pytest.fixture(scope='function')
def app(request):
    """Flask application fixture."""
    app = Flask('testapp')
    app.config.update(
        # DEBUG=True,
        TESTING=True,
        SERVER_NAME='localhost:5000',
        SQLALCHEMY_DATABASE_URI=os.environ.get(
            'SQLALCHEMY_DATABASE_URI', 'sqlite:///test.db'
        ),
        SECRET_KEY="CHANGE_ME",
        SECURITY_PASSWORD_SALT='CHANGEME',
        # this is only for tests
        LOGIN_DISABLED=False,
        WTF_CSRF_ENABLED=False,
    )
    FlaskCLI(app)
    InvenioDB(app)
    InvenioRecords(app)
    InvenioAccounts(app)
    InvenioAccess(app)
    InvenioREST(app)
    InvenioRecordsREST(app)
    InvenioSearch(app)

    # register additional extensions provided by the test
    if hasattr(request, 'param') and 'extensions' in request.param:
        for ext in request.param['extensions']:
            ext(app)

    # update the application with the configuration provided by the test
    if hasattr(request, 'param') and 'config' in request.param:
        app.config.update(**request.param['config'])

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


UserInfo = namedtuple('UserInfo', ['id', 'email', 'password'])


@pytest.fixture(scope='function')
def create_user(app):
    """Create a user."""

    users_password = '123456'
    accounts = app.extensions['invenio-accounts']

    def create(name):
        email = '{}@example.org'.format(name)
        with db.session.begin_nested():
            user = accounts.datastore.create_user(
                email=email,
                password=encrypt_password(users_password),
                active=True,
            )
            db.session.add(user)
        return UserInfo(email=email, password=users_password, id=user.id)

    return create


@pytest.fixture(scope='function')
def login_user(app):
    """Login a user."""

    with app.test_request_context():
        login_url = url_for_security('login')

    def login(user_info, client):
        res = client.post(login_url, data={
            'email': user_info.email, 'password': user_info.password})
        assert res.status_code == 302
    return login


@pytest.yield_fixture
def flask_http_responses(app):
    """Routes HTTP requests to the given flask application.

    The routing is done only when the requested URL matches the application
    endpoints.

    Args:
        app: the flask application.

    Returns:
        function: a context manager enabling the HTTP requests routing.
    """
    @contextmanager
    def router():
        """Context manager used to enable the routing."""
        def router_callback(request):
            with app.test_client() as client:
                headers = [(key, value) for key, value in
                           request.headers.items()]
                res = getattr(client, request.method.lower())(
                    request.url,
                    data=request.body,
                    headers=headers)
                return (res.status, res.headers, res.get_data())
        with responses.RequestsMock(assert_all_requests_are_fired=False) \
                as rsps:
            for rule in app.url_map.iter_rules():
                url_regexp = re.compile('http://' +
                                        app.config.get('SERVER_NAME') +
                                        re.sub(r'<[^>]+>', '\S+', rule.rule))
                for method in rule.methods:
                    rsps.add_callback(method, url_regexp,
                                        callback=router_callback)
            yield
    yield router
