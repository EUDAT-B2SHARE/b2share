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

"""B2SHARE selecting and getting files from B2DROP"""


import time
import dateutil.parser
import urllib.parse
import easywebdav2 as easywebdav

from flask import current_app

from .errors import ConnectionError, RemoteError


class B2DropClient(object):
    def __init__(self, host, protocol, path, username, password):
        self.host = host # 'b2drop.fz-juelich.de'
        self.protocol = protocol # 'https'
        if not path.endswith('/'):
            path += '/'
        self.path = path # '/remote.php/webdav/'
        self.rpath = self.path + '.'
        try:
            self.client = easywebdav.connect(self.host, \
                protocol=self.protocol, path=self.path, \
                username=username, password=password)
        except Exception as e:
            current_app.logger.error("Exception while connecting to b2drop",
                                       exc_info=True)
            raise ConnectionError("Exception while connecting to b2drop") from e

    def list(self, remote_path="/"):
        try:
            if remote_path and remote_path.startswith(self.path):
                remote_path = remote_path[len(self.path):]
            ls = self.client.ls(remote_path)
            parent = self.cleanFile(ls[0])
            files = [self.cleanFile(f) for f in ls[1:]]
            return {'parent':parent, 'files':files}
        except easywebdav.OperationFailed as e:
            current_app.logger.error("b2drop/webdav error", exc_info=True)
            raise RemoteError.from_webdav(e) from e

    def make_stream_object(self, remote_path):
        try:
            if remote_path and remote_path.startswith(self.path):
                remote_path = remote_path[len(self.path):]
            return B2DropStream(self.client, remote_path)
        except easywebdav.OperationFailed as e:
            current_app.logger.error("b2drop/webdav error", exc_info=True)
            raise RemoteError.from_webdav(e) from e

    def cleanFile(self, f):
        name_parts = f.name.split("/")
        orig_name = name_parts[-1]
        if orig_name == "":
            orig_name = name_parts[-2]
        name = urllib.parse.unquote(orig_name)
        path = f.name
        if path.startswith(self.path):
            path = path[len(self.path):]
        isdir = f.name.endswith("/")
        t = dateutil.parser.parse(f.mtime).timetuple()
        mtime = 1000*time.mktime(t)
        ret = {"path":path, "name":name, "date":mtime, "isdir":isdir}
        if not isdir:
            ret["size"] = f.size
        return ret


class B2DropStream(object):
    def __init__(self, webdav_client, remote_path):
        url = webdav_client.baseurl + str(remote_path).strip()
        self.response = webdav_client.session.request(
            'GET', url, allow_redirects=False, stream=True)
        if self.response.status_code != 200:
            current_app.logger.error("b2drop/webdav streaming error code {}".format(
                self.response.status_code))
            raise RemoteError('error while GETting b2drop file: {}'.format(url))
        self.content_iterator = None

    def length(self):
        if self.response.headers.get('Content-Encoding', '') == '':
            return int(self.response.headers['Content-Length'])
        else:
            # data is encoded (gzip, zip) thus the actual size is unknown
            return None

    def read(self, chunk_size):
        if not self.content_iterator:
            self.content_iterator = self.response.iter_content(chunk_size)
        try:
            return next(self.content_iterator)
        except StopIteration:
            return None
