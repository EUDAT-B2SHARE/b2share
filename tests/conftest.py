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
import logging
import os
import shutil
import re
import tempfile
import sys
import uuid
from contextlib import contextmanager
from copy import deepcopy
from collections import namedtuple

from flask.cli import ScriptInfo
import pytest
import responses
from jsonpatch import apply_patch
from tests.b2share_unit_tests.helpers import authenticated_user, create_user
from b2share.modules.deposit.api import Deposit as B2ShareDeposit
from b2share.modules.schemas.helpers import load_root_schemas
from b2share.modules.b2share_demo.helpers import resolve_community_id, resolve_block_schema_id
from flask_security import url_for_security
from invenio_db import db
from invenio_files_rest.models import Location
from invenio_search import current_search_client, current_search
from sqlalchemy_utils.functions import create_database, drop_database
from invenio_access.models import ActionRoles
from invenio_access.permissions import superuser_access
from b2share.modules.communities.models import Community
from b2share.modules.communities.api import Community as CommunityAPI
from sqlalchemy.exc import ProgrammingError
from invenio_accounts.models import Role
from b2share.modules.upgrade.api import alembic_stamp
from invenio_queues.proxies import current_queues
from b2share.modules.deposit.minters import b2share_deposit_uuid_minter

from b2share.config import B2SHARE_RECORDS_REST_ENDPOINTS, \
    B2SHARE_DEPOSIT_REST_ENDPOINTS

# add the demo module in sys.path
sys.path.append(
    os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
                 'demo'))
# add tests to the sys path
sys.path.append(os.path.dirname(__file__))


@pytest.yield_fixture(scope='session')
def base_app():
    """Base uninitialized flask application fixture."""
    from b2share.factory import create_api

    instance_path = tempfile.mkdtemp()
    os.environ.update(
        B2SHARE_INSTANCE_PATH=os.environ.get(
            'INSTANCE_PATH', instance_path),
    )
    app = create_api(
        TESTING=True,
        RATELIMIT_ENABLED=False,
        SERVER_NAME='localhost:5000',
        JSONSCHEMAS_HOST='localhost:5000',
        DEBUG_TB_ENABLED=False,
        SQLALCHEMY_DATABASE_URI=os.environ.get(
            'SQLALCHEMY_DATABASE_URI',
            'postgresql+psycopg2://postgres@localhost:5432/b2sharedb'),
        LOGIN_DISABLED=False,
        WTF_CSRF_ENABLED=False,
        SECRET_KEY="CHANGE_ME",
        SECURITY_PASSWORD_SALT='CHANGEME',
        # register flask_security endpoints for testing purpose.
        ACCOUNTS_REGISTER_BLUEPRINT=True,
        CELERY_ALWAYS_EAGER=True,
        CELERY_RESULT_BACKEND="cache",
        CELERY_CACHE_BACKEND="memory",
        CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
        SUPPORT_EMAIL='support@eudat.eu',
        PREFERRED_URL_SCHEME='https',
        FILES_REST_STORAGE_FACTORY='b2share.modules.files.storage.b2share_storage_factory',
        FILES_REST_STORAGE_CLASS_LIST={
            'B': 'B2SafePid',
            'S': 'Standard',
            'A': 'Archive',
        }
    )

    # Disable most of alembic logging.
    logging.getLogger('alembic').setLevel(logging.CRITICAL)
    yield app
    shutil.rmtree(instance_path)


@pytest.yield_fixture(scope='function')
def clean_app(request, base_app):
    """Application with database and elasticsearch cleaned."""
    with base_app.app_context():
        try:
            db.session.remove()
            drop_database(db.engine.url)
        except ProgrammingError:
            pass
        create_database(db.engine.url)
        # reset elasticsearch
        for deleted in current_search.delete(ignore=[404]):
            pass
        # reset queues
        current_queues.delete()
        current_queues.declare()

    yield base_app

    def finalize():
        with base_app.app_context():
            db.session.remove()
            drop_database(db.engine.url)
            # Dispose the engine in order to close all connections. This is
            # needed for sqlite in memory databases.
            db.engine.dispose()
            current_queues.delete()
    request.addfinalizer(finalize)

    return base_app


@pytest.fixture(scope='function')
def app(request, clean_app):
    """Application with database tables created."""
    with clean_app.app_context():
        ext = clean_app.extensions['invenio-db']
        db.metadata.create_all(db.session.connection())
        alembic_stamp('heads')
        db.session.commit()
        for created in current_search.create(None):
            pass
        # Note that we do not create the Migration just to simplify things.

    return clean_app


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
def custom_role(app):
    with app.app_context():
        role = Role(
            name='some_custom_role',
            description='Some custom role.'
        )
        db.session.add(role)
        db.session.commit()
        return role.id


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
    from b2share.modules.b2share_demo.helpers import load_demo_data

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
def test_community(app, test_communities):
    """Initialize member and admin of a community."""
    CommunityRef = namedtuple('CommunityRef',[
        'name', 'id', 'admin_role_id', 'member_role_id', 'admin', 'member'
    ])
    with app.app_context():
        community_name = 'MyTestCommunity1'
        community = CommunityAPI.get(name=community_name)
        admin_role_id = community.admin_role.id
        member_role_id = community.member_role.id
        com_admin = create_user('com_admin', roles=[community.admin_role])
        com_member = create_user('com_member', roles=[community.member_role])
        db.session.commit()
        return CommunityRef(community_name, community.id,
                            admin_role_id, member_role_id,
                            com_admin, com_member)


@pytest.fixture(scope='function')
def test_records_data(app, test_communities):
    """Generate test deposits data.

    Returns:
        :list: list of generated record data
    """
    records_data = [{
        'titles': [{'title':'My Test BBMRI Record'}],
        'descriptions': [{'description':"The long description of My Test BBMRI Record",
                          'description_type': "Abstract"}],
        'creators': [{'creator_name': 'Glados, R.'}, {'creator_name': 'Cube, Companion'}],
        'publisher': 'Aperture Science',
        'publication_date': '2000-12-12',
        'disciplines': ['5.14.17.10 → Weapon|Military weapons → Nuclear warfare|Nuclear'],
        'keywords': ['phaser', 'laser', 'maser', 'portal gun'],
        'contributors': [{'contributor_name': "Turret", "contributor_type": "ContactPerson"}],
        'language': "eng",
        'resource_types': [{'resource_type': "Casualities", 'resource_type_general': "Dataset"}],
        'alternate_identifiers': [{'alternate_identifier': "007",
                                   'alternate_identifier_type': "Fleming"}],
        'license': {'license':"GNU Public License", 'license_uri': "http://gnu.org"},
        'community': '$COMMUNITY_ID[MyTestCommunity1]',
        'open_access': True,
        'contact_email': 'info@aperture.org',
        'community_specific': {
            '$BLOCK_SCHEMA_ID[MyTestSchema]': {
                'study_design': ['Case-control']
            }
        }
    }, {
        'titles': [{'title':'New BBMRI dataset'}],
        'community': '$COMMUNITY_ID[MyTestCommunity1]',
        'open_access': True,
        'community_specific': {
            '$BLOCK_SCHEMA_ID[MyTestSchema]': {
                'study_design': ['Case-control']
            }
        }
    }, {
        'titles': [{'title':'BBMRI dataset 3'}],
        'community': '$COMMUNITY_ID[MyTestCommunity1]',
        'open_access': True,
        'community_specific': {
            '$BLOCK_SCHEMA_ID[MyTestSchema]': {
                'study_design': ['Case-control']
            }
        }
    }, {
        'titles': [{'title':'BBMRI dataset 4'}],
        # community 2
        'community': '$COMMUNITY_ID[MyTestCommunity2]',
        'open_access': True,
        'community_specific': {
            '$BLOCK_SCHEMA_ID[MyTestSchema]': {
                'study_design': ['Case-control']
            }
        }
    }, {
        'titles': [{'title':'BBMRI dataset 5'}],
        # community 2
        'community': '$COMMUNITY_ID[MyTestCommunity2]',
        'open_access': True,
        'community_specific': {
            '$BLOCK_SCHEMA_ID[MyTestSchema]': {
                'study_design': ['Case-control']
            }
        }
    }, {
        'titles': [{'title':'BBMRI dataset 6'}],
        # community 2
        'community': '$COMMUNITY_ID[MyTestCommunity2]',
        'open_access': True,
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


@pytest.fixture(scope='function')
def records_data_with_external_pids(app, test_communities):
    record_data = json.dumps({
        "external_pids":[
            {
                "key":"file1.txt",
                "ePIC_PID": "http://hdl.handle.net/11304/0d8dbdec-74e4-4774-954e-1a98e5c0cfa3"
            }, {
                "key":"file1_copy.txt",
                "ePIC_PID": "http://hdl.handle.net/11304/0d8dbdec-74e4-4774-954e-1a98e5c0cfa3"
            }, {
                "key":"file2.txt",
                "ePIC_PID": "http://hdl.handle.net/11304/50fafc50-4227-4464-bacc-2d85295c18a7"
            }
        ],
        'titles': [{'title':'BBMRI dataset 6'}],
        'community': '$COMMUNITY_ID[MyTestCommunity2]',
        'open_access': True,
        'community_specific': {
            '$BLOCK_SCHEMA_ID[MyTestSchema]': {
                'study_design': ['Case-control']
            }
        }
    })
    with app.app_context():
        return json.loads(resolve_block_schema_id(resolve_community_id(
            record_data)))


@pytest.fixture(scope='function')
def deposit_with_external_pids(app, records_data_with_external_pids,
                               test_communities, test_users):
    """Create a deposit with external pids."""
    with app.app_context():
        result = create_deposits(app, [records_data_with_external_pids],
                                 test_users['deposits_creator'])[0]
        db.session.commit()
        return result


@pytest.fixture(scope='function')
def test_incomplete_records_data(app, test_communities):
    """Create incomplete record data and the corresponding patch."""
    invalid_patches = [[
        # no title
            { "op": "remove", "path": "/titles"}
        ], [
        # no community_specific
            {
                "op": "remove",
                "path": "/community_specific"
            }
        ], [
        # no study_design
            {
                "op": "remove",
                "path": "/community_specific/"
                "$BLOCK_SCHEMA_ID[MyTestSchema]/study_design"
            }
        ], [
        # minItems not matched (should be >= 1)
            {
                "op": "replace",
                "path": "/community_specific/"
                "$BLOCK_SCHEMA_ID[MyTestSchema]/study_design",
                "value": []
            }
    ]]
    IncompleteRecordData = namedtuple(
        'IncompleteRecordData', ['complete_data', 'patch', 'incomplete_data']
    )
    with app.app_context():
        unresolved_data = {
            'titles': [{'title':'My Test BBMRI Record'}],
            'community': '$COMMUNITY_ID[MyTestCommunity1]',
            "open_access": True,
            'community_specific': {
                '$BLOCK_SCHEMA_ID[MyTestSchema]': {
                    'study_design': ['Case-control']
                }
            }
        }
        data = json.loads(resolve_block_schema_id(resolve_community_id(
                json.dumps(unresolved_data))))
        resolved_patches = [
            json.loads(resolve_block_schema_id(resolve_community_id(
                json.dumps(data)))
            ) for data in invalid_patches
        ]
        return [IncompleteRecordData(deepcopy(data), patch,
                                     apply_patch(data, patch))
                for patch in resolved_patches]


def create_deposits(app, test_records_data, creator):
    """Create test deposits."""
    DepositInfo = namedtuple(
        'DepositInfo', [
            'deposit_id',
            'data',
            'deposit', # FIXME: replaced by get_deposit, remove it later
            'get_deposit'
        ])

    deposits = []
    with authenticated_user(creator):
        for data in deepcopy(test_records_data):
            record_uuid = uuid.uuid4().hex
            # Create persistent identifier
            b2share_deposit_uuid_minter(record_uuid, data=data)
            deposits.append(B2ShareDeposit.create(data=data, id_=record_uuid))
    return [DepositInfo(
        dep.id, dep.dumps(), dep,
        (lambda id: lambda: B2ShareDeposit.get_record(id))(dep.id)
    ) for dep in deposits]


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

        RecordInfo = namedtuple('RecordInfo', ['deposit_id', 'pid',
                                                'record_id', 'data'])
        def publish(deposit):
            deposit.submit()
            deposit.publish()
            pid, record = deposit.fetch_published()
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
                    'https://' +
                    app.config.get('SERVER_NAME') +
                    (app.config.get('APPLICATION_ROOT') or '') +
                    re.sub(r'<[^>]+>', r'\\S+', rule.rule))
                for method in rule.methods:
                    rsps.add_callback(method, url_regexp,
                                      callback=router_callback)
            yield
    yield router


@pytest.fixture()
def script_info(app):
    """Get ScriptInfo object for testing CLI."""
    return ScriptInfo(create_app=lambda info: app)
