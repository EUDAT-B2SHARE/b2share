# -*- coding: utf-8 -*-

## This file is part of B2SHARE.
## Copyright (C) 2013 EPCC, The University of Edinburgh.
##
## B2SHARE is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## B2SHARE is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with B2SHARE; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""B2SHARE selecting and getting files from B2DROP"""

import string
import time
import os
from dateutil.parser import parse
import urllib
import easywebdav

from flask import current_app
from b2share_upload_handler import encode_filename, get_extension, create_file_metadata

class B2DropClient:
    def __init__(self, username, password):
        self.host = 'b2drop.fz-juelich.de'
        self.protocol = 'https'
        self.path = '/remote.php/webdav/'
        self.rpath = self.path + '.'
        self.client = easywebdav.connect(self.host, \
            protocol=self.protocol, path=self.path, \
            username=username, password=password)

    def list(self, remote_path="/"):
        try:
            parent = remote_path
            if remote_path and remote_path.startswith(self.path):
                remote_path = remote_path[len(self.path):]
            ls = self.client.ls(remote_path)
            parent = cleanFile(ls[0])
            files = [cleanFile(f) for f in ls[1:]]
            return {"parent": parent, "files": files}, 200
        except easywebdav.OperationFailed as e:
            return error(e)

    def download(self, sub_id, remote_path, local_name=None):
        try:
            if remote_path and remote_path.startswith(self.path):
                remote_path = remote_path[len(self.path):]
            if not local_name:
                local_name = os.path.basename(remote_path)

            CFG_B2SHARE_UPLOAD_FOLDER = current_app.config.get(
                                    "CFG_B2SHARE_UPLOAD_FOLDER")
            if not os.path.exists(CFG_B2SHARE_UPLOAD_FOLDER):
                os.makedirs(CFG_B2SHARE_UPLOAD_FOLDER)

            # webdeposit also adds userid and deptype folders, we just use unique id
            upload_dir = os.path.join(CFG_B2SHARE_UPLOAD_FOLDER, sub_id)
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)

            safename, md5 = encode_filename(local_name)
            file_unique_name = safename + "_" + md5 + get_extension(safename)
            local_path = os.path.join(upload_dir, file_unique_name)

            self.client.download(remote_path, local_path)
            filename = create_file_metadata(upload_dir, local_name, file_unique_name, local_path)
            return { "filename": filename }, 200
        except easywebdav.OperationFailed as e:
            return error(e)


def error(e):
    err = e.reason
    if e.actual_code == 401:
        err = "Login failed"
    return {"error": err, "code": e.actual_code}, e.actual_code


def cleanFile(f):
    name_parts = string.split(f.name, "/")
    orig_name = name_parts[-1]
    if orig_name == "":
        orig_name = name_parts[-2]
    name = urllib.unquote(orig_name).decode('utf8')
    isdir = f.name.endswith("/")
    t = parse(f.mtime).timetuple()
    mtime = 1000*time.mktime(t)
    ret = {"path":f.name, "orig_name":orig_name, "name":name, "mtime":mtime, "isdir":isdir}
    if not isdir:
        ret["size"] = humansize(f.size)
    return ret


def humansize(v):
    if v < 1024:
        return "%5d B" % v
    elif v < 1024*1024:
        return "%5d KB" % (v/1024.0)
    elif v < 1024*1024*1024:
        return "%5d MB" % (v/(1024.0*1024.0))
    elif v < 1024*1024*1024*1024:
        return "%5d GB" % (v/(1024.0*1024.0*1024.0))
    elif v < 1024*1024*1024*1024:
        return "%5d TB" % (v/(1024.0*1024.0*1024.0*1024.0))
