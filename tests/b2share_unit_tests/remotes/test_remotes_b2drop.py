# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2017 University of Tübingen.
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


import subprocess
import os
import json

from flask import url_for, current_app
from urllib.parse import urljoin

from invenio_records_files.models import RecordsBuckets
from invenio_db import db

from b2share.modules.communities.api import Community
from b2share.modules.deposit.api import Deposit
from b2share.modules.remotes.b2drop import B2DropClient

from b2share_unit_tests.helpers import create_user


wsgidav_conf_filename = 'wsgidav.conf'
wsgidav_conf_path = 'tests/b2share_unit_tests/remotes/'+wsgidav_conf_filename

def test_remotes_b2drop(app, test_communities, test_records_data, login_user):
    webdav_server = subprocess.Popen([
        'wsgidav', '-c', wsgidav_conf_path])

    _test_remotes_b2drop_client_api()
    _test_remotes_b2drop_rest(app, test_records_data, login_user)

    webdav_server.terminate()
    webdav_server.kill()
    webdav_server.wait()

def _test_remotes_b2drop_client_api():
    dropclient = B2DropClient('localhost', port='8080', path='webdav',
                              username="tester", password="secret")
    ls = dropclient.list()
    assert ls.keys() == set(['files', 'parent'])
    files = ls.get('files')

    b2share_dir = [x for x in files if x.get('name') == 'b2share']
    assert b2share_dir
    assert b2share_dir[0].get('isdir') is True

    license_file = [x for x in files if x.get('name') == 'LICENSE']
    assert license_file
    assert license_file[0].get('isdir') is False



def _test_remotes_b2drop_rest(app, test_records_data, login_user):
    with app.app_context():
        with app.test_client() as client:
            headers = [('Content-Type', 'application/json'),
                       ('Accept', 'application/json')]
            current_app.config['B2DROP_SERVER'] = {
                'host': 'localhost',
                'protocol': 'http',
                'port': '8080',
                'path': 'webdav',
            }
            creator = create_user('creator')
            login_user(creator, client)
            deposit = Deposit.create(data=test_records_data[0])

            remotes_url = url_for('remotes.remotes', service='b2drop')
            auth = dict(username='tester', password='secret')
            remote_res = client.put(remotes_url, data=json.dumps(auth),
                                    headers=headers)
            assert remote_res.status_code == 200

            list_url = url_for('remotes.b2drop', path=os.path.dirname(wsgidav_conf_path))
            list_res = client.get(list_url)
            assert list_res.status_code == 200

            src_url = url_for('remotes.b2drop', path=wsgidav_conf_path,
                              _external=True)
            bucket_id_uuid = RecordsBuckets.query.filter(
                RecordsBuckets.record_id == deposit.id).one().bucket_id
            file_url = url_for('invenio_files_rest.bucket_api',
                               bucket_id=str(bucket_id_uuid), _external=True)
            data = dict(source_remote_url=src_url,
                        destination_file_url=urljoin(file_url+'/', 'wsgidav.conf'))

            file_jobs_url = url_for('remotes.remotes_jobs', path=wsgidav_conf_path,
                                    _external=True)
            job_res = client.post(file_jobs_url, data=json.dumps(data),
                                  headers=headers)
            assert job_res.status_code == 200

            deposit.submit()
            db.session.commit()

            community = Community.get(name='MyTestCommunity1')
            com_admin = create_user('com_admin', roles=[community.admin_role])
            login_user(com_admin, client)
            deposit.publish()

            url = url_for('b2share_records_rest.b2rec_item', pid_value=deposit.model.id.hex)
            request_res = client.get(url, headers=headers)
            record = json.loads(request_res.get_data(as_text=True))

            assert record['files']
            assert record['files'][0]['key'] == 'wsgidav.conf'
            assert record['files'][0]['size'] > 0
