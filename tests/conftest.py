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
import shutil
import re
import tempfile
import sys
from collections import namedtuple
from contextlib import contextmanager

import pytest
import responses
from b2share.modules.schemas.helpers import load_root_schemas
from flask import Flask
from flask_cli import FlaskCLI
from flask_security import url_for_security
from flask_security.utils import encrypt_password
from invenio_access import InvenioAccess
from invenio_accounts import InvenioAccounts
from invenio_db import InvenioDB, db
from invenio_files_rest.models import Location
from invenio_records import InvenioRecords
from invenio_records_rest import InvenioRecordsREST
from invenio_rest import InvenioREST
from invenio_search import InvenioSearch, current_search_client
from invenio_pidstore import InvenioPIDStore
from invenio_files_rest import InvenioFilesREST
from sqlalchemy_utils.functions import create_database, drop_database
from werkzeug.wsgi import DispatcherMiddleware

from b2share.config import B2SHARE_RECORDS_REST_ENDPOINTS, \
    B2SHARE_DEPOSIT_REST_ENDPOINTS

# add the demo module in sys.path
sys.path.append(
    os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
                 'demo'))
# add tests to the sys path
sys.path.append(os.path.dirname(__file__))

@pytest.fixture(scope='function')
def app(request, tmpdir):
    """Flask application fixture."""
    from b2share.factory import create_app, create_api

    instance_path = tmpdir.mkdir('instance_dir').strpath
    os.environ.update(
        B2SHARE_INSTANCE_PATH=os.environ.get(
            'INSTANCE_PATH', instance_path),
    )
    app = create_api(
        TESTING=True,
        SERVER_NAME='localhost:5000',
        DEBUG_TB_ENABLED=False,
        SQLALCHEMY_DATABASE_URI=os.environ.get(
            'SQLALCHEMY_DATABASE_URI', 'sqlite:///test.db'),
        LOGIN_DISABLED=False,
        WTF_CSRF_ENABLED=False,
        SECRET_KEY="CHANGE_ME",
        SECURITY_PASSWORD_SALT='CHANGEME',
    )

    # update the application with the configuration provided by the test
    if hasattr(request, 'param') and 'config' in request.param:
        app.config.update(**request.param['config'])

    with app.app_context():
        if app.config['SQLALCHEMY_DATABASE_URI'] != 'sqlite://':
            create_database(db.engine.url)
        db.create_all()
        es_indexes = [
            B2SHARE_RECORDS_REST_ENDPOINTS['b2share_record']['search_index'],
            B2SHARE_DEPOSIT_REST_ENDPOINTS['b2share_deposit']['search_index'],
        ]
        for es_index in es_indexes:
            if current_search_client.indices.exists(es_index):
                current_search_client.indices.delete(es_index)
                current_search_client.indices.create(es_index)

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


@pytest.fixture(scope='function')
def test_communities(app, tmp_location):
    """Load test communities."""
    from b2share_demo.helpers import load_demo_data

    with app.app_context():
        tmp_location.default = True
        db.session.merge(tmp_location)
        db.session.commit()
        # load root schemas
        load_root_schemas()
        # load the demo
        load_demo_data(os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            'data'), verbose=0)
        db.session.commit()


@pytest.yield_fixture()
def tmp_location(app):
    """File system location."""
    with app.app_context():
        tmppath = tempfile.mkdtemp()

        loc = Location(
            name='extra',
            uri=tmppath,
            default=False
        )
        db.session.add(loc)
        db.session.commit()

    yield loc

    shutil.rmtree(tmppath)


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
                url_regexp = re.compile(
                    'http://' +
                    app.config.get('SERVER_NAME') +
                    (app.config.get('APPLICATION_ROOT')  or '') +
                    re.sub(r'<[^>]+>', '\S+', rule.rule))
                for method in rule.methods:
                    rsps.add_callback(method, url_regexp,
                                        callback=router_callback)
            yield
    yield router
