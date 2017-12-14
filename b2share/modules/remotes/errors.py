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

"""error class(es) for remotes"""


from invenio_rest.errors import RESTException, FieldError


class UserError(RESTException):
    code = 400

    def __init__(self, description):
        super(UserError, self).__init__(description=description)


class ConnectionError(RESTException):
    code = 502

    def __init__(self, description):
        super(ConnectionError, self).__init__(description=description)


class RemoteError(RESTException):
    code = 502

    def __init__(self, description):
        super(RemoteError, self).__init__(description=description)

    @classmethod
    def from_webdav(cls, error):
        if error.actual_code == 401:
            return cls("Remote service authentication error")
        return cls("Remote service operation error")
