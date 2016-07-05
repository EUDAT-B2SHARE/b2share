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

"""Test Invenio integration with submission tests."""

from __future__ import absolute_import, print_function

import json
from io import BytesIO

from b2share.modules.deposit.api import PublicationStates
from flask import url_for
from invenio_db import db


def test_deposit(app, test_communities, create_user, login_user,
                 test_records_data):
    with app.app_context():
        allowed_user = create_user('allowed')
        db.session.commit()

    with app.app_context():
        with app.test_client() as client:
            login_user(allowed_user, client)
            headers = [('Content-Type', 'application/json'),
                       ('Accept', 'application/json')]
            patch_headers = [('Content-Type', 'application/json-patch+json'),
                             ('Accept', 'application/json')]
            for record_data in test_records_data:
                record_list_url = (
                    lambda **kwargs:
                    url_for('b2share_records_rest.b2share_record_list',
                            **kwargs))
                draft_create_res = client.post(record_list_url(),
                                               data=json.dumps(record_data),
                                               headers=headers)
                assert draft_create_res.status_code == 201
                draft_create_data = json.loads(
                    draft_create_res.get_data(as_text=True))

                # Test file upload
                headers = {'Accept': '*/*'}
                object_url = '{0}/{1}'.format(
                    draft_create_data['links']['files'], 'myfile1.dat')
                file_content = b'contents1'
                data = {'file': (BytesIO(file_content), 'file1.dat')}
                file_put_res = client.put(object_url,
                                          data=data,
                                          headers=headers)
                assert file_put_res.status_code == 200
                file_put_data = json.loads(
                    file_put_res.get_data(as_text=True))
                assert file_put_data['size'] == len(file_content)

                # Test file upload
                headers = {'Accept': '*/*'}
                object_url = '{0}/{1}'.format(
                    draft_create_data['links']['files'], 'myfile2.dat')
                file_content = b'contents2'
                data = {'file': (BytesIO(file_content), 'file2.dat')}
                file_put_res = client.put(object_url,
                                          data=data,
                                          headers=headers)
                assert file_put_res.status_code == 200
                file_put_data = json.loads(
                    file_put_res.get_data(as_text=True))
                assert file_put_data['size'] == len(file_content)

                # Test file upload
                headers = {'Accept': '*/*'}
                file_list_res = client.get(draft_create_data['links']['files'],
                                           headers=headers)
                assert file_list_res.status_code == 200
                file_list_data = json.loads(
                    file_list_res.get_data(as_text=True))

                # test draft PATCH
                headers = [('Content-Type', 'application/json-patch+json'),
                           ('Accept', 'application/json')]
                draft_patch_res = client.patch(
                    url_for('b2share_deposit_rest.b2share_deposit_item',
                            pid_value=draft_create_data['id']),
                    data=json.dumps([{"op": "replace", "path": "/title", "value":
                                      "first-patched-title"}]),
                    headers=headers)
                assert draft_patch_res.status_code == 200
                draft_patch_data = json.loads(
                    draft_patch_res.get_data(as_text=True))

                # Test draft GET
                draft_unpublished_get_res = client.get(
                    url_for('b2share_deposit_rest.b2share_deposit_item',
                            pid_value=draft_create_data['id']),
                    headers=headers)
                assert draft_unpublished_get_res.status_code == 200
                draft_unpublished_get_data = json.loads(
                    draft_unpublished_get_res.get_data(as_text=True))

                # test draft submit
                draft_submit_res = client.patch(
                    url_for('b2share_deposit_rest.b2share_deposit_item',
                            pid_value=draft_create_data['id']),
                    data=json.dumps([{
                        "op": "replace", "path": "/publication_state",
                        "value": PublicationStates.submitted.name
                    }]),
                    headers=patch_headers)
                assert draft_submit_res.status_code == 200

                # test draft publish
                draft_publish_res = client.patch(
                    url_for('b2share_deposit_rest.b2share_deposit_item',
                            pid_value=draft_create_data['id']),
                    data=json.dumps([{
                        "op": "replace", "path": "/publication_state",
                        "value": PublicationStates.published.name
                    }]),
                    headers=patch_headers)

                assert draft_publish_res.status_code == 200
                draft_publish_data = json.loads(
                    draft_publish_res.get_data(as_text=True))

                # Test draft GET
                draft_published_get_res = client.get(
                    url_for('b2share_deposit_rest.b2share_deposit_item',
                            pid_value=draft_create_data['id']),
                    headers=headers)
                assert draft_published_get_res.status_code == 200
                draft_published_get_data = json.loads(
                    draft_published_get_res.get_data(as_text=True))

                # Test record GET
                record_get_res = client.get(
                    url_for('b2share_records_rest.b2share_record_item',
                            pid_value=draft_publish_data['id']),
                    headers=headers)
                assert record_get_res.status_code == 200
                record_get_data = json.loads(
                    record_get_res.get_data(as_text=True))

                # FIXME: test draft edition once we support it
