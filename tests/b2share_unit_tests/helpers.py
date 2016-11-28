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

"""Test helpers."""

import json
from copy import deepcopy
from contextlib import contextmanager
from collections import namedtuple

from flask_security.utils import encrypt_password
from b2share.modules.records.links import url_for_bucket
from flask import current_app, url_for
from six import string_types, BytesIO
from flask_login import login_user, logout_user
from invenio_accounts.models import User
from b2share.modules.deposit.api import Deposit
from b2share_demo.helpers import resolve_community_id, resolve_block_schema_id
from invenio_indexer.api import RecordIndexer
from invenio_db import db
from flask_principal import ActionNeed
from invenio_access.models import ActionRoles, ActionUsers
from invenio_access.permissions import ParameterizedActionNeed


def url_for_file(bucket_id, key):
    """Build the url for the given file."""
    return url_for(
        'invenio_files_rest.object_api',
        bucket_id=bucket_id, key=key,
        _external=True
    )


def subtest_self_link(response_data, response_headers, client):
    """Check that the returned self link returns the same data.
    """
    assert 'links' in response_data.keys() \
        and isinstance(response_data['links'], dict)
    assert 'self' in response_data['links'].keys() \
        and isinstance(response_data['links']['self'], string_types)
    headers = [('Accept', 'application/json')]
    self_response = client.get(response_data['links']['self'],
                               headers=headers)
    assert self_response.status_code == 200
    self_data = json.loads(self_response.get_data(as_text=True))
    assert self_data == response_data
    if response_headers:
        assert response_headers['ETag'] == self_response.headers['ETag']


def subtest_file_bucket_content(client, bucket, expected_files):
    """Check that the bucket's content matches the given data."""
    headers = [('Accept', '*/*')]
    file_list_res = client.get(url_for_bucket(bucket.id), headers=headers)

    assert file_list_res.status_code == 200
    file_list_data = json.loads(
        file_list_res.get_data(as_text=True))
    assert 'contents' in file_list_data
    assert len(file_list_data['contents']) == len(expected_files)
    for draft_file in file_list_data['contents']:
        assert 'size' in draft_file and 'key' in draft_file
        expected_content = expected_files[draft_file['key']]
        assert draft_file['size'] == len(expected_content)


def subtest_file_bucket_permissions(client, bucket, access_level=None,
                                    is_authenticated=False):
    """Check that a file bucket's permissions match the given access_level."""
    # Check the test access_level parameter
    assert access_level in [None, 'read', 'write']

    def test_files_permission(read_status, update_status, delete_status):
        if bucket.objects:
            file_url = url_for_file(bucket.id,
                                    bucket.objects[0].key)
            # test GET file
            file_get_res = client.get(file_url,
                                      headers=headers)
            assert file_get_res.status_code == read_status
            # test update file
            file_update_res = client.put(file_url,
                                         input_stream=BytesIO(b'updated'),
                                         headers=headers)
            assert file_update_res.status_code == update_status
            # test delete file
            file_delete_res = client.delete(file_url,
                                            headers=headers)
            assert file_delete_res.status_code == delete_status

    headers = [('Accept', '*/*')]
    # test get bucket
    file_list_res = client.get(url_for_bucket(bucket.id), headers=headers)
    if access_level is None:
        assert file_list_res.status_code == 404
        test_files_permission(404, 404, 404)
        return

    # access level is at least 'read'
    assert file_list_res.status_code == 200

    unauthorized_code = 403 if is_authenticated else 401
    if access_level == 'read':
        test_files_permission(200,
                              # FIXME: This is a bug in invenio-files-rest
                              # it should be 403/401
                              404,
                              unauthorized_code)
    elif access_level == 'write':
        test_files_permission(200, 200, 204)


UserInfo = namedtuple('UserInfo', ['id', 'email', 'password'])
"""Generated user information."""


def create_user(name, roles=None, permissions=None, admin_communities=None,
                member_communities=None):
    """Create a user.

    Args:
        name (str): user's name.
        roles (list): roles assigned to this new user.

    Returns:
        (UserInfo) created user's information.
    """

    users_password = '123456'
    accounts = current_app.extensions['invenio-accounts']
    security = current_app.extensions['security']

    email = '{}@example.org'.format(name)
    with db.session.begin_nested():
        user = accounts.datastore.create_user(
            email=email,
            password=encrypt_password(users_password),
            active=True,
        )
        db.session.add(user)

        if roles is not None:
            for role in roles:
                security.datastore.add_role_to_user(user, role)

        if permissions is not None:
            for permission in permissions:
                # permissions of the form [('action name', 'argument'), (...)]
                if len(permission) == 2:
                    permission = ParameterizedActionNeed(permission[0],
                                                         permission[1])
                db.session.add(ActionUsers.allow(permission, user=user))

    return UserInfo(email=email, password=users_password, id=user.id)


def create_role(name, permissions=None):
    """Create a role and assign it the given permission needs."""
    security = current_app.extensions['security']
    role = security.datastore.find_or_create_role(name)
    if permissions is not None:
        for permission in permissions:
            # permissions of the form [('action name', 'argument'), (...)]
            if len(permission) == 2:
                permission = ParameterizedActionNeed(permission[0],
                                                     permission[1])
            db.session.add(ActionRoles.allow(permission, role=role))
    return role


def build_expected_metadata(record_data, state, owners=None, draft=False):
    """Create the metadata expected for a given record/deposit GET.

    Args:
        record_data: the data given at the record's creation
        state: expected state of the record.
        owners: list of owners' ids
    """
    expected_metadata = deepcopy(record_data)
    expected_metadata['publication_state'] = state
    uri_template = '{}#/draft_json_schema' if draft else '{}#/json_schema'
    expected_metadata['$schema'] = uri_template.format(
        url_for('b2share_schemas.community_schema_item',
                community_id=record_data['community'],
                schema_version_nb=1,
                _external=True)
    )
    if owners is not None:
        expected_metadata['owners'] = owners
    return expected_metadata


@contextmanager
def authenticated_user(userinfo):
    """Authentication context manager."""
    user = User.query.filter(User.id == userinfo.id).one()
    with current_app.test_request_context():
        login_user(user)
        try:
            yield
        finally:
            logout_user()


def create_deposit(data, creator, files=None):
    """Create a deposit with the given user as creator."""
    with authenticated_user(creator):
        deposit = Deposit.create(data=deepcopy(data))
        if files is not None:
            for key, value in files.items():
                deposit.files[key] = BytesIO(value)
    return deposit


def create_record(data, creator, files=None):
    """Create a deposit with the given user as creator."""
    deposit = create_deposit(data, creator, files)
    with authenticated_user(creator):
        deposit.submit()
        deposit.publish()
    published = deposit.fetch_published()
    RecordIndexer().index(published[1])
    return (deposit, published[0], published[1])  # deposit, pid, record


def resolve_record_data(data):
    """Resolve community and block schema IDs in the given record data."""
    return json.loads(
        resolve_block_schema_id(resolve_community_id(json.dumps(data)))
    )


def generate_record_data(title='My Test BBMRI Record', open_access=True,
                         community='MyTestCommunity1',
                         block_schema='MyTestSchema',
                         block_schema_content=None, **kwargs):
    """Generate"""
    default_block_schema_content = {
        'study_design': ['Case-control']
    }
    data = {
        'title': title,
        'community': '$COMMUNITY_ID[{}]'.format(community),
        'open_access': open_access,
        'community_specific': {
            '$BLOCK_SCHEMA_ID[{}]'.format(block_schema): \
            default_block_schema_content if block_schema_content is None \
            else block_schema_content
        }
    }
    data.update(kwargs)
    return resolve_record_data(data)


def create_user_token(userid, name='token', scopes=None):
    """Create access tokens for a given user.

    Returns:
        tuple: (access token, authorization header)
    """
    if scopes is None:
        scopes = [s[0] for s in current_oauth2server.scope_choices()]
    token = Token.create_personal(
        'other_token', other_user.id,
        scopes=[s[0] for s in scopes]
    )
    return token, [('Authorization',
                    'Bearer {}'.format(allowed_token.access_token))]
