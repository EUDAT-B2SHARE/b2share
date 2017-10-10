# create new storage class for invenio-files-rest
# which disables almost everything but redirects when getting a file (send_file)

# create the FileInstance with the planted PID
# - and the required ObjectVersion

# then add the REST API enable the blueprints
# - > access it and see if it redirects

# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2017 CERN.
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

"""Test B2Share Storage Class."""

from flask import url_for
from invenio_files_rest.models import Bucket, FileInstance, \
    ObjectVersion, Location
from b2share.modules.files.storage import B2ShareFileStorage
from invenio_db import db


def test_deposit_create(app, tmp_location, login_user, test_users):
    """Test deposit creation."""
    with app.app_context():
        tmp_location = Location.query.first()
        with db.session.begin_nested():
            b1 = Bucket.create(tmp_location, storage_class='B')
            f1 = FileInstance.create()
            f1.set_uri('http://hdl.handle.net/11304/74c66f0b-f814-4202-9dcb-4889ba9b1047',
                       1, 0, storage_class='B')
            # f2 = FileInstance(uri="f2", size=1,
            #                   checksum="mychecksum", storage_class='S')
            # f2.create
            # f2.set_uri('http://hdl.handle.net/11304/74c66f0b-f814-4202-9dcb-4889ba9b1047',
                       # 1, 0, storage_class='B2SAFE')
            ObjectVersion.create(b1, 'test.txt', f1.id)
            # ObjectVersion.create(b1, 'test2.txt', f2.id)
        db.session.commit()

        with app.test_client() as client:
            login_user(test_users['normal'], client)
            resp = client.get(
                url_for('invenio_files_rest.object_api',
                        bucket_id=b1.id,
                        key='test.txt',
                        follow_redirects=True)
            )
            print(resp.data)


# move these to the functional tests
def test_create_record_with_b2safe_files(app):
    # create a record which has a file_pids field in the metadata
    pass


def test_modify_record_adding_b2safe_files(app):
    # create an empty record
    # modify it to add 2 b2safe files
    # modify it to remove 1 and add 1
    # modify it to remove all
    pass


def test_record_with_both_types_of_files(app):
    # create a record with a b2safe file
    # upload a normal record
    # modify to change the b2safe file
    # upload a second normal file
    pass


def test_getting_a_b2safe_file(app, tmp_location):
    # create a b2safe file
    # query to get the contents of the b2safe file
    # check that the redirect works
    with app.app_context():
        tmp_location = Location.query.first()
        with db.session.begin_nested():
            bucket = Bucket.create(tmp_location, storage_class='B')
            b2safe_file = FileInstance.create()
            b2safe_file.set_uri('http://hdl.handle.net/11304/74c66f0b-f814-4202-9dcb-4889ba9b1047',
                                1, 0, storage_class='B')
