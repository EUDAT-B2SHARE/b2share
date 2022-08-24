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

"""Test B2Share Ownership """

from flask import url_for
from urllib import parse

from b2share_unit_tests.helpers import create_record
from b2share_unit_tests.helpers import create_user
from b2share.modules.management.ownership.cli import find_version_master, pid2record

from invenio_records_files.api import Record


# COMMENTED OUT: API NOT USED AT THE MOMENT

# def test_ownership_is_user_allowed_to_modify(app, login_user,  test_records_data):
#     """Test if an authorized user is allowed to change the ownership."""

#     with app.app_context():
#         creator = create_user('creator')
#         _deposit, pid, _record = create_record(test_records_data[0], creator)

#         new_owner = create_user('new_owner')

#         with app.test_client() as client:
#             if creator is not None:
#                 login_user(creator, client)
#             url = url_for('b2share_ownership.record_ownership',
#                           record_pid=pid.pid_value, user_email=new_owner.email, _external=True)
#             headers = [('Accept', '*/*'), ('Content-Length', '0'),
#                        ('Accept-Encoding', 'gzip, deflate, br')]
#             url = parse.unquote(url)
#             res = client.get(url, headers=headers)
#             # 200 = 3 conditions verified :logged in user is allowed to change ownership, record exists and also new user exists.
#             assert 200 == res.status_code


# def test_ownership_modify(app, login_user,  test_records_data):
#     """Test if the owner of a record can add another existing user as owner of the record.
#     
#     Test if owner can add an user that is already owner for that record.
#     """

#     with app.app_context():
#         creator = create_user('creator')
#         _deposit, pid, _record = create_record(test_records_data[0], creator)
#         # create a new version of the same record
#         _deposit_v2, pid_v2, _record_v2 = create_record(test_records_data[0], creator, version_of=pid.pid_value)

#         new_owner = create_user('new_owner')

#         with app.test_client() as client:
#             if creator is not None:
#                 login_user(creator, client)
#             url = url_for('b2share_ownership.record_ownership',
#                           record_pid=pid.pid_value, user_email=new_owner.email, _external=True)
#             url = parse.unquote(url)
#             headers = [('Accept', '*/*'), ('Content-Length', '0'),
#                        ('Accept-Encoding', 'gzip, deflate, br')]
#             res = client.put(url, headers=headers)
#             # 200 = 3 conditions verified :logged in user is allowed to change ownership, record exists and also new user exists.
#             assert 200 == res.status_code
#             record = Record.get_record(pid.object_uuid)
#             assert new_owner.id in record['_deposit']['owners']
#             assert creator.id in record['_deposit']['owners']

#             # now we try to check if we can add the user again
#             res = client.put(url, headers=headers)
#             assert 400 == res.status_code
#             record = Record.get_record(pid.object_uuid)
#             assert new_owner.id in record['_deposit']['owners']
#             assert creator.id in record['_deposit']['owners']
#             assert len(record['_deposit']['owners']) == 2
            
#             # check if the changes are applied to all the record versions
#             version_master = find_version_master(pid.pid_value)
#             all_record_versions = version_master.children.all()
#             all_records=[Record.get_record(single_pid.object_uuid) for single_pid in all_record_versions]
#             for record_v in all_records:
#                 assert new_owner.id in record_v['_deposit']['owners']
#                 assert creator.id in record_v['_deposit']['owners']
#                 assert len(record_v['_deposit']['owners']) == 2
            



# def test_ownership_modify_not_existing_pid(app, login_user,  test_records_data):
#     """Test if owner try to get an not existing record."""

#     with app.app_context():
#         creator = create_user('creator')
#         fake_pid = "00000000000000000000000000000000"
#         new_owner = create_user('new_owner')

#         with app.test_client() as client:
#             if creator is not None:
#                 login_user(creator, client)
#             url = url_for('b2share_ownership.record_ownership',
#                           record_pid=fake_pid, user_email=new_owner.email, _external=True)
#             headers = [('Accept', '*/*'), ('Content-Length', '0'),
#                        ('Accept-Encoding', 'gzip, deflate, br')]
#             url = parse.unquote(url)
#             res = client.put(url, headers=headers)
#             assert 404 == res.status_code


# def test_ownership_modify_not_existing_owner(app, login_user,  test_records_data):
#     """Test if owner try to add a not existing user."""

#     with app.app_context():
#         creator = create_user('creator')
#         _deposit, pid, _record = create_record(test_records_data[0], creator)

#         fake_email = "fake_email@testing.csc"

#         with app.test_client() as client:
#             if creator is not None:
#                 login_user(creator, client)
#             url = url_for('b2share_ownership.record_ownership',
#                           record_pid=pid.pid_value, user_email=fake_email, _external=True)
#             headers = [('Accept', '*/*'), ('Content-Length', '0'),
#                        ('Accept-Encoding', 'gzip, deflate, br')]
#             url = parse.unquote(url)
#             res = client.put(url, headers=headers)
#             assert 400 == res.status_code


# def test_ownership_modify_unauthorized_user(app, login_user,  test_records_data):
#     """Test if a logged in user that is not the owner try to add an existing user as owner of the record."""

#     with app.app_context():
#         creator = create_user('creator')
#         _deposit, pid, _record = create_record(test_records_data[0], creator)

#         new_owner = create_user('new_owner')
#         not_the_owner = create_user('not_the_owner')

#         with app.test_client() as client:
#             if not_the_owner is not None:
#                 login_user(not_the_owner, client)
#             url = url_for('b2share_ownership.record_ownership',
#                           record_pid=pid.pid_value, user_email=new_owner.email, _external=True)
#             headers = [('Accept', '*/*'), ('Content-Length', '0'),
#                        ('Accept-Encoding', 'gzip, deflate, br')]
#             url = parse.unquote(url)
#             res = client.put(url, headers=headers)
#             assert 403 == res.status_code
#             record = Record.get_record(pid.object_uuid)
#             assert new_owner.id not in record['_deposit']['owners']
#             assert not_the_owner.id not in record['_deposit']['owners']
#             assert creator.id in record['_deposit']['owners']


# def test_ownership_modify_not_logged_in_user(app, login_user,  test_records_data):
#     """Test if a not logged in user can modify the record ownership."""

#     with app.app_context():
#         creator = create_user('creator')
#         _deposit, pid, _record = create_record(test_records_data[0], creator)

#         new_owner = create_user('new_owner')

#         with app.test_client() as client:
#             url = url_for('b2share_ownership.record_ownership',
#                           record_pid=pid.pid_value, user_email=new_owner.email, _external=True)
#             headers = [('Accept', '*/*'), ('Content-Length', '0'),
#                        ('Accept-Encoding', 'gzip, deflate, br')]
#             url = parse.unquote(url)
#             res = client.put(url, headers=headers)
#             assert 401 == res.status_code
