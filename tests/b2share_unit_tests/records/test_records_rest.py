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

"""Test B2Share deposit module's REST API."""

import json
import copy

from flask import url_for
from b2share_unit_tests.helpers import (
    create_record, generate_record_data, url_for_file,
    subtest_file_bucket_content, subtest_file_bucket_permissions,
    build_expected_metadata, subtest_self_link,
)
from b2share.modules.deposit.api import PublicationStates
from b2share.modules.records.links import url_for_bucket
from six import BytesIO
from jsonpatch import apply_patch


def test_record_content(app, test_communities,
                        create_user, login_user, admin):
    """Test record read with REST API."""

    uploaded_files = {
        'myfile1.dat': b'contents1',
        'myfile2.dat': b'contents2'
    }

    with app.app_context():
        creator = create_user('creator')
        non_creator = create_user('non-creator')

        record_data = generate_record_data()
        _, record_pid, record = create_record(
            record_data, creator, files=uploaded_files
        )

        with app.test_client() as client:
            login_user(creator, client)
            headers = [('Accept', 'application/json')]
            request_res = client.get(
                url_for('b2share_records_rest.b2share_record_item',
                        pid_value=record_pid.pid_value),
                headers=headers)

            assert request_res.status_code == 200

            request_data = json.loads(
                request_res.get_data(as_text=True))

            assert 'created' in request_data
            expected_metadata = build_expected_metadata(
                record_data,
                PublicationStates.published.name,
                owners=[creator.id],
            )
            assert request_data['metadata'] == expected_metadata

            # check that the link to the bucket is correctly generated
            expected_bucket_link = url_for_bucket(record.files.bucket)
            assert request_data['links']['files'] == expected_bucket_link
            # test self link
            subtest_self_link(request_data,
                              request_res.headers,
                              client)

######################
#  Test permissions  #
######################


def test_record_read_permissions(app, test_communities,
                                 create_user, login_user, admin):
    """Test record read with REST API."""

    uploaded_files = {
        'myfile1.dat': b'contents1',
        'myfile2.dat': b'contents2'
    }

    with app.app_context():
        creator = create_user('creator')
        non_creator = create_user('non-creator')

        open_record_data = generate_record_data(open_access=True)
        _, open_record_pid, open_record = create_record(
            open_record_data, creator, files=uploaded_files
        )

        closed_record_data = generate_record_data(open_access=False)
        _, closed_record_pid, closed_record = create_record(
            closed_record_data, creator, files=uploaded_files)

        with app.test_client() as client:
            login_user(creator, client)
            subtest_file_bucket_content(client, open_record.files.bucket,
                                        uploaded_files)
            subtest_file_bucket_content(client, closed_record.files.bucket,
                                        uploaded_files)

        def test_get(pid, record, status, user=None, files_access=None):
            with app.test_client() as client:
                if user is not None:
                    login_user(user, client)
                headers = [('Accept', 'application/json')]
                request_res = client.get(
                    url_for('b2share_records_rest.b2share_record_item',
                            pid_value=pid.pid_value),
                    headers=headers)

                request_data = json.loads(
                    request_res.get_data(as_text=True))

                assert request_res.status_code == status

                # check that the permissions to the file bucket is correct
                subtest_file_bucket_permissions(
                    client, record.files.bucket, access_level=files_access,
                    is_authenticated=user is not None
                )

        # test with anonymous user
        test_get(open_record_pid, open_record, 200, files_access='read')
        test_get(closed_record_pid, closed_record, 200)

        test_get(open_record_pid, open_record, 200, non_creator,
                 files_access='read')
        test_get(closed_record_pid, closed_record, 200, non_creator)

        test_get(open_record_pid, open_record, 200, creator,
                 files_access='read')
        test_get(closed_record_pid, closed_record, 200, creator,
                 files_access='read')

        test_get(open_record_pid, open_record, 200, admin, files_access='read')
        test_get(closed_record_pid, closed_record, 200, admin,
                 files_access='read')


def test_modify_metadata_published_record_permissions(app, test_communities,
                                                      create_user, login_user,
                                                      admin):
    """Test record's metadata modification with REST API."""
    with app.app_context():
        creator = create_user('creator')
        non_creator = create_user('non-creator')

        record_data = generate_record_data(open_access=True)

        def test_modify(status, user=None):
            patch = [{
                "op": "replace", "path": "/title",
                "value": 'newtitle'
            }]
            with app.test_client() as client:
                _, record_pid, record = create_record(record_data, creator)
                if user is not None:
                    login_user(user, client)
                # test patching the document
                headers = [('Content-Type', 'application/json-patch+json'),
                           ('Accept', 'application/json')]
                request_res = client.patch(
                    url_for('b2share_records_rest.b2share_record_item',
                            pid_value=record_pid.pid_value),
                    data=json.dumps(patch),
                    headers=headers)
                assert request_res.status_code == status

                _, record_pid, record = create_record(record_data, creator)
                # test putting the document
                data = dict(record)
                apply_patch(data, patch)
                headers = [('Content-Type', 'application/json'),
                           ('Accept', 'application/json')]
                request_res = client.put(
                    url_for('b2share_records_rest.b2share_record_item',
                            pid_value=record_pid.pid_value),
                    data=json.dumps(data),
                    headers=headers)
                assert request_res.status_code == status

        # test with anonymous user
        test_modify(401)
        test_modify(403, non_creator)
        test_modify(403, creator)
        test_modify(200, admin)
