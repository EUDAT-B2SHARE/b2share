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

"""B2share handle functions for records."""

from __future__ import absolute_import, print_function
from flask import current_app, url_for


handle_client = None


def init_handle_client(app):
    username = str(app.config.get('HANDLE_USERNAME'))
    password = str(app.config.get('HANDLE_PASSWORD'))
    handle_server_url = str(app.config.get('HANDLE_SERVER_URL'))

    from b2handle.handleclient import EUDATHandleClient
    global handle_client
    handle_client = EUDATHandleClient.instantiate_with_username_and_password(
        handle_server_url, username, password)


def register_pid(record, record_id):
    if record.get('PID'):
        current_app.logger.warning("Record already has a PID")
        return

    prefix = current_app.config.get('HANDLE_PREFIX')
    location = url_for('invenio_records_rest.recuuid_item', pid_value=record_id)
    checksum = compute_record_metadata_checksum(record)
    return handle_client.generate_and_register_handle(
        prefix=prefix, location=location, checksum=checksum)


def url_for_pid(pid):
    return "{}/{}".format(current_app.config.get('HANDLE_BASEURL'), pid)


def compute_record_metadata_checksum(record):
    import hashlib
    import json
    md5 = hashlib.md5()
    data = json.dumps(dict(record))
    md5.update(data)
    return 'md5:{}'.format(md5.hexdigest())
