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

"""B2share Storage Class."""

from flask import make_response
from invenio_files_rest.storage.pyfs import PyFSFileStorage, \
    pyfs_storage_factory


class B2ShareFileStorage(PyFSFileStorage):
    """Class for B2Share file storage interface to files."""
    def send_file(self, filename, **kwargs):
        """Redirect to the actual pid of the file."""
        headers = [('Location', self.fileurl)]
        return make_response(("Found", 302, headers))


def b2share_storage_factory(**kwargs):
    """Pass B2ShareFileStorage as parameter to pyfs_storage_factory."""
    if kwargs['fileinstance'].storage_class == 'B':
        kwargs['filestorage_class'] = B2ShareFileStorage
    return pyfs_storage_factory(**kwargs)
