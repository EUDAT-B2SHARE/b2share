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
from invenio_records_rest.utils import allow_all
from invenio_files_rest.proxies import current_files_rest


def test_b2share_storage_with_pid(base_app, app, tmp_location, login_user, test_users):
    """Check that the storage class will redirect pid files."""
    pid = 'http://hdl.handle.net/11304/74c66f0b-f814-4202-9dcb-4889ba9b1047'
    with app.app_context():
        # Disable access control for this test
        tmp_location = Location.query.first()
        with db.session.begin_nested():
            bucket = Bucket.create(tmp_location, storage_class='B')
            pid_file = FileInstance.create()
            pid_file.set_uri(pid, 1, 0, storage_class='B')
            ObjectVersion.create(bucket, 'test.txt', pid_file.id)
        db.session.commit()
        url = url_for('invenio_files_rest.object_api',
                        bucket_id=bucket.id,
                        key='test.txt')
    try:
        with app.app_context():
            permission = current_files_rest.permission_factory
            current_files_rest.permission_factory = allow_all
        # Check that accessing the file redirects to the PID
        with app.test_client() as client:
            resp = client.get(url)
            assert resp.headers['Location'] == pid
            assert resp.status_code == 302
    finally:
        with app.app_context():
            current_files_rest.permission_factory = permission
