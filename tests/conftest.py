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

import json
import os
import shutil
import re
import tempfile
import sys
from contextlib import contextmanager
from copy import deepcopy
from collections import namedtuple

from flask_cli import ScriptInfo
import pytest
import responses
from b2share_unit_tests.helpers import authenticated_user, create_user
from b2share.modules.deposit.api import Deposit
from b2share.modules.schemas.helpers import load_root_schemas
from b2share_demo.helpers import resolve_community_id, resolve_block_schema_id
from flask_security import url_for_security
from b2share.modules.deposit.api import Deposit
from invenio_db import db
from invenio_files_rest.models import Location
from invenio_search import current_search_client, current_search
from sqlalchemy_utils.functions import create_database, drop_database
from invenio_access.models import ActionRoles
from invenio_access.permissions import superuser_access
from invenio_indexer.api import RecordIndexer
from b2share.modules.communities.models import Community

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
    from b2share.factory import create_api

    instance_path = tmpdir.mkdir('instance_dir').strpath
    os.environ.update(
        B2SHARE_INSTANCE_PATH=os.environ.get(
            'INSTANCE_PATH', instance_path),
    )
    app = create_api(
        TESTING=True,
        SERVER_NAME='localhost:5000',
        JSONSCHEMAS_HOST='localhost:5000',
        DEBUG_TB_ENABLED=False,
        SQLALCHEMY_DATABASE_URI=os.environ.get(
            'SQLALCHEMY_DATABASE_URI', 'sqlite://'),
        LOGIN_DISABLED=False,
        WTF_CSRF_ENABLED=False,
        SECRET_KEY="CHANGE_ME",
        SECURITY_PASSWORD_SALT='CHANGEME',
        CELERY_ALWAYS_EAGER=True,
        CELERY_RESULT_BACKEND="cache",
        CELERY_CACHE_BACKEND="memory",
        CELERY_EAGER_PROPAGATES_EXCEPTIONS=True
    )

    # update the application with the configuration provided by the test
    if hasattr(request, 'param') and 'config' in request.param:
        app.config.update(**request.param['config'])

    with app.app_context():
        if app.config['SQLALCHEMY_DATABASE_URI'] != 'sqlite://':
            create_database(db.engine.url)
        db.create_all()
        for deleted in current_search.delete(ignore=[404]):
            pass
        for created in current_search.create(None):
            pass

    def finalize():
        with app.app_context():
            db.drop_all()
            if app.config['SQLALCHEMY_DATABASE_URI'] != 'sqlite://':
                drop_database(db.engine.url)

    request.addfinalizer(finalize)
    return app


@pytest.fixture(scope='function')
def test_users(app):
    """Create test users.

    Created users are named 'normal' and 'admin'.
    Other fixtures can add other users.

    Returns:
        (dict) A dict of username->user_info.
    """
    result = dict()
    accounts = app.extensions['invenio-accounts']
    security = app.extensions['security']
    with app.app_context():
        # create a normal user
        result['normal'] = create_user('normal')
        # create admin user
        user_info = create_user('admin')
        user = accounts.datastore.get_user(user_info.id)
        role = security.datastore.find_or_create_role('admin')
        db.session.add(ActionRoles.allow(
            superuser_access, role=role
        ))
        security.datastore.add_role_to_user(user, role)
        result['admin'] = user_info
        # create the user which will create the test deposits
        creator = create_user('deposits_creator')
        result['deposits_creator'] = creator
        db.session.commit()
    return result


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
        return {com.name: com.id for com in Community.query.all()}


@pytest.fixture(scope='function')
def test_records_data(app, test_communities):
    """Generate test deposits data.

    Returns:
        :list: list of generated record data
    """
    records_data = [{
        'title': 'My Test BBMRI Record',
        'community': '$COMMUNITY_ID[MyTestCommunity1]',
        "open_access": True,
        'community_specific': {
            '$BLOCK_SCHEMA_ID[MyTestSchema]': {
                'study_design': ['Case-control']
            }
        }
    }, {
        'title': 'New BBMRI dataset',
        'community': '$COMMUNITY_ID[MyTestCommunity1]',
        "open_access": False,
        'community_specific': {
            '$BLOCK_SCHEMA_ID[MyTestSchema]': {
                'study_design': ['Case-control']
            }
        }
    }, {
        'title': 'BBMRI dataset 3',
        'community': '$COMMUNITY_ID[MyTestCommunity1]',
        "open_access": True,
        'community_specific': {
            '$BLOCK_SCHEMA_ID[MyTestSchema]': {
                'study_design': ['Case-control']
            }
        }
    }, {
        'title': 'BBMRI dataset 4',
        # community 2
        'community': '$COMMUNITY_ID[MyTestCommunity2]',
        "open_access": True,
        'community_specific': {
            '$BLOCK_SCHEMA_ID[MyTestSchema]': {
                'study_design': ['Case-control']
            }
        }
    }, {
        'title': 'BBMRI dataset 5',
        # community 2
        'community': '$COMMUNITY_ID[MyTestCommunity2]',
        "open_access": True,
        'community_specific': {
            '$BLOCK_SCHEMA_ID[MyTestSchema]': {
                'study_design': ['Case-control']
            }
        }
    }, {
        'title': 'BBMRI dataset 6',
        # community 2
        'community': '$COMMUNITY_ID[MyTestCommunity2]',
        "open_access": True,
        'community_specific': {
            '$BLOCK_SCHEMA_ID[MyTestSchema]': {
                'study_design': ['Case-control']
            }
        }
    }]
    with app.app_context():
        return [
            json.loads(resolve_block_schema_id(resolve_community_id(
                json.dumps(data)))
            ) for data in records_data
        ]


def create_deposits(app, test_records_data, creator):
    """Create test deposits."""
    DepositInfo = namedtuple('DepositInfo', ['id', 'data', 'deposit'])
    indexer = RecordIndexer()

    with authenticated_user(creator):
        deposits = [Deposit.create(data=data)
                    for data in deepcopy(test_records_data)]
    for deposit in deposits:
        indexer.index(deposit)
        deposit.commit()
        deposit.commit()
    return [DepositInfo(dep.id, dep.dumps(), dep) for dep in deposits]


@pytest.fixture(scope='function')
def draft_deposits(app, test_records_data, test_users):
    """Fixture creating deposits in draft state."""
    with app.app_context():
        result = create_deposits(app, test_records_data,
                                 test_users['deposits_creator'])
        db.session.commit()
    return result


@pytest.fixture(scope='function')
def submitted_deposits(app, test_records_data, test_users):
    """Fixture creating deposits in submitted state."""
    with app.app_context():
        deposits = create_deposits(app, test_records_data,
                                   test_users['deposits_creator'])
        for dep in deposits:
            dep.deposit.submit()
        db.session.commit()
    return deposits


@pytest.fixture(scope='function')
def test_records(app, request, test_records_data, test_users):
    """Fixture creating test deposits."""
    with app.app_context():
        test_deposits = create_deposits(app, test_records_data,
                                        test_users['deposits_creator'])

        RecordInfo = namedtuple('DepositInfo', ['deposit_id', 'pid',
                                                'record_id', 'data'])
        indexer = RecordIndexer()
        def publish(deposit):
            deposit.submit()
            deposit.publish()
            pid, record = deposit.fetch_published()
            indexer.index(record)
            return RecordInfo(deposit.id, str(pid.pid_value), record.id,
                              record.dumps())
        result = [publish(deposit_info.deposit)
                  for deposit_info in test_deposits]
        db.session.commit()
        return result


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
                    (app.config.get('APPLICATION_ROOT') or '') +
                    re.sub(r'<[^>]+>', '\S+', rule.rule))
                for method in rule.methods:
                    rsps.add_callback(method, url_regexp,
                                      callback=router_callback)
            yield
    yield router


@pytest.fixture()
def script_info(app):
    """Get ScriptInfo object for testing CLI."""
    return ScriptInfo(create_app=lambda info: app)
